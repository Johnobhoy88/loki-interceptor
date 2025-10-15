"""
Async/parallel gate execution for improved performance
Uses concurrent.futures for parallel processing
"""
import concurrent.futures
from datetime import datetime
import hashlib

from core.universal_detectors import UniversalDetectors
from analyzers.pii_scanner import scan_pii
from core.cross_validation import CrossValidator
from core.gate_registry import gate_registry
from core.semantic_layer import SemanticLayer


class AsyncLOKIEngine:
    """
    Enhanced LOKI engine with parallel gate execution
    """

    def __init__(self, max_workers=4):
        """
        Args:
            max_workers: Maximum concurrent gate executions
        """
        self.modules = {}
        self.logger = None
        self.universal = UniversalDetectors()
        self.cross = CrossValidator()
        self.max_workers = max_workers
        self.semantic = SemanticLayer()

    def load_module(self, module_name):
        """Dynamically import module and register gates"""
        try:
            module_path = f"modules.{module_name}.module"
            imported = __import__(module_path, fromlist=[''])
            module_class_name = f"{module_name.title().replace('_', '')}Module"
            module_class = getattr(imported, module_class_name)
            module_obj = module_class()
            self.modules[module_name] = module_obj

            # Register gates in registry
            if hasattr(module_obj, 'gates'):
                for gate_id, gate_obj in module_obj.gates.items():
                    gate_version = getattr(gate_obj, 'version', '1.0.0')
                    gate_registry.register_gate(
                        module_id=module_name,
                        gate_id=gate_id,
                        gate_obj=gate_obj,
                        version=gate_version
                    )

            return True
        except Exception as e:
            print(f"Failed to load module {module_name}: {e}")
            return False

    def _execute_gate(self, gate_name, gate, text, document_type):
        """
        Execute a single gate (for parallel execution)

        Returns:
            tuple: (gate_name, result_dict)
        """
        try:
            result = gate.check(text, document_type)
            return (gate_name, result)
        except Exception as e:
            return (gate_name, {
                'status': 'ERROR',
                'severity': 'critical',
                'message': f'Gate error: {str(e)}'
            })

    def _execute_module_parallel(self, module_name, module, text, document_type):
        """
        Execute all gates in a module in parallel

        Args:
            module: Module object
            text: Document text
            document_type: Document type

        Returns:
            dict: Gate results
        """
        gates = getattr(module, 'gates', {})
        if not gates:
            return {}

        results = {}
        summary = {'pass': 0, 'fail': 0, 'warning': 0, 'error': 0, 'na': 0, 'semantic_hits': 0, 'needs_review': 0}

        # Execute gates in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all gate tasks
            future_to_gate = {
                executor.submit(self._execute_gate, gate_name, gate, text, document_type): (gate_name, gate)
                for gate_name, gate in gates.items()
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_gate):
                gate_name, gate = future_to_gate[future]
                _, result = future.result()
                normalized = self._normalize_gate_result(gate_name, gate, result)
                try:
                    normalized = self.semantic.post_process(module_name, gate_name, text, normalized)
                except Exception:
                    pass

                hits = normalized.get('semantic_hits') or []
                summary['semantic_hits'] += len(hits)
                if normalized.get('needs_human_review'):
                    summary['needs_review'] += 1

                results[gate_name] = normalized

                status = normalized.get('status', 'UNKNOWN').upper()
                if status == 'PASS':
                    summary['pass'] += 1
                elif status == 'FAIL':
                    summary['fail'] += 1
                elif status in ('WARNING', 'WARN'):
                    summary['warning'] += 1
                elif status in ('N/A', 'NA'):
                    summary['na'] += 1
                else:
                    summary['error'] += 1

        return results, summary

    def _normalize_gate_result(self, gate_name, gate_obj, result):
        """Ensure gate responses follow the standard schema."""
        legal_source = getattr(gate_obj, 'legal_source', 'Unknown')
        gate_version = getattr(gate_obj, 'version', '1.0.0')

        normalized = {
            'gate': gate_name,
            'version': gate_version,
            'legal_source': legal_source,
            'status': 'ERROR',
            'severity': 'critical',
            'message': 'Gate returned invalid response',
        }

        if isinstance(result, dict):
            status = (result.get('status') or 'UNKNOWN').upper()
            if status == 'WARN':
                status = 'WARNING'
            allowed_status = {'PASS', 'FAIL', 'WARNING', 'ERROR', 'N/A', 'NA'}
            if status not in allowed_status:
                status = 'ERROR'

            severity = (result.get('severity') or 'none').lower()
            if status in ('PASS', 'N/A', 'NA') and severity not in ('none', 'low'):
                severity = 'none'

            normalized.update(result)
            normalized['status'] = status
            normalized['severity'] = severity

            if 'message' not in normalized or not normalized['message']:
                normalized['message'] = 'Gate executed without message detail'
        else:
            normalized['detail'] = str(result)

        if 'legal_source' not in normalized or not normalized['legal_source']:
            normalized['legal_source'] = legal_source

        normalized['timestamp'] = datetime.utcnow().isoformat()
        return normalized

    def check_document(self, text, document_type, active_modules):
        """
        Run validation with parallel gate execution

        Args:
            text: Document text
            document_type: Type of document
            active_modules: List of module IDs to run

        Returns:
            dict: Validation results
        """
        try:
            if not isinstance(text, str):
                raise ValueError("text must be a string")

            if active_modules is None:
                active_modules = list(self.modules.keys())
            elif not isinstance(active_modules, (list, tuple, set)):
                active_modules = [active_modules]

            active_modules = [m for m in active_modules if m in self.modules]

            results = {
                'document_hash': self._hash_text(text or ''),
                'timestamp': datetime.utcnow().isoformat(),
                'modules': {},
                'analyzers': {},
                'overall_risk': None
            }

            # Run universal safety checks (sequential, fast)
            try:
                universal = {
                    'pii': self.universal.detect_pii(text, document_type=document_type),
                    'contradictions': self.universal.detect_contradictions(text),
                    'hallucinations': self.universal.detect_hallucination_markers(text),
                    'bias': self.universal.detect_bias(text),
                    'harm': self.universal.detect_harm(text),
                    'illegal_content': self.universal.detect_illegal_content(text),
                }
            except Exception as e:
                universal = {'error': str(e)}
            results['universal'] = universal

            # Run modules with parallel gate execution
            semantic_overview = {'total_hits': 0, 'needs_review': 0, 'modules': {}}

            for module_name in active_modules or []:
                try:
                    if module_name in self.modules:
                        module = self.modules[module_name]
                        gate_results, summary = self._execute_module_parallel(module_name, module, text, document_type)
                        results['modules'][module_name] = {
                            'name': getattr(module, 'name', module_name.title()),
                            'version': getattr(module, 'version', '1.0.0'),
                            'gates': gate_results,
                            'summary': summary
                        }
                        semantic_overview['total_hits'] += summary.get('semantic_hits', 0)
                        semantic_overview['needs_review'] += summary.get('needs_review', 0)
                        semantic_overview['modules'][module_name] = {
                            'hits': summary.get('semantic_hits', 0),
                            'needs_review': summary.get('needs_review', 0)
                        }
                except Exception as mod_err:
                    results['modules'][module_name] = {
                        'error': 'Module execution failed',
                        'detail': str(mod_err),
                        # NO TRACEBACK - security enhancement
                    }

            results['semantic'] = semantic_overview

            # Run analyzers (parallel where beneficial)
            results['analyzers'] = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    'pii': executor.submit(scan_pii, text, document_type=document_type),
                    'contradictions': executor.submit(self.universal.detect_contradictions, text),
                    'hallucinations': executor.submit(self.universal.detect_hallucination_markers, text),
                }

                for analyzer_name, future in futures.items():
                    try:
                        results['analyzers'][analyzer_name] = future.result(timeout=10)
                    except Exception as e:
                        results['analyzers'][analyzer_name] = {
                            'status': 'ERROR',
                            'message': 'Analyzer timeout or error'
                        }

            # Calculate risk
            results['overall_risk'] = self._calculate_risk(results)
            if results['overall_risk'] == 'LOW' and semantic_overview.get('needs_review'):
                results['overall_risk'] = 'MEDIUM'

            # Cross-module validation
            try:
                results['cross'] = self.cross.run(
                    text,
                    results.get('modules'),
                    results.get('universal'),
                    results.get('analyzers')
                )
            except Exception:
                results['cross'] = {'issues': []}

            return results

        except Exception as e:
            # Sanitized error response
            return {
                'error': 'Engine error',
                'message': 'Validation engine encountered an error',
                'timestamp': datetime.utcnow().isoformat(),
            }

    def _calculate_risk(self, results):
        """
        Calculate overall risk from gate results using weighted scoring

        Risk levels:
        - CRITICAL: 2+ critical FAILs OR 1 critical + 2+ high FAILs
        - HIGH: 1 critical FAIL OR 3+ high FAILs OR 1 high + 3+ medium FAILs
        - MEDIUM: 1-2 high FAILs OR 3+ medium FAILs OR 1 medium + warnings
        - LOW: All gates pass or only minor warnings
        """
        critical = 0
        high = 0
        medium = 0
        warnings = 0

        for module_result in (results.get('modules') or {}).values():
            gates = (module_result or {}).get('gates', {})
            if isinstance(gates, dict):
                gate_iter = gates.values()
            elif isinstance(gates, list):
                gate_iter = gates
            else:
                gate_iter = []

            for gate_result in gate_iter:
                if not isinstance(gate_result, dict):
                    continue
                severity = gate_result.get('severity', 'none')
                status = gate_result.get('status')
                if status == 'FAIL':
                    if severity == 'critical':
                        critical += 1
                    elif severity == 'high':
                        high += 1
                    elif severity == 'medium':
                        medium += 1
                elif status == 'WARNING':
                    warnings += 1

        # Include analyzer signals
        analyzers = results.get('analyzers') or {}
        for a in analyzers.values():
            if not isinstance(a, dict):
                continue
            status = a.get('status')
            sev = (a.get('severity') or 'none').lower()
            if status in ('FAIL', 'WARN'):
                if sev == 'critical':
                    critical += 1
                elif sev == 'high':
                    high += 1
                elif sev == 'medium':
                    medium += 1

        # Check universal detectors
        universal = results.get('universal') or {}
        if isinstance(universal, dict):
            for key, check_result in universal.items():
                if not isinstance(check_result, dict):
                    continue
                # Avoid double counting
                if key in (results.get('analyzers') or {}):
                    continue
                severity = (check_result.get('severity') or 'none').lower()
                if severity == 'critical':
                    critical += 1
                elif severity == 'high':
                    high += 1
                elif severity == 'medium':
                    medium += 1

        # Weighted risk calculation
        if critical >= 2 or (critical >= 1 and high >= 2):
            return 'CRITICAL'
        elif critical >= 1 or high >= 3 or (high >= 1 and medium >= 3):
            return 'HIGH'
        elif high >= 1 or medium >= 3 or (medium >= 1 and warnings >= 2):
            return 'MEDIUM'
        return 'LOW'

    def _hash_text(self, text):
        """SHA-256 hash for audit trail"""
        return hashlib.sha256((text or '').encode()).hexdigest()

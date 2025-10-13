from datetime import datetime
import hashlib
import traceback

from core.universal_detectors import UniversalDetectors
from analyzers.pii_scanner import scan_pii
from analyzers.bias_detector import detect_bias
from analyzers.hallucination_heuristic import assess_hallucination
from core.cross_validation import CrossValidator


class LOKIEngine:
    def __init__(self):
        self.modules = {}
        self.logger = None
        self.universal = UniversalDetectors()
        self.cross = CrossValidator()

    def load_module(self, module_name):
        """Dynamically import module from modules/{module_name}/module.py"""
        try:
            module_path = f"modules.{module_name}.module"
            imported = __import__(module_path, fromlist=[''])
            module_class_name = f"{module_name.title().replace('_', '')}Module"
            module_class = getattr(imported, module_class_name)
            self.modules[module_name] = module_class()
            return True
        except Exception as e:
            print(f"Failed to load module {module_name}: {e}")
            return False

    def check_document(self, text, document_type, active_modules):
        """Run validation on text using specified modules"""
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

            # Run universal safety checks first (for display)
            try:
                universal = {
                    'pii': self.universal.detect_pii(text, document_type=document_type),
                    'contradictions': self.universal.detect_contradictions(text),
                    'hallucinations': self.universal.detect_hallucination_markers(text),
                    'financial_promotions': self.universal.detect_financial_promotion_risk(text),
                    'consumer_duty': self.universal.detect_consumer_duty_gaps(text),
                }
            except Exception as e:
                universal = {'error': str(e)}
            results['universal'] = universal

            for module_name in active_modules or []:
                try:
                    if module_name in self.modules:
                        module = self.modules[module_name]
                        results['modules'][module_name] = module.execute(text, document_type)
                except Exception as mod_err:
                    results['modules'][module_name] = {
                        'error': 'Module execution failed',
                        'detail': str(mod_err),
                        'trace': traceback.format_exc(),
                    }

            # Run analyzers (primary for risk)
            results['analyzers'] = {}
            try:
                results['analyzers']['pii'] = scan_pii(text, document_type=document_type)
            except Exception as e:
                results['analyzers']['pii'] = {'status': 'ERROR', 'message': str(e)}
            try:
                results['analyzers']['contradictions'] = self.universal.detect_contradictions(text)
            except Exception as e:
                results['analyzers']['contradictions'] = {'status': 'ERROR', 'message': str(e)}
            try:
                results['analyzers']['hallucinations'] = self.universal.detect_hallucination_markers(text)
            except Exception as e:
                results['analyzers']['hallucinations'] = {'status': 'ERROR', 'message': str(e)}

            results['overall_risk'] = self._calculate_risk(results)

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
            return {
                'error': 'Engine error',
                'detail': str(e),
                'trace': traceback.format_exc(),
            }

    def _calculate_risk(self, results):
        """Calculate overall risk from gate results"""
        critical = 0
        high = 0

        for module_result in (results.get('modules') or {}).values():
            # module_result should be {'gates': {...}}
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

        # Include analyzer signals in risk
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

        # Check universal detectors
        universal = results.get('universal') or {}
        if isinstance(universal, dict):
            for key, check_result in universal.items():
                if not isinstance(check_result, dict):
                    continue
                # Avoid double counting if also present under analyzers
                if key in (results.get('analyzers') or {}):
                    continue
                severity = (check_result.get('severity') or 'none').lower()
                if severity == 'critical':
                    critical += 1
                elif severity == 'high':
                    high += 1

        if critical > 0:
            return 'CRITICAL'
        elif high > 0:
            return 'HIGH'
        return 'LOW'

    def _hash_text(self, text):
        """SHA-256 hash for audit trail"""
        return hashlib.sha256((text or '').encode()).hexdigest()

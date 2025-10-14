from datetime import datetime, timedelta

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
from core.async_engine import AsyncLOKIEngine  # Use async engine for better performance
from core.interceptor import AnthropicInterceptor, OpenAIInterceptor, GeminiInterceptor
from core.providers import ProviderRouter
from core.security import SecurityManager, RateLimiter, rate_limit, sanitize_error
from core.audit_log import AuditLogger
from core.cache import ValidationCache
from core.gate_registry import gate_registry
from core.corrector import DocumentCorrector  # NEW: Document correction engine

app = Flask(__name__)

# Register optional blueprints (placed after app creation to avoid circular imports)
try:
    from routes.analytics import bp as analytics_blueprint  # type: ignore

    app.register_blueprint(analytics_blueprint)
except Exception:
    # If analytics blueprint fails (e.g., during local dev without file) continue gracefully
    pass

# CORS - allow Cloudflare tunnel access
CORS(app, origins=['http://localhost:*', 'http://127.0.0.1:*', 'file://*', 'https://*.trycloudflare.com'])

# Request size limit (10MB max)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# Initialize security components
security = SecurityManager()
rate_limiter = RateLimiter()
audit_log = AuditLogger()
cache = ValidationCache(max_size=500, ttl_seconds=1800)  # 30min TTL

# Initialize async engine with parallel execution (max 4 concurrent gates)
engine = AsyncLOKIEngine(max_workers=4)
engine.load_module('hr_scottish')
engine.load_module('gdpr_uk')
engine.load_module('nda_uk')
engine.load_module('tax_uk')
engine.load_module('fca_uk')

anthropic_interceptor = AnthropicInterceptor(engine)
openai_interceptor = OpenAIInterceptor(engine)
gemini_interceptor = GeminiInterceptor(engine)
provider_router = ProviderRouter()
corrector = DocumentCorrector()  # NEW: Initialize corrector


# Error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify(sanitize_error('Request payload too large')), 413


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify(sanitize_error('Internal server error')), 500


@app.route('/', methods=['GET'])
def root():
    """Serve the frontend UI"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    """Serve frontend static files"""
    return send_from_directory('../frontend', path)


@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
@rate_limit(rate_limiter)
def health():
    """Enhanced health check with module validation"""
    try:
        # Basic health
        health_data = {
            'status': 'healthy',
            'modules': list(engine.modules.keys()),
            'modules_loaded': len(engine.modules),
        }

        # Optional: run smoke tests if ?detailed=true
        if request.args.get('detailed') == 'true':
            gate_counts = {}
            for module_name, module in engine.modules.items():
                gate_counts[module_name] = len(module.gates) if hasattr(module, 'gates') else 0

            health_data['gate_counts'] = gate_counts
            health_data['cache_stats'] = cache.get_stats()

        return jsonify(health_data)
    except Exception as e:
        print('Health check failed:', repr(e))
        return jsonify(sanitize_error(e)), 500


@app.route('/v1/messages', methods=['POST'])
@app.route('/api/v1/messages', methods=['POST'])
@rate_limit(rate_limiter)
def proxy_messages():
    try:
        data = request.json or {}
        api_key = request.headers.get('x-api-key')

        if not api_key:
            return jsonify(sanitize_error('Missing API key')), 401

        # Validate API key format
        if not security.validate_api_key_format('anthropic', api_key):
            return jsonify(sanitize_error('Invalid API key format')), 401

        # Extract optional modules for validation (default: all loaded modules)
        modules = data.pop('modules', None)

        # Use interceptor to call Anthropic and validate
        result = anthropic_interceptor.intercept_and_validate(data, api_key, modules)
        # Always return the response; UI will flag issues
        return jsonify(result), 200

    except Exception as e:
        return jsonify(sanitize_error(e)), 500


@app.route('/modules', methods=['GET'])
@app.route('/api/modules', methods=['GET'])
@rate_limit(rate_limiter)
def list_modules():
    """Return module catalog with dynamic introspection"""
    try:
        modules_list = []

        for module_id, module_obj in engine.modules.items():
            # Dynamic introspection
            gate_count = len(module_obj.gates) if hasattr(module_obj, 'gates') else 0
            module_name = getattr(module_obj, 'name', module_id.replace('_', ' ').title())
            module_version = getattr(module_obj, 'version', '1.0.0')

            modules_list.append({
                'id': module_id,
                'name': module_name,
                'version': module_version,
                'gates': gate_count
            })

        return jsonify({'modules': modules_list}), 200
    except Exception as e:
        return jsonify(sanitize_error(e)), 500


@app.route('/validate-document', methods=['POST'])
@app.route('/api/validate-document', methods=['POST'])
@cross_origin(origins="*")
@rate_limit(rate_limiter)
def validate_document():
    """Direct document validation with caching and audit logging"""
    try:
        data = request.json or {}
        text = data.get('text')
        document_type = (data.get('document_type') or 'unknown').lower()

        # Determine modules: explicit list if provided, else all loaded
        if 'modules' in (data or {}):
            modules = data.get('modules') or []
        else:
            modules = list(engine.modules.keys())

        if not text:
            return jsonify(sanitize_error('No text provided')), 400

        # Check cache first
        cached_result = cache.get(text, document_type, modules)
        if cached_result:
            cached_result['_cached'] = True
            return jsonify({
                'validation': cached_result,
                'risk': cached_result.get('overall_risk', 'LOW')
            })

        # Run validation
        validation = engine.check_document(
            text=text,
            document_type=document_type,
            active_modules=modules
        )

        # Cache result
        cache.set(text, document_type, modules, validation)

        # Audit log
        try:
            client_id = rate_limiter.get_client_id()
            audit_log.log_validation(text, document_type, modules, validation, client_id)
        except Exception:
            pass  # Don't fail request if audit fails

        if isinstance(validation, dict) and validation.get('overall_risk') is not None:
            risk = validation['overall_risk']
        else:
            risk = 'LOW'

        return jsonify({
            'validation': validation,
            'risk': risk
        })

    except Exception as e:
        return jsonify(sanitize_error(e)), 500


@app.route('/proxy', methods=['POST'])
@app.route('/api/proxy', methods=['POST'])
@rate_limit(rate_limiter)
def universal_proxy():
    try:
        data = request.get_json(force=True, silent=False)
    except Exception as e:
        return jsonify(sanitize_error('Invalid JSON payload')), 400

    provider = (data or {}).get('provider', 'anthropic')
    modules = (data or {}).get('modules')

    try:
        if provider == 'anthropic':
            api_key = request.headers.get('x-api-key') or request.headers.get('anthropic-api-key')
            if not api_key or not security.validate_api_key_format('anthropic', api_key):
                return jsonify(sanitize_error('Invalid API key')), 401
            result = anthropic_interceptor.intercept_and_validate(data, api_key, modules)
            return jsonify(result), 200

        elif provider == 'openai':
            api_key = request.headers.get('openai-api-key') or request.headers.get('x-openai-api-key') or request.headers.get('x-api-key')
            if not api_key or not security.validate_api_key_format('openai', api_key):
                return jsonify(sanitize_error('Invalid API key')), 401
            result = openai_interceptor.intercept(data, api_key, modules)
            status = 403 if isinstance(result, dict) and result.get('blocked') else 200
            return jsonify(result), status

        elif provider == 'gemini':
            api_key = request.headers.get('gemini-api-key')
            if not api_key or not security.validate_api_key_format('gemini', api_key):
                return jsonify(sanitize_error('Invalid API key')), 401
            result = gemini_interceptor.intercept(data, api_key, modules)
            status = 403 if isinstance(result, dict) and result.get('blocked') else 200
            return jsonify(result), status

        else:
            return jsonify(sanitize_error('Unsupported provider')), 400

    except Exception as e:
        return jsonify(sanitize_error(e)), 500


@app.route('/test-provider', methods=['POST'])
@app.route('/api/test-provider', methods=['POST'])
@rate_limit(rate_limiter)
def test_provider():
    data = request.json or {}
    provider = data.get('provider')
    api_key = data.get('api_key')
    prompt = data.get('prompt') or ''

    try:
        if not provider:
            return jsonify(sanitize_error('Missing provider')), 400
        if not api_key:
            return jsonify(sanitize_error('Missing api_key')), 400
        if not prompt:
            return jsonify(sanitize_error('Missing prompt')), 400

        # Validate API key format
        if not security.validate_api_key_format(provider, api_key):
            return jsonify(sanitize_error('Invalid API key format')), 401

        provider_router.configure_provider(provider, api_key)
        response_text = provider_router.call_provider(provider, prompt)

        validation = engine.check_document(
            text=response_text,
            document_type='ai_generated',
            active_modules=list(engine.modules.keys())
        )

        return jsonify({
            'provider': provider,
            'response': response_text,
            'validation': validation,
            'risk': validation.get('overall_risk')
        })
    except Exception as e:
        return jsonify(sanitize_error(e)), 500


# New endpoint: Audit stats
@app.route('/audit/stats', methods=['GET'])
@app.route('/api/audit/stats', methods=['GET'])
@rate_limit(rate_limiter)
def audit_stats():
    """Get audit log statistics"""
    try:
        since = request.args.get('since')  # ISO timestamp
        stats = audit_log.get_stats(since=since)
        return jsonify(stats), 200
    except Exception as e:
        return jsonify(sanitize_error(e)), 500


# Analytics endpoints
@app.route('/analytics/overview', methods=['GET'])
@app.route('/api/analytics/overview', methods=['GET'])
@rate_limit(rate_limiter)
def analytics_overview():
    try:
        window = request.args.get('window')
        overview = audit_log.get_overview(window_days=int(window)) if window else audit_log.get_overview()
        return jsonify(overview), 200
    except ValueError:
        return jsonify(sanitize_error('Invalid window value')), 400
    except Exception as e:
        return jsonify(sanitize_error(e)), 500


@app.route('/analytics/trends', methods=['GET'])
@app.route('/api/analytics/trends', methods=['GET'])
@rate_limit(rate_limiter)
def analytics_trends():
    try:
        days = request.args.get('days')
        trends = audit_log.get_risk_trends(days=int(days)) if days else audit_log.get_risk_trends()
        return jsonify(trends), 200
    except ValueError:
        return jsonify(sanitize_error('Invalid days value')), 400
    except Exception as e:
        return jsonify(sanitize_error(e)), 500


@app.route('/analytics/modules', methods=['GET'])
@app.route('/api/analytics/modules', methods=['GET'])
@rate_limit(rate_limiter)
def analytics_modules():
    try:
        window = request.args.get('window')
        since = None
        if window:
            try:
                window_days = max(1, min(int(window), 365))
            except ValueError:
                return jsonify(sanitize_error('Invalid window value')), 400
            since_dt = datetime.utcnow() - timedelta(days=window_days)
            since = since_dt.isoformat()

        modules = audit_log.get_module_performance(since=since)
        top_gates = audit_log.get_top_gate_failures(since=since)
        return jsonify({'modules': modules, 'top_gates': top_gates}), 200
    except Exception as e:
        return jsonify(sanitize_error(e)), 500


# New endpoint: Cache management
@app.route('/cache/stats', methods=['GET'])
@app.route('/api/cache/stats', methods=['GET'])
@rate_limit(rate_limiter)
def cache_stats():
    """Get cache statistics"""
    try:
        stats = cache.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify(sanitize_error(e)), 500


@app.route('/cache/clear', methods=['POST'])
@app.route('/api/cache/clear', methods=['POST'])
@rate_limit(rate_limiter)
def clear_cache():
    """Clear validation cache"""
    try:
        cache.clear()
        return jsonify({'message': 'Cache cleared', 'success': True}), 200
    except Exception as e:
        return jsonify(sanitize_error(e)), 500


# New endpoint: Gate registry
@app.route('/gates', methods=['GET'])
@app.route('/api/gates', methods=['GET'])
@rate_limit(rate_limiter)
def list_gates():
    """List all registered gates with version information"""
    try:
        module_id = request.args.get('module')

        if module_id:
            gates = gate_registry.get_module_gates(module_id)
        else:
            gates = gate_registry.list_all_gates()

        # Convert to serializable format
        gates_list = []
        for gate_id, gate_version in gates.items():
            gates_list.append({
                'id': gate_id,
                'version': gate_version.version,
                'module': gate_version.module_id,
                'severity': gate_version.severity,
                'legal_source': gate_version.legal_source,
                'active': gate_version.active,
                'deprecated': gate_version.deprecated,
                'deprecation_date': gate_version.deprecation_date,
                'replacement': gate_version.replacement_gate,
            })

        return jsonify({'gates': gates_list}), 200
    except Exception as e:
        return jsonify(sanitize_error(e)), 500


@app.route('/gates/deprecated', methods=['GET'])
@app.route('/api/gates/deprecated', methods=['GET'])
@rate_limit(rate_limiter)
def list_deprecated_gates():
    """List all deprecated gates"""
    try:
        deprecated = gate_registry.get_deprecated_gates()
        gates_list = [{
            'id': g.gate_id,
            'module': g.module_id,
            'deprecated_date': g.deprecation_date,
            'replacement': g.replacement_gate,
            'reason': g.changelog
        } for g in deprecated]

        return jsonify({'deprecated_gates': gates_list}), 200
    except Exception as e:
        return jsonify(sanitize_error(e)), 500


# NEW ENDPOINT: Document Correction
@app.route('/correct-document', methods=['POST'])
@app.route('/api/correct-document', methods=['POST'])
@cross_origin(origins="*")
@rate_limit(rate_limiter)
def correct_document():
    """
    Apply rule-based corrections to document based on validation results.
    NO AI - pure regex/string replacement corrections.
    """
    try:
        data = request.json or {}
        text = data.get('text')
        validation_results = data.get('validation_results')

        if not text:
            return jsonify(sanitize_error('No text provided')), 400

        if not validation_results:
            return jsonify(sanitize_error('No validation results provided')), 400

        # Apply corrections
        correction_result = corrector.correct_document(text, validation_results)

        return jsonify(correction_result), 200

    except Exception as e:
        return jsonify(sanitize_error(e)), 500


if __name__ == '__main__':
    print("LOKI Interceptor EXPERIMENTAL starting on port 5002...")
    print("Features enabled:")
    print("  - Rate limiting")
    print("  - API key validation")
    print("  - Request size limits (10MB)")
    print("  - CORS restrictions")
    print("  - Audit logging")
    print("  - Result caching (30min TTL)")
    print("  - Parallel gate execution")
    print("  - Gate version control")
    print()
    app.run(host='127.0.0.1', port=5002, debug=False)

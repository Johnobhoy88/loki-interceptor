import os
import time
from typing import Any, Dict, Optional

import requests
from flask import Blueprint, jsonify

bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

_CACHE: Dict[str, Any] = {"ts": 0.0, "data": None}
_CACHE_TTL_SECONDS = 300  # five minutes


def _fetch_observability_summary() -> Optional[Dict[str, Any]]:
    project_id = os.environ.get("VC_PROJECT_ID")
    api_token = os.environ.get("VC_API_TOKEN")
    team_id = os.environ.get("VC_TEAM_ID")

    if not project_id or not api_token:
        return None

    now = int(time.time())
    since = now - 86400  # past 24 hours

    url = f"https://api.vercel.com/v1/observability/projects/{project_id}/overview"
    params = {
        "from": since * 1000,
        "to": now * 1000,
    }
    if team_id:
        params["teamId"] = team_id

    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {api_token}", "Accept": "application/json"},
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    raw = resp.json() if resp.content else {}

    traffic = raw.get("traffic", {}) if isinstance(raw.get("traffic"), dict) else {}
    latency = raw.get("latency", {}) if isinstance(raw.get("latency"), dict) else {}
    errors = traffic.get("errors", {}) if isinstance(traffic.get("errors"), dict) else {}

    summary = {
        "raw": raw,
        "totalRequests": traffic.get("totalRequests")
            or traffic.get("requests")
            or traffic.get("total")
            or 0,
        "errorRate": traffic.get("errorRate")
            or traffic.get("rate")
            or errors.get("ratio")
            or 0,
        "latencyP95": latency.get("p95")
            or latency.get("percentile95")
            or latency.get("p95Ms")
            or 0,
        "error4xx": errors.get("4xx")
            or traffic.get("errors4xx")
            or 0,
        "error5xx": errors.get("5xx")
            or traffic.get("errors5xx")
            or 0,
    }

    return summary


@bp.route("/summary")
def summary():
    now = time.time()
    cached = _CACHE["data"]
    if cached and now - _CACHE["ts"] < _CACHE_TTL_SECONDS:
        return jsonify(cached)

    try:
        summary = _fetch_observability_summary()
    except requests.RequestException as exc:
        return jsonify({
            "error": "analytics_fetch_failed",
            "message": "Unable to retrieve analytics from Vercel.",
            "detail": str(exc),
        }), 502

    if summary is None:
        return jsonify({
            "error": "analytics_unavailable",
            "message": "Analytics credentials are not configured.",
        }), 503

    _CACHE["ts"] = now
    _CACHE["data"] = summary
    return jsonify(summary)

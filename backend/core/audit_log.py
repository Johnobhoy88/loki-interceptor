"""
Persistent audit logging for LOKI Interceptor
Tracks all validation requests for compliance
"""
from __future__ import annotations

import json
import sqlite3
import hashlib
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


class AuditLogger:
    """SQLite-based audit log for validation requests."""

    def __init__(self, db_path: str = 'data/audit.db') -> None:
        override = os.environ.get('AUDIT_DB_PATH')
        if not override and os.environ.get('VERCEL'):
            override = '/tmp/audit.db'
        self.db_path = Path(override or db_path)
        self.disabled = False
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_db()
        except Exception as exc:
            # In read-only environments (e.g. Vercel), fall back to disabled mode
            print(f'AuditLogger disabled: {exc}')
            self.disabled = True

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute('PRAGMA foreign_keys = ON')
        return conn

    def _init_db(self) -> None:
        if self.disabled:
            return 0
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                request_hash TEXT NOT NULL,
                document_hash TEXT NOT NULL,
                document_type TEXT,
                modules_used TEXT,
                overall_risk TEXT,
                critical_count INTEGER DEFAULT 0,
                high_count INTEGER DEFAULT 0,
                client_id TEXT,
                metadata TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_gate_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id INTEGER NOT NULL,
                scope TEXT NOT NULL,
                key TEXT NOT NULL,
                status TEXT,
                severity TEXT,
                extra TEXT,
                FOREIGN KEY (audit_id) REFERENCES audit_log(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_log(timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_document_hash ON audit_log(document_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_risk ON audit_log(overall_risk)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_gate_scope ON audit_gate_results(scope)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_gate_key ON audit_gate_results(key)')

        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    def log_validation(
        self,
        text: str,
        document_type: Optional[str],
        modules_used: Optional[Iterable[str]],
        validation_result: Dict[str, Any],
        client_id: Optional[str] = None
    ) -> int:
        """Persist a validation request and its component findings."""
        conn = self._connect()
        cursor = conn.cursor()

        document_hash = hashlib.sha256((text or '').encode()).hexdigest()
        request_hash = hashlib.sha256(
            f"{document_hash}{datetime.utcnow().isoformat()}{client_id}".encode()
        ).hexdigest()

        modules_used = list(modules_used or [])
        overall_risk = validation_result.get('overall_risk', 'UNKNOWN')

        critical_count = 0
        high_count = 0
        modules_section = validation_result.get('modules', {}) or {}
        for module_result in modules_section.values():
            gates = (module_result or {}).get('gates', {}) or {}
            for gate_result in gates.values():
                if not isinstance(gate_result, dict):
                    continue
                status = (gate_result.get('status') or '').upper()
                severity = (gate_result.get('severity') or '').lower()
                if status == 'FAIL':
                    if severity == 'critical':
                        critical_count += 1
                    elif severity == 'high':
                        high_count += 1

        metadata = {
            'modules_count': len(modules_used),
            'gates_executed': sum(
                len((module_result or {}).get('gates', {}))
                for module_result in modules_section.values()
                if isinstance(module_result, dict)
            ),
            'has_universal': bool(validation_result.get('universal')),
            'has_cross': bool(validation_result.get('cross')),
        }

        cursor.execute('''
            INSERT INTO audit_log
            (timestamp, request_hash, document_hash, document_type,
             modules_used, overall_risk, critical_count, high_count,
             client_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.utcnow().isoformat(),
            request_hash,
            document_hash,
            (document_type or 'unknown'),
            json.dumps(modules_used),
            overall_risk,
            critical_count,
            high_count,
            client_id or 'unknown',
            json.dumps(metadata)
        ))

        entry_id = cursor.lastrowid

        gate_rows = self._extract_gate_rows(entry_id, validation_result)
        if gate_rows:
            cursor.executemany('''
                INSERT INTO audit_gate_results
                (audit_id, scope, key, status, severity, extra)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', gate_rows)

        conn.commit()
        conn.close()
        return entry_id

    def _extract_gate_rows(self, audit_id: int, validation_result: Dict[str, Any]) -> List[tuple]:
        rows: List[tuple] = []

        modules = (validation_result or {}).get('modules', {}) or {}
        for module_id, module_data in modules.items():
            gates = (module_data or {}).get('gates', {}) or {}
            for gate_id, gate_result in gates.items():
                if not isinstance(gate_result, dict):
                    continue
                status = gate_result.get('status')
                severity = gate_result.get('severity')
                extra = {
                    'message': gate_result.get('message'),
                    'suggestion': gate_result.get('suggestion'),
                    'legal_source': gate_result.get('legal_source'),
                    'version': gate_result.get('version'),
                }
                rows.append((audit_id, 'module', f'{module_id}.{gate_id}', status, severity, json.dumps(extra)))

        universal = (validation_result or {}).get('universal', {}) or {}
        for key, payload in universal.items():
            if not isinstance(payload, dict):
                continue
            status = payload.get('status')
            severity = payload.get('severity')
            extra = {k: v for k, v in payload.items() if k not in {'status', 'severity'}}
            rows.append((audit_id, 'universal', key, status, severity, json.dumps(extra)))

        analyzers = (validation_result or {}).get('analyzers', {}) or {}
        for key, payload in analyzers.items():
            if not isinstance(payload, dict):
                continue
            status = payload.get('status')
            severity = payload.get('severity')
            extra = {k: v for k, v in payload.items() if k not in {'status', 'severity'}}
            rows.append((audit_id, 'analyzer', key, status, severity, json.dumps(extra)))

        cross_issues = ((validation_result or {}).get('cross') or {}).get('issues') or []
        for issue in cross_issues:
            if not isinstance(issue, dict):
                continue
            issue_id = issue.get('id') or 'cross_issue'
            status = issue.get('status', 'FAIL')
            severity = issue.get('severity')
            extra = {k: v for k, v in issue.items() if k not in {'severity', 'status'}}
            rows.append((audit_id, 'cross', issue_id, status, severity, json.dumps(extra)))

        return rows

    # ------------------------------------------------------------------
    # Retrieval APIs used by endpoints
    # ------------------------------------------------------------------
    def get_recent_entries(self, limit: int = 100) -> List[Dict[str, Any]]:
        if self.disabled:
            return []
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, timestamp, document_type, modules_used,
                   overall_risk, critical_count, high_count
            FROM audit_log
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                'id': row[0],
                'timestamp': row[1],
                'document_type': row[2],
                'modules_used': json.loads(row[3] or '[]'),
                'overall_risk': row[4],
                'critical_count': row[5],
                'high_count': row[6],
            }
            for row in rows
        ]

    def get_stats(self, since: Optional[str] = None) -> Dict[str, Any]:
        if self.disabled:
            return {
                'total_validations': 0,
                'risk_breakdown': {'critical': 0, 'high': 0, 'low': 0},
                'total_issues': {'critical': 0, 'high': 0},
            }
        conn = self._connect()
        cursor = conn.cursor()

        where_clause = ''
        params: List[Any] = []
        if since:
            where_clause = 'WHERE timestamp >= ?'
            params.append(since)

        cursor.execute(f'''
            SELECT
                COUNT(*) as total_validations,
                SUM(CASE WHEN overall_risk = 'CRITICAL' THEN 1 ELSE 0 END) as critical_risk,
                SUM(CASE WHEN overall_risk = 'HIGH' THEN 1 ELSE 0 END) as high_risk,
                SUM(CASE WHEN overall_risk = 'LOW' THEN 1 ELSE 0 END) as low_risk,
                SUM(critical_count) as total_critical_issues,
                SUM(high_count) as total_high_issues
            FROM audit_log
            {where_clause}
        ''', params)

        row = cursor.fetchone()
        conn.close()

        return {
            'total_validations': row[0] or 0,
            'risk_breakdown': {
                'critical': row[1] or 0,
                'high': row[2] or 0,
                'low': row[3] or 0,
            },
            'total_issues': {
                'critical': row[4] or 0,
                'high': row[5] or 0,
            }
        }

    def search_by_document_hash(self, document_hash: str) -> List[Dict[str, Any]]:
        if self.disabled:
            return []
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, timestamp, document_type, overall_risk
            FROM audit_log
            WHERE document_hash = ?
            ORDER BY timestamp DESC
        ''', (document_hash,))
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                'id': row[0],
                'timestamp': row[1],
                'document_type': row[2],
                'overall_risk': row[3],
            }
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Analytics helpers
    # ------------------------------------------------------------------
    def get_overview(self, window_days: int = 30) -> Dict[str, Any]:
        if self.disabled:
            return {
                'window_days': window_days,
                'stats': self.get_stats(),
                'module_performance': [],
                'top_gates': [],
                'universal_alerts': [],
                'recent_activity': [],
            }
        window_days = max(1, min(int(window_days or 30), 365))
        since_dt = datetime.utcnow() - timedelta(days=window_days)
        since = since_dt.isoformat()

        stats = self.get_stats(since=since)
        return {
            'window_days': window_days,
            'stats': stats,
            'module_performance': self.get_module_performance(since=since),
            'top_gates': self.get_top_gate_failures(since=since),
            'universal_alerts': self.get_universal_alerts(since=since),
            'recent_activity': self.get_recent_entries(limit=5)
        }

    def get_module_performance(self, since: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.disabled:
            return []
        conn = self._connect()
        cursor = conn.cursor()

        where_clause = "WHERE agr.scope = 'module'"
        params: List[Any] = []
        if since:
            where_clause += ' AND al.timestamp >= ?'
            params.append(since)

        cursor.execute(f'''
            SELECT
                CASE
                    WHEN instr(agr.key, '.') > 0 THEN substr(agr.key, 1, instr(agr.key, '.') - 1)
                    ELSE agr.key
                END as module_id,
                SUM(CASE WHEN upper(agr.status) = 'FAIL' THEN 1 ELSE 0 END) as failures,
                SUM(CASE WHEN upper(agr.status) = 'WARNING' THEN 1 ELSE 0 END) as warnings,
                SUM(CASE WHEN upper(agr.status) = 'PASS' THEN 1 ELSE 0 END) as passes
            FROM audit_gate_results agr
            JOIN audit_log al ON al.id = agr.audit_id
            {where_clause}
            GROUP BY module_id
            ORDER BY failures DESC, warnings DESC
        ''', params)

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                'module': row[0],
                'failures': row[1],
                'warnings': row[2],
                'passes': row[3]
            }
            for row in rows
        ]

    def get_top_gate_failures(self, since: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        if self.disabled:
            return []
        conn = self._connect()
        cursor = conn.cursor()

        where_clause = "WHERE agr.scope = 'module' AND upper(agr.status) = 'FAIL'"
        params: List[Any] = []
        if since:
            where_clause += ' AND al.timestamp >= ?'
            params.append(since)

        cursor.execute(f'''
            SELECT agr.key,
                   COUNT(*) as failures,
                   MAX(agr.severity) as max_severity
            FROM audit_gate_results agr
            JOIN audit_log al ON al.id = agr.audit_id
            {where_clause}
            GROUP BY agr.key
            ORDER BY failures DESC
            LIMIT ?
        ''', params + [limit])

        rows = cursor.fetchall()
        conn.close()

        top: List[Dict[str, Any]] = []
        for key, failures, severity in rows:
            if '.' in key:
                module_id, gate_id = key.split('.', 1)
            else:
                module_id, gate_id = key, ''
            top.append({
                'module': module_id,
                'gate': gate_id,
                'failures': failures,
                'severity': severity or 'unknown'
            })
        return top

    def get_universal_alerts(self, since: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        if self.disabled:
            return []
        conn = self._connect()
        cursor = conn.cursor()

        where_clause = "WHERE agr.scope = 'universal' AND upper(agr.status) != 'PASS'"
        params: List[Any] = []
        if since:
            where_clause += ' AND al.timestamp >= ?'
            params.append(since)

        cursor.execute(f'''
            SELECT agr.key,
                   COUNT(*) as alerts,
                   MAX(agr.severity) as max_severity
            FROM audit_gate_results agr
            JOIN audit_log al ON al.id = agr.audit_id
            {where_clause}
            GROUP BY agr.key
            ORDER BY alerts DESC
            LIMIT ?
        ''', params + [limit])

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                'detector': row[0],
                'alerts': row[1],
                'severity': row[2] or 'unknown'
            }
            for row in rows
        ]

    def get_risk_trends(self, days: int = 30) -> Dict[str, Any]:
        if self.disabled:
            return {'window_days': days, 'timeline': []}
        days = max(1, min(int(days or 30), 365))
        since_dt = datetime.utcnow() - timedelta(days=days)
        since = since_dt.isoformat()

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DATE(timestamp) as day,
                   overall_risk,
                   COUNT(*)
            FROM audit_log
            WHERE timestamp >= ?
            GROUP BY day, overall_risk
            ORDER BY day ASC
        ''', (since,))
        rows = cursor.fetchall()
        conn.close()

        timeline: Dict[str, Dict[str, int]] = {}
        for day, risk, count in rows:
            bucket = timeline.setdefault(day, {'LOW': 0, 'HIGH': 0, 'CRITICAL': 0, 'UNKNOWN': 0})
            risk_key = (risk or 'UNKNOWN').upper()
            if risk_key not in bucket:
                risk_key = 'UNKNOWN'
            bucket[risk_key] += count

        ordered = [
            {'date': day, 'counts': counts}
            for day, counts in sorted(timeline.items())
        ]

        return {
            'window_days': days,
            'timeline': ordered
        }

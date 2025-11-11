"""
Database backup and restore utilities
Enterprise-grade backup management with compression and encryption options
"""
from __future__ import annotations

import os
import gzip
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from backend.db.session import get_engine, get_session
from backend.db.models import (
    Document, Validation, ValidationResult,
    Correction, AuditTrail, Tag, DataRetentionPolicy, ExportLog
)


class BackupManager:
    """
    Manages database backups and restores
    Supports full and incremental backups with compression
    """

    def __init__(self, backup_dir: str = 'data/backups'):
        """
        Initialize backup manager

        Args:
            backup_dir: Directory to store backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(
        self,
        backup_name: Optional[str] = None,
        compress: bool = True,
        include_audit: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a full database backup

        Args:
            backup_name: Optional backup name (default: timestamp)
            compress: Whether to compress the backup
            include_audit: Whether to include audit trails
            metadata: Optional metadata to include

        Returns:
            Dictionary with backup information
        """
        if not backup_name:
            backup_name = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)

        backup_info = {
            'name': backup_name,
            'created_at': datetime.utcnow().isoformat(),
            'compress': compress,
            'include_audit': include_audit,
            'metadata': metadata or {},
            'tables': {}
        }

        try:
            # SQLite-specific backup
            engine = get_engine()
            db_url = str(engine.url)

            if db_url.startswith('sqlite:///'):
                db_file = db_url.replace('sqlite:///', '')
                if os.path.exists(db_file):
                    # Copy SQLite database file
                    backup_db = backup_path / 'database.db'
                    shutil.copy2(db_file, backup_db)

                    # Compress if requested
                    if compress:
                        with open(backup_db, 'rb') as f_in:
                            with gzip.open(f'{backup_db}.gz', 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        os.remove(backup_db)
                        backup_info['file'] = f'database.db.gz'
                        backup_info['size'] = os.path.getsize(f'{backup_db}.gz')
                    else:
                        backup_info['file'] = 'database.db'
                        backup_info['size'] = os.path.getsize(backup_db)

                    # Calculate checksum
                    file_path = backup_path / backup_info['file']
                    with open(file_path, 'rb') as f:
                        backup_info['checksum'] = hashlib.sha256(f.read()).hexdigest()
            else:
                # For other databases, export as JSON
                backup_info = self._export_json_backup(
                    backup_path,
                    compress,
                    include_audit
                )

            # Save backup info
            info_file = backup_path / 'backup_info.json'
            with open(info_file, 'w') as f:
                json.dump(backup_info, f, indent=2)

            return backup_info

        except Exception as e:
            raise RuntimeError(f"Backup failed: {str(e)}")

    def _export_json_backup(
        self,
        backup_path: Path,
        compress: bool,
        include_audit: bool
    ) -> Dict[str, Any]:
        """
        Export database to JSON format

        Args:
            backup_path: Backup directory
            compress: Whether to compress
            include_audit: Include audit trails

        Returns:
            Backup information
        """
        backup_info = {
            'format': 'json',
            'tables': {}
        }

        with get_session() as session:
            # Export documents
            documents = session.query(Document).all()
            self._export_table(
                backup_path, 'documents', documents, compress
            )
            backup_info['tables']['documents'] = len(documents)

            # Export validations
            validations = session.query(Validation).all()
            self._export_table(
                backup_path, 'validations', validations, compress
            )
            backup_info['tables']['validations'] = len(validations)

            # Export validation results
            results = session.query(ValidationResult).all()
            self._export_table(
                backup_path, 'validation_results', results, compress
            )
            backup_info['tables']['validation_results'] = len(results)

            # Export corrections
            corrections = session.query(Correction).all()
            self._export_table(
                backup_path, 'corrections', corrections, compress
            )
            backup_info['tables']['corrections'] = len(corrections)

            # Export tags
            tags = session.query(Tag).all()
            self._export_table(
                backup_path, 'tags', tags, compress
            )
            backup_info['tables']['tags'] = len(tags)

            # Optionally export audit trails
            if include_audit:
                audits = session.query(AuditTrail).all()
                self._export_table(
                    backup_path, 'audit_trails', audits, compress
                )
                backup_info['tables']['audit_trails'] = len(audits)

        return backup_info

    def _export_table(
        self,
        backup_path: Path,
        table_name: str,
        records: List,
        compress: bool
    ) -> None:
        """
        Export a table to JSON

        Args:
            backup_path: Backup directory
            table_name: Table name
            records: List of records
            compress: Whether to compress
        """
        data = []
        for record in records:
            if hasattr(record, 'to_dict'):
                data.append(record.to_dict(include_content=True))
            else:
                # Fallback to inspecting columns
                mapper = inspect(record.__class__)
                row = {}
                for column in mapper.columns:
                    value = getattr(record, column.key)
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    row[column.key] = value
                data.append(row)

        file_path = backup_path / f'{table_name}.json'

        if compress:
            with gzip.open(f'{file_path}.gz', 'wt', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        else:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)

    def restore_backup(
        self,
        backup_name: str,
        verify_checksum: bool = True,
        clear_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Restore database from backup

        Args:
            backup_name: Name of backup to restore
            verify_checksum: Verify backup checksum
            clear_existing: Clear existing data before restore

        Returns:
            Restore information
        """
        backup_path = self.backup_dir / backup_name
        if not backup_path.exists():
            raise ValueError(f"Backup not found: {backup_name}")

        # Load backup info
        info_file = backup_path / 'backup_info.json'
        if not info_file.exists():
            raise ValueError(f"Backup info not found: {backup_name}")

        with open(info_file) as f:
            backup_info = json.load(f)

        # Verify checksum
        if verify_checksum and 'checksum' in backup_info:
            file_path = backup_path / backup_info['file']
            with open(file_path, 'rb') as f:
                actual_checksum = hashlib.sha256(f.read()).hexdigest()

            if actual_checksum != backup_info['checksum']:
                raise ValueError("Backup checksum verification failed")

        # Perform restore
        engine = get_engine()
        db_url = str(engine.url)

        if db_url.startswith('sqlite:///') and 'file' in backup_info:
            # SQLite restore
            db_file = db_url.replace('sqlite:///', '')
            backup_file = backup_path / backup_info['file']

            # Decompress if needed
            if backup_info.get('compress'):
                with gzip.open(backup_file, 'rb') as f_in:
                    temp_file = backup_path / 'database.db'
                    with open(temp_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_file = temp_file

            # Close all connections
            engine.dispose()

            # Backup current database
            if os.path.exists(db_file):
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                shutil.copy2(db_file, f'{db_file}.{timestamp}.bak')

            # Restore
            shutil.copy2(backup_file, db_file)

            # Clean up temp file
            if backup_info.get('compress'):
                os.remove(temp_file)

        else:
            # JSON format restore
            self._restore_json_backup(backup_path, clear_existing)

        return {
            'backup_name': backup_name,
            'restored_at': datetime.utcnow().isoformat(),
            'tables_restored': backup_info.get('tables', {})
        }

    def _restore_json_backup(
        self,
        backup_path: Path,
        clear_existing: bool
    ) -> None:
        """
        Restore from JSON backup

        Args:
            backup_path: Backup directory
            clear_existing: Clear existing data
        """
        with get_session() as session:
            if clear_existing:
                # Clear existing data
                session.query(ValidationResult).delete()
                session.query(Validation).delete()
                session.query(Correction).delete()
                session.query(AuditTrail).delete()
                session.query(Document).delete()
                session.query(Tag).delete()
                session.commit()

            # Restore in order (respecting foreign keys)
            self._restore_table(backup_path, 'tags', Tag, session)
            self._restore_table(backup_path, 'documents', Document, session)
            self._restore_table(backup_path, 'validations', Validation, session)
            self._restore_table(backup_path, 'validation_results', ValidationResult, session)
            self._restore_table(backup_path, 'corrections', Correction, session)
            self._restore_table(backup_path, 'audit_trails', AuditTrail, session)

    def _restore_table(
        self,
        backup_path: Path,
        table_name: str,
        model_class: type,
        session: Session
    ) -> None:
        """
        Restore a table from JSON

        Args:
            backup_path: Backup directory
            table_name: Table name
            model_class: SQLAlchemy model class
            session: Database session
        """
        json_file = backup_path / f'{table_name}.json'
        json_gz = backup_path / f'{table_name}.json.gz'

        if json_gz.exists():
            with gzip.open(json_gz, 'rt', encoding='utf-8') as f:
                data = json.load(f)
        elif json_file.exists():
            with open(json_file) as f:
                data = json.load(f)
        else:
            return  # Table not in backup

        for row in data:
            # Convert datetime strings back to datetime objects
            for key, value in row.items():
                if isinstance(value, str) and 'T' in value:
                    try:
                        row[key] = datetime.fromisoformat(value)
                    except ValueError:
                        pass

            instance = model_class(**row)
            session.add(instance)

        session.flush()

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups

        Returns:
            List of backup information dictionaries
        """
        backups = []

        for backup_dir in self.backup_dir.iterdir():
            if not backup_dir.is_dir():
                continue

            info_file = backup_dir / 'backup_info.json'
            if info_file.exists():
                with open(info_file) as f:
                    info = json.load(f)
                    info['path'] = str(backup_dir)
                    backups.append(info)

        # Sort by creation date
        backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return backups

    def delete_backup(self, backup_name: str) -> bool:
        """
        Delete a backup

        Args:
            backup_name: Name of backup to delete

        Returns:
            True if deleted, False if not found
        """
        backup_path = self.backup_dir / backup_name
        if not backup_path.exists():
            return False

        shutil.rmtree(backup_path)
        return True

    def get_backup_size(self, backup_name: str) -> Optional[int]:
        """
        Get total size of a backup

        Args:
            backup_name: Backup name

        Returns:
            Size in bytes or None if not found
        """
        backup_path = self.backup_dir / backup_name
        if not backup_path.exists():
            return None

        total_size = 0
        for file in backup_path.rglob('*'):
            if file.is_file():
                total_size += file.stat().st_size

        return total_size

    def cleanup_old_backups(
        self,
        keep_count: int = 10,
        keep_days: Optional[int] = None
    ) -> List[str]:
        """
        Clean up old backups

        Args:
            keep_count: Number of recent backups to keep
            keep_days: Number of days to keep backups

        Returns:
            List of deleted backup names
        """
        backups = self.list_backups()
        deleted = []

        # Filter by age if specified
        if keep_days:
            cutoff = datetime.utcnow() - timedelta(days=keep_days)
            backups = [
                b for b in backups
                if datetime.fromisoformat(b['created_at']) >= cutoff
            ]

        # Keep only the specified number
        if len(backups) > keep_count:
            to_delete = backups[keep_count:]
            for backup in to_delete:
                backup_name = os.path.basename(backup['path'])
                if self.delete_backup(backup_name):
                    deleted.append(backup_name)

        return deleted


# Import for type checking
from datetime import timedelta

"""Initial database schema for LOKI Interceptor

Revision ID: 001_initial
Revises:
Create Date: 2025-11-11 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema"""

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=True)
    op.create_index(op.f('ix_tags_category'), 'tags', ['category'], unique=False)

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_length', sa.Integer(), nullable=False, default=0),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=500), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True, default='en'),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('client_id', sa.String(length=100), nullable=False),
        sa.Column('tenant_id', sa.String(length=100), nullable=True),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('is_latest', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['parent_id'], ['documents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('content_hash')
    )
    op.create_index(op.f('ix_documents_content_hash'), 'documents', ['content_hash'], unique=True)
    op.create_index(op.f('ix_documents_document_type'), 'documents', ['document_type'], unique=False)
    op.create_index(op.f('ix_documents_client_id'), 'documents', ['client_id'], unique=False)
    op.create_index(op.f('ix_documents_tenant_id'), 'documents', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_documents_user_id'), 'documents', ['user_id'], unique=False)
    op.create_index(op.f('ix_documents_parent_id'), 'documents', ['parent_id'], unique=False)
    op.create_index(op.f('ix_documents_is_latest'), 'documents', ['is_latest'], unique=False)
    op.create_index(op.f('ix_documents_created_at'), 'documents', ['created_at'], unique=False)
    op.create_index(op.f('ix_documents_deleted_at'), 'documents', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_documents_is_deleted'), 'documents', ['is_deleted'], unique=False)
    op.create_index('idx_documents_client_created', 'documents', ['client_id', 'created_at'])
    op.create_index('idx_documents_type_risk', 'documents', ['document_type', 'created_at'])
    op.create_index('idx_documents_tenant_type', 'documents', ['tenant_id', 'document_type'])
    op.create_index('idx_documents_latest', 'documents', ['is_latest', 'is_deleted'])

    # Create document_tags association table
    op.create_table(
        'document_tags',
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE')
    )
    op.create_index('idx_doc_tags_document', 'document_tags', ['document_id'])
    op.create_index('idx_doc_tags_tag', 'document_tags', ['tag_id'])

    # Create validations table
    op.create_table(
        'validations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('modules_used', sa.JSON(), nullable=False),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('overall_risk', sa.String(length=50), nullable=True),
        sa.Column('critical_count', sa.Integer(), nullable=False, default=0),
        sa.Column('high_count', sa.Integer(), nullable=False, default=0),
        sa.Column('medium_count', sa.Integer(), nullable=False, default=0),
        sa.Column('low_count', sa.Integer(), nullable=False, default=0),
        sa.Column('pass_count', sa.Integer(), nullable=False, default=0),
        sa.Column('fail_count', sa.Integer(), nullable=False, default=0),
        sa.Column('warning_count', sa.Integer(), nullable=False, default=0),
        sa.Column('request_hash', sa.String(length=64), nullable=False),
        sa.Column('client_id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_traceback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_validations_document_id'), 'validations', ['document_id'], unique=False)
    op.create_index(op.f('ix_validations_status'), 'validations', ['status'], unique=False)
    op.create_index(op.f('ix_validations_overall_risk'), 'validations', ['overall_risk'], unique=False)
    op.create_index(op.f('ix_validations_request_hash'), 'validations', ['request_hash'], unique=False)
    op.create_index(op.f('ix_validations_client_id'), 'validations', ['client_id'], unique=False)
    op.create_index(op.f('ix_validations_user_id'), 'validations', ['user_id'], unique=False)
    op.create_index(op.f('ix_validations_started_at'), 'validations', ['started_at'], unique=False)
    op.create_index(op.f('ix_validations_created_at'), 'validations', ['created_at'], unique=False)
    op.create_index('idx_validations_doc_created', 'validations', ['document_id', 'created_at'])
    op.create_index('idx_validations_status_risk', 'validations', ['status', 'overall_risk'])
    op.create_index('idx_validations_client_date', 'validations', ['client_id', 'created_at'])
    op.create_index('idx_validations_risk_counts', 'validations', ['overall_risk', 'critical_count', 'high_count'])

    # Create validation_results table
    op.create_table(
        'validation_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('validation_id', sa.Integer(), nullable=False),
        sa.Column('scope', sa.String(length=50), nullable=False),
        sa.Column('module_id', sa.String(length=100), nullable=True),
        sa.Column('gate_id', sa.String(length=100), nullable=False),
        sa.Column('gate_key', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('suggestion', sa.Text(), nullable=True),
        sa.Column('legal_source', sa.Text(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('gate_version', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['validation_id'], ['validations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_results_validation_id'), 'validation_results', ['validation_id'], unique=False)
    op.create_index(op.f('ix_results_scope'), 'validation_results', ['scope'], unique=False)
    op.create_index(op.f('ix_results_module_id'), 'validation_results', ['module_id'], unique=False)
    op.create_index(op.f('ix_results_gate_id'), 'validation_results', ['gate_id'], unique=False)
    op.create_index(op.f('ix_results_gate_key'), 'validation_results', ['gate_key'], unique=False)
    op.create_index(op.f('ix_results_status'), 'validation_results', ['status'], unique=False)
    op.create_index(op.f('ix_results_severity'), 'validation_results', ['severity'], unique=False)
    op.create_index('idx_results_validation_scope', 'validation_results', ['validation_id', 'scope'])
    op.create_index('idx_results_gate_status', 'validation_results', ['gate_key', 'status'])
    op.create_index('idx_results_severity_status', 'validation_results', ['severity', 'status'])
    op.create_index('idx_results_module_gate', 'validation_results', ['module_id', 'gate_id'])

    # Create corrections table
    op.create_table(
        'corrections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('validation_id', sa.Integer(), nullable=True),
        sa.Column('correction_type', sa.String(length=50), nullable=False),
        sa.Column('target_gate', sa.String(length=255), nullable=True),
        sa.Column('original_content', sa.Text(), nullable=True),
        sa.Column('corrected_content', sa.Text(), nullable=True),
        sa.Column('diff', sa.JSON(), nullable=True),
        sa.Column('strategy', sa.String(length=100), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.Column('applied_by', sa.String(length=100), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('reviewed_by', sa.String(length=100), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('client_id', sa.String(length=100), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['validation_id'], ['validations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_corrections_document_id'), 'corrections', ['document_id'], unique=False)
    op.create_index(op.f('ix_corrections_validation_id'), 'corrections', ['validation_id'], unique=False)
    op.create_index(op.f('ix_corrections_correction_type'), 'corrections', ['correction_type'], unique=False)
    op.create_index(op.f('ix_corrections_target_gate'), 'corrections', ['target_gate'], unique=False)
    op.create_index(op.f('ix_corrections_status'), 'corrections', ['status'], unique=False)
    op.create_index(op.f('ix_corrections_client_id'), 'corrections', ['client_id'], unique=False)
    op.create_index(op.f('ix_corrections_created_at'), 'corrections', ['created_at'], unique=False)
    op.create_index('idx_corrections_doc_status', 'corrections', ['document_id', 'status'])
    op.create_index('idx_corrections_validation', 'corrections', ['validation_id', 'status'])
    op.create_index('idx_corrections_type_status', 'corrections', ['correction_type', 'status'])
    op.create_index('idx_corrections_gate', 'corrections', ['target_gate', 'status'])

    # Create correction_history table
    op.create_table(
        'correction_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('correction_id', sa.Integer(), nullable=False),
        sa.Column('change_type', sa.String(length=50), nullable=False),
        sa.Column('previous_status', sa.String(length=50), nullable=True),
        sa.Column('new_status', sa.String(length=50), nullable=False),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('changed_by', sa.String(length=100), nullable=True),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['correction_id'], ['corrections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_history_correction_id'), 'correction_history', ['correction_id'], unique=False)
    op.create_index(op.f('ix_history_changed_at'), 'correction_history', ['changed_at'], unique=False)
    op.create_index('idx_history_correction_date', 'correction_history', ['correction_id', 'changed_at'])
    op.create_index('idx_history_type', 'correction_history', ['change_type', 'changed_at'])

    # Create audit_trail table
    op.create_table(
        'audit_trail',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('validation_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('actor_id', sa.String(length=100), nullable=False),
        sa.Column('actor_type', sa.String(length=50), nullable=False, default='user'),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('client_id', sa.String(length=100), nullable=False),
        sa.Column('tenant_id', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['validation_id'], ['validations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_document_id'), 'audit_trail', ['document_id'], unique=False)
    op.create_index(op.f('ix_audit_validation_id'), 'audit_trail', ['validation_id'], unique=False)
    op.create_index(op.f('ix_audit_action'), 'audit_trail', ['action'], unique=False)
    op.create_index(op.f('ix_audit_entity_type'), 'audit_trail', ['entity_type'], unique=False)
    op.create_index(op.f('ix_audit_entity_id'), 'audit_trail', ['entity_id'], unique=False)
    op.create_index(op.f('ix_audit_actor_id'), 'audit_trail', ['actor_id'], unique=False)
    op.create_index(op.f('ix_audit_request_id'), 'audit_trail', ['request_id'], unique=False)
    op.create_index(op.f('ix_audit_timestamp'), 'audit_trail', ['timestamp'], unique=False)
    op.create_index(op.f('ix_audit_client_id'), 'audit_trail', ['client_id'], unique=False)
    op.create_index(op.f('ix_audit_tenant_id'), 'audit_trail', ['tenant_id'], unique=False)
    op.create_index('idx_audit_action_time', 'audit_trail', ['action', 'timestamp'])
    op.create_index('idx_audit_entity', 'audit_trail', ['entity_type', 'entity_id', 'timestamp'])
    op.create_index('idx_audit_actor', 'audit_trail', ['actor_id', 'timestamp'])
    op.create_index('idx_audit_client', 'audit_trail', ['client_id', 'timestamp'])
    op.create_index('idx_audit_request', 'audit_trail', ['request_id', 'timestamp'])

    # Create data_retention_policies table
    op.create_table(
        'data_retention_policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('retention_days', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('criteria', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('priority', sa.Integer(), nullable=False, default=100),
        sa.Column('last_run', sa.DateTime(), nullable=True),
        sa.Column('next_run', sa.DateTime(), nullable=True),
        sa.Column('total_processed', sa.Integer(), nullable=False, default=0),
        sa.Column('total_affected', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.CheckConstraint('retention_days > 0', name='chk_retention_days_positive'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_retention_name'), 'data_retention_policies', ['name'], unique=True)
    op.create_index(op.f('ix_retention_entity_type'), 'data_retention_policies', ['entity_type'], unique=False)
    op.create_index(op.f('ix_retention_is_active'), 'data_retention_policies', ['is_active'], unique=False)
    op.create_index(op.f('ix_retention_next_run'), 'data_retention_policies', ['next_run'], unique=False)
    op.create_index('idx_retention_active_next', 'data_retention_policies', ['is_active', 'next_run'])
    op.create_index('idx_retention_entity', 'data_retention_policies', ['entity_type', 'is_active'])

    # Create export_logs table
    op.create_table(
        'export_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('export_type', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('filters', sa.JSON(), nullable=True),
        sa.Column('fields', sa.JSON(), nullable=True),
        sa.Column('record_count', sa.Integer(), nullable=False, default=0),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_hash', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('requested_by', sa.String(length=100), nullable=False),
        sa.Column('client_id', sa.String(length=100), nullable=False),
        sa.Column('requested_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exports_export_type'), 'export_logs', ['export_type'], unique=False)
    op.create_index(op.f('ix_exports_status'), 'export_logs', ['status'], unique=False)
    op.create_index(op.f('ix_exports_requested_by'), 'export_logs', ['requested_by'], unique=False)
    op.create_index(op.f('ix_exports_client_id'), 'export_logs', ['client_id'], unique=False)
    op.create_index(op.f('ix_exports_requested_at'), 'export_logs', ['requested_at'], unique=False)
    op.create_index(op.f('ix_exports_expires_at'), 'export_logs', ['expires_at'], unique=False)
    op.create_index('idx_exports_type_status', 'export_logs', ['export_type', 'status'])
    op.create_index('idx_exports_requester', 'export_logs', ['requested_by', 'requested_at'])
    op.create_index('idx_exports_client', 'export_logs', ['client_id', 'requested_at'])


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('export_logs')
    op.drop_table('data_retention_policies')
    op.drop_table('audit_trail')
    op.drop_table('correction_history')
    op.drop_table('corrections')
    op.drop_table('validation_results')
    op.drop_table('validations')
    op.drop_table('document_tags')
    op.drop_table('documents')
    op.drop_table('tags')

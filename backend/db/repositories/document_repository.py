"""
Document repository for CRUD operations on documents
"""
from __future__ import annotations

from typing import List, Optional
from datetime import datetime

from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import Session, joinedload

from backend.db.models import Document, DocumentType, Tag
from backend.db.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Repository for Document operations"""

    def __init__(self, session: Session):
        super().__init__(Document, session)

    def create_document(
        self,
        content: str,
        document_type: DocumentType,
        client_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        source: Optional[str] = None,
        language: str = 'en',
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Document:
        """
        Create a new document with automatic hash generation

        Args:
            content: Document content
            document_type: Type of document
            client_id: Client identifier
            title: Optional document title
            description: Optional description
            source: Optional source identifier
            language: Document language code
            tenant_id: Optional tenant ID
            user_id: Optional user ID
            metadata: Optional metadata dictionary

        Returns:
            Created document instance
        """
        return self.create(
            content=content,
            document_type=document_type,
            client_id=client_id,
            title=title,
            description=description,
            source=source,
            language=language,
            tenant_id=tenant_id,
            user_id=user_id,
            metadata_json=metadata,
            version=1,
            is_latest=True
        )

    def get_by_hash(self, content_hash: str) -> Optional[Document]:
        """
        Get document by content hash

        Args:
            content_hash: SHA-256 hash of content

        Returns:
            Document or None
        """
        return self.session.query(Document).filter(
            Document.content_hash == content_hash,
            Document.is_deleted == False
        ).first()

    def get_latest_version(self, document_id: int) -> Optional[Document]:
        """
        Get latest version of a document

        Args:
            document_id: Document ID or parent ID

        Returns:
            Latest version or None
        """
        # Check if the document itself is latest
        doc = self.get_by_id(document_id)
        if doc and doc.is_latest:
            return doc

        # Find latest version in the version chain
        return self.session.query(Document).filter(
            or_(
                Document.id == document_id,
                Document.parent_id == document_id
            ),
            Document.is_latest == True,
            Document.is_deleted == False
        ).first()

    def get_version_history(self, document_id: int) -> List[Document]:
        """
        Get all versions of a document

        Args:
            document_id: Document ID

        Returns:
            List of document versions ordered by version number
        """
        doc = self.get_by_id(document_id)
        if not doc:
            return []

        # Find root document
        root_id = doc.parent_id if doc.parent_id else doc.id

        # Get all versions
        return self.session.query(Document).filter(
            or_(
                Document.id == root_id,
                Document.parent_id == root_id
            )
        ).order_by(Document.version.asc()).all()

    def create_version(
        self,
        parent_id: int,
        content: str,
        user_id: Optional[str] = None
    ) -> Optional[Document]:
        """
        Create a new version of an existing document

        Args:
            parent_id: Parent document ID
            content: New content
            user_id: User creating the version

        Returns:
            New document version or None if parent not found
        """
        parent = self.get_by_id(parent_id)
        if not parent:
            return None

        # Mark parent as not latest
        parent.is_latest = False

        # Create new version
        new_version = self.create(
            content=content,
            document_type=parent.document_type,
            client_id=parent.client_id,
            title=parent.title,
            description=parent.description,
            source=parent.source,
            language=parent.language,
            tenant_id=parent.tenant_id,
            user_id=user_id or parent.user_id,
            metadata_json=parent.metadata_json,
            parent_id=parent_id,
            version=parent.version + 1,
            is_latest=True
        )

        self.flush()
        return new_version

    def search(
        self,
        query: str,
        client_id: Optional[str] = None,
        document_type: Optional[DocumentType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Document]:
        """
        Search documents by text and filters

        Args:
            query: Search query (searches in content, title, description)
            client_id: Filter by client
            document_type: Filter by document type
            start_date: Filter by creation date (from)
            end_date: Filter by creation date (to)
            limit: Maximum results
            offset: Results to skip

        Returns:
            List of matching documents
        """
        filters = [Document.is_deleted == False]

        # Text search
        if query:
            search_filter = or_(
                Document.content.contains(query),
                Document.title.contains(query) if Document.title else False,
                Document.description.contains(query) if Document.description else False
            )
            filters.append(search_filter)

        # Client filter
        if client_id:
            filters.append(Document.client_id == client_id)

        # Type filter
        if document_type:
            filters.append(Document.document_type == document_type)

        # Date range filters
        if start_date:
            filters.append(Document.created_at >= start_date)
        if end_date:
            filters.append(Document.created_at <= end_date)

        return self.session.query(Document).filter(
            and_(*filters)
        ).order_by(desc(Document.created_at)).offset(offset).limit(limit).all()

    def get_by_client(
        self,
        client_id: str,
        limit: int = 100,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[Document]:
        """
        Get documents for a specific client

        Args:
            client_id: Client identifier
            limit: Maximum results
            offset: Results to skip
            include_deleted: Include soft-deleted documents

        Returns:
            List of documents
        """
        query = self.session.query(Document).filter(
            Document.client_id == client_id
        )

        if not include_deleted:
            query = query.filter(Document.is_deleted == False)

        return query.order_by(desc(Document.created_at)).offset(offset).limit(limit).all()

    def get_by_tenant(
        self,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Document]:
        """
        Get documents for a specific tenant

        Args:
            tenant_id: Tenant identifier
            limit: Maximum results
            offset: Results to skip

        Returns:
            List of documents
        """
        return self.session.query(Document).filter(
            Document.tenant_id == tenant_id,
            Document.is_deleted == False
        ).order_by(desc(Document.created_at)).offset(offset).limit(limit).all()

    def get_with_validations(self, document_id: int) -> Optional[Document]:
        """
        Get document with eagerly loaded validations

        Args:
            document_id: Document ID

        Returns:
            Document with validations or None
        """
        return self.session.query(Document).options(
            joinedload(Document.validations)
        ).filter(
            Document.id == document_id,
            Document.is_deleted == False
        ).first()

    def add_tag(self, document_id: int, tag_name: str) -> bool:
        """
        Add a tag to a document

        Args:
            document_id: Document ID
            tag_name: Tag name

        Returns:
            True if successful, False otherwise
        """
        doc = self.get_by_id(document_id)
        if not doc:
            return False

        # Find or create tag
        tag = self.session.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            self.session.add(tag)

        # Add tag if not already present
        if tag not in doc.tags:
            doc.tags.append(tag)
            self.flush()

        return True

    def remove_tag(self, document_id: int, tag_name: str) -> bool:
        """
        Remove a tag from a document

        Args:
            document_id: Document ID
            tag_name: Tag name

        Returns:
            True if successful, False otherwise
        """
        doc = self.get_by_id(document_id)
        if not doc:
            return False

        tag = self.session.query(Tag).filter(Tag.name == tag_name).first()
        if tag and tag in doc.tags:
            doc.tags.remove(tag)
            self.flush()
            return True

        return False

    def get_statistics(self, client_id: Optional[str] = None) -> dict:
        """
        Get document statistics

        Args:
            client_id: Optional client filter

        Returns:
            Statistics dictionary
        """
        query = self.session.query(Document).filter(
            Document.is_deleted == False
        )

        if client_id:
            query = query.filter(Document.client_id == client_id)

        total = query.count()

        # Count by type
        type_counts = {}
        for doc_type in DocumentType:
            count = query.filter(Document.document_type == doc_type).count()
            if count > 0:
                type_counts[doc_type.value] = count

        # Get recent activity
        recent = query.order_by(desc(Document.created_at)).limit(5).all()

        return {
            'total_documents': total,
            'by_type': type_counts,
            'recent_documents': [doc.to_dict() for doc in recent]
        }

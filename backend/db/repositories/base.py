"""
Base repository with common CRUD operations
Generic repository pattern implementation
"""
from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from datetime import datetime

from sqlalchemy import desc, asc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.db.models import Base

T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    """
    Base repository providing common CRUD operations
    All specific repositories should inherit from this class
    """

    def __init__(self, model: Type[T], session: Session):
        """
        Initialize repository

        Args:
            model: SQLAlchemy model class
            session: Database session
        """
        self.model = model
        self.session = session

    def create(self, **kwargs) -> T:
        """
        Create a new entity

        Args:
            **kwargs: Entity attributes

        Returns:
            Created entity instance

        Raises:
            IntegrityError: If constraint violation occurs
        """
        try:
            entity = self.model(**kwargs)
            self.session.add(entity)
            self.session.flush()  # Flush to get ID without committing
            return entity
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Integrity constraint violation: {e}")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Database error: {e}")

    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Get entity by ID

        Args:
            entity_id: Entity primary key

        Returns:
            Entity instance or None if not found
        """
        return self.session.query(self.model).filter(
            self.model.id == entity_id
        ).first()

    def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None,
        ascending: bool = False
    ) -> List[T]:
        """
        Get all entities with optional pagination and sorting

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Column name to order by
            ascending: Sort order (default: descending)

        Returns:
            List of entities
        """
        query = self.session.query(self.model)

        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            order_column = getattr(self.model, order_by)
            query = query.order_by(asc(order_column) if ascending else desc(order_column))

        # Apply pagination
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        return query.all()

    def filter_by(self, **filters) -> List[T]:
        """
        Filter entities by attributes

        Args:
            **filters: Attribute filters

        Returns:
            List of matching entities
        """
        query = self.session.query(self.model)

        for attr, value in filters.items():
            if hasattr(self.model, attr):
                query = query.filter(getattr(self.model, attr) == value)

        return query.all()

    def update(self, entity_id: int, **updates) -> Optional[T]:
        """
        Update entity by ID

        Args:
            entity_id: Entity primary key
            **updates: Attributes to update

        Returns:
            Updated entity or None if not found

        Raises:
            ValueError: If update fails
        """
        entity = self.get_by_id(entity_id)
        if not entity:
            return None

        try:
            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            # Update timestamp if exists
            if hasattr(entity, 'updated_at'):
                entity.updated_at = datetime.utcnow()

            self.session.flush()
            return entity
        except (IntegrityError, SQLAlchemyError) as e:
            self.session.rollback()
            raise ValueError(f"Update failed: {e}")

    def delete(self, entity_id: int, soft_delete: bool = True) -> bool:
        """
        Delete entity by ID

        Args:
            entity_id: Entity primary key
            soft_delete: If True, mark as deleted instead of removing

        Returns:
            True if deleted, False if not found
        """
        entity = self.get_by_id(entity_id)
        if not entity:
            return False

        try:
            if soft_delete and hasattr(entity, 'is_deleted'):
                entity.is_deleted = True
                if hasattr(entity, 'deleted_at'):
                    entity.deleted_at = datetime.utcnow()
                self.session.flush()
            else:
                self.session.delete(entity)
                self.session.flush()

            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Delete failed: {e}")

    def count(self, **filters) -> int:
        """
        Count entities matching filters

        Args:
            **filters: Attribute filters

        Returns:
            Number of matching entities
        """
        query = self.session.query(self.model)

        for attr, value in filters.items():
            if hasattr(self.model, attr):
                query = query.filter(getattr(self.model, attr) == value)

        return query.count()

    def exists(self, entity_id: int) -> bool:
        """
        Check if entity exists

        Args:
            entity_id: Entity primary key

        Returns:
            True if exists, False otherwise
        """
        return self.session.query(
            self.session.query(self.model).filter(
                self.model.id == entity_id
            ).exists()
        ).scalar()

    def bulk_create(self, entities: List[Dict[str, Any]]) -> List[T]:
        """
        Bulk create entities

        Args:
            entities: List of entity attribute dictionaries

        Returns:
            List of created entities
        """
        try:
            instances = [self.model(**attrs) for attrs in entities]
            self.session.bulk_save_objects(instances, return_defaults=True)
            self.session.flush()
            return instances
        except (IntegrityError, SQLAlchemyError) as e:
            self.session.rollback()
            raise RuntimeError(f"Bulk create failed: {e}")

    def refresh(self, entity: T) -> T:
        """
        Refresh entity from database

        Args:
            entity: Entity to refresh

        Returns:
            Refreshed entity
        """
        self.session.refresh(entity)
        return entity

    def commit(self) -> None:
        """Commit current transaction"""
        try:
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Commit failed: {e}")

    def rollback(self) -> None:
        """Rollback current transaction"""
        self.session.rollback()

    def flush(self) -> None:
        """Flush pending changes"""
        try:
            self.session.flush()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RuntimeError(f"Flush failed: {e}")

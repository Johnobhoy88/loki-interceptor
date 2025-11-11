"""
Batch Corrector - Process multiple documents in batch

Features:
- Process up to 1000 documents per batch
- Parallel or sequential processing
- Progress tracking
- Error handling with partial results
- Webhook notifications
- Priority queuing
- Result aggregation
"""

import asyncio
import time
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid

try:
    from .correction_pipeline import CorrectionPipeline
    from .cache import Cache
except ImportError:
    from correction_pipeline import CorrectionPipeline
    from cache import Cache


class BatchStatus(str, Enum):
    """Batch processing status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIAL = "partial"  # Some documents failed
    FAILED = "failed"


class BatchPriority(str, Enum):
    """Batch priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class BatchCorrector:
    """
    Batch document correction processor

    Features:
    - Parallel processing with configurable concurrency
    - Progress tracking and status updates
    - Webhook notifications on completion
    - Error handling with partial results
    - Result aggregation and statistics
    """

    # Class-level batch storage (in production, use Redis or database)
    _batches: Dict[str, Dict] = {}
    _batch_lock = asyncio.Lock()

    def __init__(
        self,
        batch_id: str,
        priority: BatchPriority = BatchPriority.NORMAL,
        webhook_url: Optional[str] = None,
        max_concurrency: int = 10
    ):
        """
        Initialize batch corrector

        Args:
            batch_id: Unique batch identifier
            priority: Batch processing priority
            webhook_url: Webhook URL for completion notification
            max_concurrency: Maximum concurrent document processing
        """
        self.batch_id = batch_id
        self.priority = priority
        self.webhook_url = webhook_url
        self.max_concurrency = max_concurrency

        # Initialize cache for storing batch status
        self.cache = Cache()

        # Initialize batch status
        self._init_batch_status()

    def _init_batch_status(self):
        """Initialize batch status"""
        status = {
            'batch_id': self.batch_id,
            'status': BatchStatus.QUEUED.value,
            'priority': self.priority.value,
            'total_documents': 0,
            'completed': 0,
            'failed': 0,
            'in_progress': 0,
            'results': [],
            'errors': [],
            'started_at': datetime.utcnow(),
            'completed_at': None,
            'execution_time_ms': None,
            'webhook_url': self.webhook_url
        }

        # Store in cache
        BatchCorrector._batches[self.batch_id] = status

    async def process_batch(
        self,
        documents: List[Dict[str, Any]],
        parallel: bool = True,
        export_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Process batch of documents

        Args:
            documents: List of documents to process
                Each document: {'text': str, 'validation_results': dict, ...}
            parallel: Process documents in parallel
            export_format: Export format for results

        Returns:
            Batch processing result with all document results
        """
        start_time = time.time()

        # Update batch status
        await self._update_status({
            'status': BatchStatus.PROCESSING.value,
            'total_documents': len(documents)
        })

        try:
            if parallel:
                # Process documents in parallel with concurrency limit
                results = await self._process_parallel(documents, export_format)
            else:
                # Process documents sequentially
                results = await self._process_sequential(documents, export_format)

            # Calculate statistics
            successful = [r for r in results if r.get('status') == 'success']
            failed = [r for r in results if r.get('status') == 'error']

            # Determine final status
            if len(failed) == 0:
                final_status = BatchStatus.COMPLETED.value
            elif len(successful) > 0:
                final_status = BatchStatus.PARTIAL.value
            else:
                final_status = BatchStatus.FAILED.value

            # Calculate execution time
            execution_time_ms = (time.time() - start_time) * 1000

            # Update final status
            batch_result = {
                'batch_id': self.batch_id,
                'status': final_status,
                'total_documents': len(documents),
                'completed': len(successful),
                'failed': len(failed),
                'results': results,
                'started_at': BatchCorrector._batches[self.batch_id]['started_at'],
                'completed_at': datetime.utcnow(),
                'execution_time_ms': execution_time_ms,
                'statistics': self._calculate_statistics(results)
            }

            await self._update_status(batch_result)

            # Send webhook notification
            if self.webhook_url:
                await self._send_webhook_notification(batch_result)

            return batch_result

        except Exception as e:
            # Handle batch processing error
            error_result = {
                'status': BatchStatus.FAILED.value,
                'error': str(e),
                'completed_at': datetime.utcnow(),
                'execution_time_ms': (time.time() - start_time) * 1000
            }

            await self._update_status(error_result)

            # Send webhook notification
            if self.webhook_url:
                await self._send_webhook_notification(error_result)

            raise

    async def _process_parallel(
        self,
        documents: List[Dict[str, Any]],
        export_format: str
    ) -> List[Dict[str, Any]]:
        """Process documents in parallel with concurrency limit"""
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def process_with_semaphore(doc, index):
            async with semaphore:
                return await self._process_single_document(doc, index, export_format)

        # Process all documents concurrently
        tasks = [
            process_with_semaphore(doc, idx)
            for idx, doc in enumerate(documents)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error results
        processed_results = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'document_id': f"doc_{idx}",
                    'status': 'error',
                    'error': str(result)
                })
            else:
                processed_results.append(result)

        return processed_results

    async def _process_sequential(
        self,
        documents: List[Dict[str, Any]],
        export_format: str
    ) -> List[Dict[str, Any]]:
        """Process documents sequentially"""
        results = []

        for idx, doc in enumerate(documents):
            try:
                result = await self._process_single_document(doc, idx, export_format)
                results.append(result)

                # Update progress
                await self._update_status({
                    'completed': idx + 1
                })

            except Exception as e:
                results.append({
                    'document_id': f"doc_{idx}",
                    'status': 'error',
                    'error': str(e)
                })

        return results

    async def _process_single_document(
        self,
        document: Dict[str, Any],
        index: int,
        export_format: str
    ) -> Dict[str, Any]:
        """Process a single document"""
        doc_id = document.get('id', f"doc_{index}")
        text = document.get('text', '')
        validation_results = document.get('validation_results')
        document_type = document.get('document_type')

        try:
            # Create pipeline
            pipeline = CorrectionPipeline(
                algorithm_version="2.0.0",
                enable_caching=True
            )

            # Execute correction
            result = await pipeline.execute(
                text=text,
                validation_results=validation_results,
                document_type=document_type,
                auto_apply=document.get('auto_apply', True),
                confidence_threshold=document.get('confidence_threshold', 0.8)
            )

            # Format result
            return {
                'document_id': doc_id,
                'status': 'success',
                'original_text_length': len(text),
                'corrected_text_length': len(result.get('corrected_text', '')),
                'issues_found': result.get('issues_found', 0),
                'issues_corrected': result.get('issues_corrected', 0),
                'improvement_score': result.get('improvement_score', 0.0),
                'corrections': result.get('corrections', []),
                'execution_time_ms': result.get('pipeline_execution', {}).get('total_time_ms', 0),
                'result': result if export_format == 'full' else None
            }

        except Exception as e:
            return {
                'document_id': doc_id,
                'status': 'error',
                'error': str(e),
                'original_text_length': len(text) if text else 0
            }

    async def _update_status(self, updates: Dict[str, Any]):
        """Update batch status"""
        async with BatchCorrector._batch_lock:
            if self.batch_id in BatchCorrector._batches:
                BatchCorrector._batches[self.batch_id].update(updates)

    def _calculate_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate batch statistics"""
        successful = [r for r in results if r.get('status') == 'success']

        if not successful:
            return {
                'total_issues_found': 0,
                'total_issues_corrected': 0,
                'average_improvement_score': 0.0,
                'total_corrections': 0,
                'average_execution_time_ms': 0.0
            }

        total_issues_found = sum(r.get('issues_found', 0) for r in successful)
        total_issues_corrected = sum(r.get('issues_corrected', 0) for r in successful)
        total_corrections = sum(len(r.get('corrections', [])) for r in successful)
        avg_improvement = sum(r.get('improvement_score', 0.0) for r in successful) / len(successful)
        avg_execution_time = sum(r.get('execution_time_ms', 0.0) for r in successful) / len(successful)

        return {
            'total_issues_found': total_issues_found,
            'total_issues_corrected': total_issues_corrected,
            'average_improvement_score': round(avg_improvement, 3),
            'total_corrections': total_corrections,
            'average_execution_time_ms': round(avg_execution_time, 2),
            'success_rate': round(len(successful) / len(results), 3)
        }

    async def _send_webhook_notification(self, batch_result: Dict[str, Any]):
        """Send webhook notification on batch completion"""
        import httpx

        if not self.webhook_url:
            return

        try:
            payload = {
                'event': 'batch_completed',
                'batch_id': self.batch_id,
                'status': batch_result['status'],
                'total_documents': batch_result.get('total_documents', 0),
                'completed': batch_result.get('completed', 0),
                'failed': batch_result.get('failed', 0),
                'execution_time_ms': batch_result.get('execution_time_ms', 0),
                'statistics': batch_result.get('statistics', {}),
                'timestamp': datetime.utcnow().isoformat()
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=30.0
                )

                # Log webhook result
                if response.status_code >= 400:
                    print(f"Webhook notification failed: {response.status_code}")

        except Exception as e:
            print(f"Error sending webhook notification: {e}")

    @classmethod
    async def get_batch_status(cls, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get batch status"""
        async with cls._batch_lock:
            return cls._batches.get(batch_id)

    @classmethod
    async def list_batches(
        cls,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List batches with optional status filter"""
        async with cls._batch_lock:
            batches = list(cls._batches.values())

            # Filter by status
            if status:
                batches = [b for b in batches if b.get('status') == status]

            # Sort by started_at (most recent first)
            batches.sort(key=lambda b: b.get('started_at', datetime.min), reverse=True)

            # Limit results
            return batches[:limit]

    @classmethod
    async def cancel_batch(cls, batch_id: str) -> bool:
        """Cancel a queued or processing batch"""
        async with cls._batch_lock:
            if batch_id not in cls._batches:
                return False

            batch = cls._batches[batch_id]

            # Only cancel if not completed
            if batch['status'] in [BatchStatus.QUEUED.value, BatchStatus.PROCESSING.value]:
                batch['status'] = BatchStatus.FAILED.value
                batch['error'] = 'Cancelled by user'
                batch['completed_at'] = datetime.utcnow()
                return True

            return False

    @classmethod
    async def cleanup_old_batches(cls, max_age_hours: int = 24):
        """Clean up old completed batches"""
        async with cls._batch_lock:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            batch_ids_to_remove = []

            for batch_id, batch in cls._batches.items():
                completed_at = batch.get('completed_at')
                if completed_at and completed_at < cutoff_time:
                    batch_ids_to_remove.append(batch_id)

            for batch_id in batch_ids_to_remove:
                del cls._batches[batch_id]

            return len(batch_ids_to_remove)

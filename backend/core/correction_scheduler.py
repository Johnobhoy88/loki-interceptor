"""
Correction Scheduler - Async job scheduling and queue management

Features:
- Priority-based job queue
- Async job processing
- Job status tracking
- Webhook notifications
- Rate limiting and quota management
- Job history and analytics
"""

import asyncio
import time
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict

try:
    from .correction_pipeline import CorrectionPipeline
    from .cache import Cache
except ImportError:
    from correction_pipeline import CorrectionPipeline
    from cache import Cache


class JobStatus(str, Enum):
    """Job status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority(str, Enum):
    """Job priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# Priority weights for queue ordering
PRIORITY_WEIGHTS = {
    JobPriority.LOW: 1,
    JobPriority.NORMAL: 10,
    JobPriority.HIGH: 50,
    JobPriority.URGENT: 100
}


class CorrectionScheduler:
    """
    Async job scheduler with priority queue

    Features:
    - Priority-based scheduling
    - Concurrent job processing
    - Job status tracking
    - Webhook notifications
    - Rate limiting
    - Quota management
    """

    # Class-level storage (in production, use Redis or database)
    _jobs: Dict[str, Dict] = {}
    _job_queue: List[str] = []
    _job_lock = asyncio.Lock()
    _processing_lock = asyncio.Lock()
    _is_processing = False

    # Rate limiting and quota
    _user_quotas: Dict[str, Dict] = defaultdict(lambda: {
        'requests_used': 0,
        'requests_limit': 1000,
        'reset_at': datetime.utcnow() + timedelta(days=1),
        'rate_limit_per_minute': 60
    })
    _user_requests: Dict[str, List[datetime]] = defaultdict(list)

    def __init__(self, max_workers: int = 5):
        """
        Initialize scheduler

        Args:
            max_workers: Maximum concurrent jobs
        """
        self.max_workers = max_workers
        self.cache = Cache()

    async def schedule_job(
        self,
        job_id: str,
        text: str,
        validation_results: Optional[Dict] = None,
        priority: JobPriority = JobPriority.NORMAL,
        webhook_url: Optional[str] = None,
        callback_data: Optional[Dict] = None,
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Schedule a correction job

        Args:
            job_id: Unique job identifier
            text: Document text
            validation_results: Validation results
            priority: Job priority
            webhook_url: Webhook URL for completion notification
            callback_data: Additional callback data
            user_id: User identifier for quota management

        Returns:
            Job information
        """
        # Check rate limit
        if not await self._check_rate_limit(user_id):
            raise ValueError(f"Rate limit exceeded for user {user_id}")

        # Check quota
        if not await self._check_quota(user_id):
            raise ValueError(f"Quota exceeded for user {user_id}")

        # Create job
        job = {
            'job_id': job_id,
            'user_id': user_id,
            'text': text,
            'validation_results': validation_results,
            'priority': priority.value,
            'priority_weight': PRIORITY_WEIGHTS[priority],
            'webhook_url': webhook_url,
            'callback_data': callback_data,
            'status': JobStatus.QUEUED.value,
            'progress': 0.0,
            'stage': None,
            'result': None,
            'error': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'started_at': None,
            'completed_at': None,
            'estimated_completion': self._estimate_completion_time()
        }

        async with CorrectionScheduler._job_lock:
            # Store job
            CorrectionScheduler._jobs[job_id] = job

            # Add to queue (sorted by priority)
            CorrectionScheduler._job_queue.append(job_id)
            CorrectionScheduler._job_queue.sort(
                key=lambda jid: CorrectionScheduler._jobs[jid]['priority_weight'],
                reverse=True
            )

        # Update quota
        await self._increment_quota(user_id)

        # Start processing if not already running
        asyncio.create_task(self._process_queue())

        return {
            'job_id': job_id,
            'status': job['status'],
            'created_at': job['created_at'],
            'updated_at': job['updated_at'],
            'estimated_completion': job['estimated_completion']
        }

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status"""
        async with CorrectionScheduler._job_lock:
            job = CorrectionScheduler._jobs.get(job_id)

            if not job:
                return None

            return {
                'job_id': job['job_id'],
                'status': job['status'],
                'progress': job['progress'],
                'stage': job['stage'],
                'result': job['result'],
                'error': job['error'],
                'created_at': job['created_at'],
                'updated_at': job['updated_at'],
                'started_at': job.get('started_at'),
                'completed_at': job.get('completed_at'),
                'estimated_completion': job.get('estimated_completion')
            }

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a queued job"""
        async with CorrectionScheduler._job_lock:
            job = CorrectionScheduler._jobs.get(job_id)

            if not job:
                return False

            # Can only cancel queued jobs
            if job['status'] == JobStatus.QUEUED.value:
                job['status'] = JobStatus.CANCELLED.value
                job['updated_at'] = datetime.utcnow()
                job['completed_at'] = datetime.utcnow()

                # Remove from queue
                if job_id in CorrectionScheduler._job_queue:
                    CorrectionScheduler._job_queue.remove(job_id)

                return True

            return False

    async def _process_queue(self):
        """Process job queue"""
        # Ensure only one processing loop runs
        async with CorrectionScheduler._processing_lock:
            if CorrectionScheduler._is_processing:
                return

            CorrectionScheduler._is_processing = True

        try:
            while True:
                # Get next job
                job_id = await self._get_next_job()

                if not job_id:
                    # No more jobs
                    break

                # Process job
                await self._process_job(job_id)

                # Small delay to prevent tight loop
                await asyncio.sleep(0.1)

        finally:
            async with CorrectionScheduler._processing_lock:
                CorrectionScheduler._is_processing = False

    async def _get_next_job(self) -> Optional[str]:
        """Get next job from queue"""
        async with CorrectionScheduler._job_lock:
            if not CorrectionScheduler._job_queue:
                return None

            # Get highest priority job
            job_id = CorrectionScheduler._job_queue.pop(0)
            return job_id

    async def _process_job(self, job_id: str):
        """Process a single job"""
        async with CorrectionScheduler._job_lock:
            job = CorrectionScheduler._jobs.get(job_id)

            if not job:
                return

            # Update status
            job['status'] = JobStatus.PROCESSING.value
            job['started_at'] = datetime.utcnow()
            job['updated_at'] = datetime.utcnow()

        try:
            # Create pipeline
            pipeline = CorrectionPipeline(
                algorithm_version="2.0.0",
                enable_caching=True
            )

            # Execute correction
            result = await pipeline.execute(
                text=job['text'],
                validation_results=job['validation_results']
            )

            # Update job with result
            async with CorrectionScheduler._job_lock:
                job['status'] = JobStatus.COMPLETED.value
                job['result'] = result
                job['progress'] = 100.0
                job['completed_at'] = datetime.utcnow()
                job['updated_at'] = datetime.utcnow()

            # Send webhook notification
            if job['webhook_url']:
                await self._send_webhook(job)

        except Exception as e:
            # Update job with error
            async with CorrectionScheduler._job_lock:
                job['status'] = JobStatus.FAILED.value
                job['error'] = str(e)
                job['completed_at'] = datetime.utcnow()
                job['updated_at'] = datetime.utcnow()

            # Send webhook notification
            if job['webhook_url']:
                await self._send_webhook(job)

    async def _send_webhook(self, job: Dict):
        """Send webhook notification"""
        import httpx

        try:
            payload = {
                'event': 'job_completed',
                'job_id': job['job_id'],
                'status': job['status'],
                'result': job.get('result'),
                'error': job.get('error'),
                'callback_data': job.get('callback_data'),
                'timestamp': datetime.utcnow().isoformat()
            }

            async with httpx.AsyncClient() as client:
                await client.post(
                    job['webhook_url'],
                    json=payload,
                    timeout=30.0
                )

        except Exception as e:
            print(f"Error sending webhook: {e}")

    def _estimate_completion_time(self) -> datetime:
        """Estimate job completion time"""
        # Simple estimation: 5 seconds per job in queue
        queue_length = len(CorrectionScheduler._job_queue)
        estimated_seconds = queue_length * 5

        return datetime.utcnow() + timedelta(seconds=estimated_seconds)

    async def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user is within rate limit"""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)

        # Clean old requests
        CorrectionScheduler._user_requests[user_id] = [
            req_time for req_time in CorrectionScheduler._user_requests[user_id]
            if req_time > minute_ago
        ]

        # Check limit
        quota = CorrectionScheduler._user_quotas[user_id]
        recent_requests = len(CorrectionScheduler._user_requests[user_id])

        if recent_requests >= quota['rate_limit_per_minute']:
            return False

        # Add current request
        CorrectionScheduler._user_requests[user_id].append(now)
        return True

    async def _check_quota(self, user_id: str) -> bool:
        """Check if user has remaining quota"""
        quota = CorrectionScheduler._user_quotas[user_id]

        # Reset quota if expired
        if datetime.utcnow() > quota['reset_at']:
            quota['requests_used'] = 0
            quota['reset_at'] = datetime.utcnow() + timedelta(days=1)

        # Check limit
        return quota['requests_used'] < quota['requests_limit']

    async def _increment_quota(self, user_id: str):
        """Increment user quota"""
        quota = CorrectionScheduler._user_quotas[user_id]
        quota['requests_used'] += 1

    async def get_quota_info(self, user_id: str) -> Dict[str, Any]:
        """Get quota information for user"""
        quota = CorrectionScheduler._user_quotas[user_id]

        return {
            'user_id': user_id,
            'requests_used': quota['requests_used'],
            'requests_limit': quota['requests_limit'],
            'requests_remaining': quota['requests_limit'] - quota['requests_used'],
            'reset_at': quota['reset_at'],
            'rate_limit_per_minute': quota['rate_limit_per_minute']
        }

    @classmethod
    async def get_queue_stats(cls) -> Dict[str, Any]:
        """Get queue statistics"""
        async with cls._job_lock:
            total_jobs = len(cls._jobs)
            queued = sum(1 for j in cls._jobs.values() if j['status'] == JobStatus.QUEUED.value)
            processing = sum(1 for j in cls._jobs.values() if j['status'] == JobStatus.PROCESSING.value)
            completed = sum(1 for j in cls._jobs.values() if j['status'] == JobStatus.COMPLETED.value)
            failed = sum(1 for j in cls._jobs.values() if j['status'] == JobStatus.FAILED.value)

            # Priority breakdown
            priority_breakdown = defaultdict(int)
            for job in cls._jobs.values():
                if job['status'] == JobStatus.QUEUED.value:
                    priority_breakdown[job['priority']] += 1

            return {
                'total_jobs': total_jobs,
                'queued': queued,
                'processing': processing,
                'completed': completed,
                'failed': failed,
                'queue_length': len(cls._job_queue),
                'priority_breakdown': dict(priority_breakdown),
                'is_processing': cls._is_processing
            }

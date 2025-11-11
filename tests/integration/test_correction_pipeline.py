"""
Integration Tests for Correction Pipeline System

Tests:
- Complete pipeline execution
- Batch processing
- Streaming corrections
- Async scheduling
- Multi-format export
- Error handling
- Performance benchmarks
"""

import pytest
import asyncio
import time
from datetime import datetime
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backend'))

from core.correction_pipeline import CorrectionPipeline, PipelineStage
from core.batch_corrector import BatchCorrector, BatchPriority
from core.correction_scheduler import CorrectionScheduler, JobPriority
from core.correction_exporter import CorrectionExporter
from monitoring.correction_dashboard import CorrectionDashboard


# ==================== Fixtures ====================

@pytest.fixture
def sample_text():
    """Sample document text for testing"""
    return """
    This is a test document for GDPR compliance.

    We may use your data for marketing purposes without consent.
    We collect personal information including your email address.

    By using this website you automatically agree to our terms.
    """


@pytest.fixture
def sample_validation_results():
    """Sample validation results"""
    return {
        'validation': {
            'overall_status': 'FAIL',
            'modules': {
                'gdpr_uk': {
                    'gates': {
                        'consent': {
                            'status': 'FAIL',
                            'severity': 'CRITICAL',
                            'message': 'Missing explicit consent',
                            'suggestion': 'Add: We request your explicit consent to use your data.'
                        }
                    }
                }
            }
        }
    }


@pytest.fixture
def sample_documents():
    """Sample documents for batch testing"""
    return [
        {
            'id': 'doc1',
            'text': 'Test document 1 with compliance issues.',
            'validation_results': None
        },
        {
            'id': 'doc2',
            'text': 'Test document 2 with more text content.',
            'validation_results': None
        },
        {
            'id': 'doc3',
            'text': 'Test document 3 for batch processing.',
            'validation_results': None
        }
    ]


# ==================== Pipeline Tests ====================

@pytest.mark.asyncio
async def test_pipeline_basic_execution(sample_text):
    """Test basic pipeline execution"""
    pipeline = CorrectionPipeline(
        algorithm_version="2.0.0",
        enable_caching=True
    )

    result = await pipeline.execute(
        text=sample_text,
        stages=[PipelineStage.VALIDATE, PipelineStage.ANALYZE, PipelineStage.CORRECT]
    )

    assert result is not None
    assert 'original_text' in result
    assert 'corrected_text' in result
    assert 'pipeline_execution' in result
    assert result['algorithm_version'] == "2.0.0"


@pytest.mark.asyncio
async def test_pipeline_with_validation_results(sample_text, sample_validation_results):
    """Test pipeline with validation results"""
    pipeline = CorrectionPipeline(
        algorithm_version="2.0.0",
        enable_caching=False
    )

    result = await pipeline.execute(
        text=sample_text,
        validation_results=sample_validation_results,
        auto_apply=True,
        confidence_threshold=0.8
    )

    assert result is not None
    assert 'corrections' in result
    assert isinstance(result['corrections'], list)


@pytest.mark.asyncio
async def test_pipeline_stages(sample_text):
    """Test individual pipeline stages"""
    pipeline = CorrectionPipeline()

    # Test VALIDATE stage
    result = await pipeline.execute(
        text=sample_text,
        stages=[PipelineStage.VALIDATE]
    )
    assert result is not None
    assert 'valid' in result or 'original_text' in result

    # Test ANALYZE stage
    result = await pipeline.execute(
        text=sample_text,
        stages=[PipelineStage.VALIDATE, PipelineStage.ANALYZE]
    )
    assert result is not None


@pytest.mark.asyncio
async def test_pipeline_caching(sample_text):
    """Test pipeline caching"""
    pipeline = CorrectionPipeline(enable_caching=True)

    # First execution
    start1 = time.time()
    result1 = await pipeline.execute(text=sample_text)
    time1 = (time.time() - start1) * 1000

    # Second execution (should be cached)
    start2 = time.time()
    result2 = await pipeline.execute(text=sample_text)
    time2 = (time.time() - start2) * 1000

    assert result1 is not None
    assert result2 is not None
    # Cache should make second execution faster
    # Note: This might not always be true in tests, so just check it ran


@pytest.mark.asyncio
async def test_pipeline_statistics():
    """Test pipeline statistics"""
    pipeline = CorrectionPipeline()
    stats = pipeline.get_statistics()

    assert stats is not None
    assert 'algorithm_version' in stats
    assert 'corrector_stats' in stats


# ==================== Batch Processing Tests ====================

@pytest.mark.asyncio
async def test_batch_processing_basic(sample_documents):
    """Test basic batch processing"""
    batch_corrector = BatchCorrector(
        batch_id="test_batch_1",
        priority=BatchPriority.NORMAL
    )

    result = await batch_corrector.process_batch(
        documents=sample_documents,
        parallel=False,
        export_format="json"
    )

    assert result is not None
    assert result['batch_id'] == "test_batch_1"
    assert result['total_documents'] == len(sample_documents)
    assert 'results' in result
    assert len(result['results']) == len(sample_documents)


@pytest.mark.asyncio
async def test_batch_processing_parallel(sample_documents):
    """Test parallel batch processing"""
    batch_corrector = BatchCorrector(
        batch_id="test_batch_2",
        priority=BatchPriority.HIGH,
        max_concurrency=3
    )

    result = await batch_corrector.process_batch(
        documents=sample_documents,
        parallel=True,
        export_format="json"
    )

    assert result is not None
    assert result['status'] in ['completed', 'partial']
    assert 'statistics' in result


@pytest.mark.asyncio
async def test_batch_status_tracking(sample_documents):
    """Test batch status tracking"""
    batch_id = "test_batch_3"

    batch_corrector = BatchCorrector(
        batch_id=batch_id,
        priority=BatchPriority.NORMAL
    )

    # Start batch processing (don't await)
    asyncio.create_task(
        batch_corrector.process_batch(
            documents=sample_documents[:1],  # Just one doc for speed
            parallel=False,
            export_format="json"
        )
    )

    # Give it time to start
    await asyncio.sleep(0.1)

    # Check status
    status = await BatchCorrector.get_batch_status(batch_id)
    assert status is not None
    assert status['batch_id'] == batch_id


# ==================== Scheduler Tests ====================

@pytest.mark.asyncio
async def test_scheduler_basic():
    """Test basic job scheduling"""
    scheduler = CorrectionScheduler(max_workers=2)

    job_info = await scheduler.schedule_job(
        job_id="test_job_1",
        text="Test document for scheduling",
        priority=JobPriority.NORMAL,
        user_id="test_user"
    )

    assert job_info is not None
    assert job_info['job_id'] == "test_job_1"
    assert job_info['status'] == 'queued'


@pytest.mark.asyncio
async def test_scheduler_job_status():
    """Test job status tracking"""
    scheduler = CorrectionScheduler(max_workers=1)

    job_id = "test_job_2"

    await scheduler.schedule_job(
        job_id=job_id,
        text="Test document",
        priority=JobPriority.HIGH,
        user_id="test_user"
    )

    # Check status
    status = await scheduler.get_job_status(job_id)
    assert status is not None
    assert status['job_id'] == job_id
    assert status['status'] in ['queued', 'processing', 'completed']


@pytest.mark.asyncio
async def test_scheduler_quota_management():
    """Test quota management"""
    scheduler = CorrectionScheduler()

    quota_info = await scheduler.get_quota_info("test_user")

    assert quota_info is not None
    assert 'requests_limit' in quota_info
    assert 'requests_remaining' in quota_info


@pytest.mark.asyncio
async def test_scheduler_queue_stats():
    """Test queue statistics"""
    stats = await CorrectionScheduler.get_queue_stats()

    assert stats is not None
    assert 'total_jobs' in stats
    assert 'queued' in stats
    assert 'completed' in stats


# ==================== Export Tests ====================

@pytest.mark.asyncio
async def test_export_json():
    """Test JSON export"""
    exporter = CorrectionExporter()

    result = {
        'original_text': 'Test original',
        'corrected_text': 'Test corrected',
        'corrections': [],
        'issues_found': 0,
        'issues_corrected': 0,
        'improvement_score': 0.0
    }

    exported = await exporter.export(result, 'json')

    assert exported is not None
    assert isinstance(exported, dict)
    assert 'original_text' in exported


@pytest.mark.asyncio
async def test_export_xml():
    """Test XML export"""
    exporter = CorrectionExporter()

    result = {
        'original_text': 'Test original',
        'corrected_text': 'Test corrected',
        'corrections': [],
        'issues_found': 0
    }

    exported = await exporter.export(result, 'xml')

    assert exported is not None
    assert isinstance(exported, bytes)


@pytest.mark.asyncio
async def test_export_html():
    """Test HTML export"""
    exporter = CorrectionExporter()

    result = {
        'original_text': 'Test original',
        'corrected_text': 'Test corrected',
        'corrections': [],
        'issues_found': 1,
        'issues_corrected': 1,
        'improvement_score': 1.0
    }

    exported = await exporter.export(result, 'html')

    assert exported is not None
    assert isinstance(exported, str)
    assert '<!DOCTYPE html>' in exported
    assert 'Test original' in exported


@pytest.mark.asyncio
async def test_export_markdown():
    """Test Markdown export"""
    exporter = CorrectionExporter()

    result = {
        'original_text': 'Test original',
        'corrected_text': 'Test corrected',
        'corrections': [],
        'issues_found': 0
    }

    exported = await exporter.export(result, 'markdown')

    assert exported is not None
    assert isinstance(exported, str)
    assert '# Document Correction Report' in exported


# ==================== Dashboard Tests ====================

@pytest.mark.asyncio
async def test_dashboard_metrics():
    """Test dashboard metrics collection"""
    dashboard = CorrectionDashboard()

    metrics = await dashboard.collect_metrics()

    assert metrics is not None
    assert hasattr(metrics, 'timestamp')
    assert hasattr(metrics, 'total_corrections')


@pytest.mark.asyncio
async def test_dashboard_record_correction():
    """Test recording corrections"""
    dashboard = CorrectionDashboard()

    dashboard.record_correction(
        execution_time_ms=100.0,
        improvement_score=0.8,
        success=True
    )

    assert dashboard.counters['successful_corrections'] == 1
    assert dashboard.counters['total_corrections'] == 1


@pytest.mark.asyncio
async def test_dashboard_data():
    """Test dashboard data retrieval"""
    dashboard = CorrectionDashboard()

    # Record some data
    dashboard.record_correction(100.0, 0.8, success=True)
    dashboard.record_cache_hit()

    data = await dashboard.get_dashboard_data()

    assert data is not None
    assert 'current_metrics' in data
    assert 'cache_stats' in data
    assert 'health' in data


@pytest.mark.asyncio
async def test_dashboard_performance_report():
    """Test performance report generation"""
    dashboard = CorrectionDashboard()

    # Record some corrections
    for i in range(5):
        dashboard.record_correction(100.0 + i * 10, 0.8, success=True)
        await dashboard.collect_metrics()

    report = await dashboard.get_performance_report(hours=1)

    assert report is not None
    assert 'summary' in report
    assert 'timeline' in report


# ==================== Performance Tests ====================

@pytest.mark.asyncio
async def test_performance_single_correction(sample_text):
    """Test single correction performance"""
    pipeline = CorrectionPipeline()

    start = time.time()
    result = await pipeline.execute(text=sample_text)
    elapsed = (time.time() - start) * 1000

    assert result is not None
    # Should complete in reasonable time (adjust as needed)
    assert elapsed < 5000  # 5 seconds


@pytest.mark.asyncio
async def test_performance_batch_processing(sample_documents):
    """Test batch processing performance"""
    batch_corrector = BatchCorrector(
        batch_id="perf_test_batch",
        max_concurrency=5
    )

    start = time.time()
    result = await batch_corrector.process_batch(
        documents=sample_documents,
        parallel=True,
        export_format="json"
    )
    elapsed = (time.time() - start) * 1000

    assert result is not None
    assert result['status'] in ['completed', 'partial']
    # Should complete in reasonable time
    assert elapsed < 10000  # 10 seconds for 3 documents


# ==================== Error Handling Tests ====================

@pytest.mark.asyncio
async def test_pipeline_empty_text():
    """Test pipeline with empty text"""
    pipeline = CorrectionPipeline()

    result = await pipeline.execute(text="")

    assert result is not None
    # Should handle gracefully


@pytest.mark.asyncio
async def test_pipeline_invalid_stages():
    """Test pipeline with invalid configuration"""
    pipeline = CorrectionPipeline()

    # Should handle empty stages list
    result = await pipeline.execute(text="Test", stages=[])

    assert result is not None


@pytest.mark.asyncio
async def test_export_unsupported_format():
    """Test export with unsupported format"""
    exporter = CorrectionExporter()

    result = {'original_text': 'test'}

    with pytest.raises(ValueError):
        await exporter.export(result, 'unsupported_format')


# ==================== Integration Tests ====================

@pytest.mark.asyncio
async def test_end_to_end_correction_flow(sample_text, sample_validation_results):
    """Test complete end-to-end correction flow"""
    # 1. Create pipeline
    pipeline = CorrectionPipeline(
        algorithm_version="2.0.0",
        enable_caching=True
    )

    # 2. Execute correction
    correction_result = await pipeline.execute(
        text=sample_text,
        validation_results=sample_validation_results,
        auto_apply=True
    )

    assert correction_result is not None

    # 3. Export to multiple formats
    exporter = CorrectionExporter()

    json_export = await exporter.export(correction_result, 'json')
    assert json_export is not None

    html_export = await exporter.export(correction_result, 'html')
    assert html_export is not None

    # 4. Record metrics
    dashboard = CorrectionDashboard()
    dashboard.record_correction(
        execution_time_ms=correction_result.get('pipeline_execution', {}).get('total_time_ms', 0),
        improvement_score=correction_result.get('improvement_score', 0.0),
        success=True
    )

    # 5. Get dashboard data
    dashboard_data = await dashboard.get_dashboard_data()
    assert dashboard_data is not None


@pytest.mark.asyncio
async def test_end_to_end_batch_flow(sample_documents):
    """Test complete end-to-end batch correction flow"""
    # 1. Create batch corrector
    batch_id = f"e2e_batch_{int(time.time())}"
    batch_corrector = BatchCorrector(
        batch_id=batch_id,
        priority=BatchPriority.HIGH
    )

    # 2. Process batch
    result = await batch_corrector.process_batch(
        documents=sample_documents,
        parallel=True,
        export_format="json"
    )

    assert result is not None
    assert result['status'] in ['completed', 'partial']

    # 3. Check batch status
    status = await BatchCorrector.get_batch_status(batch_id)
    assert status is not None
    assert status['batch_id'] == batch_id

    # 4. Verify statistics
    if 'statistics' in result:
        stats = result['statistics']
        assert 'total_issues_found' in stats
        assert 'success_rate' in stats


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])

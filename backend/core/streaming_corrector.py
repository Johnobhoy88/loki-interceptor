"""
Streaming Corrector - Real-time correction streaming for large documents

Features:
- Stream corrections in real-time via WebSocket
- Chunk-based processing for large documents
- Progress updates during processing
- Incremental result delivery
- Error handling with graceful degradation
"""

import asyncio
import time
from typing import Optional, Dict, Any, AsyncIterator
from datetime import datetime
from enum import Enum

try:
    from .correction_pipeline import CorrectionPipeline, PipelineStage
except ImportError:
    from correction_pipeline import CorrectionPipeline, PipelineStage


class StreamingStage(str, Enum):
    """Streaming stages"""
    CONNECTING = "connecting"
    CHUNKING = "chunking"
    VALIDATING = "validating"
    ANALYZING = "analyzing"
    CORRECTING = "correcting"
    VERIFYING = "verifying"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    ERROR = "error"


class StreamingCorrector:
    """
    Real-time streaming corrector for large documents

    Features:
    - WebSocket-based streaming
    - Chunk-based processing
    - Real-time progress updates
    - Incremental corrections
    - Memory-efficient for large documents
    """

    def __init__(
        self,
        websocket,
        chunk_size: int = 50000,  # 50KB chunks
        update_interval: float = 0.5  # Update every 500ms
    ):
        """
        Initialize streaming corrector

        Args:
            websocket: WebSocket connection
            chunk_size: Size of document chunks in characters
            update_interval: Interval between progress updates (seconds)
        """
        self.websocket = websocket
        self.chunk_size = chunk_size
        self.update_interval = update_interval

        # Streaming state
        self.current_stage = StreamingStage.CONNECTING
        self.progress = 0.0
        self.start_time = None

    async def stream_corrections(
        self,
        text: str,
        validation_results: Optional[Dict] = None,
        document_type: Optional[str] = None
    ):
        """
        Stream corrections in real-time

        Args:
            text: Document text to correct
            validation_results: Validation results
            document_type: Document type
        """
        self.start_time = time.time()

        try:
            # Send initial connection message
            await self._send_update(StreamingStage.CONNECTING, 0.0, {
                'message': 'Connection established',
                'document_size': len(text),
                'estimated_chunks': self._estimate_chunks(text)
            })

            # Check if document needs chunking
            if len(text) > self.chunk_size:
                # Process in chunks
                await self._stream_chunked_correction(text, validation_results, document_type)
            else:
                # Process as single document
                await self._stream_single_correction(text, validation_results, document_type)

            # Send completion message
            await self._send_update(StreamingStage.COMPLETED, 100.0, {
                'message': 'Correction completed',
                'total_time_ms': (time.time() - self.start_time) * 1000
            })

        except Exception as e:
            # Send error message
            await self._send_update(StreamingStage.ERROR, self.progress, {
                'error': str(e),
                'stage': self.current_stage.value
            })
            raise

    async def _stream_single_correction(
        self,
        text: str,
        validation_results: Optional[Dict],
        document_type: Optional[str]
    ):
        """Stream correction for single (non-chunked) document"""
        # Create pipeline
        pipeline = CorrectionPipeline(
            algorithm_version="2.0.0",
            enable_caching=True
        )

        # Define stages with progress weights
        stages = [
            (PipelineStage.VALIDATE, StreamingStage.VALIDATING, 10),
            (PipelineStage.ANALYZE, StreamingStage.ANALYZING, 20),
            (PipelineStage.CORRECT, StreamingStage.CORRECTING, 50),
            (PipelineStage.VERIFY, StreamingStage.VERIFYING, 20),
        ]

        total_weight = sum(weight for _, _, weight in stages)
        cumulative_progress = 0.0

        # Execute stages with progress updates
        for pipeline_stage, streaming_stage, weight in stages:
            self.current_stage = streaming_stage

            # Send stage start update
            await self._send_update(streaming_stage, cumulative_progress, {
                'message': f'Starting {streaming_stage.value}...'
            })

            # Execute stage
            stage_result = await pipeline._execute_stage(
                pipeline_stage,
                {'original_text': text, 'corrected_text': text},
                validation_results,
                document_type,
                auto_apply=True,
                confidence_threshold=0.8
            )

            # Update progress
            cumulative_progress += (weight / total_weight) * 100
            await self._send_update(streaming_stage, cumulative_progress, {
                'message': f'Completed {streaming_stage.value}',
                'stage_result': self._summarize_stage_result(stage_result)
            })

        # Execute full pipeline for final result
        result = await pipeline.execute(
            text=text,
            validation_results=validation_results,
            document_type=document_type
        )

        # Send final result
        await self._send_update(StreamingStage.FINALIZING, 95.0, {
            'message': 'Finalizing result...',
            'result': self._format_result(result)
        })

    async def _stream_chunked_correction(
        self,
        text: str,
        validation_results: Optional[Dict],
        document_type: Optional[str]
    ):
        """Stream correction for chunked (large) document"""
        # Split document into chunks
        chunks = self._split_into_chunks(text)
        total_chunks = len(chunks)

        await self._send_update(StreamingStage.CHUNKING, 5.0, {
            'message': f'Document split into {total_chunks} chunks',
            'chunk_count': total_chunks
        })

        # Process chunks
        corrected_chunks = []
        all_corrections = []

        for idx, chunk in enumerate(chunks):
            chunk_progress = 5.0 + ((idx / total_chunks) * 85.0)

            # Update progress
            await self._send_update(StreamingStage.CORRECTING, chunk_progress, {
                'message': f'Processing chunk {idx + 1}/{total_chunks}...',
                'chunk_index': idx,
                'chunk_size': len(chunk)
            })

            # Create pipeline for chunk
            pipeline = CorrectionPipeline(
                algorithm_version="2.0.0",
                enable_caching=True
            )

            # Execute correction for chunk
            chunk_result = await pipeline.execute(
                text=chunk,
                validation_results=validation_results,
                document_type=document_type
            )

            # Collect results
            corrected_chunks.append(chunk_result.get('corrected_text', chunk))
            all_corrections.extend(chunk_result.get('corrections', []))

            # Send chunk completion update
            await self._send_update(StreamingStage.CORRECTING, chunk_progress, {
                'message': f'Completed chunk {idx + 1}/{total_chunks}',
                'chunk_corrections': len(chunk_result.get('corrections', [])),
                'chunk_improvement_score': chunk_result.get('improvement_score', 0.0)
            })

        # Merge chunks
        await self._send_update(StreamingStage.FINALIZING, 90.0, {
            'message': 'Merging corrected chunks...'
        })

        corrected_text = ''.join(corrected_chunks)

        # Send final result
        result = {
            'original_text': text,
            'corrected_text': corrected_text,
            'corrections': all_corrections,
            'issues_corrected': len(all_corrections),
            'chunks_processed': total_chunks
        }

        await self._send_update(StreamingStage.FINALIZING, 95.0, {
            'message': 'Correction completed',
            'result': self._format_result(result)
        })

    def _split_into_chunks(self, text: str) -> list:
        """Split text into processable chunks"""
        chunks = []
        current_pos = 0

        while current_pos < len(text):
            # Get chunk
            chunk_end = min(current_pos + self.chunk_size, len(text))

            # Try to split at sentence boundary
            if chunk_end < len(text):
                # Look for sentence end near chunk boundary
                for delimiter in ['. ', '.\n', '! ', '!\n', '? ', '?\n']:
                    last_delimiter = text.rfind(delimiter, current_pos, chunk_end)
                    if last_delimiter != -1:
                        chunk_end = last_delimiter + len(delimiter)
                        break

            chunk = text[current_pos:chunk_end]
            chunks.append(chunk)
            current_pos = chunk_end

        return chunks

    def _estimate_chunks(self, text: str) -> int:
        """Estimate number of chunks needed"""
        return max(1, (len(text) + self.chunk_size - 1) // self.chunk_size)

    async def _send_update(
        self,
        stage: StreamingStage,
        progress: float,
        data: Dict[str, Any]
    ):
        """Send progress update via WebSocket"""
        self.current_stage = stage
        self.progress = progress

        update = {
            'type': 'progress',
            'stage': stage.value,
            'progress': round(progress, 2),
            'timestamp': datetime.utcnow().isoformat(),
            'elapsed_ms': (time.time() - self.start_time) * 1000 if self.start_time else 0,
            'data': data
        }

        try:
            await self.websocket.send_json(update)
        except Exception as e:
            print(f"Error sending WebSocket update: {e}")

    def _summarize_stage_result(self, stage_result: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize stage result for streaming"""
        # Remove metadata and large fields
        summary = {}

        # Include key metrics only
        if 'issues_detected' in stage_result:
            summary['issues_detected'] = stage_result['issues_detected']
        if 'correctable_issues' in stage_result:
            summary['correctable_issues'] = stage_result['correctable_issues']
        if 'estimated_changes' in stage_result:
            summary['estimated_changes'] = stage_result['estimated_changes']
        if 'quality_score' in stage_result:
            summary['quality_score'] = stage_result['quality_score']
        if 'improvement_score' in stage_result:
            summary['improvement_score'] = stage_result['improvement_score']

        return summary

    def _format_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format result for streaming (exclude large text fields)"""
        return {
            'original_text_length': len(result.get('original_text', '')),
            'corrected_text_length': len(result.get('corrected_text', '')),
            'text_changed': result.get('original_text') != result.get('corrected_text'),
            'issues_found': result.get('issues_found', 0),
            'issues_corrected': result.get('issues_corrected', 0),
            'correction_count': len(result.get('corrections', [])),
            'improvement_score': result.get('improvement_score', 0.0),
            'chunks_processed': result.get('chunks_processed', 1),
            # Include corrections summary (not full text)
            'corrections_summary': [
                {
                    'gate': c.get('gate', 'unknown'),
                    'type': c.get('strategy', 'unknown'),
                    'changes': c.get('metadata', {}).get('changes', 0)
                }
                for c in result.get('corrections', [])[:10]  # First 10 only
            ]
        }


class StreamingIterator:
    """
    Async iterator for streaming corrections without WebSocket

    Useful for:
    - Server-Sent Events (SSE)
    - HTTP chunked responses
    - Custom streaming protocols
    """

    def __init__(
        self,
        text: str,
        validation_results: Optional[Dict] = None,
        chunk_size: int = 50000
    ):
        """
        Initialize streaming iterator

        Args:
            text: Document text
            validation_results: Validation results
            chunk_size: Chunk size for processing
        """
        self.text = text
        self.validation_results = validation_results
        self.chunk_size = chunk_size
        self.position = 0

    async def __aiter__(self) -> AsyncIterator[Dict[str, Any]]:
        """Async iteration over correction events"""
        start_time = time.time()

        # Yield start event
        yield {
            'event': 'start',
            'document_size': len(self.text),
            'timestamp': datetime.utcnow().isoformat()
        }

        # Create pipeline
        pipeline = CorrectionPipeline(
            algorithm_version="2.0.0",
            enable_caching=True
        )

        # Execute and yield progress
        result = await pipeline.execute(
            text=self.text,
            validation_results=self.validation_results
        )

        # Yield result event
        yield {
            'event': 'result',
            'data': {
                'corrected_text': result.get('corrected_text', ''),
                'corrections': result.get('corrections', []),
                'improvement_score': result.get('improvement_score', 0.0),
                'execution_time_ms': (time.time() - start_time) * 1000
            },
            'timestamp': datetime.utcnow().isoformat()
        }

        # Yield complete event
        yield {
            'event': 'complete',
            'timestamp': datetime.utcnow().isoformat()
        }

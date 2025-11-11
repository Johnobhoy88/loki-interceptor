"""
Async document processing utilities for LOKI Interceptor
Optimized for handling large documents and concurrent operations
"""

import asyncio
import concurrent.futures
from typing import List, Dict, Any, Callable, Optional, Tuple
import hashlib
from datetime import datetime
import time


class DocumentChunk:
    """Represents a chunk of a document for processing"""

    def __init__(self, content: str, index: int, start_pos: int, end_pos: int):
        """
        Initialize document chunk

        Args:
            content: Chunk text content
            index: Chunk index in document
            start_pos: Start position in original document
            end_pos: End position in original document
        """
        self.content = content
        self.index = index
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.hash = hashlib.md5(content.encode()).hexdigest()


class AsyncDocumentProcessor:
    """
    High-performance async document processor for large documents

    Features:
    - Automatic document chunking for large files (>1MB)
    - Parallel chunk processing
    - Connection pooling
    - Progress tracking
    - Error handling and retry logic
    - Memory-efficient streaming
    """

    def __init__(
        self,
        chunk_size: int = 50000,  # ~50KB chunks
        max_workers: int = 4,
        overlap_size: int = 500  # Overlap for context continuity
    ):
        """
        Initialize async processor

        Args:
            chunk_size: Size of document chunks in characters
            max_workers: Maximum concurrent workers
            overlap_size: Character overlap between chunks for context
        """
        self.chunk_size = chunk_size
        self.max_workers = max_workers
        self.overlap_size = overlap_size
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def chunk_document(self, text: str) -> List[DocumentChunk]:
        """
        Split large document into processable chunks with overlap

        Args:
            text: Full document text

        Returns:
            List of DocumentChunk objects
        """
        if len(text) <= self.chunk_size:
            # Small document, no chunking needed
            return [DocumentChunk(text, 0, 0, len(text))]

        chunks = []
        index = 0
        start = 0

        while start < len(text):
            # Calculate chunk end
            end = min(start + self.chunk_size, len(text))

            # Try to break at sentence/paragraph boundary
            if end < len(text):
                # Look for sentence boundaries within last 500 chars
                search_start = max(end - 500, start)
                last_period = text.rfind('.', search_start, end)
                last_newline = text.rfind('\n', search_start, end)

                boundary = max(last_period, last_newline)
                if boundary > start:
                    end = boundary + 1

            chunk_content = text[start:end]
            chunks.append(DocumentChunk(chunk_content, index, start, end))

            # Move to next chunk with overlap
            start = end - self.overlap_size if end < len(text) else end
            index += 1

        return chunks

    async def process_chunks_async(
        self,
        chunks: List[DocumentChunk],
        processor_func: Callable[[str], Dict[str, Any]],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process document chunks asynchronously

        Args:
            chunks: List of document chunks
            processor_func: Function to process each chunk
            progress_callback: Optional callback for progress updates (current, total)

        Returns:
            List of results from each chunk
        """
        results = []
        completed = 0
        total = len(chunks)

        # Create tasks for all chunks
        loop = asyncio.get_event_loop()
        tasks = []

        for chunk in chunks:
            # Run processor in thread pool to avoid blocking
            task = loop.run_in_executor(
                self.executor,
                processor_func,
                chunk.content
            )
            tasks.append((chunk, task))

        # Gather results as they complete
        for chunk, task in tasks:
            try:
                result = await task
                results.append({
                    'chunk_index': chunk.index,
                    'start_pos': chunk.start_pos,
                    'end_pos': chunk.end_pos,
                    'result': result,
                    'error': None
                })
            except Exception as e:
                results.append({
                    'chunk_index': chunk.index,
                    'start_pos': chunk.start_pos,
                    'end_pos': chunk.end_pos,
                    'result': None,
                    'error': str(e)
                })

            completed += 1
            if progress_callback:
                progress_callback(completed, total)

        return results

    def process_chunks_parallel(
        self,
        chunks: List[DocumentChunk],
        processor_func: Callable[[str], Dict[str, Any]],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process document chunks in parallel (synchronous interface)

        Args:
            chunks: List of document chunks
            processor_func: Function to process each chunk
            progress_callback: Optional callback for progress updates

        Returns:
            List of results from each chunk
        """
        results = []
        futures = {}

        # Submit all chunks for processing
        for chunk in chunks:
            future = self.executor.submit(processor_func, chunk.content)
            futures[future] = chunk

        # Collect results as they complete
        completed = 0
        total = len(chunks)

        for future in concurrent.futures.as_completed(futures):
            chunk = futures[future]
            try:
                result = future.result()
                results.append({
                    'chunk_index': chunk.index,
                    'start_pos': chunk.start_pos,
                    'end_pos': chunk.end_pos,
                    'result': result,
                    'error': None
                })
            except Exception as e:
                results.append({
                    'chunk_index': chunk.index,
                    'start_pos': chunk.start_pos,
                    'end_pos': chunk.end_pos,
                    'result': None,
                    'error': str(e)
                })

            completed += 1
            if progress_callback:
                progress_callback(completed, total)

        # Sort by chunk index to maintain order
        results.sort(key=lambda x: x['chunk_index'])

        return results

    def aggregate_chunk_results(
        self,
        chunk_results: List[Dict[str, Any]],
        aggregation_strategy: str = 'merge'
    ) -> Dict[str, Any]:
        """
        Aggregate results from multiple chunks

        Args:
            chunk_results: List of chunk processing results
            aggregation_strategy: Strategy for aggregation ('merge', 'max_severity', 'all')

        Returns:
            Aggregated results dictionary
        """
        if aggregation_strategy == 'merge':
            # Merge all findings together
            aggregated = {
                'chunks_processed': len(chunk_results),
                'chunks_with_errors': sum(1 for r in chunk_results if r['error']),
                'findings': [],
                'overall_status': 'PASS',
                'severity': 'none'
            }

            for chunk_result in chunk_results:
                if chunk_result['error']:
                    continue

                result = chunk_result['result']
                if not result:
                    continue

                # Merge findings
                if 'findings' in result and isinstance(result['findings'], list):
                    aggregated['findings'].extend(result['findings'])

                # Update overall status (worst case)
                status = result.get('status', 'PASS')
                if status == 'FAIL':
                    aggregated['overall_status'] = 'FAIL'
                elif status == 'WARNING' and aggregated['overall_status'] == 'PASS':
                    aggregated['overall_status'] = 'WARNING'

                # Update severity (worst case)
                severity = result.get('severity', 'none')
                severity_order = ['none', 'low', 'medium', 'high', 'critical']
                current_idx = severity_order.index(aggregated['severity'])
                new_idx = severity_order.index(severity) if severity in severity_order else 0
                if new_idx > current_idx:
                    aggregated['severity'] = severity

            return aggregated

        elif aggregation_strategy == 'max_severity':
            # Return chunk with highest severity
            valid_results = [r for r in chunk_results if not r['error'] and r['result']]
            if not valid_results:
                return {'error': 'No valid results', 'chunks_processed': len(chunk_results)}

            severity_order = {'none': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4}

            max_result = max(
                valid_results,
                key=lambda r: severity_order.get(r['result'].get('severity', 'none'), 0)
            )

            return {
                **max_result['result'],
                'chunks_processed': len(chunk_results),
                'source_chunk': max_result['chunk_index']
            }

        else:  # 'all' - return all results
            return {
                'chunks_processed': len(chunk_results),
                'chunks': chunk_results
            }

    def process_large_document(
        self,
        text: str,
        processor_func: Callable[[str], Dict[str, Any]],
        auto_chunk: bool = True,
        aggregation_strategy: str = 'merge',
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Complete pipeline for processing large documents

        Args:
            text: Full document text
            processor_func: Function to process text/chunks
            auto_chunk: Automatically chunk if document is large
            aggregation_strategy: How to aggregate chunk results
            progress_callback: Optional progress callback

        Returns:
            Processing results (aggregated if chunked)
        """
        start_time = time.time()

        # Determine if chunking is needed
        needs_chunking = auto_chunk and len(text) > self.chunk_size

        if not needs_chunking:
            # Process as single document
            try:
                result = processor_func(text)
                return {
                    **result,
                    'processing_time_ms': round((time.time() - start_time) * 1000, 2),
                    'chunked': False
                }
            except Exception as e:
                return {
                    'error': str(e),
                    'processing_time_ms': round((time.time() - start_time) * 1000, 2),
                    'chunked': False
                }
        else:
            # Chunk and process in parallel
            chunks = self.chunk_document(text)

            chunk_results = self.process_chunks_parallel(
                chunks,
                processor_func,
                progress_callback
            )

            aggregated = self.aggregate_chunk_results(chunk_results, aggregation_strategy)

            return {
                **aggregated,
                'processing_time_ms': round((time.time() - start_time) * 1000, 2),
                'chunked': True,
                'chunk_count': len(chunks)
            }

    def estimate_processing_time(self, document_size: int, avg_chunk_time_ms: float = 100) -> Dict[str, Any]:
        """
        Estimate processing time for a document

        Args:
            document_size: Document size in characters
            avg_chunk_time_ms: Average processing time per chunk in ms

        Returns:
            Estimation dictionary with time and chunk info
        """
        if document_size <= self.chunk_size:
            return {
                'estimated_time_ms': avg_chunk_time_ms,
                'chunks': 1,
                'parallel_batches': 1
            }

        # Calculate chunks
        num_chunks = (document_size + self.chunk_size - 1) // self.chunk_size

        # Calculate parallel batches
        batches = (num_chunks + self.max_workers - 1) // self.max_workers

        # Estimate time (batches * avg time per chunk)
        estimated_ms = batches * avg_chunk_time_ms

        return {
            'estimated_time_ms': estimated_ms,
            'chunks': num_chunks,
            'parallel_batches': batches,
            'max_workers': self.max_workers
        }

    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)


class ConnectionPool:
    """
    Simple connection pool for API clients

    Manages reusable connections to reduce overhead
    """

    def __init__(self, factory: Callable[[], Any], pool_size: int = 5):
        """
        Initialize connection pool

        Args:
            factory: Function to create new connections
            pool_size: Maximum pool size
        """
        self.factory = factory
        self.pool_size = pool_size
        self.connections: List[Any] = []
        self.in_use: List[Any] = []
        self._lock = asyncio.Lock() if asyncio.get_event_loop().is_running() else None

    def acquire(self) -> Any:
        """
        Acquire a connection from pool

        Returns:
            Connection object
        """
        if self.connections:
            conn = self.connections.pop()
            self.in_use.append(conn)
            return conn
        elif len(self.in_use) < self.pool_size:
            conn = self.factory()
            self.in_use.append(conn)
            return conn
        else:
            # Pool exhausted, create temporary connection
            return self.factory()

    def release(self, connection: Any):
        """
        Release connection back to pool

        Args:
            connection: Connection to release
        """
        if connection in self.in_use:
            self.in_use.remove(connection)

        if len(self.connections) < self.pool_size:
            self.connections.append(connection)

    def close_all(self):
        """Close all connections in pool"""
        for conn in self.connections + self.in_use:
            if hasattr(conn, 'close'):
                try:
                    conn.close()
                except Exception:
                    pass

        self.connections.clear()
        self.in_use.clear()

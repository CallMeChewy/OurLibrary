# File: ChunkedDownloader.py
# Path: /home/herb/Desktop/AndyLibrary/Source/Core/ChunkedDownloader.py
# Standard: AIDEV-PascalCase-2.1
# Created: 2025-07-24
# Last Modified: 2025-07-24 01:24PM

"""
Chunked Book Downloader - Student-Friendly Downloads
Handles large book downloads in small chunks for slow/unreliable connections
"""

import os
import sys
import time
import hashlib
import json
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import threading
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class DownloadProgress:
    """Track download progress for student feedback"""
    book_id: int
    title: str
    total_size_bytes: int
    downloaded_bytes: int
    chunk_size_bytes: int
    current_chunk: int
    total_chunks: int
    start_time: float
    estimated_time_remaining: float
    speed_bytes_per_second: float
    status: str  # 'downloading', 'paused', 'completed', 'error'

class DownloadStatus(Enum):
    """Download status for student tracking"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed" 
    ERROR = "error"
    CANCELLED = "cancelled"

class NetworkCondition(Enum):
    """Network conditions for adaptive chunk sizing"""
    DIALUP = "dialup"      # 56k - 8KB chunks
    SLOW_2G = "slow_2g"    # 2G - 16KB chunks
    FAST_2G = "fast_2g"    # 2G+ - 32KB chunks  
    SLOW_3G = "slow_3g"    # 3G - 64KB chunks
    FAST_3G = "fast_3g"    # 3G+ - 128KB chunks
    WIFI = "wifi"          # WiFi - 256KB chunks

class ChunkedDownloader:
    """Handles chunked downloads optimized for student network conditions"""
    
    def __init__(self, downloads_dir: str = "Downloads/Books"):
        self.downloads_dir = downloads_dir
        self.active_downloads = {}  # book_id -> DownloadProgress
        self.download_threads = {}  # book_id -> threading.Thread
        self.resume_info_dir = "Downloads/Resume"
        
        # Create directories
        os.makedirs(self.downloads_dir, exist_ok=True)
        os.makedirs(self.resume_info_dir, exist_ok=True)
        
        # Chunk sizes optimized for different network conditions
        self.chunk_sizes = {
            NetworkCondition.DIALUP: 8 * 1024,      # 8KB for 56k
            NetworkCondition.SLOW_2G: 16 * 1024,    # 16KB for slow 2G
            NetworkCondition.FAST_2G: 32 * 1024,    # 32KB for fast 2G
            NetworkCondition.SLOW_3G: 64 * 1024,    # 64KB for slow 3G
            NetworkCondition.FAST_3G: 128 * 1024,   # 128KB for fast 3G
            NetworkCondition.WIFI: 256 * 1024       # 256KB for WiFi
        }
    
    def DetectNetworkCondition(self) -> NetworkCondition:
        """Detect network condition for adaptive chunk sizing"""
        # Simple heuristic: measure small download speed
        # In real implementation, this would test actual connection speed
        
        # For now, default to slow connection (conservative for students)
        return NetworkCondition.SLOW_3G
    
    def GetOptimalChunkSize(self, network_condition: NetworkCondition = None) -> int:
        """Get optimal chunk size for current network conditions"""
        if network_condition is None:
            network_condition = self.DetectNetworkCondition()
        
        return self.chunk_sizes[network_condition]
    
    def StartChunkedDownload(
        self,
        book_id: int,
        title: str,
        file_size_bytes: int,
        download_url: str,
        progress_callback: Callable[[DownloadProgress], None] = None,
        network_condition: NetworkCondition = None
    ) -> str:
        """Start chunked download of a book"""
        
        if book_id in self.active_downloads:
            return f"Download already in progress for book {book_id}"
        
        # Get optimal chunk size
        chunk_size = self.GetOptimalChunkSize(network_condition)
        total_chunks = (file_size_bytes + chunk_size - 1) // chunk_size
        
        # Create download progress tracker
        progress = DownloadProgress(
            book_id=book_id,
            title=title,
            total_size_bytes=file_size_bytes,
            downloaded_bytes=0,
            chunk_size_bytes=chunk_size,
            current_chunk=0,
            total_chunks=total_chunks,
            start_time=time.time(),
            estimated_time_remaining=0.0,
            speed_bytes_per_second=0.0,
            status=DownloadStatus.PENDING.value
        )
        
        self.active_downloads[book_id] = progress
        
        # Start download in background thread
        download_thread = threading.Thread(
            target=self._DownloadWorker,
            args=(book_id, download_url, progress_callback),
            daemon=True
        )
        
        self.download_threads[book_id] = download_thread
        download_thread.start()
        
        return f"Download started for: {title}"
    
    def _DownloadWorker(
        self,
        book_id: int,
        download_url: str,
        progress_callback: Callable[[DownloadProgress], None] = None
    ):
        """Worker thread for downloading book in chunks"""
        
        progress = self.active_downloads[book_id]
        output_file = os.path.join(self.downloads_dir, f"book_{book_id}.pdf")
        resume_file = os.path.join(self.resume_info_dir, f"book_{book_id}.json")
        
        try:
            progress.status = DownloadStatus.DOWNLOADING.value
            
            # Check for existing partial download
            start_byte = 0
            if os.path.exists(resume_file):
                with open(resume_file, 'r') as f:
                    resume_data = json.load(f)
                    start_byte = resume_data.get('downloaded_bytes', 0)
                    progress.downloaded_bytes = start_byte
                    progress.current_chunk = start_byte // progress.chunk_size_bytes
            
            # Simulate chunked download (replace with actual Google Drive API calls)
            with open(output_file, 'ab' if start_byte > 0 else 'wb') as f:
                current_byte = start_byte
                
                while current_byte < progress.total_size_bytes:
                    # Check if download was cancelled
                    if progress.status == DownloadStatus.CANCELLED.value:
                        break
                    
                    # Calculate chunk size for this iteration
                    remaining_bytes = progress.total_size_bytes - current_byte
                    chunk_size = min(progress.chunk_size_bytes, remaining_bytes)
                    
                    # Simulate network delay and chunk download
                    chunk_start_time = time.time()
                    
                    # TODO: Replace with actual Google Drive API call
                    # chunk_data = download_chunk_from_gdrive(download_url, current_byte, chunk_size)
                    chunk_data = b'0' * chunk_size  # Simulated data
                    
                    # Simulate network conditions (add delay for slow connections)
                    network_delay = self._SimulateNetworkDelay(chunk_size)
                    time.sleep(network_delay)
                    
                    # Write chunk to file
                    f.write(chunk_data)
                    f.flush()  # Ensure data is written
                    
                    # Update progress
                    current_byte += chunk_size
                    progress.downloaded_bytes = current_byte
                    progress.current_chunk += 1
                    
                    # Calculate speed and ETA
                    elapsed_time = time.time() - progress.start_time
                    if elapsed_time > 0:
                        progress.speed_bytes_per_second = current_byte / elapsed_time
                        remaining_bytes = progress.total_size_bytes - current_byte
                        progress.estimated_time_remaining = remaining_bytes / progress.speed_bytes_per_second
                    
                    # Save resume information
                    self._SaveResumeInfo(book_id, progress)
                    
                    # Call progress callback for UI updates
                    if progress_callback:
                        progress_callback(progress)
                    
                    # Student-friendly: yield CPU to avoid blocking
                    time.sleep(0.001)
            
            # Mark as completed
            if current_byte >= progress.total_size_bytes:
                progress.status = DownloadStatus.COMPLETED.value
                progress.downloaded_bytes = progress.total_size_bytes
                
                # Clean up resume file
                if os.path.exists(resume_file):
                    os.remove(resume_file)
                
                if progress_callback:
                    progress_callback(progress)
        
        except Exception as e:
            progress.status = DownloadStatus.ERROR.value
            print(f"Download error for book {book_id}: {e}")
            if progress_callback:
                progress_callback(progress)
        
        finally:
            # Clean up
            if book_id in self.download_threads:
                del self.download_threads[book_id]
    
    def _SimulateNetworkDelay(self, chunk_size: int) -> float:
        """Simulate network delay based on chunk size (for testing)"""
        # Simulate different connection speeds
        bytes_per_second = {
            NetworkCondition.DIALUP: 7 * 1024,      # 56k = ~7KB/s
            NetworkCondition.SLOW_2G: 20 * 1024,    # Slow 2G = ~20KB/s
            NetworkCondition.FAST_2G: 50 * 1024,    # Fast 2G = ~50KB/s
            NetworkCondition.SLOW_3G: 100 * 1024,   # Slow 3G = ~100KB/s
            NetworkCondition.FAST_3G: 300 * 1024,   # Fast 3G = ~300KB/s
            NetworkCondition.WIFI: 1000 * 1024      # WiFi = ~1MB/s
        }
        
        current_condition = self.DetectNetworkCondition()
        speed = bytes_per_second[current_condition]
        
        return chunk_size / speed  # Time to download this chunk
    
    def _SaveResumeInfo(self, book_id: int, progress: DownloadProgress):
        """Save resume information for interrupted downloads"""
        resume_file = os.path.join(self.resume_info_dir, f"book_{book_id}.json")
        
        resume_data = {
            'book_id': book_id,
            'title': progress.title,
            'total_size_bytes': progress.total_size_bytes,
            'downloaded_bytes': progress.downloaded_bytes,
            'current_chunk': progress.current_chunk,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(resume_file, 'w') as f:
            json.dump(resume_data, f)
    
    def PauseDownload(self, book_id: int) -> bool:
        """Pause an active download"""
        if book_id in self.active_downloads:
            self.active_downloads[book_id].status = DownloadStatus.PAUSED.value
            return True
        return False
    
    def ResumeDownload(self, book_id: int) -> bool:
        """Resume a paused download"""
        if book_id in self.active_downloads:
            progress = self.active_downloads[book_id]
            if progress.status == DownloadStatus.PAUSED.value:
                progress.status = DownloadStatus.DOWNLOADING.value
                return True
        return False
    
    def CancelDownload(self, book_id: int) -> bool:
        """Cancel an active download"""
        if book_id in self.active_downloads:
            self.active_downloads[book_id].status = DownloadStatus.CANCELLED.value
            
            # Clean up files
            output_file = os.path.join(self.downloads_dir, f"book_{book_id}.pdf")
            resume_file = os.path.join(self.resume_info_dir, f"book_{book_id}.json")
            
            for file_path in [output_file, resume_file]:
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Remove from active downloads
            del self.active_downloads[book_id]
            
            return True
        return False
    
    def GetDownloadProgress(self, book_id: int) -> Optional[DownloadProgress]:
        """Get current download progress for a book"""
        return self.active_downloads.get(book_id)
    
    def GetAllActiveDownloads(self) -> Dict[int, DownloadProgress]:
        """Get all active downloads"""
        return self.active_downloads.copy()
    
    def GetStudentFriendlyProgress(self, book_id: int) -> Optional[Dict[str, Any]]:
        """Get student-friendly progress information"""
        progress = self.GetDownloadProgress(book_id)
        if not progress:
            return None
        
        # Calculate percentages
        percentage_complete = (progress.downloaded_bytes / progress.total_size_bytes) * 100
        
        # Format time remaining
        eta_minutes = progress.estimated_time_remaining / 60 if progress.estimated_time_remaining > 0 else 0
        
        # Format speed
        speed_kbps = progress.speed_bytes_per_second / 1024 if progress.speed_bytes_per_second > 0 else 0
        
        return {
            'book_title': progress.title,
            'status': progress.status,
            'percentage_complete': round(percentage_complete, 1),
            'downloaded_mb': round(progress.downloaded_bytes / (1024 * 1024), 1),
            'total_mb': round(progress.total_size_bytes / (1024 * 1024), 1),
            'current_chunk': progress.current_chunk,
            'total_chunks': progress.total_chunks,
            'speed_kbps': round(speed_kbps, 1),
            'eta_minutes': round(eta_minutes, 1),
            'student_message': self._GenerateStudentMessage(progress)
        }
    
    def _GenerateStudentMessage(self, progress: DownloadProgress) -> str:
        """Generate encouraging message for students"""
        if progress.status == DownloadStatus.DOWNLOADING.value:
            percentage = (progress.downloaded_bytes / progress.total_size_bytes) * 100
            if percentage < 25:
                return "📚 Starting your download - hang in there!"
            elif percentage < 50:
                return "🚀 Making good progress - keep going!"
            elif percentage < 75:
                return "💪 More than halfway there - almost done!"
            else:
                return "🎯 Almost finished - your book is nearly ready!"
        
        elif progress.status == DownloadStatus.PAUSED.value:
            return "⏸️ Download paused - tap resume when ready"
        
        elif progress.status == DownloadStatus.COMPLETED.value:
            return "🎉 Download complete - enjoy your book!"
        
        elif progress.status == DownloadStatus.ERROR.value:
            return "❌ Download failed - check your connection and try again"
        
        else:
            return "📱 Ready to download"

# Example usage for testing
if __name__ == "__main__":
    print("🔄 Testing Chunked Downloader")
    
    def progress_callback(progress: DownloadProgress):
        percentage = (progress.downloaded_bytes / progress.total_size_bytes) * 100
        print(f"📊 Progress: {percentage:.1f}% - {progress.current_chunk}/{progress.total_chunks} chunks")
    
    downloader = ChunkedDownloader()
    
    # Simulate downloading a 5MB book
    result = downloader.StartChunkedDownload(
        book_id=1,
        title="Test Book",
        file_size_bytes=5 * 1024 * 1024,  # 5MB
        download_url="https://example.com/book.pdf",
        progress_callback=progress_callback,
        network_condition=NetworkCondition.SLOW_3G
    )
    
    print(f"✅ {result}")
    
    # Monitor progress
    time.sleep(1)
    while True:
        progress_info = downloader.GetStudentFriendlyProgress(1)
        if progress_info:
            print(f"📱 {progress_info['student_message']} ({progress_info['percentage_complete']}%)")
            if progress_info['status'] in ['completed', 'error', 'cancelled']:
                break
        time.sleep(2)
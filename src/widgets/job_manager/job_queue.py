"""
Job Queue Data Structures
Phase 6: Persistent job queue with status tracking
"""

import json
import os
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal

class JobStatus(Enum):
    """Job execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed" 
    FAILED = "failed"
    SKIPPED = "skipped"
    HELD = "held"

class JobItem:
    """Individual job item in the queue"""
    
    def __init__(self, file_path: str, name: str = None):
        self.file_path = file_path
        self.name = name or os.path.basename(file_path)
        self.status = JobStatus.PENDING
        self.created_time = datetime.now()
        self.start_time = None
        self.end_time = None
        self.error_message = None
        self.metadata = {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'file_path': self.file_path,
            'name': self.name,
            'status': self.status.value,
            'created_time': self.created_time.isoformat(),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'error_message': self.error_message,
            'metadata': self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JobItem':
        """Create JobItem from dictionary"""
        item = cls(data['file_path'], data['name'])
        item.status = JobStatus(data['status'])
        item.created_time = datetime.fromisoformat(data['created_time'])
        item.start_time = datetime.fromisoformat(data['start_time']) if data['start_time'] else None
        item.end_time = datetime.fromisoformat(data['end_time']) if data['end_time'] else None
        item.error_message = data.get('error_message')
        item.metadata = data.get('metadata', {})
        return item
        
    @property
    def duration(self) -> float:
        """Get job duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
        
    def start(self):
        """Mark job as started"""
        self.status = JobStatus.RUNNING
        self.start_time = datetime.now()
        
    def complete(self):
        """Mark job as completed"""
        self.status = JobStatus.COMPLETED
        self.end_time = datetime.now()
        
    def fail(self, error_message: str = None):
        """Mark job as failed"""
        self.status = JobStatus.FAILED
        self.end_time = datetime.now()
        self.error_message = error_message
        
    def skip(self):
        """Mark job as skipped"""
        self.status = JobStatus.SKIPPED
        self.end_time = datetime.now()
        
    def hold(self):
        """Put job on hold"""
        self.status = JobStatus.HELD
        
    def resume(self):
        """Resume held job"""
        if self.status == JobStatus.HELD:
            self.status = JobStatus.PENDING

class JobQueue(QObject):
    """Job queue with persistence and management"""
    
    # Signals
    job_added = pyqtSignal(JobItem)
    job_removed = pyqtSignal(int)  # index
    job_moved = pyqtSignal(int, int)  # from_index, to_index
    job_status_changed = pyqtSignal(int, JobStatus)  # index, status
    queue_started = pyqtSignal()
    queue_paused = pyqtSignal()
    queue_stopped = pyqtSignal()
    
    def __init__(self, queue_file: str = None):
        super().__init__()
        
        self.queue_file = queue_file or os.path.expanduser("~/linuxcnc/configs/job_queue.json")
        self.jobs: List[JobItem] = []
        self.history: List[JobItem] = []
        self.current_job_index = -1
        self.is_running = False
        self.is_paused = False
        
        self.load_queue()
        
    def add_job(self, file_path: str, name: str = None) -> JobItem:
        """Add a job to the queue"""
        job = JobItem(file_path, name)
        self.jobs.append(job)
        self.job_added.emit(job)
        self.save_queue()
        return job
        
    def remove_job(self, index: int) -> bool:
        """Remove a job from the queue"""
        if 0 <= index < len(self.jobs):
            job = self.jobs.pop(index)
            self.job_removed.emit(index)
            
            # Adjust current job index
            if index <= self.current_job_index:
                self.current_job_index -= 1
                
            self.save_queue()
            return True
        return False
        
    def move_job(self, from_index: int, to_index: int) -> bool:
        """Move a job in the queue"""
        if (0 <= from_index < len(self.jobs) and 
            0 <= to_index < len(self.jobs) and 
            from_index != to_index):
            
            job = self.jobs.pop(from_index)
            self.jobs.insert(to_index, job)
            
            # Adjust current job index
            if from_index == self.current_job_index:
                self.current_job_index = to_index
            elif from_index < self.current_job_index <= to_index:
                self.current_job_index -= 1
            elif to_index <= self.current_job_index < from_index:
                self.current_job_index += 1
                
            self.job_moved.emit(from_index, to_index)
            self.save_queue()
            return True
        return False
        
    def get_job(self, index: int) -> JobItem:
        """Get job by index"""
        if 0 <= index < len(self.jobs):
            return self.jobs[index]
        return None
        
    def get_next_pending_job(self) -> JobItem:
        """Get next pending job"""
        for job in self.jobs:
            if job.status == JobStatus.PENDING:
                return job
        return None
        
    def start_queue(self):
        """Start queue execution"""
        self.is_running = True
        self.is_paused = False
        self.queue_started.emit()
        
    def pause_queue(self):
        """Pause queue execution"""
        self.is_paused = True
        self.queue_paused.emit()
        
    def stop_queue(self):
        """Stop queue execution"""
        self.is_running = False
        self.is_paused = False
        self.current_job_index = -1
        self.queue_stopped.emit()
        
    def skip_current_job(self):
        """Skip the current job"""
        if 0 <= self.current_job_index < len(self.jobs):
            job = self.jobs[self.current_job_index]
            job.skip()
            self.job_status_changed.emit(self.current_job_index, job.status)
            self.save_queue()
            
    def hold_job(self, index: int):
        """Put a job on hold"""
        if 0 <= index < len(self.jobs):
            job = self.jobs[index]
            job.hold()
            self.job_status_changed.emit(index, job.status)
            self.save_queue()
            
    def resume_job(self, index: int):
        """Resume a held job"""
        if 0 <= index < len(self.jobs):
            job = self.jobs[index]
            job.resume()
            self.job_status_changed.emit(index, job.status)
            self.save_queue()
            
    def clear_completed(self):
        """Clear completed/failed jobs from queue"""
        completed_jobs = []
        remaining_jobs = []
        
        for i, job in enumerate(self.jobs):
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.SKIPPED]:
                completed_jobs.append(job)
                # Add to history
                if job not in self.history:
                    self.history.append(job)
            else:
                remaining_jobs.append(job)
                
        if completed_jobs:
            self.jobs = remaining_jobs
            self.current_job_index = -1
            self.save_queue()
            
    def get_queue_status(self) -> Dict[str, int]:
        """Get queue status summary"""
        status_counts = {status.value: 0 for status in JobStatus}
        for job in self.jobs:
            status_counts[job.status.value] += 1
        return status_counts
        
    def save_queue(self):
        """Save queue to file"""
        try:
            os.makedirs(os.path.dirname(self.queue_file), exist_ok=True)
            
            data = {
                'queue': [job.to_dict() for job in self.jobs],
                'history': [job.to_dict() for job in self.history[-50:]],  # Keep last 50
                'current_job_index': self.current_job_index,
                'is_running': self.is_running,
                'is_paused': self.is_paused,
                'saved_time': datetime.now().isoformat()
            }
            
            with open(self.queue_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving job queue: {e}")
            
    def load_queue(self):
        """Load queue from file"""
        try:
            if os.path.exists(self.queue_file):
                with open(self.queue_file, 'r') as f:
                    data = json.load(f)
                    
                self.jobs = [JobItem.from_dict(job_data) for job_data in data.get('queue', [])]
                self.history = [JobItem.from_dict(job_data) for job_data in data.get('history', [])]
                self.current_job_index = data.get('current_job_index', -1)
                
                # Don't restore running state - always start stopped
                self.is_running = False
                self.is_paused = False
                
        except Exception as e:
            print(f"Error loading job queue: {e}")
            self.jobs = []
            self.history = []
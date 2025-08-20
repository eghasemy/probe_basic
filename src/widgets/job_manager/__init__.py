"""
Job Manager Widget for PB-Touch Phase 6
Provides job queue management with persistent storage
"""

from .job_manager import JobManagerWidget
from .job_queue import JobQueue, JobItem

__all__ = ['JobManagerWidget', 'JobQueue', 'JobItem']
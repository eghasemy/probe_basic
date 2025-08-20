"""
Job Manager Widget - Main UI Component
Phase 6: Job queue management with run/hold/skip functionality
"""

import os
from datetime import datetime
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QPushButton, QGroupBox,
                             QProgressBar, QTextEdit, QSplitter, QMessageBox,
                             QMenu, QAction, QFileDialog, QComboBox)
from PyQt5.QtGui import QIcon, QFont, QColor

from .job_queue import JobQueue, JobItem, JobStatus

class JobListItem(QListWidgetItem):
    """Custom list item for job display"""
    
    def __init__(self, job: JobItem, index: int):
        super().__init__()
        self.job = job
        self.index = index
        self.update_display()
        
    def update_display(self):
        """Update the display text and appearance"""
        # Status icon/color
        status_colors = {
            JobStatus.PENDING: QColor(200, 200, 200),
            JobStatus.RUNNING: QColor(100, 200, 100),
            JobStatus.COMPLETED: QColor(150, 255, 150),
            JobStatus.FAILED: QColor(255, 150, 150),
            JobStatus.SKIPPED: QColor(255, 255, 150),
            JobStatus.HELD: QColor(255, 200, 100)
        }
        
        # Set text
        duration_text = ""
        if self.job.duration > 0:
            duration_text = f" ({self.job.duration:.1f}s)"
            
        self.setText(f"{self.job.name} - {self.job.status.value.title()}{duration_text}")
        
        # Set color
        color = status_colors.get(self.job.status, QColor(200, 200, 200))
        self.setBackground(color)

class JobManagerWidget(QWidget):
    """Job Manager with queue, history, and execution control"""
    
    # Signals
    job_execute_requested = pyqtSignal(str)  # file_path
    
    def __init__(self, parent=None):
        super(JobManagerWidget, self).__init__(parent)
        
        # Job queue
        self.job_queue = JobQueue()
        
        # Execution timer
        self.execution_timer = QTimer()
        self.execution_timer.timeout.connect(self.process_next_job)
        
        # Current execution state
        self.current_executing_job = None
        
        self.init_ui()
        self.setup_connections()
        self.refresh_display()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Queue controls
        controls_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Queue")
        self.start_btn.setStyleSheet("background-color: #4CAF50; font-weight: bold;")
        controls_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setEnabled(False)
        controls_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)
        
        controls_layout.addStretch()
        
        self.add_file_btn = QPushButton("Add File")
        controls_layout.addWidget(self.add_file_btn)
        
        self.clear_completed_btn = QPushButton("Clear Completed")
        controls_layout.addWidget(self.clear_completed_btn)
        
        layout.addLayout(controls_layout)
        
        # Status display
        status_layout = QHBoxLayout()
        
        self.queue_status_label = QLabel("Queue: 0 jobs")
        status_layout.addWidget(self.queue_status_label)
        
        self.current_job_label = QLabel("Current: None")
        status_layout.addWidget(self.current_job_label)
        
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Job queue list
        queue_panel = self.create_queue_panel()
        splitter.addWidget(queue_panel)
        
        # Job details panel
        details_panel = self.create_details_panel()
        splitter.addWidget(details_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 300])
        layout.addWidget(splitter)
        
    def create_queue_panel(self):
        """Create the job queue panel"""
        panel = QGroupBox("Job Queue")
        layout = QVBoxLayout(panel)
        
        # Queue list
        self.queue_list = QListWidget()
        self.queue_list.setAlternatingRowColors(True)
        self.queue_list.setDragDropMode(QListWidget.InternalMove)
        layout.addWidget(self.queue_list)
        
        # Context menu
        self.queue_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.queue_list.customContextMenuRequested.connect(self.show_job_context_menu)
        
        return panel
        
    def create_details_panel(self):
        """Create the job details panel"""
        panel = QGroupBox("Job Details")
        layout = QVBoxLayout(panel)
        
        # Job info
        self.job_name_label = QLabel("No job selected")
        self.job_name_label.setFont(QFont("", 10, QFont.Bold))
        layout.addWidget(self.job_name_label)
        
        self.job_path_label = QLabel("")
        self.job_path_label.setWordWrap(True)
        layout.addWidget(self.job_path_label)
        
        self.job_status_label = QLabel("")
        layout.addWidget(self.job_status_label)
        
        self.job_times_label = QLabel("")
        layout.addWidget(self.job_times_label)
        
        # Error display
        self.error_text = QTextEdit()
        self.error_text.setMaximumHeight(100)
        self.error_text.setPlaceholderText("No errors")
        self.error_text.setReadOnly(True)
        layout.addWidget(self.error_text)
        
        # Job actions
        action_layout = QHBoxLayout()
        
        self.run_job_btn = QPushButton("Run Job")
        self.run_job_btn.setEnabled(False)
        action_layout.addWidget(self.run_job_btn)
        
        self.hold_job_btn = QPushButton("Hold")
        self.hold_job_btn.setEnabled(False)
        action_layout.addWidget(self.hold_job_btn)
        
        self.skip_job_btn = QPushButton("Skip")
        self.skip_job_btn.setEnabled(False)
        action_layout.addWidget(self.skip_job_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        return panel
        
    def setup_connections(self):
        """Setup signal connections"""
        # Queue controls
        self.start_btn.clicked.connect(self.start_queue)
        self.pause_btn.clicked.connect(self.pause_queue)
        self.stop_btn.clicked.connect(self.stop_queue)
        self.add_file_btn.clicked.connect(self.add_file_dialog)
        self.clear_completed_btn.clicked.connect(self.clear_completed_jobs)
        
        # Job list
        self.queue_list.itemSelectionChanged.connect(self.on_job_selected)
        self.queue_list.itemChanged.connect(self.on_item_moved)
        
        # Job actions
        self.run_job_btn.clicked.connect(self.run_selected_job)
        self.hold_job_btn.clicked.connect(self.hold_selected_job)
        self.skip_job_btn.clicked.connect(self.skip_selected_job)
        
        # Queue signals
        self.job_queue.job_added.connect(self.on_job_added)
        self.job_queue.job_removed.connect(self.on_job_removed)
        self.job_queue.job_status_changed.connect(self.on_job_status_changed)
        self.job_queue.queue_started.connect(self.on_queue_started)
        self.job_queue.queue_paused.connect(self.on_queue_paused)
        self.job_queue.queue_stopped.connect(self.on_queue_stopped)
        
    def refresh_display(self):
        """Refresh the entire display"""
        # Clear and rebuild queue list
        self.queue_list.clear()
        
        for i, job in enumerate(self.job_queue.jobs):
            item = JobListItem(job, i)
            self.queue_list.addItem(item)
            
        # Update status
        self.update_status_display()
        
    def update_status_display(self):
        """Update status labels"""
        status = self.job_queue.get_queue_status()
        total_jobs = len(self.job_queue.jobs)
        pending_jobs = status.get('pending', 0)
        
        self.queue_status_label.setText(f"Queue: {total_jobs} jobs ({pending_jobs} pending)")
        
        # Current job
        if self.current_executing_job:
            self.current_job_label.setText(f"Current: {self.current_executing_job.name}")
        else:
            self.current_job_label.setText("Current: None")
            
    def start_queue(self):
        """Start queue execution"""
        if not self.job_queue.jobs:
            QMessageBox.information(self, "Info", "No jobs in queue")
            return
            
        self.job_queue.start_queue()
        self.execution_timer.start(1000)  # Check every second
        
    def pause_queue(self):
        """Pause queue execution"""
        self.job_queue.pause_queue()
        self.execution_timer.stop()
        
    def stop_queue(self):
        """Stop queue execution"""
        self.job_queue.stop_queue()
        self.execution_timer.stop()
        self.current_executing_job = None
        
    def process_next_job(self):
        """Process the next job in the queue"""
        if self.job_queue.is_paused or not self.job_queue.is_running:
            return
            
        # If no current job, find next pending job
        if not self.current_executing_job:
            next_job = self.job_queue.get_next_pending_job()
            if next_job:
                self.execute_job(next_job)
            else:
                # No more jobs - stop queue
                self.stop_queue()
                QMessageBox.information(self, "Complete", "All jobs completed")
                
    def execute_job(self, job: JobItem):
        """Execute a specific job"""
        self.current_executing_job = job
        job.start()
        
        # Find job index and update display
        for i, queue_job in enumerate(self.job_queue.jobs):
            if queue_job is job:
                self.job_queue.job_status_changed.emit(i, job.status)
                break
                
        # Emit signal for external execution
        self.job_execute_requested.emit(job.file_path)
        
        # For demo purposes, simulate job completion after 3 seconds
        QTimer.singleShot(3000, lambda: self.complete_current_job())
        
    def complete_current_job(self, success=True, error_message=None):
        """Complete the current job"""
        if self.current_executing_job:
            if success:
                self.current_executing_job.complete()
            else:
                self.current_executing_job.fail(error_message)
                
            # Update display
            for i, job in enumerate(self.job_queue.jobs):
                if job is self.current_executing_job:
                    self.job_queue.job_status_changed.emit(i, job.status)
                    break
                    
            self.current_executing_job = None
            self.update_status_display()
            
    def add_file_dialog(self):
        """Show dialog to add file to queue"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Add Job File", "", 
            "G-code Files (*.ngc *.nc *.gcode);;All Files (*)"
        )
        
        if file_path:
            self.add_job_file(file_path)
            
    def add_job_file(self, file_path: str):
        """Add a file to the job queue"""
        if os.path.exists(file_path):
            self.job_queue.add_job(file_path)
            
    def clear_completed_jobs(self):
        """Clear completed jobs from queue"""
        self.job_queue.clear_completed()
        self.refresh_display()
        
    def on_job_selected(self):
        """Handle job selection"""
        items = self.queue_list.selectedItems()
        if not items:
            self.clear_job_details()
            return
            
        item = items[0]
        if isinstance(item, JobListItem):
            self.show_job_details(item.job)
            
    def show_job_details(self, job: JobItem):
        """Show details for selected job"""
        self.job_name_label.setText(job.name)
        self.job_path_label.setText(job.file_path)
        self.job_status_label.setText(f"Status: {job.status.value.title()}")
        
        # Times
        created = job.created_time.strftime("%Y-%m-%d %H:%M:%S")
        times_text = f"Created: {created}"
        
        if job.start_time:
            started = job.start_time.strftime("%Y-%m-%d %H:%M:%S")
            times_text += f"\nStarted: {started}"
            
        if job.end_time:
            ended = job.end_time.strftime("%Y-%m-%d %H:%M:%S")
            times_text += f"\nEnded: {ended}"
            
        if job.duration > 0:
            times_text += f"\nDuration: {job.duration:.1f}s"
            
        self.job_times_label.setText(times_text)
        
        # Error message
        if job.error_message:
            self.error_text.setPlainText(job.error_message)
        else:
            self.error_text.setPlainText("")
            
        # Enable/disable buttons
        can_run = job.status in [JobStatus.PENDING, JobStatus.HELD]
        can_hold = job.status == JobStatus.PENDING
        can_skip = job.status in [JobStatus.PENDING, JobStatus.RUNNING]
        
        self.run_job_btn.setEnabled(can_run)
        self.hold_job_btn.setEnabled(can_hold)
        self.skip_job_btn.setEnabled(can_skip)
        
    def clear_job_details(self):
        """Clear job details display"""
        self.job_name_label.setText("No job selected")
        self.job_path_label.setText("")
        self.job_status_label.setText("")
        self.job_times_label.setText("")
        self.error_text.setPlainText("")
        
        self.run_job_btn.setEnabled(False)
        self.hold_job_btn.setEnabled(False)
        self.skip_job_btn.setEnabled(False)
        
    def run_selected_job(self):
        """Run the selected job immediately"""
        items = self.queue_list.selectedItems()
        if items and isinstance(items[0], JobListItem):
            job = items[0].job
            if job.status in [JobStatus.PENDING, JobStatus.HELD]:
                job.resume()  # In case it was held
                self.execute_job(job)
                
    def hold_selected_job(self):
        """Hold the selected job"""
        items = self.queue_list.selectedItems()
        if items and isinstance(items[0], JobListItem):
            job_item = items[0]
            self.job_queue.hold_job(job_item.index)
            
    def skip_selected_job(self):
        """Skip the selected job"""
        items = self.queue_list.selectedItems()
        if items and isinstance(items[0], JobListItem):
            job_item = items[0]
            self.job_queue.skip_current_job() if job_item.job is self.current_executing_job else None
            
    def show_job_context_menu(self, position):
        """Show context menu for job list"""
        item = self.queue_list.itemAt(position)
        if not item or not isinstance(item, JobListItem):
            return
            
        menu = QMenu(self)
        
        # Run action
        if item.job.status in [JobStatus.PENDING, JobStatus.HELD]:
            run_action = QAction("Run Job", self)
            run_action.triggered.connect(self.run_selected_job)
            menu.addAction(run_action)
            
        # Hold/Resume action
        if item.job.status == JobStatus.PENDING:
            hold_action = QAction("Hold Job", self)
            hold_action.triggered.connect(self.hold_selected_job)
            menu.addAction(hold_action)
        elif item.job.status == JobStatus.HELD:
            resume_action = QAction("Resume Job", self)
            resume_action.triggered.connect(lambda: self.job_queue.resume_job(item.index))
            menu.addAction(resume_action)
            
        # Remove action
        remove_action = QAction("Remove Job", self)
        remove_action.triggered.connect(lambda: self.job_queue.remove_job(item.index))
        menu.addAction(remove_action)
        
        menu.exec_(self.queue_list.mapToGlobal(position))
        
    def on_job_added(self, job: JobItem):
        """Handle job added to queue"""
        self.refresh_display()
        
    def on_job_removed(self, index: int):
        """Handle job removed from queue"""
        self.refresh_display()
        
    def on_job_status_changed(self, index: int, status: JobStatus):
        """Handle job status change"""
        # Update the specific item
        if 0 <= index < self.queue_list.count():
            item = self.queue_list.item(index)
            if isinstance(item, JobListItem):
                item.update_display()
                
        self.update_status_display()
        
        # Refresh details if this job is selected
        items = self.queue_list.selectedItems()
        if items and isinstance(items[0], JobListItem) and items[0].index == index:
            self.show_job_details(items[0].job)
            
    def on_queue_started(self):
        """Handle queue started"""
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        
    def on_queue_paused(self):
        """Handle queue paused"""
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        
    def on_queue_stopped(self):
        """Handle queue stopped"""
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.current_executing_job = None
        self.update_status_display()
        
    def on_item_moved(self, item):
        """Handle item moved in list"""
        # This would be called when drag/drop reordering happens
        # For now, we'll keep it simple and just refresh
        pass
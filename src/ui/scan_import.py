# src/ui/scan_import.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QPushButton, QFileDialog, QListWidget,
                             QListWidgetItem, QLineEdit, QCheckBox, QGroupBox,
                             QProgressBar, QMessageBox, QTabWidget, QTextEdit)
from PySide6.QtCore import Qt, Signal, Slot, QMimeData, QThread
from PySide6.QtGui import QFont, QIcon, QDragEnterEvent, QDropEvent

import os
import time
from pathlib import Path


class ScanImportThread(QThread):
    """Thread for importing scan files to prevent UI freezing"""
    
    # Signals
    progress_updated = Signal(int, int)  # current, total
    status_updated = Signal(str)
    import_complete = Signal(bool, str)  # success, message
    
    def __init__(self, files, options, parent=None):
        super().__init__(parent)
        self.files = files
        self.options = options
    
    def run(self):
        """Run the thread"""
        try:
            total_files = len(self.files)
            
            # Process each file
            for i, file_path in enumerate(self.files):
                # Update progress
                self.progress_updated.emit(i + 1, total_files)
                self.status_updated.emit(f"Processing {os.path.basename(file_path)}...")
                
                # Simulate processing time
                time.sleep(0.5)
            
            # Simulate database processing
            self.status_updated.emit("Storing data in database...")
            time.sleep(1)
            
            # Simulate CVE matching if enabled
            if self.options.get("cve_match", False):
                self.status_updated.emit("Matching services to CVE database...")
                time.sleep(1.5)
            
            # Simulate consolidation if enabled
            if self.options.get("consolidate", False):
                self.status_updated.emit("Consolidating assets...")
                time.sleep(1)
            
            # Complete
            self.import_complete.emit(True, f"Successfully imported {total_files} scan files.")
        
        except Exception as e:
            self.import_complete.emit(False, f"Error importing scan files: {str(e)}")


class ScanImportWidget(QWidget):
    """Widget for importing scan files"""
    
    # Signal emitted when import is complete
    import_completed = Signal(bool, str)
    
    def __init__(self, config=None):
        super().__init__()
        
        self.config = config or {}
        self.selected_files = []
        self.import_thread = None
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Create layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Create import tab
        self._create_import_tab()
        
        # Create scan history tab
        self._create_history_tab()
    
    def _create_import_tab(self):
        """Create the import tab"""
        import_tab = QWidget()
        import_layout = QVBoxLayout(import_tab)
        
        # Create file selection section
        file_group = QGroupBox("Select Scan Files")
        file_layout = QVBoxLayout(file_group)
        
        # Add file selection button
        file_button_layout = QHBoxLayout()
        
        browse_button = QPushButton("Browse Files")
        browse_button.clicked.connect(self._browse_files)
        file_button_layout.addWidget(browse_button)
        
        drag_label = QLabel("or drag and drop files here")
        file_button_layout.addWidget(drag_label)
        
        file_button_layout.addStretch()
        
        file_layout.addLayout(file_button_layout)
        
        # Add selected files list
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(150)
        file_layout.addWidget(self.file_list)
        
        import_layout.addWidget(file_group)
        
        # Create import options section
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout(options_group)
        
        # Add scan name field
        name_layout = QHBoxLayout()
        name_label = QLabel("Scan Name:")
        name_layout.addWidget(name_label)
        
        self.scan_name_edit = QLineEdit()
        self.scan_name_edit.setPlaceholderText("Enter a name for this scan")
        name_layout.addWidget(self.scan_name_edit)
        
        options_layout.addLayout(name_layout)
        
        # Add options checkboxes
        self.auto_detect_check = QCheckBox("Auto-detect file format")
        self.auto_detect_check.setChecked(True)
        options_layout.addWidget(self.auto_detect_check)
        
        self.consolidate_check = QCheckBox("Consolidate assets across scans")
        self.consolidate_check.setChecked(True)
        options_layout.addWidget(self.consolidate_check)
        
        self.cve_match_check = QCheckBox("Match services to CVE database")
        self.cve_match_check.setChecked(True)
        options_layout.addWidget(self.cve_match_check)
        
        self.overwrite_check = QCheckBox("Overwrite existing data")
        self.overwrite_check.setChecked(False)
        options_layout.addWidget(self.overwrite_check)
        
        # Add tags field
        tags_layout = QHBoxLayout()
        tags_label = QLabel("Tags:")
        tags_layout.addWidget(tags_label)
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Enter tags separated by commas (e.g., internal, quarterly)")
        tags_layout.addWidget(self.tags_edit)
        
        options_layout.addLayout(tags_layout)
        
        import_layout.addWidget(options_group)
        
        # Create progress section
        progress_group = QGroupBox("Import Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to import")
        progress_layout.addWidget(self.status_label)
        
        import_layout.addWidget(progress_group)
        
        # Add import buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self._cancel_import)
        button_layout.addWidget(cancel_button)
        
        self.import_button = QPushButton("Import Scans")
        self.import_button.clicked.connect(self._import_scans)
        self.import_button.setEnabled(False)
        button_layout.addWidget(self.import_button)
        
        import_layout.addLayout(button_layout)
        
        # Add import tab
        self.tabs.addTab(import_tab, "Import Scan")
    
    def _create_history_tab(self):
        """Create the scan history tab"""
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        # Search and filter
        filter_layout = QHBoxLayout()
        
        search_label = QLabel("Search:")
        filter_layout.addWidget(search_label)
        
        self.history_search = QLineEdit()
        self.history_search.setPlaceholderText("Search scan history...")
        filter_layout.addWidget(self.history_search)
        
        filter_layout.addStretch()
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._refresh_history)
        filter_layout.addWidget(refresh_button)
        
        history_layout.addLayout(filter_layout)
        
        # Scan history table
        self.history_list = QListWidget()
        history_layout.addWidget(self.history_list)
        
        # Scan details
        details_group = QGroupBox("Scan Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        history_layout.addWidget(details_group)
        
        # Add history tab
        self.tabs.addTab(history_tab, "Scan History")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events for file drag and drop"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events for file drag and drop"""
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            for url in mime_data.urls():
                file_path = url.toLocalFile()
                if file_path and self._is_valid_scan_file(file_path):
                    self._add_file(file_path)
            
            self._update_import_button()
            event.acceptProposedAction()
    
    def _is_valid_scan_file(self, file_path):
        """Check if a file is likely a valid scan file"""
        # In a real application, this would perform more sophisticated validation
        valid_extensions = ['.xml', '.nmap', '.gnmap', '.txt']
        return any(file_path.lower().endswith(ext) for ext in valid_extensions)
    
    def _browse_files(self):
        """Open file dialog to browse for scan files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Nmap Scan Files",
            "",
            "Nmap Files (*.xml *.nmap *.gnmap);;All Files (*.*)"
        )
        
        if files:
            for file_path in files:
                self._add_file(file_path)
            
            self._update_import_button()
    
    def _add_file(self, file_path):
        """Add a file to the selected files list"""
        # Check if file is already in the list
        for i in range(self.file_list.count()):
            if self.file_list.item(i).data(Qt.UserRole) == file_path:
                return
        
        # Add file to the list
        file_name = os.path.basename(file_path)
        file_size = self._get_file_size(file_path)
        item = QListWidgetItem(f"{file_name} ({file_size})")
        item.setData(Qt.UserRole, file_path)
        self.file_list.addItem(item)
        
        # Add file to selected files
        self.selected_files.append(file_path)
        
        # If scan name is empty, use the first file name as default
        if not self.scan_name_edit.text() and len(self.selected_files) == 1:
            default_name = os.path.splitext(file_name)[0].replace('_', ' ').title()
            self.scan_name_edit.setText(default_name)
    
    def _get_file_size(self, file_path):
        """Get the file size in human-readable format"""
        try:
            size_bytes = os.path.getsize(file_path)
            
            # Convert to human-readable format
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024 or unit == 'GB':
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024
            
            return "0 B"  # Fallback
        except Exception as e:
            print(f"Error getting file size: {e}")
            return "Unknown"
    
    def _update_import_button(self):
        """Update the import button state based on selected files"""
        self.import_button.setEnabled(len(self.selected_files) > 0)
    
    def _cancel_import(self):
        """Cancel the import operation"""
        if self.import_thread and self.import_thread.isRunning():
            # Terminate thread if running
            self.import_thread.terminate()
            self.import_thread.wait()
            self.status_label.setText("Import cancelled")
        
        # Clear file list
        self.file_list.clear()
        self.selected_files.clear()
        
        # Reset UI
        self.progress_bar.setValue(0)
        self.scan_name_edit.clear()
        self.tags_edit.clear()
        self.import_button.setEnabled(False)
    
    def _import_scans(self):
        """Import the selected scan files"""
        # Validate input
        if not self.selected_files:
            return
        
        scan_name = self.scan_name_edit.text().strip()
        if not scan_name:
            QMessageBox.warning(self, "Missing Information", 
                              "Please enter a name for this scan.")
            return
        
        # Disable UI during import
        self.import_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting import...")
        
        # Collect import options
        options = {
            'scan_name': scan_name,
            'auto_detect': self.auto_detect_check.isChecked(),
            'consolidate': self.consolidate_check.isChecked(),
            'cve_match': self.cve_match_check.isChecked(),
            'overwrite': self.overwrite_check.isChecked(),
            'tags': [t.strip() for t in self.tags_edit.text().split(',') if t.strip()]
        }
        
        # Create and start import thread
        self.import_thread = ScanImportThread(self.selected_files, options, self)
        self.import_thread.progress_updated.connect(self._on_progress_updated)
        self.import_thread.status_updated.connect(self._on_status_updated)
        self.import_thread.import_complete.connect(self._on_import_complete)
        self.import_thread.start()
    
    @Slot(int, int)
    def _on_progress_updated(self, current, total):
        """Update the progress bar"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
    
    @Slot(str)
    def _on_status_updated(self, status):
        """Update the status label"""
        self.status_label.setText(status)
    
    @Slot(bool, str)
    def _on_import_complete(self, success, message):
        """Handle import completion"""
        # Reset progress bar
        self.progress_bar.setValue(100)
        
        # Update status
        if success:
            self.status_label.setText("Import completed successfully")
        else:
            self.status_label.setText("Import failed")
        
        # Clear file list on success
        if success:
            self.file_list.clear()
            self.selected_files.clear()
            self.scan_name_edit.clear()
            self.tags_edit.clear()
        else:
            self.import_button.setEnabled(True)
        
        # Emit completion signal
        self.import_completed.emit(success, message)
        
        # Refresh history tab
        self._refresh_history()
    
    def _refresh_history(self):
        """Refresh the scan history list"""
        # In a real implementation, this would fetch data from the database
        # For now, we'll use dummy data
        self.history_list.clear()
        
        # Sample data
        history_items = [
            {"name": "Internal Network Scan", "date": "2023-05-20 08:30:45", 
             "files": 3, "assets": 42, "vulnerabilities": 15},
            {"name": "DMZ Servers Scan", "date": "2023-05-19 14:22:10", 
             "files": 2, "assets": 8, "vulnerabilities": 12},
            {"name": "External Interface Scan", "date": "2023-05-18 09:15:32", 
             "files": 1, "assets": 5, "vulnerabilities": 7}
        ]
        
        for item in history_items:
            list_item = QListWidgetItem(f"{item['name']} - {item['date']}")
            list_item.setData(Qt.UserRole, item)
            self.history_list.addItem(list_item)
        
        # Connect selection signal if not already connected
        try:
            self.history_list.itemClicked.disconnect()
        except:
            pass
        self.history_list.itemClicked.connect(self._on_history_item_selected)
    
    def _on_history_item_selected(self, item):
        """Handle selection of a history item"""
        # Get item data
        item_data = item.data(Qt.UserRole)
        
        # Update details text
        details = f"Scan Name: {item_data['name']}\n"
        details += f"Date: {item_data['date']}\n"
        details += f"Files: {item_data['files']}\n"
        details += f"Assets Discovered: {item_data['assets']}\n"
        details += f"Vulnerabilities Found: {item_data['vulnerabilities']}\n\n"
        
        # Add dummy file details
        details += "Files Included:\n"
        for i in range(item_data['files']):
            details += f"- scan_{i+1}.xml\n"
        
        self.details_text.setText(details)
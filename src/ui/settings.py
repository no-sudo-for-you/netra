# src/ui/settings.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QLineEdit, QComboBox, QSpinBox, QCheckBox,
                             QPushButton, QFileDialog, QTabWidget, QFormLayout,
                             QGroupBox, QMessageBox, QScrollArea)
from PySide6.QtCore import Qt, Signal, Slot, QSettings
from PySide6.QtGui import QFont

import os
import yaml
import shutil
from pathlib import Path


class SettingsWidget(QWidget):
    """Widget for configuring application settings"""
    
    # Signal emitted when settings are updated
    settings_updated = Signal()
    
    def __init__(self, config=None):
        super().__init__()
        
        self.config = config or {}
        self.original_config = config.copy() if config else {}
        
        # Create layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create content widget
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.content_layout.addWidget(self.tabs)
        
        # Create general settings tab
        self._create_general_tab()
        
        # Create database settings tab
        self._create_database_tab()
        
        # Create LLM settings tab
        self._create_llm_tab()
        
        # Create reporting settings tab
        self._create_reporting_tab()
        
        # Create advanced settings tab
        self._create_advanced_tab()
        
        # Add buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self._reset_settings)
        button_layout.addWidget(reset_button)
        
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self._save_settings)
        button_layout.addWidget(save_button)
        
        self.content_layout.addLayout(button_layout)
        
        # Set scroll area widget
        scroll_area.setWidget(content_widget)
        self.main_layout.addWidget(scroll_area)
        
        # Load settings
        self._load_settings()
    
    def _create_general_tab(self):
        """Create the general settings tab"""
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("System")
        self.theme_combo.addItem("Light")
        self.theme_combo.addItem("Dark")
        appearance_layout.addRow("Theme:", self.theme_combo)
        
        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(24)
        self.font_size_spin.setValue(12)
        appearance_layout.addRow("Font Size:", self.font_size_spin)
        
        general_layout.addWidget(appearance_group)
        
        # User information group
        user_group = QGroupBox("User Information")
        user_layout = QFormLayout(user_group)
        
        # Company name
        self.company_name_edit = QLineEdit()
        user_layout.addRow("Company Name:", self.company_name_edit)
        
        # Assessor name
        self.assessor_name_edit = QLineEdit()
        user_layout.addRow("Assessor Name:", self.assessor_name_edit)
        
        # Company logo
        logo_layout = QHBoxLayout()
        self.company_logo_edit = QLineEdit()
        logo_layout.addWidget(self.company_logo_edit)
        
        browse_logo_button = QPushButton("Browse")
        browse_logo_button.clicked.connect(self._browse_logo)
        logo_layout.addWidget(browse_logo_button)
        
        user_layout.addRow("Company Logo:", logo_layout)
        
        general_layout.addWidget(user_group)
        
        # Updates group
        updates_group = QGroupBox("Updates")
        updates_layout = QFormLayout(updates_group)
        
        # Auto-update CVE database
        self.auto_update_cve_check = QCheckBox("Automatically update CVE database")
        updates_layout.addRow("", self.auto_update_cve_check)
        
        # Update interval
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setMinimum(1)
        self.update_interval_spin.setMaximum(30)
        self.update_interval_spin.setValue(7)
        self.update_interval_spin.setSuffix(" days")
        updates_layout.addRow("Update Interval:", self.update_interval_spin)
        
        general_layout.addWidget(updates_group)
        
        # Add vertical spacer
        general_layout.addStretch()
        
        # Add tab
        self.tabs.addTab(general_tab, "General")
    
    def _create_database_tab(self):
        """Create the database settings tab"""
        database_tab = QWidget()
        database_layout = QVBoxLayout(database_tab)
        
        # Database location group
        location_group = QGroupBox("Database Location")
        location_layout = QFormLayout(location_group)
        
        # Database path
        db_layout = QHBoxLayout()
        self.database_path_edit = QLineEdit()
        self.database_path_edit.setReadOnly(True)
        db_layout.addWidget(self.database_path_edit)
        
        browse_db_button = QPushButton("Browse")
        browse_db_button.clicked.connect(self._browse_database)
        db_layout.addWidget(browse_db_button)
        
        location_layout.addRow("Database File:", db_layout)
        
        # Backup directory
        backup_layout = QHBoxLayout()
        self.backup_dir_edit = QLineEdit()
        self.backup_dir_edit.setReadOnly(True)
        backup_layout.addWidget(self.backup_dir_edit)
        
        browse_backup_button = QPushButton("Browse")
        browse_backup_button.clicked.connect(self._browse_backup_dir)
        backup_layout.addWidget(browse_backup_button)
        
        location_layout.addRow("Backup Directory:", backup_layout)
        
        database_layout.addWidget(location_group)
        
        # Backup settings group
        backup_group = QGroupBox("Backup Settings")
        backup_layout = QFormLayout(backup_group)
        
        # Auto-backup
        self.auto_backup_check = QCheckBox("Automatically backup database")
        backup_layout.addRow("", self.auto_backup_check)
        
        # Backup interval
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setMinimum(1)
        self.backup_interval_spin.setMaximum(30)
        self.backup_interval_spin.setValue(7)
        self.backup_interval_spin.setSuffix(" days")
        backup_layout.addRow("Backup Interval:", self.backup_interval_spin)
        
        # Backup count
        self.backup_count_spin = QSpinBox()
        self.backup_count_spin.setMinimum(1)
        self.backup_count_spin.setMaximum(20)
        self.backup_count_spin.setValue(5)
        backup_layout.addRow("Keep Backups:", self.backup_count_spin)
        
        database_layout.addWidget(backup_group)
        
        # Database maintenance group
        maintenance_group = QGroupBox("Database Maintenance")
        maintenance_layout = QVBoxLayout(maintenance_group)
        
        # Backup now button
        backup_now_button = QPushButton("Backup Database Now")
        backup_now_button.clicked.connect(self._backup_database)
        maintenance_layout.addWidget(backup_now_button)
        
        # Optimize button
        optimize_button = QPushButton("Optimize Database")
        optimize_button.clicked.connect(self._optimize_database)
        maintenance_layout.addWidget(optimize_button)
        
        # Reset button (with warning)
        reset_button = QPushButton("Reset Database")
        reset_button.clicked.connect(self._reset_database)
        reset_button.setStyleSheet("color: #c0392b;")
        maintenance_layout.addWidget(reset_button)
        
        database_layout.addWidget(maintenance_group)
        
        # Add vertical spacer
        database_layout.addStretch()
        
        # Add tab
        self.tabs.addTab(database_tab, "Database")
    
    def _create_llm_tab(self):
        """Create the LLM settings tab"""
        llm_tab = QWidget()
        llm_layout = QVBoxLayout(llm_tab)
        
        # Model settings group
        model_group = QGroupBox("Model Settings")
        model_layout = QFormLayout(model_group)
        
        # Model path
        model_path_layout = QHBoxLayout()
        self.model_path_edit = QLineEdit()
        self.model_path_edit.setReadOnly(True)
        model_path_layout.addWidget(self.model_path_edit)
        
        browse_model_button = QPushButton("Browse")
        browse_model_button.clicked.connect(self._browse_model)
        model_path_layout.addWidget(browse_model_button)
        
        model_layout.addRow("Model File:", model_path_layout)
        
        # Context size
        self.context_size_spin = QSpinBox()
        self.context_size_spin.setMinimum(512)
        self.context_size_spin.setMaximum(8192)
        self.context_size_spin.setValue(4096)
        self.context_size_spin.setSingleStep(512)
        model_layout.addRow("Context Size:", self.context_size_spin)
        
        # GPU layers
        self.gpu_layers_spin = QSpinBox()
        self.gpu_layers_spin.setMinimum(0)
        self.gpu_layers_spin.setMaximum(100)
        self.gpu_layers_spin.setValue(35)
        model_layout.addRow("GPU Layers:", self.gpu_layers_spin)
        
        # Threads
        self.threads_spin = QSpinBox()
        self.threads_spin.setMinimum(1)
        self.threads_spin.setMaximum(32)
        self.threads_spin.setValue(4)
        model_layout.addRow("CPU Threads:", self.threads_spin)
        
        llm_layout.addWidget(model_group)
        
        # Model management group
        management_group = QGroupBox("Model Management")
        management_layout = QVBoxLayout(management_group)
        
        # Download model button
        download_button = QPushButton("Download New Model")
        download_button.clicked.connect(self._download_model)
        management_layout.addWidget(download_button)
        
        llm_layout.addWidget(management_group)
        
        # Prompt templates group
        templates_group = QGroupBox("Prompt Templates")
        templates_layout = QFormLayout(templates_group)
        
        # Templates path
        templates_path_layout = QHBoxLayout()
        self.templates_path_edit = QLineEdit()
        self.templates_path_edit.setReadOnly(True)
        templates_path_layout.addWidget(self.templates_path_edit)
        
        browse_templates_button = QPushButton("Browse")
        browse_templates_button.clicked.connect(self._browse_templates)
        templates_path_layout.addWidget(browse_templates_button)
        
        templates_layout.addRow("Templates Path:", templates_path_layout)
        
        llm_layout.addWidget(templates_group)
        
        # Add vertical spacer
        llm_layout.addStretch()
        
        # Add tab
        self.tabs.addTab(llm_tab, "LLM")
    
    def _create_reporting_tab(self):
        """Create the reporting settings tab"""
        reporting_tab = QWidget()
        reporting_layout = QVBoxLayout(reporting_tab)
        
        # Output settings group
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout(output_group)
        
        # Templates directory
        templates_dir_layout = QHBoxLayout()
        self.templates_dir_edit = QLineEdit()
        self.templates_dir_edit.setReadOnly(True)
        templates_dir_layout.addWidget(self.templates_dir_edit)
        
        browse_templates_dir_button = QPushButton("Browse")
        browse_templates_dir_button.clicked.connect(self._browse_templates_dir)
        templates_dir_layout.addWidget(browse_templates_dir_button)
        
        output_layout.addRow("Templates Directory:", templates_dir_layout)
        
        # Output directory
        output_dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setReadOnly(True)
        output_dir_layout.addWidget(self.output_dir_edit)
        
        browse_output_dir_button = QPushButton("Browse")
        browse_output_dir_button.clicked.connect(self._browse_output_dir)
        output_dir_layout.addWidget(browse_output_dir_button)
        
        output_layout.addRow("Output Directory:", output_dir_layout)
        
        reporting_layout.addWidget(output_group)
        
        # Report settings group
        report_group = QGroupBox("Report Settings")
        report_layout = QFormLayout(report_group)
        
        # Default format
        self.format_combo = QComboBox()
        self.format_combo.addItem("Microsoft Word (DOCX)")
        self.format_combo.addItem("PDF")
        report_layout.addRow("Default Format:", self.format_combo)
        
        # Include company logo
        self.include_logo_check = QCheckBox("Include company logo in reports")
        report_layout.addRow("", self.include_logo_check)
        
        # Include executive summary
        self.include_summary_check = QCheckBox("Include executive summary")
        self.include_summary_check.setChecked(True)
        report_layout.addRow("", self.include_summary_check)
        
        # Include recommendations
        self.include_recommendations_check = QCheckBox("Include recommendations")
        self.include_recommendations_check.setChecked(True)
        report_layout.addRow("", self.include_recommendations_check)
        
        # Include charts
        self.include_charts_check = QCheckBox("Include charts and visualizations")
        self.include_charts_check.setChecked(True)
        report_layout.addRow("", self.include_charts_check)
        
        # Include raw data
        self.include_raw_data_check = QCheckBox("Include raw scan data")
        report_layout.addRow("", self.include_raw_data_check)
        
        reporting_layout.addWidget(report_group)
        
        # Add vertical spacer
        reporting_layout.addStretch()
        
        # Add tab
        self.tabs.addTab(reporting_tab, "Reporting")
    
    def _create_advanced_tab(self):
        """Create the advanced settings tab"""
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        # Debug group
        debug_group = QGroupBox("Debug Settings")
        debug_layout = QFormLayout(debug_group)
        
        # Enable debug mode
        self.debug_mode_check = QCheckBox("Enable debug mode")
        debug_layout.addRow("", self.debug_mode_check)
        
        # Log level
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItem("INFO")
        self.log_level_combo.addItem("DEBUG")
        self.log_level_combo.addItem("WARNING")
        self.log_level_combo.addItem("ERROR")
        debug_layout.addRow("Log Level:", self.log_level_combo)
        
        # Log file
        log_file_layout = QHBoxLayout()
        self.log_file_edit = QLineEdit()
        self.log_file_edit.setReadOnly(True)
        log_file_layout.addWidget(self.log_file_edit)
        
        browse_log_file_button = QPushButton("Browse")
        browse_log_file_button.clicked.connect(self._browse_log_file)
        log_file_layout.addWidget(browse_log_file_button)
        
        debug_layout.addRow("Log File:", log_file_layout)
        
        advanced_layout.addWidget(debug_group)
        
        # Advanced options group
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout_form = QFormLayout(advanced_group)
        
        # Dashboard refresh interval
        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setMinimum(0)
        self.refresh_interval_spin.setMaximum(3600)
        self.refresh_interval_spin.setValue(300)
        self.refresh_interval_spin.setSuffix(" seconds")
        self.refresh_interval_spin.setSpecialValueText("Disabled")
        advanced_layout_form.addRow("Dashboard Refresh Interval:", self.refresh_interval_spin)
        
        # Concurrent scans
        self.concurrent_scans_spin = QSpinBox()
        self.concurrent_scans_spin.setMinimum(1)
        self.concurrent_scans_spin.setMaximum(16)
        self.concurrent_scans_spin.setValue(4)
        advanced_layout_form.addRow("Concurrent Scan Imports:", self.concurrent_scans_spin)
        
        advanced_layout.addWidget(advanced_group)
        
        # Export/Import settings group
        export_group = QGroupBox("Configuration Management")
        export_layout = QVBoxLayout(export_group)
        
        # Export button
        export_button = QPushButton("Export Configuration")
        export_button.clicked.connect(self._export_config)
        export_layout.addWidget(export_button)
        
        # Import button
        import_button = QPushButton("Import Configuration")
        import_button.clicked.connect(self._import_config)
        export_layout.addWidget(import_button)
        
        advanced_layout.addWidget(export_group)
        
        # Add vertical spacer
        advanced_layout.addStretch()
        
        # Add tab
        self.tabs.addTab(advanced_tab, "Advanced")
    
    def _load_settings(self):
        """Load settings from config"""
        # General settings
        ui_config = self.config.get("ui", {})
        theme = ui_config.get("theme", "system").lower()
        self.theme_combo.setCurrentText(theme.capitalize())
        self.font_size_spin.setValue(ui_config.get("font_size", 12))
        
        reporting_config = self.config.get("reporting", {})
        self.company_name_edit.setText(reporting_config.get("company_name", ""))
        self.assessor_name_edit.setText(reporting_config.get("assessor_name", ""))
        self.company_logo_edit.setText(reporting_config.get("company_logo", ""))
        
        cve_config = self.config.get("cve", {})
        self.auto_update_cve_check.setChecked(cve_config.get("auto_update", True))
        self.update_interval_spin.setValue(cve_config.get("update_interval_days", 7))
        
        # Database settings
        db_config = self.config.get("database", {})
        self.database_path_edit.setText(db_config.get("path", ""))
        self.backup_dir_edit.setText(db_config.get("backup_dir", ""))
        self.auto_backup_check.setChecked(db_config.get("auto_backup", True))
        self.backup_interval_spin.setValue(db_config.get("backup_interval_days", 7))
        self.backup_count_spin.setValue(db_config.get("backup_count", 5))
        
        # LLM settings
        llm_config = self.config.get("llm", {})
        self.model_path_edit.setText(llm_config.get("model_path", ""))
        self.context_size_spin.setValue(llm_config.get("context_size", 4096))
        self.gpu_layers_spin.setValue(llm_config.get("gpu_layers", 35))
        self.threads_spin.setValue(llm_config.get("threads", 4))
        self.templates_path_edit.setText(llm_config.get("templates_path", ""))
        
        # Reporting settings
        self.templates_dir_edit.setText(reporting_config.get("templates_dir", ""))
        self.output_dir_edit.setText(reporting_config.get("output_dir", ""))
        
        format_mapping = {
            "docx": 0,
            "pdf": 1
        }
        self.format_combo.setCurrentIndex(format_mapping.get(reporting_config.get("default_format", "docx"), 0))
        
        self.include_logo_check.setChecked(reporting_config.get("include_logo", True))
        self.include_summary_check.setChecked(reporting_config.get("include_summary", True))
        self.include_recommendations_check.setChecked(reporting_config.get("include_recommendations", True))
        self.include_charts_check.setChecked(reporting_config.get("include_charts", True))
        self.include_raw_data_check.setChecked(reporting_config.get("include_raw_data", False))
        
        # Advanced settings
        debug = self.config.get("debug", False)
        self.debug_mode_check.setChecked(debug)
        
        log_config = self.config.get("logging", {})
        level_mapping = {
            "info": 0,
            "debug": 1,
            "warning": 2,
            "error": 3
        }
        self.log_level_combo.setCurrentIndex(level_mapping.get(log_config.get("level", "info").lower(), 0))
        self.log_file_edit.setText(log_config.get("file", ""))
        
        self.refresh_interval_spin.setValue(ui_config.get("dashboard_refresh_interval", 300))
        self.concurrent_scans_spin.setValue(ui_config.get("concurrent_scans", 4))
    
    def _save_settings(self):
        """Save settings to config"""
        try:
            # General settings
            if "ui" not in self.config:
                self.config["ui"] = {}
            
            self.config["ui"]["theme"] = self.theme_combo.currentText().lower()
            self.config["ui"]["font_size"] = self.font_size_spin.value()
            self.config["ui"]["dashboard_refresh_interval"] = self.refresh_interval_spin.value()
            self.config["ui"]["concurrent_scans"] = self.concurrent_scans_spin.value()
            
            if "reporting" not in self.config:
                self.config["reporting"] = {}
            
            self.config["reporting"]["company_name"] = self.company_name_edit.text()
            self.config["reporting"]["assessor_name"] = self.assessor_name_edit.text()
            self.config["reporting"]["company_logo"] = self.company_logo_edit.text()
            
            if "cve" not in self.config:
                self.config["cve"] = {}
            
            self.config["cve"]["auto_update"] = self.auto_update_cve_check.isChecked()
            self.config["cve"]["update_interval_days"] = self.update_interval_spin.value()
            
            # Database settings
            if "database" not in self.config:
                self.config["database"] = {}
            
            self.config["database"]["path"] = self.database_path_edit.text()
            self.config["database"]["backup_dir"] = self.backup_dir_edit.text()
            self.config["database"]["auto_backup"] = self.auto_backup_check.isChecked()
            self.config["database"]["backup_interval_days"] = self.backup_interval_spin.value()
            self.config["database"]["backup_count"] = self.backup_count_spin.value()
            
            # LLM settings
            if "llm" not in self.config:
                self.config["llm"] = {}
            
            self.config["llm"]["model_path"] = self.model_path_edit.text()
            self.config["llm"]["context_size"] = self.context_size_spin.value()
            self.config["llm"]["gpu_layers"] = self.gpu_layers_spin.value()
            self.config["llm"]["threads"] = self.threads_spin.value()
            self.config["llm"]["templates_path"] = self.templates_path_edit.text()
            
            # Reporting settings
            self.config["reporting"]["templates_dir"] = self.templates_dir_edit.text()
            self.config["reporting"]["output_dir"] = self.output_dir_edit.text()
            
            format_mapping = {
                0: "docx",
                1: "pdf"
            }
            self.config["reporting"]["default_format"] = format_mapping.get(self.format_combo.currentIndex(), "docx")
            
            self.config["reporting"]["include_logo"] = self.include_logo_check.isChecked()
            self.config["reporting"]["include_summary"] = self.include_summary_check.isChecked()
            self.config["reporting"]["include_recommendations"] = self.include_recommendations_check.isChecked()
            self.config["reporting"]["include_charts"] = self.include_charts_check.isChecked()
            self.config["reporting"]["include_raw_data"] = self.include_raw_data_check.isChecked()
            
            # Advanced settings
            self.config["debug"] = self.debug_mode_check.isChecked()
            
            if "logging" not in self.config:
                self.config["logging"] = {}
            
            level_mapping = {
                0: "info",
                1: "debug",
                2: "warning",
                3: "error"
            }
            self.config["logging"]["level"] = level_mapping.get(self.log_level_combo.currentIndex(), "info")
            self.config["logging"]["file"] = self.log_file_edit.text()
            
            # Save to file if available
            config_path = os.environ.get("NART_CONFIG", os.path.expanduser("~/.nart/config.yaml"))
            
            if os.path.exists(os.path.dirname(config_path)):
                # Create backup of existing config
                if os.path.exists(config_path):
                    backup_path = config_path + ".bak"
                    shutil.copy2(config_path, backup_path)
                
                # Save new config
                with open(config_path, "w") as f:
                    yaml.dump(self.config, f, default_flow_style=False)
            
            # Emit signal to notify of settings update
            self.settings_updated.emit()
            
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")
            
            return True
        
        except Exception as e:
            QMessageBox.critical(self, "Error Saving Settings", f"An error occurred while saving settings: {e}")
            return False
    
    def _reset_settings(self):
        """Reset settings to original values"""
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to their previous values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset config
            self.config = self.original_config.copy()
            
            # Reload settings
            self._load_settings()
            
            QMessageBox.information(self, "Settings Reset", "Settings have been reset successfully.")
    
    def _browse_logo(self):
        """Browse for company logo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Company Logo",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            self.company_logo_edit.setText(file_path)
    
    def _browse_database(self):
        """Browse for database file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Database File",
            "",
            "SQLite Database (*.db);;All Files (*.*)"
        )
        
        if file_path:
            self.database_path_edit.setText(file_path)
    
    def _browse_backup_dir(self):
        """Browse for backup directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Directory"
        )
        
        if dir_path:
            self.backup_dir_edit.setText(dir_path)
    
    def _browse_model(self):
        """Browse for LLM model file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select LLM Model File",
            "",
            "GGUF Models (*.gguf);;All Files (*.*)"
        )
        
        if file_path:
            self.model_path_edit.setText(file_path)
    
    def _browse_templates(self):
        """Browse for LLM prompt templates file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Prompt Templates File",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_path:
            self.templates_path_edit.setText(file_path)
    
    def _browse_templates_dir(self):
        """Browse for report templates directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Report Templates Directory"
        )
        
        if dir_path:
            self.templates_dir_edit.setText(dir_path)
    
    def _browse_output_dir(self):
        """Browse for report output directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Report Output Directory"
        )
        
        if dir_path:
            self.output_dir_edit.setText(dir_path)
    
    def _browse_log_file(self):
        """Browse for log file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Log File",
            "",
            "Log Files (*.log);;All Files (*.*)"
        )
        
        if file_path:
            self.log_file_edit.setText(file_path)
    
    def _backup_database(self):
        """Backup the database"""
        try:
            # Get database and backup paths
            db_path = self.database_path_edit.text()
            backup_dir = self.backup_dir_edit.text()
            
            if not db_path or not os.path.exists(db_path):
                QMessageBox.warning(self, "Backup Error", "Database file not found.")
                return
            
            if not backup_dir:
                backup_dir = os.path.join(os.path.dirname(db_path), "backups")
            
            # Create backup directory if it doesn't exist
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"nart_backup_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Copy database file
            shutil.copy2(db_path, backup_path)
            
            QMessageBox.information(self, "Backup Complete", 
                                  f"Database backed up to {backup_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"An error occurred: {e}")
    
    def _optimize_database(self):
        """Optimize the database"""
        try:
            # Get database path
            db_path = self.database_path_edit.text()
            
            if not db_path or not os.path.exists(db_path):
                QMessageBox.warning(self, "Optimization Error", "Database file not found.")
                return
            
            # In a real application, this would use SQLite's VACUUM command
            # For this example, we'll just show a success message
            
            # Show progress dialog
            from PySide6.QtWidgets import QProgressDialog
            progress = QProgressDialog("Optimizing database...", "Cancel", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setAutoClose(True)
            progress.setAutoReset(True)
            
            # Simulate optimization process
            for i in range(1, 101):
                progress.setValue(i)
                
                # Process events to keep UI responsive
                from PySide6.QtCore import QCoreApplication
                QCoreApplication.processEvents()
                
                # Simulate work
                import time
                time.sleep(0.02)
                
                if progress.wasCanceled():
                    break
            
            if not progress.wasCanceled():
                QMessageBox.information(self, "Optimization Complete", 
                                      "Database has been optimized successfully.")
        
        except Exception as e:
            QMessageBox.critical(self, "Optimization Error", f"An error occurred: {e}")
    
    def _reset_database(self):
        """Reset the database (with confirmation)"""
        # Confirm with user
        reply = QMessageBox.warning(
            self,
            "Reset Database",
            "Are you sure you want to reset the database? This will delete all data "
            "and cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            # Get database path
            db_path = self.database_path_edit.text()
            
            if not db_path:
                QMessageBox.warning(self, "Reset Error", "Database path not specified.")
                return
            
            # Backup the database first
            backup_dir = self.backup_dir_edit.text()
            
            if not backup_dir:
                backup_dir = os.path.join(os.path.dirname(db_path), "backups")
            
            # Create backup directory if it doesn't exist
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"nart_backup_before_reset_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            if os.path.exists(db_path):
                # Copy database file to backup
                shutil.copy2(db_path, backup_path)
                
                # Delete existing database
                os.remove(db_path)
            
            # In a real application, this would initialize a new database
            # For this example, we'll just show a success message
            
            QMessageBox.information(self, "Reset Complete", 
                                  f"Database has been reset. A backup was saved to {backup_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Reset Error", f"An error occurred: {e}")
    
    def _download_model(self):
        """Open dialog to download a new LLM model"""
        try:
            # In a real application, this would open a dialog to select and download a model
            # For this example, we'll just show a message
            
            QMessageBox.information(self, "Download Model", 
                                  "This would open the model download dialog.\n\n"
                                  "In a real application, you would select a model to download "
                                  "and it would be saved to the models directory.")
        
        except Exception as e:
            QMessageBox.critical(self, "Download Error", f"An error occurred: {e}")
    
    def _export_config(self):
        """Export configuration to a file"""
        try:
            # Get save path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Configuration",
                "",
                "YAML Files (*.yaml);;All Files (*.*)"
            )
            
            if not file_path:
                return
            
            # Save config to file
            with open(file_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False)
            
            QMessageBox.information(self, "Export Complete", 
                                  f"Configuration exported to {file_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred: {e}")
    
    def _import_config(self):
        """Import configuration from a file"""
        try:
            # Get file path
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import Configuration",
                "",
                "YAML Files (*.yaml);;All Files (*.*)"
            )
            
            if not file_path or not os.path.exists(file_path):
                return
            
            # Confirm with user
            reply = QMessageBox.warning(
                self,
                "Import Configuration",
                "Importing a configuration file will overwrite your current settings. "
                "Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Load config from file
            with open(file_path, "r") as f:
                new_config = yaml.safe_load(f)
            
            if not new_config or not isinstance(new_config, dict):
                QMessageBox.warning(self, "Import Error", "Invalid configuration file.")
                return
            
            # Update config
            self.config = new_config
            
            # Reload settings
            self._load_settings()
            
            QMessageBox.information(self, "Import Complete", 
                                  "Configuration imported successfully.")
        
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"An error occurred: {e}")
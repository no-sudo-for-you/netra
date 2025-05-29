# src/ui/llm_interface.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QComboBox, QSlider, QSpinBox,
                             QProgressBar, QSplitter, QFrame, QTreeWidget, 
                             QTreeWidgetItem, QMessageBox)
from PySide6.QtCore import Qt, Signal, Slot, QThread, QSize
from PySide6.QtGui import QFont, QIcon

import time
import os
import json
from pathlib import Path

from ..llm.model_manager import ModelManager


class GenerateTextThread(QThread):
    """Thread for generating text with LLM to prevent UI freezing"""
    
    # Signal emitted when generation is complete
    generation_complete = Signal(str)
    
    def __init__(self, prompt, max_tokens=1024, temperature=0.7, parent=None):
        super().__init__(parent)
        self.prompt = prompt
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model_manager = ModelManager()
    
    def run(self):
        """Run the thread"""
        try:
            # Generate text
            response = self.model_manager.generate_text(
                self.prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Emit the result
            self.generation_complete.emit(response)
        except Exception as e:
            self.generation_complete.emit(f"Error: {str(e)}")


class PromptTemplate:
    """Represents a prompt template"""
    
    def __init__(self, name, description, template, max_tokens=1024, temperature=0.7):
        self.name = name
        self.description = description
        self.template = template
        self.max_tokens = max_tokens
        self.temperature = temperature


class LLMInterfaceWidget(QWidget):
    """Widget for interacting with the LLM"""
    
    def __init__(self, config=None):
        super().__init__()
        
        self.config = config or {}
        self.model_manager = ModelManager(config)
        self.generate_thread = None
        self.prompt_templates = self._load_prompt_templates()
        
        # Create layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create model status section
        self._create_model_status_section()
        
        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter, 1)
        
        # Create left panel (templates and options)
        self._create_left_panel()
        
        # Create right panel (prompt and response)
        self._create_right_panel()
        
        # Set splitter sizes
        self.splitter.setSizes([300, 700])
        
        # Update model status
        self._update_model_status()
    
    def _create_model_status_section(self):
        """Create model status section"""
        status_frame = QFrame()
        status_frame.setFrameShape(QFrame.StyledPanel)
        status_frame.setMaximumHeight(80)
        
        status_layout = QVBoxLayout(status_frame)
        
        # Status header
        status_header = QLabel("LLM Status")
        status_header.setFont(QFont("Arial", 12, QFont.Bold))
        status_layout.addWidget(status_header)
        
        # Status details
        status_details_layout = QHBoxLayout()
        
        # Model info
        self.model_info_label = QLabel("Model: Not loaded")
        status_details_layout.addWidget(self.model_info_label)
        
        status_details_layout.addStretch()
        
        # Load button
        self.load_model_button = QPushButton("Load Model")
        self.load_model_button.clicked.connect(self._load_model)
        status_details_layout.addWidget(self.load_model_button)
        
        # Unload button
        self.unload_model_button = QPushButton("Unload Model")
        self.unload_model_button.clicked.connect(self._unload_model)
        self.unload_model_button.setEnabled(False)
        status_details_layout.addWidget(self.unload_model_button)
        
        status_layout.addLayout(status_details_layout)
        
        self.main_layout.addWidget(status_frame)
    
    def _create_left_panel(self):
        """Create left panel with templates and options"""
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Templates section
        templates_label = QLabel("Prompt Templates")
        templates_label.setFont(QFont("Arial", 12, QFont.Bold))
        left_layout.addWidget(templates_label)
        
        # Template tree
        self.template_tree = QTreeWidget()
        self.template_tree.setHeaderLabels(["Templates"])
        self.template_tree.setMinimumWidth(250)
        
        # Add templates to tree
        self._populate_template_tree()
        
        # Connect template selection
        self.template_tree.itemClicked.connect(self._on_template_selected)
        
        left_layout.addWidget(self.template_tree)
        
        # Generation options
        options_label = QLabel("Generation Options")
        options_label.setFont(QFont("Arial", 12, QFont.Bold))
        left_layout.addWidget(options_label)
        
        # Temperature option
        temp_layout = QHBoxLayout()
        temp_label = QLabel("Temperature:")
        temp_layout.addWidget(temp_label)
        
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setMinimum(1)
        self.temperature_slider.setMaximum(100)
        self.temperature_slider.setValue(70)  # Default 0.7
        temp_layout.addWidget(self.temperature_slider)
        
        self.temperature_value = QLabel("0.7")
        temp_layout.addWidget(self.temperature_value)
        
        # Connect slider
        self.temperature_slider.valueChanged.connect(self._on_temperature_changed)
        
        left_layout.addLayout(temp_layout)
        
        # Max tokens option
        tokens_layout = QHBoxLayout()
        tokens_label = QLabel("Max Tokens:")
        tokens_layout.addWidget(tokens_label)
        
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setMinimum(64)
        self.max_tokens_spin.setMaximum(4096)
        self.max_tokens_spin.setValue(1024)
        self.max_tokens_spin.setSingleStep(64)
        tokens_layout.addWidget(self.max_tokens_spin)
        
        left_layout.addLayout(tokens_layout)
        
        left_layout.addStretch()
        
        self.splitter.addWidget(left_panel)
    
    def _create_right_panel(self):
        """Create right panel with prompt and response"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Prompt section
        prompt_label = QLabel("Prompt")
        prompt_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(prompt_label)
        
        # Prompt editor
        self.prompt_editor = QTextEdit()
        self.prompt_editor.setMinimumHeight(200)
        self.prompt_editor.setPlaceholderText("Enter your prompt here...")
        right_layout.addWidget(self.prompt_editor)
        
        # Generate button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.template_description = QLabel("")
        button_layout.addWidget(self.template_description)
        
        button_layout.addStretch()
        
        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self._generate_text)
        self.generate_button.setMinimumWidth(120)
        button_layout.addWidget(self.generate_button)
        
        right_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximum(0)  # Indeterminate
        self.progress_bar.setMinimum(0)
        self.progress_bar.hide()
        right_layout.addWidget(self.progress_bar)
        
        # Response section
        response_label = QLabel("Response")
        response_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(response_label)
        
        # Response display
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        self.response_display.setPlaceholderText("LLM response will appear here...")
        right_layout.addWidget(self.response_display)
        
        # Copy button
        copy_layout = QHBoxLayout()
        copy_layout.addStretch()
        
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self._copy_to_clipboard)
        copy_layout.addWidget(self.copy_button)
        
        right_layout.addLayout(copy_layout)
        
        self.splitter.addWidget(right_panel)
    
    def _load_prompt_templates(self):
        """Load prompt templates from config or defaults"""
        templates = {}
        
        # Default templates
        templates["vulnerability_analysis"] = PromptTemplate(
            "Vulnerability Analysis",
            "Analyze a vulnerability and provide detailed information",
            "You are a cybersecurity expert analyzing a vulnerability.\n\n"
            "Vulnerability: [VULNERABILITY]\n\n"
            "Please provide a detailed analysis including:\n"
            "1. Description of the vulnerability\n"
            "2. Potential impact\n"
            "3. Attack vectors\n"
            "4. Recommended mitigations",
            max_tokens=1024,
            temperature=0.3
        )
        
        templates["remediation_plan"] = PromptTemplate(
            "Remediation Plan",
            "Generate a remediation plan for vulnerabilities",
            "You are a cybersecurity expert creating a remediation plan.\n\n"
            "Vulnerabilities:\n[VULNERABILITIES]\n\n"
            "Please provide a comprehensive remediation plan including:\n"
            "1. Prioritized list of actions\n"
            "2. Specific steps for each vulnerability\n"
            "3. Timeline recommendations\n"
            "4. Testing procedures to verify fixes",
            max_tokens=1536,
            temperature=0.4
        )
        
        templates["executive_summary"] = PromptTemplate(
            "Executive Summary",
            "Generate an executive summary for a security assessment report",
            "You are a cybersecurity expert writing an executive summary for a security assessment report.\n\n"
            "Assessment Overview:\n[ASSESSMENT_OVERVIEW]\n\n"
            "Please write a professional executive summary that includes:\n"
            "1. Key findings\n"
            "2. Risk assessment\n"
            "3. High-level recommendations\n"
            "4. Business impact",
            max_tokens=1024,
            temperature=0.5
        )
        
        templates["custom"] = PromptTemplate(
            "Custom Prompt",
            "Create your own custom prompt",
            "",
            max_tokens=2048,
            temperature=0.7
        )
        
        # Load custom templates from config
        custom_templates_path = self.config.get("llm", {}).get("templates_path", "")
        if custom_templates_path and os.path.exists(custom_templates_path):
            try:
                with open(custom_templates_path, "r") as f:
                    custom_templates = json.load(f)
                
                for key, template in custom_templates.items():
                    templates[key] = PromptTemplate(
                        template.get("name", key),
                        template.get("description", ""),
                        template.get("template", ""),
                        max_tokens=template.get("max_tokens", 1024),
                        temperature=template.get("temperature", 0.7)
                    )
            except Exception as e:
                print(f"Error loading custom templates: {e}")
        
        return templates
    
    def _populate_template_tree(self):
        """Populate template tree with available templates"""
        self.template_tree.clear()
        
        # Add categories
        security_category = QTreeWidgetItem(self.template_tree, ["Security Templates"])
        report_category = QTreeWidgetItem(self.template_tree, ["Report Templates"])
        custom_category = QTreeWidgetItem(self.template_tree, ["Custom Templates"])
        
        # Add templates to categories
        for key, template in self.prompt_templates.items():
            if key == "vulnerability_analysis" or key == "remediation_plan":
                item = QTreeWidgetItem(security_category, [template.name])
                item.setData(0, Qt.UserRole, key)
            elif key == "executive_summary":
                item = QTreeWidgetItem(report_category, [template.name])
                item.setData(0, Qt.UserRole, key)
            elif key == "custom":
                item = QTreeWidgetItem(custom_category, [template.name])
                item.setData(0, Qt.UserRole, key)
            else:
                # Determine category based on name
                if "vulnerability" in key.lower() or "remediation" in key.lower() or "security" in key.lower():
                    item = QTreeWidgetItem(security_category, [template.name])
                    item.setData(0, Qt.UserRole, key)
                elif "report" in key.lower() or "summary" in key.lower():
                    item = QTreeWidgetItem(report_category, [template.name])
                    item.setData(0, Qt.UserRole, key)
                else:
                    item = QTreeWidgetItem(custom_category, [template.name])
                    item.setData(0, Qt.UserRole, key)
        
        # Expand all categories
        self.template_tree.expandAll()
    
    def _update_model_status(self):
        """Update the model status display"""
        model_available = self.model_manager.is_model_available()
        model_loaded = self.model_manager.model_loaded
        
        if model_loaded:
            model_path = self.model_manager.model_path
            model_name = os.path.basename(model_path)
            self.model_info_label.setText(f"Model: {model_name} (Loaded)")
            self.load_model_button.setEnabled(False)
            self.unload_model_button.setEnabled(True)
            self.generate_button.setEnabled(True)
        elif model_available:
            model_path = self.model_manager.model_path
            model_name = os.path.basename(model_path)
            self.model_info_label.setText(f"Model: {model_name} (Available)")
            self.load_model_button.setEnabled(True)
            self.unload_model_button.setEnabled(False)
            self.generate_button.setEnabled(True)
        else:
            self.model_info_label.setText("Model: Not available")
            self.load_model_button.setEnabled(False)
            self.unload_model_button.setEnabled(False)
            self.generate_button.setEnabled(False)
    
    @Slot()
    def _load_model(self):
        """Load the LLM model"""
        # Show progress
        self.progress_bar.show()
        self.load_model_button.setEnabled(False)
        
        # Load model in a separate thread to avoid freezing UI
        class LoadModelThread(QThread):
            load_complete = Signal(bool, str)
            
            def __init__(self, model_manager, parent=None):
                super().__init__(parent)
                self.model_manager = model_manager
            
            def run(self):
                try:
                    success = self.model_manager.load_model()
                    if success:
                        self.load_complete.emit(True, "Model loaded successfully")
                    else:
                        self.load_complete.emit(False, f"Error: {self.model_manager.last_error}")
                except Exception as e:
                    self.load_complete.emit(False, f"Error: {str(e)}")
        
        # Create and start thread
        self.load_thread = LoadModelThread(self.model_manager, self)
        self.load_thread.load_complete.connect(self._on_model_loaded)
        self.load_thread.start()
    
    @Slot(bool, str)
    def _on_model_loaded(self, success, message):
        """Handle model loading completion"""
        # Hide progress
        self.progress_bar.hide()
        
        if success:
            # Update UI
            self._update_model_status()
        else:
            # Show error
            QMessageBox.warning(self, "Model Loading Error", message)
            self.load_model_button.setEnabled(True)
    
    @Slot()
    def _unload_model(self):
        """Unload the LLM model"""
        self.model_manager.unload_model()
        self._update_model_status()
    
    @Slot()
    def _on_temperature_changed(self, value):
        """Handle temperature slider change"""
        temperature = value / 100.0
        self.temperature_value.setText(f"{temperature:.2f}")
    
    @Slot(QTreeWidgetItem, int)
    def _on_template_selected(self, item, column):
        """Handle template selection"""
        # Get template key
        template_key = item.data(0, Qt.UserRole)
        if not template_key:
            return
        
        # Get template
        template = self.prompt_templates.get(template_key)
        if not template:
            return
        
        # Update prompt editor
        self.prompt_editor.setText(template.template)
        
        # Update temperature and max tokens
        self.temperature_slider.setValue(int(template.temperature * 100))
        self.max_tokens_spin.setValue(template.max_tokens)
        
        # Update description
        self.template_description.setText(template.description)
    
    @Slot()
    def _generate_text(self):
        """Generate text using the LLM"""
        # Get prompt
        prompt = self.prompt_editor.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Empty Prompt", "Please enter a prompt before generating text.")
            return
        
        # Check if model is available
        if not self.model_manager.is_model_available():
            QMessageBox.warning(self, "Model Not Available", 
                              "The LLM model is not available. Please check your configuration.")
            return
        
        # Get generation parameters
        temperature = self.temperature_slider.value() / 100.0
        max_tokens = self.max_tokens_spin.value()
        
        # Show progress
        self.progress_bar.show()
        self.generate_button.setEnabled(False)
        self.response_display.clear()
        
        # Generate text in a separate thread
        self.generate_thread = GenerateTextThread(prompt, max_tokens, temperature, self)
        self.generate_thread.generation_complete.connect(self._on_generation_complete)
        self.generate_thread.start()
    
    @Slot(str)
    def _on_generation_complete(self, text):
        """Handle text generation completion"""
        # Hide progress
        self.progress_bar.hide()
        self.generate_button.setEnabled(True)
        
        # Display response
        self.response_display.setText(text)
    
     @Slot()
    def _copy_to_clipboard(self):
        """Copy response to clipboard"""
        text = self.response_display.toPlainText()
        if text:
            from PySide6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            # Show temporary message
            self.parent().statusBar().showMessage("Copied to clipboard", 2000)
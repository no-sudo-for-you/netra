# src/ui/recommendation_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton, QComboBox, QLineEdit, QMenu, QAction,
                             QToolButton, QSplitter, QTabWidget, QTextEdit,
                             QMessageBox, QListWidget, QListWidgetItem, QDialog,
                             QFormLayout, QDialogButtonBox)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QFont, QIcon, QColor

import os
import json
from datetime import datetime


class AddRecommendationDialog(QDialog):
    """Dialog for adding or editing a recommendation"""
    
    def __init__(self, parent=None, recommendation=None):
        super().__init__(parent)
        
        self.setWindowTitle("Add Recommendation" if recommendation is None else "Edit Recommendation")
        self.setMinimumWidth(500)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create form
        form_layout = QFormLayout()
        
        # Title
        self.title_edit = QLineEdit()
        if recommendation:
            self.title_edit.setText(recommendation.get("title", ""))
        form_layout.addRow("Title:", self.title_edit)
        
        # Category
        self.category_combo = QComboBox()
        categories = ["Network Security", "Application Security", "System Hardening", 
                    "Authentication", "Encryption", "Patch Management", "Other"]
        self.category_combo.addItems(categories)
        
        if recommendation:
            category = recommendation.get("category", "")
            index = self.category_combo.findText(category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        
        form_layout.addRow("Category:", self.category_combo)
        
        # Description
        self.description_edit = QTextEdit()
        if recommendation:
            self.description_edit.setText(recommendation.get("description", ""))
        form_layout.addRow("Description:", self.description_edit)
        
        # Remediation steps
        self.remediation_edit = QTextEdit()
        if recommendation:
            self.remediation_edit.setText(recommendation.get("remediation_steps", ""))
        form_layout.addRow("Remediation Steps:", self.remediation_edit)
        
        # Impact
        self.impact_combo = QComboBox()
        impacts = ["Low", "Medium", "High"]
        self.impact_combo.addItems(impacts)
        
        if recommendation:
            impact = recommendation.get("impact", "")
            index = self.impact_combo.findText(impact)
            if index >= 0:
                self.impact_combo.setCurrentIndex(index)
        
        form_layout.addRow("Impact:", self.impact_combo)
        
        # Effort
        self.effort_combo = QComboBox()
        efforts = ["Low", "Medium", "High"]
        self.effort_combo.addItems(efforts)
        
        if recommendation:
            effort = recommendation.get("effort", "")
            index = self.effort_combo.findText(effort)
            if index >= 0:
                self.effort_combo.setCurrentIndex(index)
        
        form_layout.addRow("Effort:", self.effort_combo)
        
        # References
        self.references_edit = QTextEdit()
        if recommendation:
            self.references_edit.setText(recommendation.get("references", ""))
        self.references_edit.setMaximumHeight(100)
        form_layout.addRow("References:", self.references_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_recommendation(self):
        """Get the recommendation data"""
        return {
            "title": self.title_edit.text(),
            "category": self.category_combo.currentText(),
            "description": self.description_edit.toPlainText(),
            "remediation_steps": self.remediation_edit.toPlainText(),
            "impact": self.impact_combo.currentText(),
            "effort": self.effort_combo.currentText(),
            "references": self.references_edit.toPlainText()
        }


class RecommendationViewWidget(QWidget):
    """Widget for displaying and managing security recommendations"""
    
    def __init__(self, config=None):
        super().__init__()
        
        self.config = config or {}
        self.selected_recommendation = None
        
        # Create layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Create toolbar
        self._create_toolbar()
        
        # Create splitter
        self.splitter = QSplitter(Qt.Vertical)
        self.main_layout.addWidget(self.splitter)
        
        # Create recommendations table
        self._create_recommendations_table()
        
        # Create recommendation details
        self._create_recommendation_details()
        
        # Set initial splitter sizes
        self.splitter.setSizes([400, 400])
    
    def _create_toolbar(self):
        """Create the toolbar"""
        toolbar_layout = QHBoxLayout()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search recommendations...")
        self.search_box.setClearButtonEnabled(True)
        self.search_box.setMinimumWidth(300)
        self.search_box.textChanged.connect(self._filter_recommendations)
        toolbar_layout.addWidget(self.search_box)
        
        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("All Categories")
        self.filter_combo.addItem("Network Security")
        self.filter_combo.addItem("Application Security")
        self.filter_combo.addItem("System Hardening")
        self.filter_combo.addItem("Authentication")
        self.filter_combo.addItem("Encryption")
        self.filter_combo.addItem("Patch Management")
        self.filter_combo.addItem("Other")
        self.filter_combo.currentIndexChanged.connect(self._update_filter)
        toolbar_layout.addWidget(self.filter_combo)
        
        toolbar_layout.addStretch()
        
        # Add recommendation button
        self.add_button = QPushButton("Add Recommendation")
        self.add_button.clicked.connect(self._add_recommendation)
        toolbar_layout.addWidget(self.add_button)
        
        # Import/Export button
        self.import_export_button = QPushButton("Import/Export")
        toolbar_layout.addWidget(self.import_export_button)
        
        # Set up import/export menu
        import_export_menu = QMenu(self)
        import_action = QAction("Import Recommendations", self)
        import_action.triggered.connect(self._import_recommendations)
        import_export_menu.addAction(import_action)
        
        export_action = QAction("Export Recommendations", self)
        export_action.triggered.connect(self._export_recommendations)
        import_export_menu.addAction(export_action)
        
        self.import_export_button.setMenu(import_export_menu)
        
        # Add to main layout
        self.main_layout.addLayout(toolbar_layout)
    
    def _create_recommendations_table(self):
        """Create the recommendations table"""
        self.recommendations_table = QTableWidget()
        self.recommendations_table.setColumnCount(5)
        self.recommendations_table.setHorizontalHeaderLabels(
            ["Title", "Category", "Impact", "Effort", "Usage Count"]
        )
        
        # Configure table appearance
        self.recommendations_table.horizontalHeader().setStretchLastSection(True)
        self.recommendations_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.recommendations_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recommendations_table.setSelectionMode(QTableWidget.SingleSelection)
        self.recommendations_table.setAlternatingRowColors(True)
        self.recommendations_table.setShowGrid(True)
        self.recommendations_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                selection-background-color: #e6f3ff;
                selection-color: #000000;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)
        
        # Connect signals
        self.recommendations_table.cellClicked.connect(self._on_recommendation_selected)
        
        # Add context menu
        self.recommendations_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.recommendations_table.customContextMenuRequested.connect(self._show_context_menu)
        
        # Add to splitter
        self.splitter.addWidget(self.recommendations_table)
    
    def _create_recommendation_details(self):
        """Create the recommendation details section"""
        self.details_frame = QFrame()
        self.details_frame.setFrameShape(QFrame.StyledPanel)
        self.details_frame.setFrameShadow(QFrame.Raised)
        self.details_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
            }
        """)
        
        details_layout = QVBoxLayout(self.details_frame)
        
        # Recommendation title
        self.recommendation_title = QLabel("Select a recommendation to view details")
        self.recommendation_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        details_layout.addWidget(self.recommendation_title)
        
        # Details tabs
        self.details_tabs = QTabWidget()
        
        # Details tab
        details_tab = QWidget()
        details_layout = QVBoxLayout(details_tab)
        
        # Description section
        description_label = QLabel("Description:")
        description_label.setStyleSheet("font-weight: bold;")
        details_layout.addWidget(description_label)
        
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMaximumHeight(100)
        details_layout.addWidget(self.description_text)
        
        # Remediation steps section
        remediation_label = QLabel("Remediation Steps:")
        remediation_label.setStyleSheet("font-weight: bold;")
        details_layout.addWidget(remediation_label)
        
        self.remediation_text = QTextEdit()
        self.remediation_text.setReadOnly(True)
        details_layout.addWidget(self.remediation_text)
        
        # Add details tab
        self.details_tabs.addTab(details_tab, "Details")
        
        # Metadata tab
        metadata_tab = QWidget()
        metadata_layout = QFormLayout(metadata_tab)
        
        # Category
        category_label = QLabel("Category:")
        category_label.setStyleSheet("font-weight: bold;")
        self.category_value = QLabel("--")
        metadata_layout.addRow(category_label, self.category_value)
        
        # Impact
        impact_label = QLabel("Impact:")
        impact_label.setStyleSheet("font-weight: bold;")
        self.impact_value = QLabel("--")
        metadata_layout.addRow(impact_label, self.impact_value)
        
        # Effort
        effort_label = QLabel("Effort:")
        effort_label.setStyleSheet("font-weight: bold;")
        self.effort_value = QLabel("--")
        metadata_layout.addRow(effort_label, self.effort_value)
        
        # References
        references_label = QLabel("References:")
        references_label.setStyleSheet("font-weight: bold;")
        self.references_value = QTextEdit()
        self.references_value.setReadOnly(True)
        self.references_value.setMaximumHeight(100)
        metadata_layout.addRow(references_label, self.references_value)
        
        # Add metadata tab
        self.details_tabs.addTab(metadata_tab, "Metadata")
        
        # Usage tab
        usage_tab = QWidget()
        usage_layout = QVBoxLayout(usage_tab)
        
        # Usage list
        self.usage_list = QListWidget()
        usage_layout.addWidget(self.usage_list)
        
        # Add usage tab
        self.details_tabs.addTab(usage_tab, "Usage")
        
        # Add tabs to layout
        details_layout.addWidget(self.details_tabs)
        
        # Add buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self._edit_recommendation)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._delete_recommendation)
        self.delete_button.setStyleSheet("color: #c0392b;")
        button_layout.addWidget(self.delete_button)
        
        details_layout.addLayout(button_layout)
        
        # Add to splitter
        self.splitter.addWidget(self.details_frame)
    
    def _load_dummy_data(self):
        """Load dummy data for demonstration"""
        # Clear existing data
        self.recommendations_table.setRowCount(0)
        
        # Sample data
        recommendations = [
            {
                "title": "Enable Multi-Factor Authentication",
                "category": "Authentication",
                "description": "Multi-factor authentication (MFA) adds an additional layer of security by requiring users to provide two or more verification factors to gain access to a resource.",
                "remediation_steps": "1. Identify critical systems that require MFA\n2. Select an appropriate MFA solution\n3. Configure the MFA solution\n4. Test the implementation\n5. Deploy to production\n6. Train users on the new authentication process",
                "impact": "High",
                "effort": "Medium",
                "references": "NIST SP 800-63B\nhttps://pages.nist.gov/800-63-3/sp800-63b.html",
                "usage_count": 12,
                "usage": [
                    "Internal Network Scan - May 2023",
                    "External Security Assessment - April 2023",
                    "Compliance Audit - March 2023"
                ]
            },
            {
                "title": "Update SSL/TLS Configuration",
                "category": "Encryption",
                "description": "Outdated SSL/TLS configurations can expose services to known vulnerabilities and weak cipher suites.",
                "remediation_steps": "1. Disable SSL 2.0, SSL 3.0, TLS 1.0, and TLS 1.1\n2. Enable TLS 1.2 and TLS 1.3\n3. Configure strong cipher suites\n4. Implement proper certificate validation\n5. Enable HSTS for web servers\n6. Test configuration with scanning tools",
                "impact": "Medium",
                "effort": "Low",
                "references": "NIST SP 800-52 Rev. 2\nhttps://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-52r2.pdf",
                "usage_count": 8,
                "usage": [
                    "Web Server Assessment - June 2023",
                    "DMZ Security Scan - May 2023"
                ]
            },
            {
                "title": "Implement Network Segmentation",
                "category": "Network Security",
                "description": "Network segmentation divides a network into multiple segments or subnets, each acting as its own small network. This allows security administrators to control the flow of traffic between segments based on granular policies.",
                "remediation_steps": "1. Identify critical assets and group them logically\n2. Define security zones and trust levels\n3. Design network segments based on security zones\n4. Implement firewalls and access controls between segments\n5. Monitor and log traffic between segments\n6. Regularly review and update segmentation policies",
                "impact": "High",
                "effort": "High",
                "references": "NIST SP 800-125B\nCIS Controls v8: Control 12",
                "usage_count": 5,
                "usage": [
                    "Network Architecture Review - April 2023",
                    "Internal Security Assessment - February 2023"
                ]
            }
        ]
        
        # Add recommendations to table
        for recommendation in recommendations:
            row = self.recommendations_table.rowCount()
            self.recommendations_table.insertRow(row)
            
            # Set data
            self.recommendations_table.setItem(row, 0, QTableWidgetItem(recommendation["title"]))
            self.recommendations_table.setItem(row, 1, QTableWidgetItem(recommendation["category"]))
            self.recommendations_table.setItem(row, 2, QTableWidgetItem(recommendation["impact"]))
            self.recommendations_table.setItem(row, 3, QTableWidgetItem(recommendation["effort"]))
            self.recommendations_table.setItem(row, 4, QTableWidgetItem(str(recommendation["usage_count"])))
            
            # Store full recommendation data
            self.recommendations_table.item(row, 0).setData(Qt.UserRole, recommendation)
    
    def _filter_recommendations(self):
        """Filter recommendations by search text"""
        search_text = self.search_box.text().lower()
        
        for row in range(self.recommendations_table.rowCount()):
            match = False
            
            # Check each column for a match
            for col in range(self.recommendations_table.columnCount()):
                item = self.recommendations_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            
            # Show/hide row based on match
            self.recommendations_table.setRowHidden(row, not match)
    
    def _update_filter(self, index):
        """Update filter based on combo box selection"""
        # Reset search first
        self.search_box.clear()
        
        # Show all rows
        for row in range(self.recommendations_table.rowCount()):
            self.recommendations_table.setRowHidden(row, False)
        
        # If not "All Categories", filter by category
        if index > 0:
            category = self.filter_combo.currentText()
            
            for row in range(self.recommendations_table.rowCount()):
                item = self.recommendations_table.item(row, 1)  # Category column
                if item and item.text() != category:
                    self.recommendations_table.setRowHidden(row, True)
    
    def _on_recommendation_selected(self, row, column):
        """Handle recommendation selection in the table"""
        # Get recommendation data
        rec_data = self.recommendations_table.item(row, 0).data(Qt.UserRole)
        self.selected_recommendation = rec_data
        
        # Update recommendation title
        self.recommendation_title.setText(rec_data["title"])
        
        # Update details tab
        self.description_text.setPlainText(rec_data["description"])
        self.remediation_text.setPlainText(rec_data["remediation_steps"])
        
        # Update metadata tab
        self.category_value.setText(rec_data["category"])
        
        # Set impact with color
        impact_text = rec_data["impact"]
        if impact_text == "High":
            self.impact_value.setStyleSheet("color: #e74c3c; font-weight: bold;")
        elif impact_text == "Medium":
            self.impact_value.setStyleSheet("color: #f39c12; font-weight: bold;")
        elif impact_text == "Low":
            self.impact_value.setStyleSheet("color: #2ecc71; font-weight: bold;")
        else:
            self.impact_value.setStyleSheet("color: #333333;")
        self.impact_value.setText(impact_text)
        
        # Set effort with color
        effort_text = rec_data["effort"]
        if effort_text == "High":
            self.effort_value.setStyleSheet("color: #e74c3c; font-weight: bold;")
        elif effort_text == "Medium":
            self.effort_value.setStyleSheet("color: #f39c12; font-weight: bold;")
        elif effort_text == "Low":
            self.effort_value.setStyleSheet("color: #2ecc71; font-weight: bold;")
        else:
            self.effort_value.setStyleSheet("color: #333333;")
        self.effort_value.setText(effort_text)
        
        self.references_value.setPlainText(rec_data.get("references", ""))
        
        # Update usage tab
        self.usage_list.clear()
        for usage in rec_data.get("usage", []):
            self.usage_list.addItem(usage)
    
    def _show_context_menu(self, pos):
        """Show context menu for recommendations table"""
        # Get the row under the cursor
        row = self.recommendations_table.rowAt(pos.y())
        if row < 0:
            return
        
        # Create menu
        menu = QMenu(self)
        
        # Add actions
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(lambda: self._edit_recommendation(row))
        menu.addAction(edit_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self._delete_recommendation(row))
        menu.addAction(delete_action)
        
        # Show menu
        menu.exec_(self.recommendations_table.mapToGlobal(pos))
    
    def _add_recommendation(self):
        """Add a new recommendation"""
        dialog = AddRecommendationDialog(self)
        
        if dialog.exec_():
            # Get recommendation data
            rec_data = dialog.get_recommendation()
            
            # Add dummy usage data
            rec_data["usage_count"] = 0
            rec_data["usage"] = []
            
            # Add to table
            row = self.recommendations_table.rowCount()
            self.recommendations_table.insertRow(row)
            
            # Set data
            self.recommendations_table.setItem(row, 0, QTableWidgetItem(rec_data["title"]))
            self.recommendations_table.setItem(row, 1, QTableWidgetItem(rec_data["category"]))
            self.recommendations_table.setItem(row, 2, QTableWidgetItem(rec_data["impact"]))
            self.recommendations_table.setItem(row, 3, QTableWidgetItem(rec_data["effort"]))
            self.recommendations_table.setItem(row, 4, QTableWidgetItem(str(rec_data["usage_count"])))
            
            # Store full recommendation data
            self.recommendations_table.item(row, 0).setData(Qt.UserRole, rec_data)
            
            # Select the new recommendation
            self.recommendations_table.selectRow(row)
            self._on_recommendation_selected(row, 0)
    
    def _edit_recommendation(self, row=None):
        """Edit the selected recommendation"""
        # If row is specified, use that, otherwise use selected recommendation
        if row is None:
            if not self.selected_recommendation:
                return
        else:
            self.selected_recommendation = self.recommendations_table.item(row, 0).data(Qt.UserRole)
        
        dialog = AddRecommendationDialog(self, self.selected_recommendation)
        
        if dialog.exec_():
            # Get updated recommendation data
            rec_data = dialog.get_recommendation()
            
            # Preserve usage data
            rec_data["usage_count"] = self.selected_recommendation.get("usage_count", 0)
            rec_data["usage"] = self.selected_recommendation.get("usage", [])
            
            # Update table
            row = self.recommendations_table.currentRow()
            
            self.recommendations_table.item(row, 0).setText(rec_data["title"])
            self.recommendations_table.item(row, 1).setText(rec_data["category"])
            self.recommendations_table.item(row, 2).setText(rec_data["impact"])
            self.recommendations_table.item(row, 3).setText(rec_data["effort"])
            
            # Update stored data
            self.recommendations_table.item(row, 0).setData(Qt.UserRole, rec_data)
            
            # Update details
            self.selected_recommendation = rec_data
            self._on_recommendation_selected(row, 0)
    
    def _delete_recommendation(self, row=None):
        """Delete the selected recommendation"""
        # If row is specified, use that, otherwise use current selection
        if row is None:
            row = self.recommendations_table.currentRow()
            if row < 0:
                return
        
        # Get recommendation title
        title = self.recommendations_table.item(row, 0).text()
        
        # Confirm deletion
        reply = QMessageBox.warning(
            self,
            "Delete Recommendation",
            f'Are you sure you want to delete "{title}"?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove from table
            self.recommendations_table.removeRow(row)
            
            # Clear selection
            self.selected_recommendation = None
            self.recommendation_title.setText("Select a recommendation to view details")
            self.description_text.clear()
            self.remediation_text.clear()
            self.category_value.setText("--")
            self.impact_value.setText("--")
            self.effort_value.setText("--")
            self.references_value.clear()
            self.usage_list.clear()
    
    def _import_recommendations(self):
        """Import recommendations from a file"""
        # Get file path
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Recommendations",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if not file_path or not os.path.exists(file_path):
            return
        
        try:
            # Load recommendations from file
            with open(file_path, "r") as f:
                recommendations = json.load(f)
            
            if not isinstance(recommendations, list):
                QMessageBox.warning(self, "Import Error", "Invalid recommendations file format.")
                return
            
            # Clear existing recommendations
            reply = QMessageBox.question(
                self,
                "Import Recommendations",
                "Do you want to replace existing recommendations or append to them?",
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Ok
            )
            
            if reply == QMessageBox.Ok:
                # Replace existing
                self.recommendations_table.setRowCount(0)
            
            # Add recommendations to table
            for rec in recommendations:
                row = self.recommendations_table.rowCount()
                self.recommendations_table.insertRow(row)
                
                # Set data
                self.recommendations_table.setItem(row, 0, QTableWidgetItem(rec.get("title", "")))
                self.recommendations_table.setItem(row, 1, QTableWidgetItem(rec.get("category", "")))
                self.recommendations_table.setItem(row, 2, QTableWidgetItem(rec.get("impact", "")))
                self.recommendations_table.setItem(row, 3, QTableWidgetItem(rec.get("effort", "")))
                self.recommendations_table.setItem(row, 4, QTableWidgetItem(str(rec.get("usage_count", 0))))
                
                # Store full recommendation data
                self.recommendations_table.item(row, 0).setData(Qt.UserRole, rec)
            
            QMessageBox.information(self, "Import Complete", 
                                  f"Successfully imported {len(recommendations)} recommendations.")
        
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"An error occurred: {e}")
    
    def _export_recommendations(self):
        """Export recommendations to a file"""
        # Get file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Recommendations",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            # Collect recommendations
            recommendations = []
            
            for row in range(self.recommendations_table.rowCount()):
                rec = self.recommendations_table.item(row, 0).data(Qt.UserRole)
                recommendations.append(rec)
            
            # Save to file
            with open(file_path, "w") as f:
                json.dump(recommendations, f, indent=2)
            
            QMessageBox.information(self, "Export Complete", 
                                  f"Successfully exported {len(recommendations)} recommendations.")
        
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred: {e}")
    
    @Slot()
    def refresh_data(self):
        """Refresh the recommendations data"""
        # In a real implementation, this would fetch data from the database
        self._load_dummy_data()
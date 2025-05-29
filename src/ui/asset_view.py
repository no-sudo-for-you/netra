# src/ui/asset_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton, QComboBox, QLineEdit, QMenu, QAction,
                             QToolButton, QSplitter, QTabWidget, QListWidget,
                             QListWidgetItem, QMessageBox)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QFont, QIcon, QColor

import os
import json
from datetime import datetime


class AssetViewWidget(QWidget):
    """Widget for displaying and managing assets"""
    
    def __init__(self, config=None):
        super().__init__()
        
        self.config = config or {}
        self.selected_asset = None
        
        # Create layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Create toolbar
        self._create_toolbar()
        
        # Create splitter
        self.splitter = QSplitter(Qt.Vertical)
        self.main_layout.addWidget(self.splitter)
        
        # Create assets table
        self._create_assets_table()
        
        # Create asset details
        self._create_asset_details()
        
        # Set initial splitter sizes
        self.splitter.setSizes([400, 400])
    
    def _create_toolbar(self):
        """Create the toolbar"""
        toolbar_layout = QHBoxLayout()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search assets...")
        self.search_box.setClearButtonEnabled(True)
        self.search_box.setMinimumWidth(300)
        self.search_box.textChanged.connect(self._filter_assets)
        toolbar_layout.addWidget(self.search_box)
        
        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("All Assets")
        self.filter_combo.addItem("By IP Address")
        self.filter_combo.addItem("By Operating System")
        self.filter_combo.addItem("By Risk Level")
        self.filter_combo.currentIndexChanged.connect(self._update_filter)
        toolbar_layout.addWidget(self.filter_combo)
        
        toolbar_layout.addStretch()
        
        # Export button
        self.export_button = QPushButton("Export")
        toolbar_layout.addWidget(self.export_button)
        
        # Add to main layout
        self.main_layout.addLayout(toolbar_layout)
    
    def _create_assets_table(self):
        """Create the assets table"""
        self.assets_table = QTableWidget()
        self.assets_table.setColumnCount(7)
        self.assets_table.setHorizontalHeaderLabels(
            ["IP Address", "Hostname", "OS", "Open Ports", "Vulnerabilities", "Risk Level", "Last Seen"]
        )
        
        # Configure table appearance
        self.assets_table.horizontalHeader().setStretchLastSection(True)
        self.assets_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.assets_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.assets_table.setSelectionMode(QTableWidget.SingleSelection)
        self.assets_table.setAlternatingRowColors(True)
        self.assets_table.setShowGrid(True)
        self.assets_table.setStyleSheet("""
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
        self.assets_table.cellClicked.connect(self._on_asset_selected)
        
        # Add to splitter
        self.splitter.addWidget(self.assets_table)
    
    def _create_asset_details(self):
        """Create the asset details section"""
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
        
        # Asset title
        self.asset_title = QLabel("Select an asset to view details")
        self.asset_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        details_layout.addWidget(self.asset_title)
        
        # Details tabs
        self.details_tabs = QTabWidget()
        
        # Overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        
        # Basic info section
        info_frame = QFrame()
        info_layout = QHBoxLayout(info_frame)
        
        # IP and hostname
        ip_layout = QVBoxLayout()
        ip_label = QLabel("IP Address:")
        ip_label.setStyleSheet("font-weight: bold;")
        ip_layout.addWidget(ip_label)
        
        self.ip_value = QLabel("--")
        ip_layout.addWidget(self.ip_value)
        
        hostname_label = QLabel("Hostname:")
        hostname_label.setStyleSheet("font-weight: bold;")
        ip_layout.addWidget(hostname_label)
        
        self.hostname_value = QLabel("--")
        ip_layout.addWidget(self.hostname_value)
        
        info_layout.addLayout(ip_layout)
        
        # OS and MAC
        os_layout = QVBoxLayout()
        os_label = QLabel("Operating System:")
        os_label.setStyleSheet("font-weight: bold;")
        os_layout.addWidget(os_label)
        
        self.os_value = QLabel("--")
        os_layout.addWidget(self.os_value)
        
        mac_label = QLabel("MAC Address:")
        mac_label.setStyleSheet("font-weight: bold;")
        os_layout.addWidget(mac_label)
        
        self.mac_value = QLabel("--")
        os_layout.addWidget(self.mac_value)
        
        info_layout.addLayout(os_layout)
        
        # Status and risk
        status_layout = QVBoxLayout()
        status_label = QLabel("Status:")
        status_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(status_label)
        
        self.status_value = QLabel("--")
        status_layout.addWidget(self.status_value)
        
        risk_label = QLabel("Risk Level:")
        risk_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(risk_label)
        
        self.risk_value = QLabel("--")
        status_layout.addWidget(self.risk_value)
        
        info_layout.addLayout(status_layout)
        
        overview_layout.addWidget(info_frame)
        
        # Last seen and notes
        last_seen_label = QLabel("Last Seen:")
        last_seen_label.setStyleSheet("font-weight: bold;")
        overview_layout.addWidget(last_seen_label)
        
        self.last_seen_value = QLabel("--")
        overview_layout.addWidget(self.last_seen_value)
        
        notes_label = QLabel("Notes:")
        notes_label.setStyleSheet("font-weight: bold;")
        overview_layout.addWidget(notes_label)
        
        self.notes_value = QLabel("No notes available")
        overview_layout.addWidget(self.notes_value)
        
        overview_layout.addStretch()
        
        # Add overview tab
        self.details_tabs.addTab(overview_tab, "Overview")
        
        # Ports tab
        ports_tab = QWidget()
        ports_layout = QVBoxLayout(ports_tab)
        
        self.ports_list = QTableWidget()
        self.ports_list.setColumnCount(4)
        self.ports_list.setHorizontalHeaderLabels(
            ["Port", "Protocol", "Service", "State"]
        )
        
        # Configure table appearance
        self.ports_list.horizontalHeader().setStretchLastSection(True)
        self.ports_list.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.ports_list.setAlternatingRowColors(True)
        
        ports_layout.addWidget(self.ports_list)
        
        # Add ports tab
        self.details_tabs.addTab(ports_tab, "Ports")
        
        # Vulnerabilities tab
        vulns_tab = QWidget()
        vulns_layout = QVBoxLayout(vulns_tab)
        
        self.vulns_list = QTableWidget()
        self.vulns_list.setColumnCount(4)
        self.vulns_list.setHorizontalHeaderLabels(
            ["CVE", "Severity", "CVSS Score", "Description"]
        )
        
        # Configure table appearance
        self.vulns_list.horizontalHeader().setStretchLastSection(True)
        self.vulns_list.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.vulns_list.setAlternatingRowColors(True)
        
        vulns_layout.addWidget(self.vulns_list)
        
        # Add vulnerabilities tab
        self.details_tabs.addTab(vulns_tab, "Vulnerabilities")
        
        # History tab
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        self.history_list = QListWidget()
        history_layout.addWidget(self.history_list)
        
        # Add history tab
        self.details_tabs.addTab(history_tab, "History")
        
        # Add tabs to layout
        details_layout.addWidget(self.details_tabs)
        
        # Add to splitter
        self.splitter.addWidget(self.details_frame)
    
    def _load_dummy_data(self):
        """Load dummy data for demonstration"""
        # Clear existing data
        self.assets_table.setRowCount(0)
        
        # Sample data
        assets = [
            {
                "ip_address": "192.168.1.1",
                "hostname": "gateway",
                "os": "Linux 5.10",
                "open_ports": 3,
                "vulnerabilities": 2,
                "risk_level": "Medium",
                "last_seen": "2023-05-20 08:30:45",
                "mac_address": "00:11:22:33:44:55",
                "status": "Online",
                "notes": "Main gateway router",
                "ports": [
                    {"port": 22, "protocol": "TCP", "service": "SSH", "state": "open"},
                    {"port": 80, "protocol": "TCP", "service": "HTTP", "state": "open"},
                    {"port": 443, "protocol": "TCP", "service": "HTTPS", "state": "open"}
                ],
                "vulnerabilities_list": [
                    {"cve": "CVE-2021-28041", "severity": "Medium", "cvss": 6.8, 
                     "description": "OpenSSH through 8.5 has an Observable Discrepancy vulnerability."},
                    {"cve": "CVE-2020-15778", "severity": "Medium", "cvss": 6.8, 
                     "description": "scp in OpenSSH through 8.3p1 allows command injection."}
                ],
                "history": [
                    "2023-05-20 08:30:45 - Discovered in scan",
                    "2023-05-19 14:22:10 - Last ping response",
                    "2023-05-18 09:15:32 - Service scan completed"
                ]
            },
            {
                "ip_address": "192.168.1.10",
                "hostname": "webserver",
                "os": "Ubuntu 22.04",
                "open_ports": 5,
                "vulnerabilities": 3,
                "risk_level": "High",
                "last_seen": "2023-05-20 08:32:15",
                "mac_address": "AA:BB:CC:DD:EE:FF",
                "status": "Online",
                "notes": "Main web server",
                "ports": [
                    {"port": 22, "protocol": "TCP", "service": "SSH", "state": "open"},
                    {"port": 80, "protocol": "TCP", "service": "HTTP", "state": "open"},
                    {"port": 443, "protocol": "TCP", "service": "HTTPS", "state": "open"},
                    {"port": 3306, "protocol": "TCP", "service": "MySQL", "state": "open"},
                    {"port": 5432, "protocol": "TCP", "service": "PostgreSQL", "state": "open"}
                ],
                "vulnerabilities_list": [
                    {"cve": "CVE-2022-22965", "severity": "Critical", "cvss": 9.8, 
                     "description": "Spring Framework RCE via Data Binding"},
                    {"cve": "CVE-2021-44228", "severity": "Critical", "cvss": 10.0, 
                     "description": "Apache Log4j RCE - Log4Shell"},
                    {"cve": "CVE-2022-1292", "severity": "High", "cvss": 7.5, 
                     "description": "OpenSSL - c_rehash script allows command injection"}
                ],
                "history": [
                    "2023-05-20 08:32:15 - Discovered in scan",
                    "2023-05-20 08:35:22 - Vulnerability scan completed",
                    "2023-05-19 16:45:10 - Service scan completed"
                ]
            }
        ]
         # Add assets to table
        for asset in assets:
            row = self.assets_table.rowCount()
            self.assets_table.insertRow(row)
            
            # Set data
            self.assets_table.setItem(row, 0, QTableWidgetItem(asset["ip_address"]))
            self.assets_table.setItem(row, 1, QTableWidgetItem(asset["hostname"]))
            self.assets_table.setItem(row, 2, QTableWidgetItem(asset["os"]))
            self.assets_table.setItem(row, 3, QTableWidgetItem(str(asset["open_ports"])))
            self.assets_table.setItem(row, 4, QTableWidgetItem(str(asset["vulnerabilities"])))
            
            # Set risk level with color
            risk_item = QTableWidgetItem(asset["risk_level"])
            if asset["risk_level"] == "High":
                risk_item.setForeground(QColor("#e74c3c"))
            elif asset["risk_level"] == "Medium":
                risk_item.setForeground(QColor("#f39c12"))
            elif asset["risk_level"] == "Low":
                risk_item.setForeground(QColor("#2ecc71"))
            self.assets_table.setItem(row, 5, risk_item)
            
            self.assets_table.setItem(row, 6, QTableWidgetItem(asset["last_seen"]))
            
            # Store full asset data
            self.assets_table.item(row, 0).setData(Qt.UserRole, asset)
    
    def _filter_assets(self):
        """Filter assets by search text"""
        search_text = self.search_text.lower()
        
        for row in range(self.assets_table.rowCount()):
            match = False
            
            # Check each column for a match
            for col in range(self.assets_table.columnCount()):
                item = self.assets_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            
            # Show/hide row based on match
            self.assets_table.setRowHidden(row, not match)
    
    def _update_filter(self, index):
        """Update filter based on combo box selection"""
        # Reset search first
        self.search_box.clear()
        
        # Show all rows
        for row in range(self.assets_table.rowCount()):
            self.assets_table.setRowHidden(row, False)
        
        # Update placeholder text based on filter
        if index == 0:  # All Assets
            self.search_box.setPlaceholderText("Search assets...")
        elif index == 1:  # By IP Address
            self.search_box.setPlaceholderText("Search by IP address...")
        elif index == 2:  # By Operating System
            self.search_box.setPlaceholderText("Search by OS...")
        elif index == 3:  # By Risk Level
            self.search_box.setPlaceholderText("Search by risk level...")
    
    def _on_asset_selected(self, row, column):
        """Handle asset selection in the table"""
        # Get asset data
        asset_data = self.assets_table.item(row, 0).data(Qt.UserRole)
        self.selected_asset = asset_data
        
        # Update asset title
        self.asset_title.setText(f"{asset_data['hostname']} ({asset_data['ip_address']})")
        
        # Update overview tab
        self.ip_value.setText(asset_data["ip_address"])
        self.hostname_value.setText(asset_data["hostname"])
        self.os_value.setText(asset_data["os"])
        self.mac_value.setText(asset_data["mac_address"])
        self.status_value.setText(asset_data["status"])
        
        # Set risk level with color
        risk_text = asset_data["risk_level"]
        if risk_text == "High":
            self.risk_value.setStyleSheet("color: #e74c3c; font-weight: bold;")
        elif risk_text == "Medium":
            self.risk_value.setStyleSheet("color: #f39c12; font-weight: bold;")
        elif risk_text == "Low":
            self.risk_value.setStyleSheet("color: #2ecc71; font-weight: bold;")
        else:
            self.risk_value.setStyleSheet("color: #333333;")
        self.risk_value.setText(risk_text)
        
        self.last_seen_value.setText(asset_data["last_seen"])
        self.notes_value.setText(asset_data.get("notes", "No notes available"))
        
        # Update ports tab
        self.ports_list.setRowCount(0)
        for port in asset_data.get("ports", []):
            row = self.ports_list.rowCount()
            self.ports_list.insertRow(row)
            
            self.ports_list.setItem(row, 0, QTableWidgetItem(str(port["port"])))
            self.ports_list.setItem(row, 1, QTableWidgetItem(port["protocol"]))
            self.ports_list.setItem(row, 2, QTableWidgetItem(port["service"]))
            self.ports_list.setItem(row, 3, QTableWidgetItem(port["state"]))
        
        # Update vulnerabilities tab
        self.vulns_list.setRowCount(0)
        for vuln in asset_data.get("vulnerabilities_list", []):
            row = self.vulns_list.rowCount()
            self.vulns_list.insertRow(row)
            
            self.vulns_list.setItem(row, 0, QTableWidgetItem(vuln["cve"]))
            
            # Set severity with color
            severity_item = QTableWidgetItem(vuln["severity"])
            if vuln["severity"] == "Critical":
                severity_item.setForeground(QColor("#c0392b"))
            elif vuln["severity"] == "High":
                severity_item.setForeground(QColor("#e74c3c"))
            elif vuln["severity"] == "Medium":
                severity_item.setForeground(QColor("#f39c12"))
            elif vuln["severity"] == "Low":
                severity_item.setForeground(QColor("#2ecc71"))
            self.vulns_list.setItem(row, 1, severity_item)
            
            self.vulns_list.setItem(row, 2, QTableWidgetItem(str(vuln["cvss"])))
            self.vulns_list.setItem(row, 3, QTableWidgetItem(vuln["description"]))
        
        # Update history tab
        self.history_list.clear()
        for event in asset_data.get("history", []):
            self.history_list.addItem(event)
    
    @Slot()
    def refresh_data(self):
        """Refresh the assets data"""
        # In a real implementation, this would fetch data from the database
        self._load_dummy_data()
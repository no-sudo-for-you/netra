import sys
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QStackedWidget, QLabel, QPushButton, QToolButton,
                             QFrame, QSizePolicy, QSpacerItem, QMessageBox)
from PySide6.QtCore import Qt, QSize, Signal, Slot, QTimer
from PySide6.QtGui import QIcon, QPixmap, QFont

from .dashboard import DashboardWidget
from .scan_import import ScanImportWidget
from .asset_view import AssetViewWidget
from .vulnerability_view import VulnerabilityViewWidget
from .report_generator import ReportGeneratorWidget
from .recommendation_view import RecommendationViewWidget
from .settings import SettingsWidget
from .llm_interface import LLMInterfaceWidget

# Try to import darkdetect for theme detection
try:
    import darkdetect
    HAS_DARKDETECT = True
except ImportError:
    HAS_DARKDETECT = False


class NavigationButton(QPushButton):
    """Custom styled navigation button"""
    
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFlat(True)
        
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24))
        
        # Style the button
        self.setMinimumHeight(48)
        self.setFont(QFont("Arial", 10))


class MainWindow(QMainWindow):
    """Main application window with modern UI"""
    
    def __init__(self, config=None):
        super().__init__()
        
        self.config = config or {}
        
        # Set window properties
        self.setWindowTitle("RedBlue Labs NART - Network Assessment Reporting Tool")
        self.setMinimumSize(1200, 800)
        
        # Apply theme
        self._apply_theme()
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create left sidebar
        self._create_sidebar()
        
        # Create content area
        self._create_content_area()
        
        # Create status bar with additional info
        self._create_status_bar()
        
        # Create widgets for each section
        self._create_page_widgets()
        
        # Initialize to dashboard
        self.dashboard_button.setChecked(True)
        self.show_dashboard()
        
        # Setup theme update timer if darkdetect is available
        if HAS_DARKDETECT:
            self.theme_timer = QTimer(self)
            self.theme_timer.timeout.connect(self._check_theme_change)
            self.theme_timer.start(5000)  # Check every 5 seconds
            self.current_theme = darkdetect.theme()
    
    def _create_sidebar(self):
        """Create the sidebar with navigation buttons"""
        # Create sidebar container
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        
        # Create sidebar layout
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Create logo area
        logo_frame = QFrame()
        logo_layout = QVBoxLayout(logo_frame)
        logo_label = QLabel("NART")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFont(QFont("Arial", 18, QFont.Bold))
        logo_label.setObjectName("logo")
        logo_layout.addWidget(logo_label)
        
        # Add subtitle
        subtitle_label = QLabel("Network Assessment Reporting Tool")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Arial", 9))
        subtitle_label.setObjectName("subtitle")
        logo_layout.addWidget(subtitle_label)
        
        # Add to sidebar
        sidebar_layout.addWidget(logo_frame)
        
        # Add spacing
        sidebar_layout.addSpacing(20)
        
        # Navigation area
        nav_frame = QFrame()
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(10, 0, 10, 0)
        nav_layout.setSpacing(8)
        
        # Navigation buttons
        # In a real app, you would use actual icon files
        self.dashboard_button = NavigationButton("Dashboard", None)
        self.dashboard_button.clicked.connect(self.show_dashboard)
        nav_layout.addWidget(self.dashboard_button)
        
        self.scans_button = NavigationButton("Scan Import", None)
        self.scans_button.clicked.connect(self.show_scan_import)
        nav_layout.addWidget(self.scans_button)
        
        self.assets_button = NavigationButton("Assets", None)
        self.assets_button.clicked.connect(self.show_assets)
        nav_layout.addWidget(self.assets_button)
        
        self.vulnerabilities_button = NavigationButton("Vulnerabilities", None)
        self.vulnerabilities_button.clicked.connect(self.show_vulnerabilities)
        nav_layout.addWidget(self.vulnerabilities_button)
        
        self.recommendations_button = NavigationButton("Recommendations", None)
        self.recommendations_button.clicked.connect(self.show_recommendations)
        nav_layout.addWidget(self.recommendations_button)
        
        self.reports_button = NavigationButton("Reports", None)
        self.reports_button.clicked.connect(self.show_report_generator)
        nav_layout.addWidget(self.reports_button)
        
        self.llm_button = NavigationButton("AI Assistant", None)
        self.llm_button.clicked.connect(self.show_llm_interface)
        nav_layout.addWidget(self.llm_button)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        nav_layout.addWidget(separator)
        
        self.settings_button = NavigationButton("Settings", None)
        self.settings_button.clicked.connect(self.show_settings)
        nav_layout.addWidget(self.settings_button)
        
        # Add spacer at the bottom
        nav_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Add navigation to sidebar
        sidebar_layout.addWidget(nav_frame)
        
        # Add sidebar to main layout
        self.main_layout.addWidget(self.sidebar)
    
    def _create_content_area(self):
        """Create the main content area"""
        # Create content container
        self.content_container = QFrame()
        
        # Create content layout
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create header
        self.header = QFrame()
        self.header.setObjectName("header")
        self.header.setMinimumHeight(60)
        self.header.setMaximumHeight(60)
        
        # Header layout
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        # Page title
        self.page_title = QLabel("Dashboard")
        self.page_title.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(self.page_title)
        
        # Header spacer
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Header buttons (if needed)
        # ...
        
        # Add header to content layout
        content_layout.addWidget(self.header)
        
        # Create stacked widget for content pages
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        
        # Add content container to main layout
        self.main_layout.addWidget(self.content_container)
    
    def _create_status_bar(self):
        """Create an enhanced status bar"""
        self.statusBar().setMinimumHeight(30)
        
        # Permanent widgets in status bar
        self.db_status_label = QLabel("Database: Connected")
        self.statusBar().addPermanentWidget(self.db_status_label)
        
        self.llm_status_label = QLabel("LLM: Not Loaded")
        self.statusBar().addPermanentWidget(self.llm_status_label)
        
        self.cve_status_label = QLabel("CVE DB: Up to date")
        self.statusBar().addPermanentWidget(self.cve_status_label)
        
        self.version_label = QLabel("v1.0.0")
        self.statusBar().addPermanentWidget(self.version_label)
        
        # Set initial status
        self.statusBar().showMessage("Ready")
    
    def _create_page_widgets(self):
        """Create widgets for each page"""
        # Dashboard
        self.dashboard_widget = DashboardWidget(self.config)
        self.content_stack.addWidget(self.dashboard_widget)
        
        # Scan Import
        self.scan_import_widget = ScanImportWidget(self.config)
        self.scan_import_widget.import_completed.connect(self.on_import_completed)
        self.content_stack.addWidget(self.scan_import_widget)
        
        # Assets View
        self.asset_view_widget = AssetViewWidget(self.config)
        self.content_stack.addWidget(self.asset_view_widget)
        
        # Vulnerabilities View
        self.vulnerability_view_widget = VulnerabilityViewWidget(self.config)
        self.content_stack.addWidget(self.vulnerability_view_widget)
        
        # Recommendations View
        self.recommendation_view_widget = RecommendationViewWidget(self.config)
        self.content_stack.addWidget(self.recommendation_view_widget)
        
        # Report Generator
        self.report_generator_widget = ReportGeneratorWidget(self.config)
        self.content_stack.addWidget(self.report_generator_widget)
        
        # LLM Interface
        self.llm_interface_widget = LLMInterfaceWidget(self.config)
        self.content_stack.addWidget(self.llm_interface_widget)
        
        # Settings
        self.settings_widget = SettingsWidget(self.config)
        self.settings_widget.settings_updated.connect(self.on_settings_updated)
        self.content_stack.addWidget(self.settings_widget)
    
    def _apply_theme(self):
        """Apply theme based on configuration or system theme"""
        theme = self.config.get("ui", {}).get("theme", "system")
        
        # Determine theme based on setting
        if theme == "system" and HAS_DARKDETECT:
            theme = darkdetect.theme().lower()
        
        # Default to light if system detection failed
        if theme not in ["light", "dark"]:
            theme = "light"
        
        # Apply the theme
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                #sidebar {
                    background-color: #252526;
                    border-right: 1px solid #333333;
                }
                #header {
                    background-color: #252526;
                    border-bottom: 1px solid #333333;
                }
                #logo {
                    color: #3ba1e8;
                }
                #subtitle {
                    color: #cccccc;
                }
                QPushButton {
                    background-color: #2d2d30;
                    color: #ffffff;
                    border: 1px solid #3f3f46;
                    border-radius: 4px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #3e3e42;
                }
                QPushButton:pressed, QPushButton:checked {
                    background-color: #007acc;
                    border-color: #007acc;
                }
                QFrame {
                    background-color: transparent;
                }
                QTableView, QTreeView, QListView {
                    background-color: #252526;
                    alternate-background-color: #2d2d30;
                    color: #ffffff;
                    border: 1px solid #3f3f46;
                }
                QHeaderView::section {
                    background-color: #2d2d30;
                    color: #ffffff;
                    border: 1px solid #3f3f46;
                }
                QStatusBar {
                    background-color: #007acc;
                    color: #ffffff;
                }
                QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
                    background-color: #2d2d30;
                    color: #ffffff;
                    border: 1px solid #3f3f46;
                    border-radius: 4px;
                    padding: 4px;
                }
                QTabWidget::pane {
                    border: 1px solid #3f3f46;
                    background-color: #252526;
                }
                QTabBar::tab {
                    background-color: #2d2d30;
                    color: #ffffff;
                    border: 1px solid #3f3f46;
                    padding: 6px 12px;
                }
                QTabBar::tab:selected {
                    background-color: #007acc;
                    border-color: #007acc;
                }
            """)
        else:
            # Light theme
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #f5f5f5;
                    color: #212121;
                }
                #sidebar {
                    background-color: #e0e0e0;
                    border-right: 1px solid #cccccc;
                }
                #header {
                    background-color: #ffffff;
                    border-bottom: 1px solid #cccccc;
                }
                #logo {
                    color: #205493;
                }
                #subtitle {
                    color: #666666;
                }
                QPushButton {
                    background-color: #ffffff;
                    color: #212121;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                }
                QPushButton:pressed, QPushButton:checked {
                    background-color: #205493;
                    color: #ffffff;
                    border-color: #205493;
                }
                QFrame {
                    background-color: transparent;
                }
                QTableView, QTreeView, QListView {
                    background-color: #ffffff;
                    alternate-background-color: #f9f9f9;
                    color: #212121;
                    border: 1px solid #cccccc;
                }
                QHeaderView::section {
                    background-color: #e0e0e0;
                    color: #212121;
                    border: 1px solid #cccccc;
                }
                QStatusBar {
                    background-color: #205493;
                    color: #ffffff;
                }
                QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
                    background-color: #ffffff;
                    color: #212121;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 4px;
                }
                QTabWidget::pane {
                    border: 1px solid #cccccc;
                    background-color: #ffffff;
                }
                QTabBar::tab {
                    background-color: #e0e0e0;
                    color: #212121;
                    border: 1px solid #cccccc;
                    padding: 6px 12px;
                }
                QTabBar::tab:selected {
                    background-color: #205493;
                    color: #ffffff;
                    border-color: #205493;
                }
            """)
    
    def _check_theme_change(self):
        """Check if system theme has changed"""
        if HAS_DARKDETECT and self.config.get("ui", {}).get("theme", "system") == "system":
            new_theme = darkdetect.theme()
            if new_theme != self.current_theme:
                self.current_theme = new_theme
                self._apply_theme()
    
    def _clear_nav_buttons(self):
        """Clear the checked state of all navigation buttons"""
        for button in [self.dashboard_button, self.scans_button, self.assets_button,
                     self.vulnerabilities_button, self.recommendations_button,
                     self.reports_button, self.llm_button, self.settings_button]:
            button.setChecked(False)
    
    @Slot()
    def show_dashboard(self):
        """Show the dashboard view"""
        self._clear_nav_buttons()
        self.dashboard_button.setChecked(True)
        self.page_title.setText("Dashboard")
        self.content_stack.setCurrentWidget(self.dashboard_widget)
        self.statusBar().showMessage("Dashboard")
        
        # Refresh dashboard data
        self.dashboard_widget.refresh_data()
    
    @Slot()
    def show_scan_import(self):
        """Show the scan import view"""
        self._clear_nav_buttons()
        self.scans_button.setChecked(True)
        self.page_title.setText("Scan Import")
        self.content_stack.setCurrentWidget(self.scan_import_widget)
        self.statusBar().showMessage("Scan Import")
    
    @Slot()
    def show_assets(self):
        """Show the assets view"""
        self._clear_nav_buttons()
        self.assets_button.setChecked(True)
        self.page_title.setText("Assets")
        self.content_stack.setCurrentWidget(self.asset_view_widget)
        self.statusBar().showMessage("Assets")
        
        # Refresh assets data
        self.asset_view_widget.refresh_data()
    
    @Slot()
    def show_vulnerabilities(self):
        """Show the vulnerabilities view"""
        self._clear_nav_buttons()
        self.vulnerabilities_button.setChecked(True)
        self.page_title.setText("Vulnerabilities")
        self.content_stack.setCurrentWidget(self.vulnerability_view_widget)
        self.statusBar().showMessage("Vulnerabilities")
        
        # Refresh vulnerabilities data
        self.vulnerability_view_widget.refresh_data()
    
    @Slot()
    def show_recommendations(self):
        """Show the recommendations view"""
        self._clear_nav_buttons()
        self.recommendations_button.setChecked(True)
        self.page_title.setText("Recommendations")
        self.content_stack.setCurrentWidget(self.recommendation_view_widget)
        self.statusBar().showMessage("Recommendations")
        
        # Refresh recommendations data
        self.recommendation_view_widget.refresh_data()
    
    @Slot()
    def show_report_generator(self):
        """Show the report generator view"""
        self._clear_nav_buttons()
        self.reports_button.setChecked(True)
        self.page_title.setText("Report Generator")
        self.content_stack.setCurrentWidget(self.report_generator_widget)
        self.statusBar().showMessage("Report Generator")
    
    @Slot()
    def show_llm_interface(self):
        """Show the LLM interface view"""
        self._clear_nav_buttons()
        self.llm_button.setChecked(True)
        self.page_title.setText("AI Assistant")
        self.content_stack.setCurrentWidget(self.llm_interface_widget)
        self.statusBar().showMessage("AI Assistant")
    
    @Slot()
    def show_settings(self):
        """Show the settings view"""
        self._clear_nav_buttons()
        self.settings_button.setChecked(True)
        self.page_title.setText("Settings")
        self.content_stack.setCurrentWidget(self.settings_widget)
        self.statusBar().showMessage("Settings")
    
    @Slot(bool, str)
    def on_import_completed(self, success, message):
        """Handle scan import completion"""
        if success:
            QMessageBox.information(self, "Import Successful", message)
            
            # Refresh relevant data
            self.dashboard_widget.refresh_data()
        else:
            QMessageBox.warning(self, "Import Failed", message)
    
    @Slot()
    def on_settings_updated(self):
        """Handle settings update"""
        # Re-apply theme
        self._apply_theme()
        
        # Update status bar
        self.version_label.setText(f"v{self.config.get('version', '1.0.0')}")
        
        # Notify user
        self.statusBar().showMessage("Settings updated", 3000)
# src/ui/dashboard.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QSizePolicy, QScrollArea, QPushButton)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtGui import QFont, QColor, QPalette, QIcon

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class StatCard(QFrame):
    """Widget for displaying a statistic with a title"""
    
    clicked = Signal()
    
    def __init__(self, title, value="0", subtitle="", color="#205493", icon_path=None):
        super().__init__()
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumHeight(120)
        self.setMaximumHeight(120)
        self.setCursor(Qt.PointingHandCursor)
        
        # Style the card
        self.setStyleSheet(f"""
            StatCard {{
                background-color: white;
                border-radius: 8px;
                border-left: 5px solid {color};
            }}
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Add title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #666666; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Add value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        layout.addWidget(value_label)
        self.value_label = value_label
        
        # Add subtitle if provided
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #999999; font-size: 12px;")
            layout.addWidget(subtitle_label)
            self.subtitle_label = subtitle_label
    
    def mousePressEvent(self, event):
        """Handle mouse press events to emit clicked signal"""
        self.clicked.emit()
        super().mousePressEvent(event)
    
    def update_value(self, value):
        """Update the displayed value"""
        self.value_label.setText(str(value))


class ChartWidget(QFrame):
    """Widget for displaying a chart"""
    
    def __init__(self, title):
        super().__init__()
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(300)
        
        # Style the widget
        self.setStyleSheet("""
            ChartWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Add title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #333333; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")
        layout.addWidget(self.canvas)
        
        # Store reference to axes for later updates
        self.ax = self.figure.add_subplot(111)


class RecentActivityItem(QFrame):
    """Widget for displaying a recent activity item"""
    
    def __init__(self, icon_path, title, description, timestamp):
        super().__init__()
        
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumHeight(60)
        self.setMaximumHeight(60)
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Add icon
        icon_label = QLabel()
        if icon_path and os.path.exists(icon_path):
            icon_label.setPixmap(QPixmap(icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_label.setText("●")
            icon_label.setStyleSheet("font-size: 24px; color: #205493;")
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Add text content
        content_layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; color: #333333;")
        content_layout.addWidget(title_label)
        
        description_label = QLabel(description)
        description_label.setStyleSheet("color: #666666;")
        content_layout.addWidget(description_label)
        
        layout.addLayout(content_layout)
        
        # Add timestamp
        timestamp_label = QLabel(timestamp)
        timestamp_label.setStyleSheet("color: #999999; font-size: 12px;")
        timestamp_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(timestamp_label)


class DashboardWidget(QWidget):
    """Dashboard widget displaying overview of the system status"""
    
    def __init__(self, config=None):
        super().__init__()
        
        self.config = config or {}
        self.refresh_timer = None
        
        # Create layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Create stat cards section
        self._create_stat_cards()
        
        # Create charts section
        self._create_charts()
        
        # Create recent activity section
        self._create_recent_activity()
        
        # Set up refresh timer
        refresh_interval = self.config.get("ui", {}).get("dashboard_refresh_interval", 300)
        if refresh_interval > 0:
            self.refresh_timer = QTimer(self)
            self.refresh_timer.timeout.connect(self.refresh_data)
            self.refresh_timer.start(refresh_interval * 1000)
    
    def _create_stat_cards(self):
        """Create the stat cards section"""
        # Create stat cards layout
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Add stat cards
        self.assets_card = StatCard("Assets", "0", "Total discovered assets", "#3498db")
        stats_layout.addWidget(self.assets_card)
        
        self.vulns_card = StatCard("Vulnerabilities", "0", "Total vulnerabilities", "#e74c3c")
        stats_layout.addWidget(self.vulns_card)
        
        self.critical_card = StatCard("Critical", "0", "Critical vulnerabilities", "#c0392b")
        stats_layout.addWidget(self.critical_card)
        
        self.ports_card = StatCard("Open Ports", "0", "Total open ports", "#2ecc71")
        stats_layout.addWidget(self.ports_card)
        
        # Add to main layout
        self.main_layout.addLayout(stats_layout)
    
    def _create_charts(self):
        """Create the charts section"""
        # Create charts layout
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # Add charts
        self.severity_chart = ChartWidget("Vulnerability Severity")
        charts_layout.addWidget(self.severity_chart)
        
        self.service_chart = ChartWidget("Service Distribution")
        charts_layout.addWidget(self.service_chart)
        
        # Add to main layout
        self.main_layout.addLayout(charts_layout)
    
    def _create_recent_activity(self):
        """Create the recent activity section"""
        # Create container
        activity_frame = QFrame()
        activity_frame.setFrameShape(QFrame.StyledPanel)
        activity_frame.setFrameShadow(QFrame.Raised)
        activity_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
            }
        """)
        
        activity_layout = QVBoxLayout(activity_frame)
        
        # Add header
        header_layout = QHBoxLayout()
        
        activity_title = QLabel("Recent Activity")
        activity_title.setStyleSheet("color: #333333; font-size: 16px; font-weight: bold;")
        header_layout.addWidget(activity_title)
        
        header_layout.addStretch()
        
        view_all_button = QPushButton("View All")
        view_all_button.setFlat(True)
        view_all_button.setStyleSheet("color: #205493;")
        header_layout.addWidget(view_all_button)
        
        activity_layout.addLayout(header_layout)
        
        # Create scrollable area for activity items
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        self.activity_list_layout = QVBoxLayout(scroll_content)
        self.activity_list_layout.setContentsMargins(0, 0, 0, 0)
        self.activity_list_layout.setSpacing(0)
        
        # Add placeholder items
        for i in range(5):
            self.activity_list_layout.addWidget(
                RecentActivityItem(None, f"Placeholder Activity {i+1}", 
                                 "This is a placeholder description", "Just now")
            )
        
        # Add stretching space at the end
        self.activity_list_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        activity_layout.addWidget(scroll_area)
        
        # Add to main layout
        self.main_layout.addWidget(activity_frame)
    
    def _update_vulnerability_chart(self, data=None):
        """Update the vulnerability severity chart"""
        # Clear previous plot
        self.severity_chart.ax.clear()
        
        # Use dummy data if none provided
        if data is None:
            labels = ['Critical', 'High', 'Medium', 'Low']
            sizes = [5, 15, 30, 50]
            colors = ['#e74c3c', '#e67e22', '#f1c40f', '#3498db']
        else:
            labels = data.get('labels', [])
            sizes = data.get('sizes', [])
            colors = data.get('colors', [])
        
        # Create pie chart
        self.severity_chart.ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                 startangle=90, colors=colors)
        self.severity_chart.ax.axis('equal')
        
        # Redraw canvas
        self.severity_chart.canvas.draw()
    
    def _update_service_chart(self, data=None):
        """Update the service distribution chart"""
        # Clear previous plot
        self.service_chart.ax.clear()
        
        # Use dummy data if none provided
        if data is None:
            services = ['SSH', 'HTTP', 'HTTPS', 'SMB', 'RDP', 'Other']
            counts = [25, 40, 35, 20, 15, 10]
            colors = ['#3498db'] * len(services)
        else:
            services = data.get('services', [])
            counts = data.get('counts', [])
            colors = data.get('colors', ['#3498db'] * len(services))
        
        # Create bar chart
        bars = self.service_chart.ax.bar(services, counts, color=colors)
        
        # Add labels
        for bar in bars:
            height = bar.get_height()
            self.service_chart.ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                                     f'{int(height)}', ha='center', va='bottom')
        
        # Customize grid
        self.service_chart.ax.set_axisbelow(True)
        self.service_chart.ax.yaxis.grid(True, linestyle='--', alpha=0.7)
        self.service_chart.ax.set_xticklabels(services, rotation=45, ha='right')
        
        # Redraw canvas
        self.service_chart.canvas.draw()
    
    def _update_recent_activity(self, activities=None):
        """Update the recent activity list"""
        # Clear previous items
        while self.activity_list_layout.count() > 0:
            item = self.activity_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Use dummy data if none provided
        if activities is None:
            activities = [
                {
                    'icon': None,
                    'title': 'Scan Imported',
                    'description': 'Internal Network Scan',
                    'timestamp': '10 min ago'
                },
                {
                    'icon': None,
                    'title': 'Report Generated',
                    'description': 'Monthly Security Assessment',
                    'timestamp': '2 hours ago'
                },
                {
                    'icon': None,
                    'title': 'CVE Database Updated',
                    'description': '250 new entries added',
                    'timestamp': '3 hours ago'
                },
                {
                    'icon': None,
                    'title': 'Vulnerability Discovered',
                    'description': 'Critical severity in web server',
                    'timestamp': '5 hours ago'
                },
                {
                    'icon': None,
                    'title': 'Recommendation Added',
                    'description': 'Update OpenSSH to latest version',
                    'timestamp': '1 day ago'
                }
            ]
        
        # Add new items
        for activity in activities:
            self.activity_list_layout.addWidget(
                RecentActivityItem(
                    activity.get('icon'),
                    activity.get('title', ''),
                    activity.get('description', ''),
                    activity.get('timestamp', '')
                )
            )
        
        # Add stretching space at the end
        self.activity_list_layout.addStretch()
    
    @Slot()
    def refresh_data(self):
        """Refresh all dashboard data"""
        try:
            # In a real implementation, this would fetch data from the database
            # For now, we'll use dummy data
            
            # Update stat cards
            self.assets_card.update_value("42")
            self.vulns_card.update_value("128")
            self.critical_card.update_value("15")
            self.ports_card.update_value("256")
            
            # Update charts
            self._update_vulnerability_chart()
            self._update_service_chart()
            
            # Update activity
            self._update_recent_activity()
            
        except Exception as e:
            print(f"Error refreshing dashboard data: {e}")
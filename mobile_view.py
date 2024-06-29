import os
from PyQt6.QtWidgets import  QWidget, QVBoxLayout,  QFileDialog,QLabel,QSlider
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl,Qt

class MobileView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)


        # Create a container widget for the web view
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_widget.setLayout(self.container_layout)
        
        

        
        # Apply border styling to the container widget
        

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setStyleSheet("border:none;")
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(500)
        self.zoom_slider.setValue(250)  # Initial zoom level
        self.zoom_slider.valueChanged.connect(self.zoom_changed)
        
        self.web_view = QWebEngineView()
        self.container_layout.addWidget(self.web_view)
        self.container_layout.addWidget(self.zoom_slider)    

        

        # Add the container widget to the main layout
        self.layout.addWidget(self.container_widget)

        self.set_border_color(None)


        self.web_view.page().profile().downloadRequested.connect(self.handle_download)

    def set_border_color(self, color):
        if color:
            self.setStyleSheet(f"border: 2px solid {color};")
        else:
            self.setStyleSheet("border: none;")

    def zoom_changed(self, value):
        # Set zoom level in percentage (100% is default)
        self.web_view.setZoomFactor(value / 500.0)

    def load_file_preview(self, file_path):
        # Get the file name without the extension
        file_name = os.path.splitext(os.path.basename(file_path))[0]

        folder_name = os.path.basename(os.path.dirname(os.path.dirname(file_path)))

        # Construct the preview URL
        preview_url = f"http://localhost/{folder_name}/RDFView.php?ui={file_name}" 

        url = QUrl(preview_url)
        self.web_view.load(url)
    
    def clear_view(self):
    # Load a blank page
        self.web_view.setHtml("<html><body></body></html>")

    def handle_download(self, download):
        # Choose the default directory and file path
        default_path = os.path.join(os.path.expanduser('~'), 'Downloads', download.downloadFileName())
        
        # Show a file dialog to let the user choose the location
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", default_path)
        
        if file_path:
            download.setPath(file_path)
            download.accept()
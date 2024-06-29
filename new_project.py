import sys
import os
import shutil
import json
from PyQt6.QtWidgets import (QApplication, QWizard, QWizardPage, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QLineEdit, QFileDialog,
                             QMessageBox, QComboBox, QHBoxLayout)
from PyQt6.QtCore import pyqtSignal,Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
from project_view import ProjectView

class NewProjectWizard(QWizard):
    project_created = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle('New Project Wizard')
        self.setGeometry(100, 100, 800, 600)

        
        # Create the mobile view widget
        self.mobile_view = QWebEngineView()
        self.mobile_view.setFixedSize(300, 400)
        

        # Create pages
        self.create_intro_page()
        self.create_copy_sample_page()
        self.create_new_project_page()

        # Add pages to wizard
        self.addPage(self.intro_page)
        self.addPage(self.copy_sample_page)
        self.addPage(self.new_project_page)

        # Hide the default Next and Back buttons
        self.setButtonLayout([QWizard.WizardButton.BackButton, QWizard.WizardButton.CancelButton])

        # Connect the cancel button to a custom slot
        self.button(QWizard.WizardButton.CancelButton).clicked.connect(self.handle_cancel)

        self.setStyleSheet("""
            QWizard {
                background-color: #f2f2f2;
            }
            QWizardPage {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit, QComboBox, QPushButton {
                font-size: 14px;
                padding: 5px;
            }
        """)

        self.project_view = ProjectView()

    def create_intro_page(self):
        try:
            self.intro_page = QWizardPage()
            self.intro_page.setTitle("Setup New Project")
            self.intro_page.setSubTitle("Choose whether to copy a sample project or create a new one from scratch.")

            layout = QVBoxLayout()

            button_layout = QHBoxLayout()

            self.copy_sample_button = QPushButton("Copy a Sample Project")
            self.copy_sample_button.setStyleSheet("""
            QPushButton {
                background-color: #6200EE;
                color: white;
                border: none;
                padding: 15px 30px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 10px;
                border-radius: 12px;
                transition: background-color 0.3s, transform 0.3s;
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
            }
            QPushButton:hover {
                background-color: #3700B3;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #03DAC6;
                transform: scale(1.02);
            }""")
            self.create_new_button = QPushButton("Create New Project")
            self.create_new_button.setStyleSheet("""
            QPushButton {
                background-color: #6200EE;
                color: white;
                border: none;
                padding: 15px 30px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 10px;
                border-radius: 12px;
                transition: background-color 0.3s, transform 0.3s;
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
            }
            QPushButton:hover {
                background-color: #3700B3;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #03DAC6;
                transform: scale(1.02);
                """)
            self.copy_sample_button.setToolTip("Copy a predefined sample project to a new location.")
            self.create_new_button.setToolTip("Create a new project with a blank structure.")
            

            button_layout.addWidget(self.copy_sample_button)
            button_layout.addWidget(self.create_new_button)

             # Add stretch to push buttons to the top 
            layout.addLayout(button_layout)
            self.intro_page.setLayout(layout)
            
            
            self.copy_sample_button.clicked.connect(self.goto_copy_sample_page)
            self.create_new_button.clicked.connect(self.goto_new_project_page)
        except Exception as e:
            print(f"An error occurred while setting up the intro page: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while setting up the intro page: {e}")

    def create_copy_sample_page(self):
        try:
            self.copy_sample_page = QWizardPage()
            self.copy_sample_page.setTitle("Copy Sample Project")
            self.copy_sample_page.setSubTitle("Provide details for copying a sample project.")

            layout = QVBoxLayout()

            self.sample_project_label = QLabel("Select a sample project:")
            self.sample_project_combo = QComboBox()
            self.sample_project_combo.addItems(["-- Select Sample Project --"] + self.get_sample_projects())

            self.copy_project_name_label = QLabel("Enter Project Name:")
            self.copy_project_name_input = QLineEdit()
            self.copy_project_button = QPushButton("Copy Project")

            self.copy_project_name_input.setToolTip("Enter the name of the new project.")
            self.copy_project_button.setToolTip("Click to copy the sample project.")

            # Add widgets to the layout with stretches for better spacing
            layout.addWidget(self.sample_project_label)
            layout.addWidget(self.sample_project_combo)
            layout.addStretch()  # Add stretch to create space between elements
            layout.addWidget(self.copy_project_name_label)
            layout.addWidget(self.copy_project_name_input)
            layout.addStretch()  # Add stretch to create space between elements
            layout.addWidget(self.copy_project_button)

            self.copy_project_button.setEnabled(False)

            # Stylesheet for QPushButton
            self.copy_project_button.setStyleSheet("""
                QPushButton {
                    background-color: #6200EE;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    transition-duration: 0.4s;
                    cursor: pointer;
                }
                QPushButton:hover {
                    background-color: white;
                    color: black;
                    border: 2px solid #6200EE;
                }
            """)
            
            # Stylesheet for QLineEdit
            self.copy_project_name_input.setStyleSheet("""
                QLineEdit {
                    padding: 5px;
                    border: 2px solid #6200EE;
                    border-radius: 4px;
                }
            """)

            # Stylesheet for QComboBox
            self.sample_project_combo.setStyleSheet("""
                QComboBox {
                    border: 2px solid #6200EE;
                    border-radius: 4px;
                    padding: 5px;
                    background-color: #f0f0f0;
                    min-width: 150px;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 25px;
                    border-left-width: 1px;
                    border-left-color: #6200EE;
                    border-left-style: solid;
                    border-top-right-radius: 4px;
                    border-bottom-right-radius: 4px;
                    background-color: #f0f0f0;
                }
                QComboBox::down-arrow {
                    image: ""  # You need to have an image named down_arrow.png
                    width: 14px;
                    height: 14px;
                }
                QComboBox QAbstractItemView {
                    border: 2px solid #6200EE;
                    selection-background-color: #d1d1d1;
                }
            """)

            # Create a QWidget for mobile view with a solid black border
            self.mobile_view_widget = QWidget()
            self.mobile_view_widget.setStyleSheet("""
                QWidget {
                    border-radius:4px;
                    border: 2px solid black;
                }
            """)

            mobile_layout = QVBoxLayout()
            mobile_layout.addWidget(self.mobile_view)
            self.mobile_view_widget.setLayout(mobile_layout)

            # Horizontal layout to include mobile view
            horizontal_layout = QHBoxLayout()
            horizontal_layout.addLayout(layout)
            horizontal_layout.addWidget(self.mobile_view_widget)

            self.copy_sample_page.setLayout(horizontal_layout)

            self.sample_project_combo.currentIndexChanged.connect(self.update_mobile_view)
            self.copy_project_name_input.textChanged.connect(self.check_copy_form_complete)
            self.copy_project_button.clicked.connect(self.copy_sample_project)
        except Exception as e:
            print(f"An error occurred while setting up the copy sample project page: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while setting up the copy sample project page: {e}")

    def create_new_project_page(self):
        try:
            self.new_project_page = QWizardPage()
            self.new_project_page.setTitle("Create New Project")
            self.new_project_page.setSubTitle("Provide details for your new project.")

            layout = QVBoxLayout()

            self.new_project_name_label = QLabel("Enter Project Name:")
            self.new_project_name_input = QLineEdit()
            self.create_project_button = QPushButton("Create Project")

            self.new_project_name_input.setToolTip("Enter the name of the new project.")
            self.new_project_name_input.setStyleSheet("""
                QLineEdit {
                    padding: 5px;
                    border: 2px solid #6200EE;
                    border-radius: 4px;
                }
            """)
            self.create_project_button.setToolTip("Click to create the new project.")
            self.create_project_button.setStyleSheet("""
                QPushButton {
                    background-color: #6200EE;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    transition-duration: 0.4s;
                    cursor: pointer;
                }
                QPushButton:hover {
                    background-color: white;
                    color: black;
                    border: 2px solid #6200EE;
                }
            """)

            layout.addWidget(self.new_project_name_label)
            layout.addWidget(self.new_project_name_input)
            layout.addWidget(self.create_project_button)

            self.create_project_button.setEnabled(False)

            # Horizontal layout
            horizontal_layout = QHBoxLayout()
            horizontal_layout.addLayout(layout)

            self.new_project_page.setLayout(horizontal_layout)

            self.create_project_button.clicked.connect(self.create_new_project)
            self.new_project_name_input.textChanged.connect(self.check_new_form_complete)
        except Exception as e:
            print(f"An error occurred while setting up the new project page: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while setting up the new project page: {e}")

    def get_sample_projects(self):
        try:
            # Get the list of sample projects from the project_templates directory
            template_dir = os.path.join(os.path.dirname(__file__), 'project_templates')
            if not os.path.exists(template_dir):
                return []
            return [name for name in os.listdir(template_dir) if os.path.isdir(os.path.join(template_dir, name))]
        except Exception as e:
            print(f"An error occurred while getting sample projects: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while getting sample projects: {e}")
            return []

    def goto_copy_sample_page(self):
        try:
            self.setCurrentId(1)
        except Exception as e:
            print(f"An error occurred while navigating to the copy sample project page: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while navigating to the copy sample project page: {e}")

    def goto_new_project_page(self):
        try:
            self.setCurrentId(2)
        except Exception as e:
            print(f"An error occurred while navigating to the new project page: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while navigating to the new project page: {e}")

    def browse_copy_destination(self):
        try:
            directory = QFileDialog.getExistingDirectory(self, "Select Directory")
            if directory:
                self.copy_destination_path.setText(directory)
        except Exception as e:
            print(f"An error occurred while browsing for a destination directory: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while browsing for a destination directory: {e}")

    def check_copy_form_complete(self):
        if self.copy_project_name_input.text():
            self.copy_project_button.setEnabled(True)
        else:
            self.copy_project_button.setEnabled(False)

    def browse_new_destination(self):
        try:
            directory = QFileDialog.getExistingDirectory(self, "Select Directory")
            if directory:
                self.new_destination_path.setText(directory)
        except Exception as e:
            print(f"An error occurred while browsing for a destination directory: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while browsing for a destination directory: {e}")

    def check_new_form_complete(self):
        if self.new_project_name_input.text():
            self.create_project_button.setEnabled(True)
        else:
            self.create_project_button.setEnabled(False)

    def update_mobile_view(self):
        try:
            selected_project = self.sample_project_combo.currentText()
            if selected_project != "-- Select Sample Project --":
                template_dir = os.path.join(os.path.dirname(__file__), 'project_templates', selected_project)
                project_info_path = os.path.join(template_dir, "ProjectInfo.json")
                if os.path.exists(project_info_path):
                    with open(project_info_path, 'r') as file:
                        project_info = json.load(file)
                        ui_file_name = project_info.get('init', '')
                        ui_file_path = os.path.join(template_dir, "RDF_UI", ui_file_name)
                        if os.path.exists(ui_file_path):
                            with open(ui_file_path, 'r', encoding='utf-8') as ui_file:
                                html_content = ui_file.read()
                            self.mobile_view.setHtml(html_content)
                            return
                        else:
                            QMessageBox.warning(self, "Error", f"UI file '{ui_file_path}' not found!")
                else:
                    QMessageBox.warning(self, "Error", f"Project info file '{project_info_path}' not found!")
            else:
                print(self, "Error", "Please select a valid project from the list.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while updating the mobile view: {e}")
        # Default content in case of failure
        self.mobile_view.setHtml("<html><body><p>No content available</p></body></html>")

    def copy_sample_project(self):
        try:
            sample_project_name = self.sample_project_combo.currentText()
            project_name = self.copy_project_name_input.text()

            # Fixed destination directory in C:\xampp\htdocs
            destination_dir = r'C:\xampp\htdocs'
            
            if sample_project_name == "-- Select Sample Project --" or not project_name:
                QMessageBox.warning(self, "Incomplete Form", "Please complete all fields.")
                return

            # Construct source and destination paths
            source_dir = os.path.join(os.path.dirname(__file__), 'project_templates', sample_project_name)
            dest_dir = os.path.join(destination_dir, project_name)

            # Check if destination directory already exists
            if os.path.exists(dest_dir):
                QMessageBox.warning(self, "Project Exists", "A project with this name already exists in the selected directory.")
                return

            # Perform the copy operation
            shutil.copytree(source_dir, dest_dir)

            # Emit signal and show success message
            QMessageBox.information(self, "Success", "Sample project copied successfully.")
            self.reset_wizard()
            self.close()
        except Exception as e:
            print(f"An error occurred while copying the sample project: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while copying the sample project: {e}")

    def create_new_project(self):
        try:
            destination_dir = r'C:\xampp\htdocs'
            project_name = self.new_project_name_input.text()

            if not destination_dir or not project_name:
                QMessageBox.warning(self, "Incomplete Form", "Please complete all fields.")
                return

            dest_dir = os.path.join(destination_dir, project_name)

            if os.path.exists(dest_dir):
                QMessageBox.warning(self, "Project Exists", "A project with this name already exists in the selected directory.")
                return

            os.makedirs(dest_dir)

            # Create initial project structure
            os.makedirs(os.path.join(dest_dir, "RDF_UI"))
            os.makedirs(os.path.join(dest_dir, "RDF_ACTION"))
            os.makedirs(os.path.join(dest_dir, "RDF_BW"))
            os.makedirs(os.path.join(dest_dir, "RDF_BVO"))
            os.makedirs(os.path.join(dest_dir, "RDF_DATA"))

            # Create a default ProjectInfo.json file
            project_info = {
                "init": ""
            }

            with open(os.path.join(dest_dir, "ProjectInfo.json"), 'w') as file:
                json.dump(project_info, file, indent=4)

            self.project_created.emit(dest_dir)
            QMessageBox.information(self, "Success", "New project created successfully.")
            self.project_view.populate_tables(dest_dir)
            self.reset_wizard()
            self.close()
        except Exception as e:
            print(f"An error occurred while creating the new project: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while creating the new project: {e}")

    def reset_wizard(self):
        self.sample_project_combo.setCurrentIndex(0)
        self.copy_project_name_input.clear()
        self.new_project_name_input.clear()
        self.mobile_view.setHtml("<html><body><p>No content available</p></body></html>")

    def handle_cancel(self):
    # Reset the wizard fields
        self.reset_wizard()
        # Close the wizard
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wizard = NewProjectWizard()
    wizard.show()
    sys.exit(app.exec())
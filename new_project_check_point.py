import sys
import os
import shutil
import json
from PyQt6.QtWidgets import (QApplication, QWizard, QWizardPage, QVBoxLayout,
                             QPushButton, QLabel, QLineEdit, QFileDialog,
                             QMessageBox, QComboBox)
from PyQt6.QtCore import pyqtSignal
from project_view import ProjectView


class NewProjectWizard(QWizard):
    project_created = pyqtSignal(str)
    def __init__(self):
        super().__init__()

        self.setWindowTitle('New Project Wizard')

        # Create pages
        self.create_intro_page()
        self.create_project_info_page()

        # Add pages to wizard
        self.addPage(self.intro_page)
        self.addPage(self.project_info_page)

        # Hide the default Next and Back buttons
        self.setOption(QWizard.WizardOption.NoDefaultButton)

        # Set the stylesheet for the wizard
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
            QLineEdit, QComboBox {
                border: 1px solid #dcdcdc;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        

    def create_intro_page(self):
        try:
            self.intro_page = QWizardPage()
            self.intro_page.setTitle("Setup New Project")
            self.intro_page.setSubTitle("Choose whether to copy a sample project or create a new one from scratch.")

            layout = QVBoxLayout()

            self.copy_sample_button = QPushButton("Copy a Sample Project")
            self.create_new_button = QPushButton("Create New Project")

            self.copy_sample_button.setToolTip("Copy a predefined sample project to a new location.")
            self.create_new_button.setToolTip("Create a new project with a blank structure.")

            layout.addWidget(self.copy_sample_button)
            layout.addWidget(self.create_new_button)

            layout.addStretch(1)  # Add stretch to push buttons to the top

            self.intro_page.setLayout(layout)
            self.copy_sample_button.clicked.connect(self.goto_project_info_page_copy)
            self.create_new_button.clicked.connect(self.goto_project_info_page_new)
        except Exception as e:
            print(f"An error occurred while setting up the intro page: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while setting up the intro page: {e}")

    def create_project_info_page(self):
        try:
            self.project_info_page = QWizardPage()
            self.project_info_page.setTitle("Project Information")
            self.project_info_page.setSubTitle("Provide details for your new project.")

            layout = QVBoxLayout()

            self.sample_project_label = QLabel("Select a sample project:")
            self.sample_project_combo = QComboBox()
            self.sample_project_combo.addItems(["-- Select Sample Project --"] + self.get_sample_projects())

            self.destination_label = QLabel("Select Destination Directory:")
            self.destination_path = QLineEdit()
            self.browse_button = QPushButton("Browse")
            self.project_name_label = QLabel("Enter Project Name:")
            self.project_name_input = QLineEdit()
            self.create_project_button = QPushButton("Create Project")

            self.browse_button.setToolTip("Browse to select the destination directory.")
            self.project_name_input.setToolTip("Enter the name of the new project.")
            self.create_project_button.setToolTip("Click to create the new project.")

            layout.addWidget(self.sample_project_label)
            layout.addWidget(self.sample_project_combo)
            layout.addWidget(self.destination_label)
            layout.addWidget(self.destination_path)
            layout.addWidget(self.browse_button)
            layout.addWidget(self.project_name_label)
            layout.addWidget(self.project_name_input)
            layout.addWidget(self.create_project_button)

            self.sample_project_label.setVisible(False)
            self.sample_project_combo.setVisible(False)
            self.project_view = ProjectView()
            self.project_info_page.setLayout(layout)
            self.browse_button.clicked.connect(self.browse_destination)
            self.create_project_button.clicked.connect(self.create_project)
            self.destination_path.textChanged.connect(self.check_form_complete)
            self.project_name_input.textChanged.connect(self.check_form_complete)
        except Exception as e:
            print(f"An error occurred while setting up the project info page: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while setting up the project info page: {e}")

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

    def goto_project_info_page_copy(self):
        try:
            self.is_copy_sample = True
            self.sample_project_label.setVisible(True)
            self.sample_project_combo.setVisible(True)
            self.next()
        except Exception as e:
            print(f"An error occurred while navigating to the project info page for copying: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while navigating to the project info page for copying: {e}")

    def goto_project_info_page_new(self):
        try:
            self.is_copy_sample = False
            self.sample_project_label.setVisible(False)
            self.sample_project_combo.setVisible(False)
            self.next()
        except Exception as e:
            print(f"An error occurred while navigating to the project info page for new project creation: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while navigating to the project info page for new project creation: {e}")

    def browse_destination(self):
        try:
            directory = QFileDialog.getExistingDirectory(self, "Select Directory")
            if directory:
                self.destination_path.setText(directory)
        except Exception as e:
            print(f"An error occurred while browsing for a destination directory: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while browsing for a destination directory: {e}")

    def check_form_complete(self):
        if self.destination_path.text() and self.project_name_input.text():
            self.create_project_button.setEnabled(True)
        else:
            self.create_project_button.setEnabled(False)

    def create_project(self):
        try:
            project_name = self.project_name_input.text()
            destination = self.destination_path.text()

            if not project_name:
                QMessageBox.warning(self, "Error", "Project name cannot be empty!")
                return

            if not destination or not os.path.isdir(destination):
                QMessageBox.warning(self, "Error", "Please select a valid directory!")
                return

            folder_path = os.path.join(destination, project_name)

            try:
                if self.is_copy_sample and self.sample_project_combo.currentText() != "-- Select Sample Project --":
                    # Copy from selected sample project
                    template_dir = os.path.join(os.path.dirname(__file__), 'project_templates', self.sample_project_combo.currentText())
                    shutil.copytree(template_dir, folder_path)
                else:
                    # Create a new blank project
                    os.makedirs(folder_path)
                    for folder in ["RDF_UI", "RDF_ACTION", "RDF_BW", "RDF_BVO", "RDF_DATA"]:
                        os.makedirs(os.path.join(folder_path, folder))

                    project_info = {"name": project_name}
                    with open(os.path.join(folder_path, "ProjectInfo.json"), 'w') as json_file:
                        json.dump(project_info, json_file)

                QMessageBox.information(self, "Success", "Project created successfully!")
                
                self.project_created.emit(folder_path)
                self.project_created.connect(self.project_view.project_created_handler)

                self.close()
                
                self.reset_wizard()

                
            except Exception as e:
                print(f"An error occurred while creating the project: {e}")
                QMessageBox.critical(self, "Error", f"An error occurred while creating the project: {e}")
        except Exception as e:
            print(f"An error occurred while setting up the project creation: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while setting up the project creation: {e}")

    def reset_wizard(self):
        # Reset all fields and pages to their initial state
        self.destination_path.clear()
        self.project_name_input.clear()
        self.sample_project_combo.setCurrentIndex(0)
        self.is_copy_sample = False
        self.sample_project_label.setVisible(False)
        self.sample_project_combo.setVisible(False)
        self.create_project_button.setEnabled(False)

    def reset_wizard(self):
        # Reset all fields and pages to their initial state
        self.destination_path.clear()
        self.project_name_input.clear()
        self.sample_project_combo.setCurrentIndex(0)
        self.is_copy_sample = False
        self.sample_project_label.setVisible(False)
        self.sample_project_combo.setVisible(False)
        self.create_project_button.setEnabled(False)

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        wizard = NewProjectWizard()
        wizard.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"An error occurred while running the application: {e}")
        QMessageBox.critical(None, "Error", f"An error occurred while running the application: {e}")

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QFileDialog, QTableWidgetItem, QHeaderView, QLineEdit, QHBoxLayout,QLabel,QMessageBox,QMenu,QInputDialog
from PyQt6.QtCore import Qt, QDir, pyqtSignal, QSettings
from PyQt6.QtGui import QMouseEvent,QAction

import os
import json
import re
import shutil
from pathlib import Path


# def extract_file_name(file_path):
#     """
#     Extracts the file name from a given file path.
#     """
#     base_name = os.path.basename(file_path)
#     file_name = re.sub(r'BW\.php.*', 'BW.php', base_name)
#     return file_name



def extract_file_name(path):
    return os.path.basename(path)

def read_project_info(folder_path):
    linked_files = []

    # Construct the path to the ProjectInfo.json file
    project_info_path = os.path.join(folder_path, "ProjectInfo.json")

    # Check if the file exists
    if os.path.isfile(project_info_path):
        print(f"ProjectInfo.json file found at: {project_info_path}")
        # Read the contents of the ProjectInfo.json file
        with open(project_info_path, "r") as file:
            project_info = json.load(file)

        # Get the value of the "init" key
        init_file = project_info.get("init", "")

        # Check if the init_file ends with UI.php
        if init_file.endswith("UI.php"):
            linked_files.append(init_file)
            print(f"UI file found: {init_file}")

            # Search for the UI.php file in the RDF_UI folder
            ui_file_path = os.path.join(folder_path, "RDF_UI", init_file)
            if os.path.isfile(ui_file_path):
                print(f"UI file found at: {ui_file_path}")
                # Read the contents of the UI.php file
                with open(ui_file_path, "r") as file:
                    file_contents = file.read()

                # Find text ending with .js using a regular expression
                js_files = re.findall(r'"(.*?\.js)"', file_contents)
                linked_files.extend([extract_file_name(js_file) for js_file in js_files])
                print(f"Found {len(js_files)} .js files in the UI file")

                # Search for the .js file in the RDF_ACTION folder
                for js_file in os.listdir(os.path.join(folder_path, "RDF_ACTION")):
                    if js_file.endswith(".js"):
                        js_file_path = os.path.join(folder_path, "RDF_ACTION", js_file)
                        if os.path.isfile(js_file_path):
                            print(f"Found .js file at: {js_file_path}")
                            # Read the contents of the .js file
                            with open(js_file_path, "r") as file:
                                js_file_contents = file.read()

                            # Find text containing BW.php using a regular expression
                            bw_files = re.findall(r'[\w/]+/(.*?BW.php)', js_file_contents)

                            # Extract the file name without the directory path
                            bw_file_names = [extract_file_name(f) for f in bw_files]

                            # Deduplicate the list of file names
                            bw_file_names = list(set(bw_file_names))
                            
                            linked_files.extend(bw_file_names)
                            print(f"Found {len(bw_file_names)} BW.php files in the .js file")
                            
                        # Search for the BW.php file in the RDF_BW folder
                        for bw_file in bw_files:
                            bw_file_path = os.path.join(folder_path, "RDF_BW", bw_file)
                            if os.path.isfile(bw_file_path):
                                print(f"Found BW.php file at: {bw_file_path}")
                                
                                # Read the contents of the BW.php file
                                with open(bw_file_path, "r") as file:
                                    bw_file_contents = file.read()

                                # Find text ending with BVO.php using a regular expression
                                bvo_files = re.findall(r'[\w\/]+\/(.*?BVO\.php)', bw_file_contents)
                                linked_files.extend([extract_file_name(bvo_file) for bvo_file in bvo_files])
                                print(f"Found {len(bvo_files)} BVO.php files in the BW.php file")

                                # Search for the BVO.php file in the RDF_BVO folder
                                for bvo_file in bvo_files:
                                    bvo_file_path = os.path.join(folder_path, "RDF_BVO", bvo_file)
                                    if os.path.isfile(bvo_file_path):
                                        print(f"Found BVO.php file at: {bvo_file_path}")
                                        # Read the contents of the BVO.php file
                                        with open(bvo_file_path, "r") as file:
                                            bvo_file_contents = file.read()

                                        # Find text ending with Data.json using a regular expression
                                        data_files = re.findall(r'[\w\/]+\/(.*?Data\.json)', bvo_file_contents)
                                        linked_files.extend(set([extract_file_name(data_file) for data_file in data_files]))  # Use a set to avoid duplicates
                                        print(f"Found {len(data_files)} Data.json files in the BVO.php file")
                                    else:
                                        print(f"BVO.php file not found at: {bvo_file_path}")
                            else:
                                print(f"BW.php file not found at: {bw_file_path}")
                    else:
                        print(f".js file not found at: {js_file_path}")
            else:
                print(f"UI file not found at: {ui_file_path}")
        else:
            print(f"No UI file found in ProjectInfo.json")
    else:
        print(f"ProjectInfo.json file not found at: {project_info_path}")
        show_alert(f"Warning: ProjectInfo.json file not found at root. All files will be marked as Unlinked.")

    print(f"Linked Files: {linked_files}")
    return linked_files

def show_alert(message):
    alert = QMessageBox()
    alert.setIcon(QMessageBox.Icon.Warning)
    alert.setText(message)
    alert.setWindowTitle("Warning")
    alert.exec()

def get_all_file_names(directory):
    file_names = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_names.append(file)
    print(f"get_all_file_names - directory: {directory}, file_names: {file_names}")
    return file_names

class ProjectView(QWidget):
    file_double_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.showMaximized()
        self.setWindowFlags(Qt.WindowType.Window)
        self.setWindowTitle("Project View")

        # Create the main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create the "Select Workspace" button and QLineEdit
        button_layout = QHBoxLayout()
        self.path_line_edit = QLineEdit()
        self.path_line_edit.setReadOnly(True)
        button_layout.addWidget(self.path_line_edit)

        refresh_button = QPushButton("Refresh")
        refresh_button.setMaximumWidth(100)
        refresh_button.clicked.connect(self.refresh_directory)
        button_layout.addWidget(refresh_button)

        merge_button = QPushButton("Merge")
        merge_button.setMaximumWidth(100)
        merge_button.clicked.connect(self.merge_project)
        button_layout.addWidget(merge_button)

        self.folder_path = None

        layout.addLayout(button_layout)

        # Create the table view
        self.table_view = QTableWidget()
        self.table_view.setColumnCount(5)
        self.table_view.setHorizontalHeaderLabels(["RDF_UI", "RDF_ACTION", "RDF_BW", "RDF_BVO", "RDF_DATA"])
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_view)
        self.table_view.cellDoubleClicked.connect(self.cell_double_clicked)

        # Add a title for the unlinked files table
        unlinked_files_title = QLabel("Unlinked Files")
        unlinked_files_title.setStyleSheet("font-weight: bold;")  # Make the title bold
        layout.addWidget(unlinked_files_title)

        

        # Create the unlinked files table
        self.unlinked_table = QTableWidget()
        self.unlinked_table.setColumnCount(1)
        self.unlinked_table.setHorizontalHeaderLabels(["Unlinked Files"])
        self.unlinked_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.unlinked_table)
        self.unlinked_table.cellDoubleClicked.connect(self.cell_double_clicked)


        
        self.context_menu = QMenu(self)
        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(self.rename_file)
        self.context_menu.addAction(rename_action)

    

        

    def create_new_file(self):
        if not self.folder_path:
            QMessageBox.critical(self, "Project Not Opened", "Open a project first to create a new file.")
            return
            

        # Define the list of folders
        folders = ['RDF_UI', 'RDF_ACTION', 'RDF_BW', 'RDF_BVO', 'RDF_DATA']

        # Show the folder selection dialog
        folder_name, ok = QInputDialog.getItem(self, "Select Folder", "Select a folder to create a new file:", folders, 0, False)
        
        if ok and folder_name:
            # Ask for the file name
            file_name, ok = QInputDialog.getText(self, "Create New File", f"Enter the name for the new file in {folder_name}:")
            
            if ok and file_name:
                # Determine the file extension based on the selected folder
                if folder_name == 'RDF_UI' or folder_name == 'RDF_BW' or folder_name == 'RDF_BVO':
                    extension = '.php'
                elif folder_name == 'RDF_ACTION':
                    extension = '.js'
                elif folder_name == 'RDF_DATA':
                    extension = '.json'
                else:
                    extension = ''

                # Construct the file path
                file_path = os.path.join(self.folder_path, folder_name, file_name + extension)

                try:
                    # Create the file
                    with open(file_path, "w") as file:
                        file.write("")  # Create an empty file

                    # Optionally refresh the directory view or update UI
                    self.refresh_directory()  # Replace with your own logic

                    QMessageBox.information(self, "File Created", f"Successfully created file:\n{file_path}")

                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to create new file:{e}")
    
    def get_folder_name_from_column(self, column):
        folder_names = ["RDF_UI", "RDF_ACTION", "RDF_BW", "RDF_BVO", "RDF_DATA"]
        if column >= 0 and column < len(folder_names):
            return folder_names[column]
        return None

    def highlight_cell(self, row, column):
        item = self.table_view.item(row, column)
        if item:
            item.setBackground(Qt.GlobalColor.yellow)

    def highlight_unlinked_cell(self, row, column):
        item = self.unlinked_table.item(row, column)
        if item:
            item.setBackground(Qt.GlobalColor.yellow)

    def unhighlight_cells(self):
        for row in range(self.table_view.rowCount()):
            for column in range(self.table_view.columnCount()):
                item = self.table_view.item(row, column)
                if item:
                    item.setBackground(Qt.GlobalColor.white)
    

    def select_workspace(self):
        # Open a file dialog to select a directory
        folder_path = QFileDialog.getExistingDirectory(self, "Select Workspace")

        if folder_path:
            self.folder_path = folder_path  # Store the folder path
            self.populate_tables(folder_path)
    def merge_project(self):
    # Prompt the user to select another project folder to merge
        merge_folder_path = QFileDialog.getExistingDirectory(self, "Select Project to Merge", QDir.homePath())
        if merge_folder_path:
            current_project_path = self.path_line_edit.text()
            if current_project_path:
                success = self.merge_project_data(current_project_path, merge_folder_path)
                if success:
                    QMessageBox.information(self, "Merge Successful", "Project merged successfully.")
                else:
                    QMessageBox.critical(self, "Merge Failed", "Failed to merge project.")
                    self.populate_tables(current_project_path)

    def merge_project_data(self, current_project_path, merge_folder_path):
        try:
            current_linked_files = read_project_info(current_project_path)
            merge_linked_files = read_project_info(merge_folder_path)

            # Combine linked files
            combined_linked_files = list(set(current_linked_files + merge_linked_files))

            # Copy files from the merge project to the current project
            folders = ["RDF_UI", "RDF_ACTION", "RDF_BW", "RDF_BVO", "RDF_DATA"]
            for folder in folders:
                current_folder_path = os.path.join(current_project_path, folder)
                merge_folder_path_specific = os.path.join(merge_folder_path, folder)

                if os.path.exists(merge_folder_path_specific):
                    for file_name in os.listdir(merge_folder_path_specific):
                        merge_file_path = os.path.join(merge_folder_path_specific, file_name)
                        current_file_path = os.path.join(current_folder_path, file_name)

                        if os.path.isfile(merge_file_path):
                            # Ensure the current folder exists
                            os.makedirs(current_folder_path, exist_ok=True)

                            # Copy file to the current project folder
                            shutil.copy2(merge_file_path, current_file_path)

                            # Add the file to the corresponding table column
                            column_index = folders.index(folder)
                            row_count = self.table_view.rowCount()
                            self.table_view.insertRow(row_count)
                            file_item = QTableWidgetItem(file_name)
                            self.table_view.setItem(row_count, column_index, file_item)

            return True

        except Exception as e:
            print(f"Error merging project: {e}")
            return False

    
    def project_created_handler(self, folder_path):
        try:
            self.path_line_edit.setText(folder_path)
            self.populate_tables(folder_path)  # Update tables with new project data
        except Exception as e:
            print(f"An error occurred in project_created_handler: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred in project_created_handler: {e}")

    def refresh_directory(self):
        folder_path = self.path_line_edit.text()
        if folder_path:
            self.populate_tables(folder_path)

    def cell_double_clicked(self, row, column):
        if row == 0:
            folder_name_item = self.table_view.horizontalHeaderItem(column)
            file_name_item = self.table_view.item(row, column)
            if folder_name_item and file_name_item:
                folder_name = folder_name_item.text()
                file_name = file_name_item.text()
                if file_name:
                    file_path = os.path.join(self.folder_path, folder_name, file_name)
                    if os.path.exists(file_path):
                        self.file_double_clicked.emit(file_path)
        else:
            column_map = {0: 'RDF_UI', 1: 'RDF_ACTION', 2: 'RDF_BW', 3: 'RDF_BVO', 4: 'RDF_DATA'}
            folder_name = column_map.get(column)
            if folder_name:
                file_name = self.table_view.item(row, column).text()
                if file_name:
                    file_path = os.path.join(self.folder_path, folder_name, file_name)
                    if os.path.exists(file_path):
                        self.file_double_clicked.emit(file_path)

        # Handle double-click for the unlinked table
        if self.unlinked_table.currentItem():
            file_name = self.unlinked_table.currentItem().text()
            folder_name = self.get_folder_name_from_extension(file_name)
            if folder_name:
                file_path = os.path.join(self.folder_path, folder_name, file_name)
                if os.path.exists(file_path):
                    self.file_double_clicked.emit(file_path)
                else:
                    print(f"Unlinked file not found: {file_path}")
            else:
                print(f"Unable to determine folder for unlinked file: {file_name}")

        # Prevent editing the cell on double-click
        self.table_view.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.unlinked_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def get_folder_name_from_extension(self, file_name):
        if file_name.endswith("UI.php"):
            return "RDF_UI"
        elif file_name.endswith(".js"):
            return "RDF_ACTION"
        elif file_name.endswith("BW.php"):
            return "RDF_BW"
        elif file_name.endswith("BVO.php"):
            return "RDF_BVO"
        elif file_name.endswith("Data.json"):
            return "RDF_DATA"
        else:
            return ""

    def populate_tables(self, folder_path):
        # Set the path in the QLineEdit
        self.path_line_edit.setText(folder_path)
        
        # Clear both tables
        self.table_view.setRowCount(0)
        self.unlinked_table.setRowCount(0)

        # Get the linked files
        linked_files = read_project_info(folder_path)

        # Get all file names in the selected directory and its subdirectories
        all_file_names = get_all_file_names(folder_path)

        # Create a list of unlinked files, excluding ProjectInfo.json and RDFView.php
        unlinked_files = [filename for filename in all_file_names if filename not in linked_files and not (filename == "ProjectInfo.json" or filename == "RDFView.php")]

        # Create separate lists for each column
        ui_files = []
        action_files = []
        bw_files = []
        bvo_files = []
        data_files = []

        for file_name in linked_files:
            if file_name.endswith("UI.php"):
                ui_files.append(file_name)
            elif file_name.endswith(".js"):
                action_files.append(file_name)
            elif file_name.endswith("BW.php"):
                bw_files.append(file_name)
            elif file_name.endswith("BVO.php"):
                bvo_files.append(file_name)
            elif file_name.endswith("Data.json"):
                data_files.append(file_name)

        # Set the row count and populate the table
        row_count = max(len(ui_files), len(action_files), len(bw_files), len(bvo_files), len(data_files))
        self.table_view.setRowCount(row_count)
        self.table_view.setColumnCount(5)
        self.table_view.setHorizontalHeaderLabels(["RDF_UI", "RDF_ACTION", "RDF_BW", "RDF_BVO", "RDF_DATA"])
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for row, file_name in enumerate(ui_files):
            file_item = QTableWidgetItem(file_name)
            self.table_view.setItem(row, 0, file_item)

        for row, file_name in enumerate(action_files):
            file_item = QTableWidgetItem(file_name)
            self.table_view.setItem(row, 1, file_item)

        for row, file_name in enumerate(bw_files):
            file_item = QTableWidgetItem(file_name)
            self.table_view.setItem(row, 2, file_item)

        for row, file_name in enumerate(bvo_files):
            file_item = QTableWidgetItem(file_name)
            self.table_view.setItem(row, 3, file_item)

        for row, file_name in enumerate(data_files):
            file_item = QTableWidgetItem(file_name)
            self.table_view.setItem(row, 4, file_item)

        # Populate the unlinked files table
        self.unlinked_table.setRowCount(0)  # Clear any existing rows
        self.unlinked_table.setColumnCount(5)
        self.unlinked_table.setHorizontalHeaderLabels(["RDF_UI", "RDF_ACTION", "RDF_BW", "RDF_BVO", "RDF_DATA"])
        self.unlinked_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        unlinked_ui_files = [file_name for file_name in unlinked_files if file_name.endswith("UI.php")]
        unlinked_action_files = [file_name for file_name in unlinked_files if file_name.endswith(".js")]
        unlinked_bw_files = [file_name for file_name in unlinked_files if file_name.endswith("BW.php")]
        unlinked_bvo_files = [file_name for file_name in unlinked_files if file_name.endswith("BVO.php")]
        unlinked_data_files = [file_name for file_name in unlinked_files if file_name.endswith("Data.json")]

        row_count = max(len(unlinked_ui_files), len(unlinked_action_files), len(unlinked_bw_files), len(unlinked_bvo_files), len(unlinked_data_files))
        self.unlinked_table.setRowCount(row_count)

        for row, file_name in enumerate(unlinked_ui_files):
            file_item = QTableWidgetItem(file_name)
            self.unlinked_table.setItem(row, 0, file_item)

        for row, file_name in enumerate(unlinked_action_files):
            file_item = QTableWidgetItem(file_name)
            self.unlinked_table.setItem(row, 1, file_item)

        for row, file_name in enumerate(unlinked_bw_files):
            file_item = QTableWidgetItem(file_name)
            self.unlinked_table.setItem(row, 2, file_item)

        for row, file_name in enumerate(unlinked_bvo_files):
            file_item = QTableWidgetItem(file_name)
            self.unlinked_table.setItem(row, 3, file_item)

        for row, file_name in enumerate(unlinked_data_files):
            file_item = QTableWidgetItem(file_name)
            self.unlinked_table.setItem(row, 4, file_item)

        print(f"UI Files: {ui_files}")
        print(f"Action Files: {action_files}")
        print(f"BW Files: {bw_files}")
        print(f"BVO Files: {bvo_files}")
        print(f"Data Files: {data_files}")
        print(f"Unlinked Files: {unlinked_files}")


    def rename_file(self):
        table = self.sender().parent()
        if table == self.table_view:
            current_item = self.table_view.currentItem()
            if current_item:
                current_file_name = current_item.text()
                new_file_name, ok = QInputDialog.getText(self, "Rename File", "Enter new file name:", text=current_file_name)
                if ok and new_file_name != current_file_name:
                    current_row = self.table_view.currentRow()
                    current_column = self.table_view.currentColumn()
                    folder_name = self.get_folder_name_from_column(current_column)
                    old_file_path = os.path.join(self.folder_path, folder_name, current_file_name)
                    new_file_path = os.path.join(self.folder_path, folder_name, new_file_name)

                    try:
                        os.rename(old_file_path, new_file_path)
                        self.table_view.setItem(current_row, current_column, QTableWidgetItem(new_file_name))
                        self.refresh_directory()  # Refresh the directory after renaming the file
                        self.update_linked_files(current_row, current_column, new_file_name)  # Update the linked files
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to rename file: {e}")
        else:
            item = self.unlinked_table.currentItem()
            if item:
                current_file_name = item.text()
                new_file_name, ok = QInputDialog.getText(self, "Rename File", "Enter new file name:", text=current_file_name)
                if ok and new_file_name != current_file_name:
                    folder_name = self.get_folder_name_from_extension(current_file_name)
                    old_file_path = os.path.join(self.folder_path, folder_name, current_file_name)
                    new_file_path = os.path.join(self.folder_path, folder_name, new_file_name)

                    try:
                        os.rename(old_file_path, new_file_path)
                        row = self.unlinked_table.currentRow()
                        self.unlinked_table.setItem(row, 0, QTableWidgetItem(new_file_name))
                        self.refresh_directory()  # Refresh the directory after renaming the file
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to rename file: {e}")

    
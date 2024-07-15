import re
import json
import os,sys
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout,QVBoxLayout, QWidget, QSplitter, QTreeView, QPlainTextEdit, QToolBar, QFileDialog, QToolButton, QLineEdit,QTabWidget, QApplication, QMessageBox,  QPushButton, QTextEdit,QScrollBar
from PyQt6.QtGui import QAction, QFileSystemModel, QIcon, QFont, QPainter, QColor, QTextCharFormat, QTextCursor,QKeySequence, QShortcut
from PyQt6.QtCore import Qt, QModelIndex, QTimer, QDir, pyqtSlot, QSize, QRect,QProcess
from terminal_widget import TerminalWidget
from mobile_view import MobileView
from project_view import ProjectView
from syntax_highlighter import MultiLanguageHighlighter
from new_project import NewProjectWizard
from theme import DarkTheme  



class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)


class CustomCodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)

        self.zoom_level = 0

        self.updateLineNumberAreaWidth(0)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

    def zoom_in(self):
        self.zoom_level += 1
        current_font = self.font()
        current_font.setPointSize(current_font.pointSize() + 1)
        self.setFont(current_font)

    def zoom_out(self):
        self.zoom_level -= 1
        current_font = self.font()
        current_font.setPointSize(current_font.pointSize() - 1)
        self.setFont(current_font)

    def lineNumberAreaWidth(self):
        digits = 1
        max_val = max(1, self.blockCount())
        while max_val >= 10:
            max_val //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.GlobalColor.lightGray)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.GlobalColor.black)
                painter.drawText(0, top, self.lineNumberArea.width(), self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1


    

    
    @pyqtSlot()
    def format_code(self):
        # Example formatting: replace tabs with 4 spaces (this should be replaced with a proper formatter)
        text = self.toPlainText()
        formatted_text = text.replace('\t', '    ')
        self.setPlainText(formatted_text)

class CodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Editor")
        self.showMaximized()
        self.setWindowFlags(Qt.WindowType.Window)
        self.setGeometry(100, 100, 800, 600)

        self.project_view = ProjectView(self)
        self.project_view.file_double_clicked.connect(self.open_file_from_project_view)

        # Create the main layout
        self.main_layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

         # Create the custom code editor
        self.codeEditor = CustomCodeEditor()
        
        # Create a horizontal scrollbar
        self.hScrollBar = QScrollBar(Qt.Orientation.Horizontal)
        
        # Synchronize the code editor's horizontal scrollbar with the custom scrollbar
        self.hScrollBar.valueChanged.connect(self.syncScrollBar)
        self.codeEditor.horizontalScrollBar().valueChanged.connect(self.syncEditorScrollBar)

        

        # Create the toolbar
        self.toolbar = QToolBar()
        #create file button 
        self.create_file_action = QAction('Create File', self) 
        self.create_file_action.triggered.connect(self.project_view.create_new_file)

        self.restart_application_button = QAction("Restart",self)
        self.restart_application_button.triggered.connect(self.restart_application)

        self.project_view_action = QAction(QIcon("project_view.png"), "Reset View", self)
        self.project_view_action.triggered.connect(self.toggle_sidebar)
        self.open_project_action = QAction("Open Project",self)
        self.open_project_action.triggered.connect(self.new_project_workspace)
        self.new_project_action = QAction("Create Project",self)
        self.new_project_action.triggered.connect(self.new_project)
        self.save_action = QAction("Save", self)
        self.save_action.triggered.connect(self.save_file)
        self.validate_action = QAction("Validate", self)
        self.validate_action.triggered.connect(self.validate_file)
        
        self.dark_mode_button = QPushButton("Dark Mode")
        self.dark_mode_button.clicked.connect(self.toggle_dark_theme)
        self.toolbar.addWidget(self.dark_mode_button)

        
        self.installEventFilter(self)
        

        

        # self.boilerplate_action = QAction("Boilerplate", self)
        # self.boilerplate_action.triggered.connect(self.insert_boilerplate_code)
        self.toolbar.addAction(self.project_view_action)
        self.toolbar.addAction(self.open_project_action)
        self.toolbar.addAction(self.new_project_action)
        self.toolbar.addAction(self.create_file_action)
        self.toolbar.addAction(self.save_action)
        
        
        
        
        # self.toolbar.addAction(self.boilerplate_action)
        self.toolbar.addAction(self.validate_action)
        


        self.toolbar.addAction(self.restart_application_button)
        self.main_layout.addWidget(self.toolbar)
        
       
        

        

        # Create the tab widget for managing multiple files
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.update_live_preview)

        # Create the mobile view
        self.mobile_view = MobileView()

        self.terminal = TerminalWidget()

        self.wizard = NewProjectWizard()

         

        # Create the main split screen
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.project_view)
        self.splitter.addWidget(self.tab_widget)
        self.splitter.addWidget(self.mobile_view)
        self.main_layout.addWidget(self.splitter)

        # Timer for live preview updates
        self.live_preview_timer = QTimer()
        self.live_preview_timer.setInterval(1000)  # Update interval in milliseconds
        self.live_preview_timer.timeout.connect(self.update_live_preview)

        # Add a shortcut for saving the file
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_file)

         # Store the current file path
        self.current_file_path = None
        
        # Connect the live button signal
        # self.live_button.toggled.connect(self.toggle_live_preview)
        self.project_view.show()
        # Rules dictionary pointing to files in the rules directory
        self.rules_directory = os.path.join(os.getcwd(), 'rules')
        self.rules = {
            "UI": os.path.join(self.rules_directory, "rules_ui.json"),
            "Data": os.path.join(self.rules_directory, "rules_json.json"),
            "BW": os.path.join(self.rules_directory, "rules_bw.json"),
            "BVO": os.path.join(self.rules_directory, "rules_bvo.json"),
            "Action": os.path.join(self.rules_directory, "rules_action.json")
        }
        self.dark_theme_enabled = False


    def toggle_sidebar(self):
        if self.project_view.isHidden():
            self.project_view.show()
        else:
            self.project_view.hide()    
    

    def close_tab(self, index):
        self.tab_widget.removeTab(index)

    def close_all_tabs(self):
        try:
            while self.tab_widget.count() > 0:
                self.tab_widget.removeTab(0)
        except Exception as e:
            QMessageBox.warning(self,f"no tabs is there to be closed{e}") 

    def new_project_workspace(self):
        try:
            if self.tab_widget.count() == 0:
                self.mobile_view.clear_view()
                self.project_view.select_workspace()
            else:
                self.close_all_tabs()
                self.mobile_view.clear_view()
                self.project_view.select_workspace()
            
                
        except Exception as e:
            QMessageBox.critical(self,f"{e}")
        

    def new_project(self):
        self.wizard.exec()

    def load_file(self, index: QModelIndex):
        if self.sidebar_model.isDir(index):
            return

        file_path = self.sidebar_model.filePath(index)
        self.open_file_in_new_tab(file_path)

    def save_file(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            editor = current_widget.findChild(QPlainTextEdit)
            if editor and hasattr(current_widget, 'file_path'):
                try:
                    with open(current_widget.file_path, 'w') as file:
                        file.write(editor.toPlainText())
                    terminal = current_widget.findChild(TerminalWidget)
                    if terminal:
                        terminal.write(f"Saved file: {current_widget.file_path}\n")
                    self.mobile_view.load_file_preview(current_widget.file_path)  # Reload the mobile view
                except Exception as e:
                    if terminal:
                        terminal.write(f"Error saving file: {e}\n")
            else:
                terminal.write("No file opened to save.\n")

    def toggle_live_preview(self, checked):
        if checked:
            # Live preview enabled
            self.live_preview_timer.start()
        else:
            # Live preview disabled
            self.live_preview_timer.stop()

    def update_live_preview(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            self.mobile_view.load_file_preview(current_widget.file_path)

    def validate_file(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            self.validate_and_apply_rules(current_widget.file_path)
        else:
            current_widget.findChild(TerminalWidget).write("No file opened to validate.\n")

    def validate_and_apply_rules(self, file_path):
        file_name = os.path.basename(file_path)
        file_base_name = os.path.splitext(file_name)[0]

        rule_file = None
        for key in self.rules:
            if file_base_name.endswith(key):
                rule_file = self.rules[key]
                break

        if rule_file:
            try:
                with open(rule_file, 'r') as file:
                    rules = json.load(file)

                    current_widget = self.tab_widget.currentWidget()
                    editor = current_widget.findChild(QPlainTextEdit)
                    content = editor.toPlainText() if editor else ""
                    errors = self.apply_rules(content, rules)
                    terminal = current_widget.findChild(TerminalWidget)
                if errors:
                    for error in errors:
                        terminal.write(f"Error: {error}\n",color = "red")
                else:
                    terminal.write("No errors found.\n",color = "white")
                if errors:
                    self.mobile_view.set_border_color("red")
                else:
                    self.mobile_view.set_border_color(None)
            except Exception as e:
                terminal.write(f"Error loading rules: {e}\n")
        else:
            terminal.write("No rule file found for this file.\n")

    def apply_rules(self, content, rules):
        errors = []
        table_rule_present = False
        table_rule = None
        
        for rule in rules["rules"]:
            if rule["description"] == "File must contain a table tag":
                table_rule_present = True
                table_rule = rule
                continue
            
            if re.search(rule["pattern"], content):
                errors.append(rule["description"])
        
        if table_rule_present and not re.search(table_rule["pattern"], content):
            errors.append("Table tag should be present")
            
        return errors

    def open_file_from_project_view(self, file_path):
        self.open_file_in_new_tab(file_path)

    def open_file_in_new_tab(self, file_path):
        # Check if the file is already open in a tab
        for i in range(self.tab_widget.count()):
            if self.tab_widget.widget(i).file_path == file_path:
                self.tab_widget.setCurrentIndex(i)
                return

        # Create a new tab with a search bar and code editor
        tab = QWidget()
        tab.file_path = file_path
        layout = QVBoxLayout()
        
        
                
        editor = CustomCodeEditor()
        editor.setFont(QFont("Consolas", 12))
        terminal = TerminalWidget()

        search_bar = QLineEdit()
        search_bar.setVisible(False)
        search_bar.setPlaceholderText("Search...")
        search_bar.textChanged.connect(lambda text:self.search_text(text))
        
        
        search_tab_layout = QHBoxLayout()
        search_tab_layout.addStretch()
        search_tab_layout.addWidget(search_bar)
        layout.addLayout(search_tab_layout)
        
        # Create a splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(editor)
        splitter.addWidget(terminal)
        splitter.setSizes([int(self.height() * 0.75), int(self.height() * 0.25)])
        
        # Add the splitter to the layout
        layout.addWidget(splitter)
        
        # Add a button to toggle the terminal visibility
        button_layout = QHBoxLayout()
        toggle_button = QPushButton("▲")
        toggle_button.setFixedSize(30, 30)
        button_layout.addWidget(toggle_button)
        button_layout.addStretch()


        zoom_in_button = QPushButton("Zoom In")
        zoom_out_button = QPushButton("Zoom Out")
        button_layout.addWidget(zoom_in_button)
        button_layout.addWidget(zoom_out_button)

        layout.addLayout(button_layout)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, os.path.basename(file_path))
        self.tab_widget.setCurrentWidget(tab)
        
        # Connect the button
        toggle_button.clicked.connect(lambda: self.toggle_terminal(splitter, toggle_button))
        toggle_button.clicked.connect(lambda: self.toggle_terminal(splitter, toggle_button))
        zoom_in_button.clicked.connect(editor.zoom_in)
        zoom_out_button.clicked.connect(editor.zoom_out)

        try:
            with open(file_path, 'r') as file:
                file_contents = file.read()
                editor.setPlainText(file_contents)
                terminal.write(f"Loaded file: {file_path}\n")
                self.validate_and_apply_rules(file_path)
                
                # Set the syntax highlighter for the current tab's editor
                highlighter = MultiLanguageHighlighter(editor.document())
                self.set_highlighter_language(file_path, highlighter)
                
                # Unhighlight all cells
                self.project_view.unhighlight_cells()
                
                # Find the row and column of the opened file in the ProjectView table
                folder_name = self.project_view.get_folder_name_from_extension(os.path.basename(file_path))
                column = ["RDF_UI", "RDF_ACTION", "RDF_BW", "RDF_BVO", "RDF_DATA"].index(folder_name)
                file_name = os.path.basename(file_path)
                
                # Find the row of the file in the ProjectView table
                for row in range(self.project_view.table_view.rowCount()):
                    item = self.project_view.table_view.item(row, column)
                    if item and item.text() == file_name:
                        # Highlight the cell
                        self.project_view.highlight_cell(row, column)
                        break
        
        except Exception as e:
            terminal.write(f"Error loading file: {e}\n")
            QMessageBox.critical(self, "Load File Error", f"An error occurred while loading file: {str(e)}")


    def toggle_terminal(self, splitter, toggle_button):
        if splitter.sizes()[1] == 0:
            splitter.setSizes([int(self.height() * 0.75), int(self.height() * 0.25)])
            toggle_button.setText("▼")
        else:
            splitter.setSizes([int(self.height() * 0.75), 0])
            toggle_button.setText("▲")

    def set_highlighter_language(self, file_path, highlighter):
        try:
            extension = os.path.splitext(file_path)[1][1:]  # Get file extension without the dot
            if extension == "html":
                highlighter.set_language("html")
            elif extension == "js":
                highlighter.set_language("javascript")
            elif extension == "css":
                highlighter.set_language("css")
            elif extension == "json":
                highlighter.set_language("json")
            # Add more cases as needed for other file types

            # Apply the syntax highlighting
            highlighter.rehighlight()
        except Exception as e:
            QMessageBox.critical(self, "Syntax Highlighting Error", f"An error occurred while setting syntax highlighting: {str(e)}")

    def toggle_dark_theme(self):
        if self.dark_theme_enabled:
            QApplication.instance().setPalette(QApplication.style().standardPalette())
        else:
            DarkTheme.apply()
        self.dark_theme_enabled = not self.dark_theme_enabled
    
    def syncScrollBar(self, value):
        self.codeEditor.horizontalScrollBar().setValue(value)
    
    def syncEditorScrollBar(self):
        self.hScrollBar.setValue(self.codeEditor.horizontalScrollBar().value())
       
    def eventFilter(self, source, event):
        if event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_F and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                # Toggle search bar visibility for the current tab
                current_widget = self.tab_widget.currentWidget()
                search_bar = current_widget.findChild(QLineEdit)
                if search_bar:
                    search_bar.setVisible(not search_bar.isVisible())
                    if search_bar.isVisible():
                        search_bar.setFocus()
                return True
        return super().eventFilter(source, event)

    def restart_application(self):
        # Restart the application
        qapp = QApplication.instance()
        qapp.quit()
        QProcess.startDetached(sys.executable,sys.argv)

    def search_text(self, text):
        print(f"Searching text: {text}")
        try:
            current_widget = self.tab_widget.currentWidget()
            print(f"Current widget type: {type(current_widget)}")
            if isinstance(current_widget, QPlainTextEdit):
                print(f"Found QPlainTextEdit: {current_widget}")
                self.highlight_text(current_widget, text)
            else:
                # Check if there's a layout or nested widgets to access QPlainTextEdit
                editor = current_widget.findChild(QPlainTextEdit)
                if editor:
                    print(f"Found QPlainTextEdit via findChild: {editor}")
                    self.highlight_text(editor, text)
                else:
                    print("No QPlainTextEdit found in current editor widget.")
        except Exception as e:
            self.show_error_message(f"Error searching text: {e}")
            

    def highlight_text(self, text_edit, text):
        try:
            extra_selections = []

            # Clear previous selections
            text_edit.setExtraSelections(extra_selections)

            if not text:
                print("no text to highlight")
                return

            # Set up the highlight format
            highlight_format = QTextCharFormat()
            highlight_format.setBackground(QColor("yellow"))

            cursor = text_edit.document().find(text)
            while not cursor.isNull():
                print(f"text found {text} at position {cursor.position()}")
                selection = QTextEdit.ExtraSelection()
                selection.format = highlight_format
                selection.cursor = cursor
                extra_selections.append(selection)
                cursor = text_edit.document().find(text, cursor)

            text_edit.setExtraSelections(extra_selections)
        except Exception as e:
            self.show_error_message(f"Error highlighting text: {e}")


    def toggle_search_bar(self, search_bar):
        try:
            search_bar.setVisible(not search_bar.isVisible())
            if search_bar.isVisible():
                search_bar.setFocus()
        except Exception as e:
            print(f"Error toggling search bar visibility: {e}")
            self.show_error_message(f"Error toggling search bar visibility: {e}")

    def show_error_message(self, message):
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("An error occurred")
        error_dialog.setInformativeText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec()

   
    

    
        




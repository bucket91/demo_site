#!/usr/bin/env python3
import os, re, shutil, sys
from PyQt5 import QtWidgets, QtCore

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
REF_FILE = os.path.join(SITE_DIR, "template reference.txt")

def scan_categories():
    skip = {'.git', '__pycache__', 'node_modules'}
    cats = []
    for item in sorted(os.listdir(SITE_DIR)):
        d = os.path.join(SITE_DIR, item)
        if os.path.isdir(d) and item not in skip:
            html_count = len([f for f in os.listdir(d) if f.endswith('.html')])
            if html_count > 0 or item in ('blog', 'grammar'):
                cats.append(item)
    return cats

def add_ref_entry(category, display_name, file_path):
    rel_path = '/' + os.path.relpath(file_path, SITE_DIR).replace('\\', '/')
    entry_block = f'\n\t\t{{Name:"{display_name}"\n\t\t File: "{rel_path}"}}'

    if not os.path.exists(REF_FILE):
        with open(REF_FILE, 'w') as f:
            f.write(f'SideMenu\n\t{category.capitalize()}{entry_block}\n')
        return True

    with open(REF_FILE) as f:
        content = f.read()

    cat_header = '\t' + category.capitalize()
    if cat_header in content:
        lines = content.split('\n')
        new_lines = []
        inserted = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            stripped = line.rstrip()
            if not inserted and stripped == cat_header:
                next_i = i + 1
                while next_i < len(lines) and lines[next_i].strip() == '':
                    next_i += 1
                if next_i < len(lines) and lines[next_i].strip().startswith('{Name:'):
                    new_lines.append('')
                    new_lines.append(entry_block.strip())
                else:
                    new_lines.append('')
                    new_lines.append(entry_block.strip())
                inserted = True
        content = '\n'.join(new_lines)
    else:
        content += f'\n{cat_header}{entry_block}\n'

    with open(REF_FILE, 'w') as f:
        f.write(content)
    return True

class RefManagerWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QLabel { color: #e0e0e0; }
            QLabel.dim { color: #999; font-size: 11px; }
            QLabel.heading { font-size: 14px; font-weight: bold; color: #eee; margin-top: 8px; }
            QLineEdit, QComboBox {
                background: #2a2a2a; color: #e0e0e0; border: 1px solid #333;
                border-radius: 6px; padding: 6px 10px; font-size: 13px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: none; border-left: 5px solid #999; border-top: 5px solid transparent; border-bottom: 5px solid transparent; }
            QComboBox QAbstractItemView {
                background: #2a2a2a; color: #e0e0e0; selection-background-color: #555;
                border: 1px solid #333;
            }
            QPushButton {
                background: #555; color: #fff; border: none;
                border-radius: 6px; padding: 8px 16px; font-size: 13px;
            }
            QPushButton:hover { background: #666; }
            QPushButton:disabled { background: #333; color: #666; }
            QPushButton.primary { background: #1a6b3c; }
            QPushButton.primary:hover { background: #218c4e; }
            QTextEdit {
                background: #2a2a2a; color: #e0e0e0; border: 1px solid #333;
                border-radius: 6px; padding: 6px; font-size: 13px;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # --- File selection ---
        file_label = QtWidgets.QLabel("HTML File to add:")
        file_label.setProperty("class", "heading")
        layout.addWidget(file_label)

        file_row = QtWidgets.QHBoxLayout()
        self.path_input = QtWidgets.QLineEdit()
        self.path_input.setPlaceholderText("Select an HTML file...")
        file_row.addWidget(self.path_input, 1)
        browse_btn = QtWidgets.QPushButton("Browse")
        browse_btn.clicked.connect(self.browse)
        file_row.addWidget(browse_btn)
        layout.addLayout(file_row)

        # --- Display name ---
        name_label = QtWidgets.QLabel("Sidebar display name:")
        name_label.setProperty("class", "heading")
        layout.addWidget(name_label)

        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("e.g. My Page")
        layout.addWidget(self.name_input)

        # --- Category ---
        cat_label = QtWidgets.QLabel("Category (subdirectory):")
        cat_label.setProperty("class", "heading")
        layout.addWidget(cat_label)

        cat_row = QtWidgets.QHBoxLayout()
        self.cat_combo = QtWidgets.QComboBox()
        self.cat_combo.setEditable(True)
        self.cat_combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.refresh_categories()
        cat_row.addWidget(self.cat_combo, 1)
        layout.addLayout(cat_row)

        hint = QtWidgets.QLabel("Select an existing category or type a new one. A new subdirectory will be created if it doesn't exist.")
        hint.setProperty("class", "dim")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        layout.addStretch()

        # --- Current reference content preview ---
        preview_label = QtWidgets.QLabel("Current reference entries:")
        preview_label.setProperty("class", "heading")
        layout.addWidget(preview_label)

        self.preview = QtWidgets.QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMaximumHeight(180)
        layout.addWidget(self.preview)
        self.refresh_preview()

        # --- Status ---
        self.status = QtWidgets.QLabel("")
        self.status.setProperty("class", "dim")
        layout.addWidget(self.status)

        # --- Buttons ---
        btn_row = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add Entry & Generate")
        self.add_btn.setProperty("class", "primary")
        self.add_btn.setMinimumHeight(40)
        self.add_btn.clicked.connect(self.add_entry)
        btn_row.addWidget(self.add_btn)

        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_all)
        btn_row.addWidget(refresh_btn)
        layout.addLayout(btn_row)

    def browse(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select HTML file", "", "HTML Files (*.html *.htm)")
        if p:
            self.path_input.setText(p)

    def refresh_categories(self):
        current = self.cat_combo.currentText()
        self.cat_combo.clear()
        for cat in scan_categories():
            self.cat_combo.addItem(cat)
        idx = self.cat_combo.findText(current)
        if idx >= 0:
            self.cat_combo.setCurrentIndex(idx)

    def refresh_preview(self):
        if os.path.exists(REF_FILE):
            with open(REF_FILE) as f:
                self.preview.setPlainText(f.read())
        else:
            self.preview.setPlainText("(no reference file yet)")

    def refresh_all(self):
        self.refresh_categories()
        self.refresh_preview()
        self.status.setText("Refreshed")

    def add_entry(self):
        src = self.path_input.text().strip()
        display_name = self.name_input.text().strip()
        category = self.cat_combo.currentText().strip().lower()

        if not src:
            self.status.setText("Please select an HTML file")
            return
        if not display_name:
            self.status.setText("Please enter a display name")
            return
        if not category:
            self.status.setText("Please enter a category")
            return
        if not src.endswith('.html'):
            self.status.setText("Selected file must be an HTML file")
            return

        target_dir = os.path.join(SITE_DIR, category)
        os.makedirs(target_dir, exist_ok=True)

        basename = os.path.basename(src)
        dst = os.path.join(target_dir, basename)
        if os.path.abspath(src) == os.path.abspath(dst):
            self.status.setText("File is already in the target directory")
            return
        if os.path.exists(dst):
            reply = QtWidgets.QMessageBox.question(
                self, "File exists",
                f"{basename} already exists in '{category}/'. Overwrite?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if reply != QtWidgets.QMessageBox.Yes:
                return

        try:
            shutil.copy2(src, dst)
        except Exception as e:
            self.status.setText(f"Error copying file: {e}")
            return

        try:
            add_ref_entry(category, display_name, dst)
        except Exception as e:
            self.status.setText(f"Error updating reference file: {e}")
            return

        self.status.setText(f"Added '{display_name}' to '{category}/'. Running generate...")
        QtWidgets.QApplication.processEvents()

        import generate
        output = generate.run_generate_captured()
        self.status.setText(output)

        self.refresh_all()
        self.path_input.clear()
        self.name_input.clear()

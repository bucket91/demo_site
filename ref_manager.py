#!/usr/bin/env python3
import os, re, shutil, sys
from PyQt5 import QtWidgets, QtCore

SITE_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
REF_FILE = os.path.join(SITE_DIR, "template reference.txt")

def scan_categories():
    skip = {'.git', '__pycache__', 'node_modules', 'build', 'build_venv', 'dist', '.github', 'fonts', 'bundled-git', 'mingit'}
    cats = []
    for item in sorted(os.listdir(SITE_DIR)):
        d = os.path.join(SITE_DIR, item)
        if os.path.isdir(d) and item not in skip:
            html_count = len([f for f in os.listdir(d) if f.endswith('.html')])
            if html_count > 0 or item in ('blog', 'grammar'):
                cats.append(item)
    return cats

def parse_entries():
    """Return list of (category, name, file_path) from the reference file."""
    if not os.path.exists(REF_FILE):
        return []
    entries = []
    current_cat = None
    entry_pattern = re.compile(r'\{Name:"([^"]*)"\s*File:\s*"([^"]*)"\}')
    with open(REF_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            m = re.match(r'^\t(\w+)', line)
            if m:
                current_cat = m.group(1)
            entry_m = entry_pattern.search(line)
            if entry_m and current_cat:
                entries.append((current_cat, entry_m.group(1), entry_m.group(2)))
            elif '{Name:' in line and current_cat:
                name_m = re.search(r'\{Name:"([^"]*)"', line)
                if name_m:
                    file_m = re.search(r'File:\s*"([^"]*)"', line)
                    entries.append((current_cat, name_m.group(1), file_m.group(1) if file_m else ''))
    return entries


def delete_entry(category, display_name):
    """Remove a specific entry from the reference file by category + name."""
    if not os.path.exists(REF_FILE):
        return False
    with open(REF_FILE, encoding="utf-8") as f:
        lines = f.readlines()

    cat_header = '\t' + category
    new_lines = []
    i = 0
    in_target_cat = False
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()
        if stripped == cat_header:
            in_target_cat = True
            new_lines.append(line)
            i += 1
            continue
        if in_target_cat:
            if stripped.startswith('\t') and not stripped.startswith('\t\t'):
                in_target_cat = False
                new_lines.append(line)
                i += 1
                continue
            if stripped.startswith('\t\t'):
                name_m = re.search(r'\{Name:"([^"]*)"', stripped)
                if name_m and name_m.group(1) == display_name:
                    entry_lines = []
                    while i < len(lines) and lines[i].strip():
                        entry_lines.append(lines[i])
                        i += 1
                    while i < len(lines) and not lines[i].strip():
                        i += 1
                    continue
        new_lines.append(line)
        i += 1

    content = ''.join(new_lines).strip()
    if content:
        with open(REF_FILE, 'w', encoding="utf-8") as f:
            f.write(content + '\n')
    else:
        os.remove(REF_FILE)
    return True


def add_ref_entry(category, display_name, file_path):
    rel_path = '/' + os.path.relpath(file_path, SITE_DIR).replace('\\', '/')
    entry_block = f'\n\t\t{{Name:"{display_name}"\n\t\t File: "{rel_path}"}}'

    if not os.path.exists(REF_FILE):
        with open(REF_FILE, 'w', encoding="utf-8") as f:
            f.write(f'SideMenu\n\t{category.capitalize()}{entry_block}\n')
        return True

    with open(REF_FILE, encoding="utf-8") as f:
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

    with open(REF_FILE, 'w', encoding="utf-8") as f:
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
            QTextEdit, QListWidget {
                background: #2a2a2a; color: #e0e0e0; border: 1px solid #333;
                border-radius: 6px; padding: 6px; font-size: 13px;
            }
            QListWidget::item:selected { background: #555; }
            QListWidget::item:hover { background: #3a3a3a; }
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

        # --- Entries + Raw view (horizontal split) ---
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        left_panel = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        entries_label = QtWidgets.QLabel("Current reference entries:")
        entries_label.setProperty("class", "heading")
        left_layout.addWidget(entries_label)

        self.entry_list = QtWidgets.QListWidget()
        left_layout.addWidget(self.entry_list)
        splitter.addWidget(left_panel)

        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        raw_label = QtWidgets.QLabel("Raw file (template reference.txt):")
        raw_label.setProperty("class", "heading")
        right_layout.addWidget(raw_label)

        self.raw_preview = QtWidgets.QTextEdit()
        self.raw_preview.setReadOnly(True)
        self.raw_preview.setStyleSheet("font-family: monospace; font-size: 12px;")
        right_layout.addWidget(self.raw_preview)
        splitter.addWidget(right_panel)

        splitter.setSizes([300, 400])
        layout.addWidget(splitter, 1)

        # --- Buttons ---
        btn_row = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add Entry & Generate")
        self.add_btn.setProperty("class", "primary")
        self.add_btn.setMinimumHeight(40)
        self.add_btn.clicked.connect(self.add_entry)
        btn_row.addWidget(self.add_btn)

        self.delete_btn = QtWidgets.QPushButton("Delete Selected")
        self.delete_btn.setMinimumHeight(40)
        self.delete_btn.clicked.connect(self.delete_selected)
        btn_row.addWidget(self.delete_btn)

        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.clicked.connect(self.refresh_all)
        btn_row.addWidget(refresh_btn)
        layout.addLayout(btn_row)

        # --- Status ---
        self.status = QtWidgets.QLabel("")
        self.status.setProperty("class", "dim")
        layout.addWidget(self.status)

    def set_file_path(self, path):
        self.path_input.setText(path)
        basename = os.path.splitext(os.path.basename(path))[0]
        self.name_input.setText(basename)

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

    def refresh_entries(self):
        self.entry_list.clear()
        for cat, name, path in parse_entries():
            item = QtWidgets.QListWidgetItem(f"{cat} / {name}")
            item.setData(QtCore.Qt.UserRole, (cat, name))
            self.entry_list.addItem(item)

    def refresh_raw(self):
        if os.path.exists(REF_FILE):
            with open(REF_FILE, encoding="utf-8") as f:
                self.raw_preview.setPlainText(f.read())
        else:
            self.raw_preview.setPlainText("(file does not exist yet)")

    @QtCore.pyqtSlot()
    def delete_selected(self):
        item = self.entry_list.currentItem()
        if not item:
            self.status.setText("Select an entry to delete")
            return
        cat, name = item.data(QtCore.Qt.UserRole)
        reply = QtWidgets.QMessageBox.question(
            self, "Delete entry",
            f"Remove '{name}' from '{cat}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply != QtWidgets.QMessageBox.Yes:
            return
        if delete_entry(cat, name):
            self.status.setText(f"Deleted '{name}'. Regenerating...")
            QtWidgets.QApplication.processEvents()
            import generate
            output = generate.run_generate_captured()
            self.status.setText(output)
            self.refresh_all()
        else:
            self.status.setText("Failed to delete entry")

    def refresh_all(self):
        self.refresh_categories()
        self.refresh_entries()
        self.refresh_raw()
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
        already_in_place = os.path.abspath(src) == os.path.abspath(dst)
        if not already_in_place:
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

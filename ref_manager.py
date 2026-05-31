#!/usr/bin/env python3
import os, sys, shutil, glob
import re, html as html_mod
from PyQt6 import QtWidgets, QtCore, QtGui

_APP_DIR = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.join(_APP_DIR, "site")

import sidebar_util
sidebar_util.SITE_DIR = SITE_DIR


class _DropTree(QtWidgets.QTreeWidget):
    dropped = QtCore.pyqtSignal()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.dropped.emit()


class RefManagerWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QLabel { color: #c9d1d9; }
            QLabel.dim { color: #6e7681; }
            QLabel.heading { font-weight: bold; color: #c9d1d9; margin-top: 8px; }
            QLineEdit, QComboBox {
                background: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                border-radius: 6px; padding: 6px 10px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-top: 5px solid transparent; border-bottom: 5px solid transparent; }
            QComboBox QAbstractItemView {
                background: #0d1117; color: #c9d1d9; selection-background-color: #21262d;
                border: 1px solid #30363d;
            }
            QPushButton {
                background: #21262d; color: #c9d1d9; border: none;
                border-radius: 6px; padding: 8px 16px;
            }
            QPushButton:hover { background: #30363d; }
            QPushButton:disabled { background: #30363d; color: #484f58; }
            QPushButton.primary { background: #58a6ff; }
            QPushButton.primary:hover { background: #79c0ff; }
            QTreeWidget {
                background: #161b22; color: #c9d1d9; border: 1px solid #30363d;
                border-radius: 6px; padding: 4px;
            }
            QTreeWidget::item { padding: 4px 2px; }
            QTreeWidget::item:selected { background: #21262d; }
            QTreeWidget::item:hover { background: #21262d; }
            QGroupBox {
                color: #c9d1d9; font-weight: bold;
                border: 1px solid #30363d; border-radius: 6px; margin-top: 8px;
                padding: 10px 8px 6px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        top_row = QtWidgets.QHBoxLayout()
        heading = QtWidgets.QLabel("Pages")
        heading.setProperty("class", "heading")
        top_row.addWidget(heading, 1)

        self.add_btn = QtWidgets.QPushButton("+ Add")
        self.add_btn.setMinimumHeight(36)
        self.add_btn.clicked.connect(self.show_add_dialog)
        top_row.addWidget(self.add_btn)

        self.discover_btn = QtWidgets.QPushButton("\u27f3")
        self.discover_btn.setToolTip("Scan for new HTML files")
        self.discover_btn.setMinimumHeight(36)
        self.discover_btn.clicked.connect(self.refresh_all)
        top_row.addWidget(self.discover_btn)

        new_page_btn = QtWidgets.QPushButton("New Page (experimental)")
        new_page_btn.setMinimumHeight(36)
        new_page_btn.clicked.connect(self._new_page)
        top_row.addWidget(new_page_btn)

        import_btn = QtWidgets.QPushButton("Import")
        import_btn.setMinimumHeight(36)
        import_btn.clicked.connect(self._import_file)
        top_row.addWidget(import_btn)

        layout.addLayout(top_row)

        self.tree = _DropTree()
        self.tree.setHeaderHidden(True)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.tree.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
        self.tree.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)
        self.tree.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._context_menu)
        self.tree.itemChanged.connect(self._on_item_changed)
        self.tree.dropped.connect(self._on_drop)
        layout.addWidget(self.tree, 1)

        self.discover_group = QtWidgets.QGroupBox("Discovered files (not in sidebar)")
        self.discover_group.hide()
        discover_layout = QtWidgets.QVBoxLayout(self.discover_group)
        self.discover_list = QtWidgets.QWidget()
        self.discover_list_layout = QtWidgets.QVBoxLayout(self.discover_list)
        self.discover_list_layout.setContentsMargins(0, 0, 0, 0)
        discover_layout.addWidget(self.discover_list)
        layout.addWidget(self.discover_group)

        btn_row = QtWidgets.QHBoxLayout()

        self.remove_btn = QtWidgets.QPushButton("Remove")
        self.remove_btn.setMinimumHeight(40)
        self.remove_btn.clicked.connect(self.remove_selected)
        btn_row.addWidget(self.remove_btn)

        self.delete_btn = QtWidgets.QPushButton("Delete File")
        self.delete_btn.setMinimumHeight(40)
        self.delete_btn.clicked.connect(self.delete_selected)
        btn_row.addWidget(self.delete_btn)

        btn_row.addStretch()

        self.convert_media_btn = QtWidgets.QPushButton("Convert Media")
        self.convert_media_btn.setMinimumHeight(40)
        self.convert_media_btn.clicked.connect(self.convert_media)
        btn_row.addWidget(self.convert_media_btn)

        self.gen_btn = QtWidgets.QPushButton("Generate")
        self.gen_btn.setProperty("class", "primary")
        self.gen_btn.setMinimumHeight(40)
        self.gen_btn.clicked.connect(self.generate)
        btn_row.addWidget(self.gen_btn)
        layout.addLayout(btn_row)

        self.status = QtWidgets.QLabel("")
        self.status.setProperty("class", "dim")
        layout.addWidget(self.status)

        self._sidebar_data = []
        self.refresh_all()

    def _tree_to_sidebar(self):
        data = []
        for i in range(self.tree.topLevelItemCount()):
            cat_item = self.tree.topLevelItem(i)
            cat_name = cat_item.text(0)
            entries = []
            for j in range(cat_item.childCount()):
                entry_item = cat_item.child(j)
                entry_data = entry_item.data(0, QtCore.Qt.ItemDataRole.UserRole)
                if entry_data and "file" in entry_data:
                    d = {"name": entry_item.text(0), "file": entry_data["file"]}
                    if "comments" in entry_data:
                        d["comments"] = entry_data["comments"]
                    entries.append(d)
            data.append({"category": cat_name, "entries": entries})
        return data

    def _rebuild_tree(self):
        self.tree.blockSignals(True)
        self.tree.clear()
        for cat in self._sidebar_data:
            cat_item = QtWidgets.QTreeWidgetItem([cat["category"]])
            cat_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, {"type": "category"})
            cat_item.setFlags(cat_item.flags() | QtCore.Qt.ItemFlag.ItemIsDropEnabled)
            for entry in cat["entries"]:
                entry_item = QtWidgets.QTreeWidgetItem([entry["name"]])
                entry_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, {
                    "type": "entry", "category": cat["category"],
                    "name": entry["name"], "file": entry["file"],
                    "comments": entry.get("comments", True)
                })
                entry_item.setFlags(entry_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable | QtCore.Qt.ItemFlag.ItemIsDragEnabled)
                cat_item.addChild(entry_item)
            self.tree.addTopLevelItem(cat_item)
        self.tree.expandAll()
        self.tree.blockSignals(False)

    def _refresh_discovered(self):
        for i in reversed(range(self.discover_list_layout.count())):
            w = self.discover_list_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        discovered = sidebar_util.auto_discover()
        if not discovered:
            self.discover_group.hide()
            return
        self.discover_group.show()

        for d in discovered:
            row = QtWidgets.QHBoxLayout()
            row.setContentsMargins(4, 2, 4, 2)
            label = QtWidgets.QLabel(f"{d['category']} / {d['name']}")
            label.setStyleSheet("color: #c9d1d9;")
            row.addWidget(label, 1)
            add_btn = QtWidgets.QPushButton("+")
            add_btn.setFixedWidth(30)
            add_btn.setFixedHeight(26)
            f = d["file"]
            n = d["name"]
            c = d["category"]
            add_btn.clicked.connect(lambda checked, cat=c, file_path=f, name=n: self._add_discovered(cat, file_path, name))
            row.addWidget(add_btn)
            self.discover_list_layout.addLayout(row)

    def refresh_all(self):
        self._sidebar_data = sidebar_util.load_sidebar()
        self._rebuild_tree()
        self._refresh_discovered()
        self.status.setText("Refreshed")

    def _on_item_changed(self, item, column):
        data = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        if data and data.get("type") == "entry":
            new_name = item.text(0).strip()
            if new_name and new_name != data.get("name"):
                for cat in self._sidebar_data:
                    if cat["category"] == data["category"]:
                        for entry in cat["entries"]:
                            if entry["file"] == data["file"]:
                                entry["name"] = new_name
                                sidebar_util.save_sidebar(self._sidebar_data)
                                self.status.setText(f"Renamed to '{new_name}'")
                                return

    def _on_drop(self):
        self._sidebar_data = self._tree_to_sidebar()
        sidebar_util.save_sidebar(self._sidebar_data)
        self.status.setText("Order updated")

    def _context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return
        data = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        if not data:
            return
        menu = QtWidgets.QMenu(self)
        if data.get("type") == "entry":
            edit_action = menu.addAction("Edit in WYSIWYG")
            rename_action = menu.addAction("Rename")
            menu.addSeparator()
            remove_action = menu.addAction("Remove from sidebar")
            delete_action = menu.addAction("Delete file")
            menu.addSeparator()
            comments_on = data.get("comments", True)
            comments_action = menu.addAction("Comments: On" if comments_on else "Comments: Off")
            action = menu.exec_(self.tree.viewport().mapToGlobal(pos))
            if action == edit_action:
                self._edit_page(data)
            elif action == rename_action:
                self.tree.editItem(item, 0)
            elif action == remove_action:
                self._remove_entry(data)
            elif action == delete_action:
                self._delete_entry(data)
            elif action == comments_action:
                self._toggle_comments(data)
        elif data.get("type") == "category":
            remove_action = menu.addAction("Remove category from sidebar")
            delete_action = menu.addAction("Delete category and all files")
            action = menu.exec_(self.tree.viewport().mapToGlobal(pos))
            if action == remove_action:
                self._remove_category(item.text(0))
            elif action == delete_action:
                self._delete_category(item.text(0))

    def _remove_entry(self, data):
        reply = QtWidgets.QMessageBox.question(
            self, "Remove", f"Remove '{data['name']}' from sidebar?\nThe file will be kept on disk.",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        for cat in self._sidebar_data:
            if cat["category"] == data["category"]:
                cat["entries"] = [e for e in cat["entries"] if e["file"] != data["file"]]
                break
        sidebar_util.save_sidebar(self._sidebar_data)
        self.refresh_all()
        self.status.setText(f"Removed '{data['name']}' from sidebar")

    def _delete_entry(self, data):
        reply = QtWidgets.QMessageBox.question(
            self, "Delete File",
            f"Delete '{data['name']}'?\nThe file '{data['file']}' will be permanently deleted.",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        fpath = os.path.join(SITE_DIR, data["file"].lstrip("/"))
        removed = False
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
                removed = True
            except Exception as e:
                self.status.setText(f"Error deleting file: {e}")
                return
        for cat in self._sidebar_data:
            if cat["category"] == data["category"]:
                cat["entries"] = [e for e in cat["entries"] if e["file"] != data["file"]]
                break
        sidebar_util.save_sidebar(self._sidebar_data)
        self.refresh_all()
        self.status.setText(f"Deleted '{data['name']}'{' and file' if removed else ''}")

    def _remove_category(self, category):
        reply = QtWidgets.QMessageBox.question(
            self, "Remove Category",
            f"Remove '{category}' from sidebar?\nFiles and folder will be kept on disk.",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        self._sidebar_data = [c for c in self._sidebar_data if c["category"] != category]
        sidebar_util.save_sidebar(self._sidebar_data)
        self.refresh_all()
        self.status.setText(f"Removed category '{category}' from sidebar")

    def _delete_category(self, category):
        cat_dir = os.path.join(SITE_DIR, category)
        file_count = 0
        if os.path.isdir(cat_dir):
            file_count = sum(1 for f in os.listdir(cat_dir) if os.path.isfile(os.path.join(cat_dir, f)))
        reply = QtWidgets.QMessageBox.question(
            self, "Delete Category",
            f"Delete '{category}' and all {file_count} file(s) inside?\nThis cannot be undone.",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        self._sidebar_data = [c for c in self._sidebar_data if c["category"] != category]
        sidebar_util.save_sidebar(self._sidebar_data)
        if os.path.isdir(cat_dir):
            import shutil
            try:
                shutil.rmtree(cat_dir)
            except Exception as e:
                self.status.setText(f"Error deleting directory: {e}")
                self.refresh_all()
                return
        self.refresh_all()
        self.status.setText(f"Deleted category '{category}' and {file_count} file(s)")

    def _add_discovered(self, category, file_path, name):
        for cat in self._sidebar_data:
            if cat["category"] == category:
                cat["entries"].append({"name": name, "file": file_path})
                sidebar_util.save_sidebar(self._sidebar_data)
                self.refresh_all()
                self.status.setText(f"Added '{name}' to '{category}'")
                return
        self._sidebar_data.append({"category": category, "entries": [{"name": name, "file": file_path}]})
        sidebar_util.save_sidebar(self._sidebar_data)
        self.refresh_all()
        self.status.setText(f"Added '{name}' to new category '{category}'")

    def _toggle_comments(self, data):
        for cat in self._sidebar_data:
            if cat["category"] == data["category"]:
                for entry in cat["entries"]:
                    if entry["file"] == data["file"]:
                        current = entry.get("comments", True)
                        entry["comments"] = not current
                        sidebar_util.save_sidebar(self._sidebar_data)
                        self.refresh_all()
                        self.status.setText(f"{'Enabled' if not current else 'Disabled'} comments for '{data['name']}'")
                        return

    def _wrap_content(self, body_html, title, file_path=None):
        if file_path:
            rel = os.path.relpath(SITE_DIR, os.path.dirname(os.path.abspath(file_path))).replace('\\', '/')
        else:
            rel = os.path.relpath(SITE_DIR, os.path.join(SITE_DIR, "pages")).replace('\\', '/')
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html_mod.escape(title)}</title>
  <link rel="stylesheet" href="{rel}/style.css">
</head>
<body>
  <header>
    <button class="sidebar-toggle" onclick="toggleSidebar()">&#9776;</button>
    <h1><a href="{rel}/index.html">{html_mod.escape(title)}</a></h1>
    <button class="theme-toggle" onclick="toggleTheme()">&#x2600;&#xFE0F;</button>
  </header>
  <div class="layout">
    <aside class="sidebar" id="sidebar">
    </aside>
    <main>
{body_html}
    </main>
  </div>
</body>
</html>"""

    def _edit_page(self, data):
        fpath = os.path.join(SITE_DIR, data["file"].lstrip("/"))
        if not os.path.exists(fpath):
            self.status.setText(f"File not found: {data['file']}")
            return
        with open(fpath, encoding="utf-8") as f:
            src = f.read()
        m = re.search(r'<main[^>]*>(.*?)</main>', src, re.DOTALL)
        body = m.group(1).strip() if m else src
        from wysiwyg_editor import WysiwygEditor
        dlg = WysiwygEditor(body, self)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            html = dlg.result_html()
            if html:
                wrapped = self._wrap_content(html, data["name"], fpath)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(wrapped)
                self.status.setText(f"Saved '{data['name']}'")

    def _new_page(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("New Page")
        dlg.setMinimumWidth(380)
        dl = QtWidgets.QVBoxLayout(dlg)
        dl.setSpacing(8)
        cat_label = QtWidgets.QLabel("Category (folder):")
        cat_label.setStyleSheet("color: #c9d1d9;")
        dl.addWidget(cat_label)
        cat_input = QtWidgets.QLineEdit("blog")
        dl.addWidget(cat_input)
        title_label = QtWidgets.QLabel("Page title:")
        title_label.setStyleSheet("color: #c9d1d9;")
        dl.addWidget(title_label)
        title_input = QtWidgets.QLineEdit()
        title_input.setPlaceholderText("My New Page")
        dl.addWidget(title_input)
        btns = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("Create & Edit")
        ok_btn.setProperty("class", "primary")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(dlg.reject)
        btns.addWidget(cancel_btn)
        btns.addWidget(ok_btn)
        dl.addLayout(btns)

        def do_create():
            cat = cat_input.text().strip()
            title = title_input.text().strip()
            if not cat or not title:
                QtWidgets.QMessageBox.warning(dlg, "Missing", "Enter both category and title")
                return
            target_dir = os.path.join(SITE_DIR, cat)
            os.makedirs(target_dir, exist_ok=True)
            slug = title.lower().replace(' ', '-').replace('--', '-')
            slug = re.sub(r'[^a-z0-9-]', '', slug)
            fname = slug + '.html'
            fpath = os.path.join(target_dir, fname)
            if os.path.exists(fpath):
                QtWidgets.QMessageBox.warning(dlg, "Exists", f"'{fname}' already exists")
                return
            from wysiwyg_editor import WysiwygEditor
            dlg.accept()
            ed = WysiwygEditor("", self)
            if ed.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                html = ed.result_html()
                if html:
                    wrapped = self._wrap_content(html, title, fpath)
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(wrapped)
                    rel = '/' + os.path.relpath(fpath, SITE_DIR).replace('\\', '/')
                    for c in self._sidebar_data:
                        if c["category"] == cat:
                            c["entries"].append({"name": title, "file": rel})
                            break
                    else:
                        self._sidebar_data.append({"category": cat, "entries": [{"name": title, "file": rel}]})
                    sidebar_util.save_sidebar(self._sidebar_data)
                    self.refresh_all()
                    self.status.setText(f"Created '{title}'")

        ok_btn.clicked.connect(do_create)
        dlg.exec()

    def _import_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Import File", "",
            "Google Docs Export (*.zip);;MHT files (*.mht *.mhtml)")
        if not path:
            return
        from docx2html import convert_file
        result, err = convert_file(path)
        if err:
            QtWidgets.QMessageBox.warning(self, "Import Error", err)
            return
        if not result.get('ok'):
            QtWidgets.QMessageBox.warning(self, "Import Error", result.get('error', 'Unknown error'))
            return
        imported_html = result['html']
        imported_title = result['title']

        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Import Page")
        dlg.setMinimumWidth(380)
        dl = QtWidgets.QVBoxLayout(dlg)
        dl.setSpacing(8)

        cat_label = QtWidgets.QLabel("Category (folder):")
        cat_label.setStyleSheet("color: #c9d1d9;")
        dl.addWidget(cat_label)
        cat_input = QtWidgets.QLineEdit("blog")
        dl.addWidget(cat_input)

        title_label = QtWidgets.QLabel("Page title:")
        title_label.setStyleSheet("color: #c9d1d9;")
        dl.addWidget(title_label)
        title_input = QtWidgets.QLineEdit(imported_title)
        dl.addWidget(title_input)

        btns = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("Import & Save")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(dlg.reject)
        btns.addWidget(cancel_btn)
        btns.addWidget(ok_btn)
        dl.addLayout(btns)

        def do_import():
            cat = cat_input.text().strip()
            title = title_input.text().strip()
            if not cat or not title:
                QtWidgets.QMessageBox.warning(dlg, "Missing", "Enter both category and title")
                return
            target_dir = os.path.join(SITE_DIR, cat)
            os.makedirs(target_dir, exist_ok=True)
            slug = title.lower().replace(' ', '-').replace('--', '-')
            slug = re.sub(r'[^a-z0-9-]', '', slug)
            fname = slug + '.html'
            fpath = os.path.join(target_dir, fname)
            if os.path.exists(fpath):
                QtWidgets.QMessageBox.warning(dlg, "Exists", f"'{fname}' already exists")
                return
            dlg.accept()
            wrapped = self._wrap_content(imported_html, title, fpath)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(wrapped)
            rel = '/' + os.path.relpath(fpath, SITE_DIR).replace('\\', '/')
            for c in self._sidebar_data:
                if c["category"] == cat:
                    c["entries"].append({"name": title, "file": rel})
                    break
            else:
                self._sidebar_data.append({"category": cat, "entries": [{"name": title, "file": rel}]})
            sidebar_util.save_sidebar(self._sidebar_data)
            self.refresh_all()
            self.status.setText(f"Imported '{title}'")

        ok_btn.clicked.connect(do_import)
        dlg.exec()

    def remove_selected(self):
        item = self.tree.currentItem()
        if not item:
            self.status.setText("Select an entry to remove")
            return
        data = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        if not data:
            return
        if data.get("type") == "entry":
            self._remove_entry(data)
        elif data.get("type") == "category":
            self._remove_category(item.text(0))

    def delete_selected(self):
        item = self.tree.currentItem()
        if not item:
            self.status.setText("Select an entry to delete")
            return
        data = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        if not data:
            return
        if data.get("type") == "entry":
            self._delete_entry(data)
        elif data.get("type") == "category":
            self._delete_category(item.text(0))

    def set_file_path(self, path, category=None):
        self.refresh_all()

    def show_add_dialog(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Add Page to Site")
        dlg.setMinimumWidth(420)
        dl = QtWidgets.QVBoxLayout(dlg)
        dl.setSpacing(8)

        file_label = QtWidgets.QLabel("HTML File:")
        file_label.setStyleSheet("color: #c9d1d9;")
        dl.addWidget(file_label)
        file_row = QtWidgets.QHBoxLayout()
        file_input = QtWidgets.QLineEdit()
        file_input.setPlaceholderText("Select an HTML file...")
        file_row.addWidget(file_input, 1)
        browse_btn = QtWidgets.QPushButton("Browse")
        file_row.addWidget(browse_btn)
        dl.addLayout(file_row)

        cat_label = QtWidgets.QLabel("Category:")
        cat_label.setStyleSheet("color: #c9d1d9;")
        dl.addWidget(cat_label)
        cat_combo = QtWidgets.QComboBox()
        cat_combo.setView(QtWidgets.QListView())
        cat_combo.setEditable(True)
        cat_combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        for cat in self._sidebar_data:
            cat_combo.addItem(cat["category"])
        dl.addWidget(cat_combo)

        name_label = QtWidgets.QLabel("Display Name (shown in sidebar):")
        name_label.setStyleSheet("color: #c9d1d9;")
        dl.addWidget(name_label)
        name_input = QtWidgets.QLineEdit()
        name_input.setPlaceholderText("My Page")
        dl.addWidget(name_input)

        dl.addSpacing(8)

        btns = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("Add")
        ok_btn.setProperty("class", "primary")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        dl.addLayout(btns)

        def browse():
            p, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Select HTML", "", "HTML Files (*.html)")
            if p:
                file_input.setText(p)
                basename = os.path.splitext(os.path.basename(p))[0].replace('-', ' ').title()
                name_input.setText(basename)
        browse_btn.clicked.connect(browse)
        cancel_btn.clicked.connect(dlg.reject)

        def do_add():
            src = file_input.text().strip()
            cat = cat_combo.currentText().strip()
            name = name_input.text().strip()
            if not src:
                QtWidgets.QMessageBox.warning(dlg, "Missing", "Select an HTML file")
                return
            if not cat:
                QtWidgets.QMessageBox.warning(dlg, "Missing", "Enter a category")
                return
            if not name:
                QtWidgets.QMessageBox.warning(dlg, "Missing", "Enter a display name")
                return
            target_dir = os.path.join(SITE_DIR, cat)
            os.makedirs(target_dir, exist_ok=True)
            dst = os.path.join(target_dir, os.path.basename(src))
            if os.path.abspath(src) != os.path.abspath(dst):
                try:
                    shutil.copy2(src, dst)
                except Exception as e:
                    QtWidgets.QMessageBox.warning(dlg, "Error", f"Failed to copy file: {e}")
                    return
            rel = '/' + os.path.relpath(dst, SITE_DIR).replace('\\', '/')
            for c in self._sidebar_data:
                if c["category"] == cat:
                    c["entries"].append({"name": name, "file": rel})
                    break
            else:
                self._sidebar_data.append({"category": cat, "entries": [{"name": name, "file": rel}]})
            sidebar_util.save_sidebar(self._sidebar_data)
            dlg.accept()
            self.refresh_all()
            self.status.setText(f"Added '{name}' to '{cat}'")

        ok_btn.clicked.connect(do_add)
        dlg.exec()

    def convert_media(self):
        self.convert_media_btn.setEnabled(False)
        self.convert_media_btn.setText("Converting...")
        self.status.setText("Converting media in background...")

        class ConvertThread(QtCore.QThread):
            done = QtCore.pyqtSignal(str)

            def run(self):
                from advanced_theme import convert_to_webp, convert_to_webm
                media_dir = os.path.join(SITE_DIR, "media")
                html_files = glob.glob(os.path.join(SITE_DIR, "**/*.html"), recursive=True)
                skip_dirs = {'.git', '__pycache__', 'node_modules', 'build', 'build_venv', 'dist', '.github', 'fonts', 'bundled-git', 'mingit', 'ckeditor'}
                converted = 0
                errors = []
                img_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif'}
                vid_exts = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'}

                for fp in html_files:
                    rel = os.path.relpath(fp, SITE_DIR)
                    if any(part in skip_dirs for part in rel.split(os.sep)):
                        continue
                    with open(fp, encoding="utf-8") as f:
                        src = f.read()

                    changed = False

                    def replace_img(m):
                        nonlocal changed, converted, errors
                        url = m.group(1)
                        if url.startswith('data:') or url.startswith('http://') or url.startswith('https://'):
                            return m.group(0)
                        ext = os.path.splitext(url)[1].lower()
                        if ext not in img_exts:
                            return m.group(0)
                        abs_path = os.path.join(os.path.dirname(fp), url)
                        if not os.path.exists(abs_path):
                            return m.group(0)
                        ok, result = convert_to_webp(abs_path, media_dir)
                        if ok:
                            webp_rel = os.path.relpath(result, os.path.dirname(fp)).replace('\\', '/')
                            converted += 1
                            changed = True
                            return f'<img src="{webp_rel}"'
                        else:
                            errors.append(f"{rel}: {result}")
                            return m.group(0)

                    def replace_vid(m):
                        nonlocal changed, converted, errors
                        url = m.group(1)
                        if url.startswith('data:') or url.startswith('http://') or url.startswith('https://'):
                            return m.group(0)
                        ext = os.path.splitext(url)[1].lower()
                        if ext not in vid_exts:
                            return m.group(0)
                        abs_path = os.path.join(os.path.dirname(fp), url)
                        if not os.path.exists(abs_path):
                            return m.group(0)
                        ok, result = convert_to_webm(abs_path, media_dir)
                        if ok:
                            webm_rel = os.path.relpath(result, os.path.dirname(fp)).replace('\\', '/')
                            converted += 1
                            changed = True
                            return f'<source src="{webm_rel}"'
                        else:
                            errors.append(f"{rel}: {result}")
                            return m.group(0)

                    src = re.sub(r'<img\s+src="([^"]+)"', replace_img, src)
                    src = re.sub(r'<source\s+src="([^"]+)"', replace_vid, src)

                    if changed:
                        with open(fp, "w", encoding="utf-8") as f:
                            f.write(src)

                parts = [f"Converted {converted} media file(s)"]
                if errors:
                    parts.append(f"Errors: {'; '.join(errors[:3])}")
                    if len(errors) > 3:
                        parts.append(f"... and {len(errors)-3} more")
                self.done.emit(" | ".join(parts))

        self._convert_thread = ConvertThread()
        self._convert_thread.done.connect(lambda msg: (
            self.status.setText(msg),
            self.convert_media_btn.setEnabled(True),
            self.convert_media_btn.setText("Convert Media"),
        ))
        self._convert_thread.start()

    def generate(self):
        self.status.setText("Generating...")
        self.gen_btn.setEnabled(False)
        self.gen_btn.setText("Generating...")

        self._gen_worker = _GenerateWorker()
        self._gen_worker.finished.connect(self._on_generate_done)
        self._gen_worker.start()

    def _on_generate_done(self, output):
        self.gen_btn.setEnabled(True)
        self.gen_btn.setText("Generate")
        self.status.setText(output)


class _GenerateWorker(QtCore.QThread):
    finished = QtCore.pyqtSignal(str)

    def run(self):
        import generate
        try:
            output = generate.run_generate_captured()
        except Exception as e:
            output = f"Error: {e}"
        self.finished.emit(output)

    def refresh_categories(self):
        pass

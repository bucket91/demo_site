#!/usr/bin/env python3
import json, os, sys, urllib.request, urllib.error
from PyQt5 import QtWidgets, QtCore, QtGui

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SITE_DIR, "config.json")

def load():
    default = {
        "supabase_url": "",
        "supabase_anon_key": "",
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return {**default, **json.load(f)}
    return default

CFG = load()
BASE = CFG.get("supabase_url", "").rstrip("/")
KEY = CFG.get("supabase_anon_key", "")
HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Prefer": "return=representation",
}

def req(method, path, data=None):
    url = f"{BASE}/rest/v1/{path}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method, headers=HEADERS)
    try:
        with urllib.request.urlopen(r) as resp:
            ct = resp.headers.get("Content-Type", "")
            if "json" in ct:
                return json.loads(resp.read())
            return resp.read()
    except urllib.error.HTTPError as e:
        raise Exception(f"HTTP {e.code}: {e.read().decode(errors='replace')}")

class CommentModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.comments = []
        self.columns = ["ID", "Page", "Name", "Body", "Created"]

    def load(self):
        try:
            data = req("GET", "comments?select=id,page,name,body,created_at&order=created_at.desc")
            self.beginResetModel()
            self.comments = data
            self.endResetModel()
            return True
        except Exception as e:
            return str(e)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.comments)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.columns)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        c = self.comments[index.row()]
        col = index.column()
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return str(c.get("id", ""))
            if col == 1:
                return c.get("page", "")
            if col == 2:
                return c.get("name", "")
            if col == 3:
                return c.get("body", "")
            if col == 4:
                return c.get("created_at", "")[:19].replace("T", " ")
        if role == QtCore.Qt.UserRole:
            return c
        return None

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.columns[section]
        return None

    def remove_comment(self, row):
        cid = self.comments[row]["id"]
        req("DELETE", f"comments?id=eq.{cid}")
        self.beginRemoveRows(QtCore.QModelIndex(), row, row)
        self.comments.pop(row)
        self.endRemoveRows()

    def update_comment(self, row, data):
        cid = self.comments[row]["id"]
        req("PATCH", f"comments?id=eq.{cid}", data)
        self.comments[row].update(data)

class EditDialog(QtWidgets.QDialog):
    def __init__(self, comment):
        super().__init__()
        self.setWindowTitle(f"Edit Comment #{comment['id']}")
        self.setMinimumWidth(480)
        self.comment = comment

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)

        def field(label, key):
            fl = QtWidgets.QFormLayout()
            inp = QtWidgets.QLineEdit(str(comment.get(key, "")))
            fl.addRow(label, inp)
            layout.addLayout(fl)
            return inp

        self.page = field("Page", "page")
        self.name = field("Name", "name")
        self.body_inp = QtWidgets.QTextEdit()
        self.body_inp.setPlainText(comment.get("body", ""))
        self.body_inp.setMinimumHeight(100)
        fl = QtWidgets.QFormLayout()
        fl.addRow("Body", self.body_inp)
        layout.addLayout(fl)

        btns = QtWidgets.QHBoxLayout()
        save = QtWidgets.QPushButton("Save")
        save.clicked.connect(self.accept)
        cancel = QtWidgets.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        btns.addWidget(save)
        btns.addWidget(cancel)
        layout.addLayout(btns)

    def get_data(self):
        return {
            "page": self.page.text(),
            "name": self.name.text(),
            "body": self.body_inp.toPlainText(),
        }

class CommentAdminWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QTableView {
                background: #333; color: #eee; gridline-color: #2a2a2a;
                border: none; font-size: 13px; selection-background-color: #555;
            }
            QTableView::item { padding: 6px; }
            QHeaderView::section {
                background: #2a2a2a; color: #eee; padding: 8px;
                border: none; font-weight: bold; font-size: 12px;
            }
            QLabel { color: #999; font-size: 13px; }
            QPushButton {
                background: #555; color: #fff; border: none;
                border-radius: 6px; padding: 8px 16px; font-size: 13px;
            }
            QPushButton:hover { background: #666; }
            QPushButton.danger { background: #b71c1c; }
            QPushButton.danger:hover { background: #d32f2f; }
            QPushButton:disabled { background: #333; color: #666; }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # header
        hdr = QtWidgets.QFrame()
        hdr.setStyleSheet("background: #2a2a2a; padding: 16px 20px;")
        hl = QtWidgets.QHBoxLayout(hdr)
        title = QtWidgets.QLabel("Comment Admin")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #eee;")
        hl.addWidget(title)
        hl.addStretch()
        self.status = QtWidgets.QLabel("")
        self.status.setStyleSheet("color: #999;")
        hl.addWidget(self.status)
        layout.addWidget(hdr)

        # table
        self.model = CommentModel()
        self.table = QtWidgets.QTableView()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableView { alternate-background-color: #3a3a3a; }
        """)
        hdr_v = self.table.horizontalHeader()
        hdr_v.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        hdr_v.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        hdr_v.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        layout.addWidget(self.table, 1)

        # toolbar
        bar = QtWidgets.QFrame()
        bar.setStyleSheet("background: #2a2a2a; padding: 10px 20px;")
        bl = QtWidgets.QHBoxLayout(bar)
        bl.setSpacing(8)

        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        bl.addWidget(refresh_btn)

        edit_btn = QtWidgets.QPushButton("Edit Selected")
        edit_btn.clicked.connect(self.edit_selected)
        bl.addWidget(edit_btn)

        delete_btn = QtWidgets.QPushButton("Delete Selected")
        delete_btn.setProperty("class", "danger")
        delete_btn.setStyleSheet("background: #b71c1c; color: #fff; border: none; border-radius: 6px; padding: 8px 16px; font-size: 13px;")
        delete_btn.clicked.connect(self.delete_selected)
        bl.addWidget(delete_btn)

        bl.addStretch()
        layout.addWidget(bar)

        self.refresh()

    def refresh(self):
        err = self.model.load()
        if err is True:
            self.status.setText(f"{len(self.model.comments)} comments")
        else:
            self.status.setText(f"Error: {err}")

    def selected_row(self):
        sel = self.table.selectionModel().selectedRows()
        if sel:
            return sel[0].row()
        return None

    def edit_selected(self):
        row = self.selected_row()
        if row is None:
            return
        c = self.model.comments[row]
        dlg = EditDialog(c)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            data = dlg.get_data()
            self.model.update_comment(row, data)
            self.model.layoutChanged.emit()
            self.status.setText("Comment updated")

    def delete_selected(self):
        row = self.selected_row()
        if row is None:
            return
        c = self.model.comments[row]
        confirm = QtWidgets.QMessageBox.question(
            self, "Delete Comment",
            f"Delete comment #{c['id']} by '{c['name']}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if confirm == QtWidgets.QMessageBox.Yes:
            self.model.remove_comment(row)
            self.status.setText(f"Comment #{c['id']} deleted")

class AdminWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comment Admin")
        self.setMinimumSize(800, 500)
        self.setCentralWidget(CommentAdminWidget())

def main():
    if not BASE or not KEY:
        print("Error: supabase_url and supabase_anon_key must be set in config.json")
        sys.exit(1)
    app = QtWidgets.QApplication(sys.argv)
    w = AdminWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

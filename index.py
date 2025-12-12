from tkinter import *
from tkinter import filedialog
import sqlite3
import tkinter.ttk as ttk
import tkinter.messagebox as tkMessageBox
import csv
from pathlib import Path

# ======================= DATABASE CONFIG ============================
# "sqlite"  -> local file DB
# "mysql"   -> MySQL / AWS RDS (MySQL engine)
DB_BACKEND = "sqlite"  # "sqlite" ya "mysql" me se ek choose karo

SQLITE_DB_NAME = "pythontut.db"

if DB_BACKEND == "mysql":
    try:
        import mysql.connector
    except ImportError:
        raise ImportError(
            "mysql-connector-python install karo: pip install mysql-connector-python"
        )

    MYSQL_CONFIG = {
        "host": "localhost",        # AWS RDS ho to yahan endpoint doge
        "user": "root",             # apna MySQL username
        "password": "password123",  # apna password
        "database": "contact_db",   # apna DB naam
    }


def get_connection():
    """DB backend ke hisaab se connection return karega."""
    if DB_BACKEND == "sqlite":
        return sqlite3.connect(SQLITE_DB_NAME)
    elif DB_BACKEND == "mysql":
        return mysql.connector.connect(**MYSQL_CONFIG)
    else:
        raise ValueError("Invalid DB_BACKEND value")


PLACEHOLDER = "?" if DB_BACKEND == "sqlite" else "%s"


class ContactApp:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Contact Management System")

        # Window size & position
        width = 820
        height = 480
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.config(bg="#0f172a")  # dark background

        # Tkinter variables
        self.FIRSTNAME = StringVar()
        self.LASTNAME = StringVar()
        self.GENDER = StringVar()
        self.AGE = StringVar()
        self.ADDRESS = StringVar()
        self.CONTACT = StringVar()
        self.SEARCH_TERM = StringVar()

        # Currently selected member id
        self.selected_mem_id = None

        # UI + DB
        self.create_widgets()
        self.init_db()
        self.load_contacts()

    # ============================ DATABASE ============================

    def init_db(self):
        """Create table if not exists."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS member (
                mem_id   INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
                firstname TEXT,
                lastname  TEXT,
                gender    TEXT,
                age       TEXT,
                address   TEXT,
                contact   TEXT
            )
            """
            if DB_BACKEND == "mysql"
            else """
            CREATE TABLE IF NOT EXISTS member (
                mem_id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                firstname TEXT,
                lastname  TEXT,
                gender    TEXT,
                age       TEXT,
                address   TEXT,
                contact   TEXT
            )
            """
        )
        conn.commit()
        cursor.close()
        conn.close()

    def load_contacts(self, search: str = ""):
        """Load contacts from DB into Treeview. Optional search."""
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        query = "SELECT mem_id, firstname, lastname, gender, age, address, contact FROM member"
        params = ()
        if search.strip():
            if DB_BACKEND == "sqlite":
                query += " WHERE firstname LIKE ? OR lastname LIKE ? OR contact LIKE ?"
            else:
                query += " WHERE firstname LIKE %s OR lastname LIKE %s OR contact LIKE %s"
            like = f"%{search.strip()}%"
            params = (like, like, like)

        query += " ORDER BY lastname ASC"

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        for data in rows:
            self.tree.insert("", "end", values=data)

        self.update_status_bar(len(rows), search)

    def insert_contact(self, firstname, lastname, gender, age, address, contact):
        conn = get_connection()
        cursor = conn.cursor()
        query = (
            f"INSERT INTO member (firstname, lastname, gender, age, address, contact) "
            f"VALUES ({PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER})"
        )
        cursor.execute(query, (firstname, lastname, gender, age, address, contact))
        conn.commit()
        cursor.close()
        conn.close()

    def update_contact(self, mem_id, firstname, lastname, gender, age, address, contact):
        conn = get_connection()
        cursor = conn.cursor()
        query = (
            f"UPDATE member SET firstname = {PLACEHOLDER}, lastname = {PLACEHOLDER}, "
            f"gender = {PLACEHOLDER}, age = {PLACEHOLDER}, address = {PLACEHOLDER}, contact = {PLACEHOLDER} "
            f"WHERE mem_id = {PLACEHOLDER}"
        )
        cursor.execute(
            query, (firstname, lastname, gender, age, address, contact, mem_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def delete_contact_from_db(self, mem_id):
        conn = get_connection()
        cursor = conn.cursor()
        query = f"DELETE FROM member WHERE mem_id = {PLACEHOLDER}"
        cursor.execute(query, (mem_id,))
        conn.commit()
        cursor.close()
        conn.close()

    # ============================ VALIDATION ============================

    def validate_contact_form(self):
        """Basic form validation. Returns (ok, message)."""
        if not self.FIRSTNAME.get().strip():
            return False, "Please enter Firstname."
        if not self.LASTNAME.get().strip():
            return False, "Please enter Lastname."
        if not self.GENDER.get().strip():
            return False, "Please select Gender."
        if not self.AGE.get().strip():
            return False, "Please enter Age."
        if not self.AGE.get().isdigit():
            return False, "Age must be a number."
        if int(self.AGE.get()) <= 0:
            return False, "Age must be greater than 0."
        if not self.ADDRESS.get().strip():
            return False, "Please enter Address."
        if not self.CONTACT.get().strip():
            return False, "Please enter Contact number."
        if not self.CONTACT.get().isdigit():
            return False, "Contact must contain only digits."
        if len(self.CONTACT.get()) < 7:
            return False, "Contact number looks too short."
        return True, ""

    def clear_form(self):
        self.FIRSTNAME.set("")
        self.LASTNAME.set("")
        self.GENDER.set("")
        self.AGE.set("")
        self.ADDRESS.set("")
        self.CONTACT.set("")

    # ============================ STATUS BAR ============================

    def update_status_bar(self, count: int, search: str):
        if search.strip():
            msg = f"Showing {count} contact(s) for search: '{search.strip()}'"
        else:
            msg = f"Total contacts: {count}"
        self.status_label.config(text=msg)

    # ============================ UI SETUP ============================

    def create_widgets(self):
        # -------- Menu Bar --------
        menubar = Menu(self.root, bg="#020617", fg="white", tearoff=0)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Import from CSV", command=self.import_from_csv)
        file_menu.add_command(label="Export to CSV", command=self.export_to_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

        # Top title frame
        top = Frame(self.root, width=800, bd=0, bg="#020617")
        top.pack(side=TOP, fill=X)
        lbl_title = Label(
            top,
            text="📇 Contact Management System",
            font=("Segoe UI", 18, "bold"),
            bg="#020617",
            fg="#e5e7eb",
            pady=10,
        )
        lbl_title.pack(fill=X)

        # Middle frame: left buttons + search
        mid = Frame(self.root, width=800, bg="#0f172a")
        mid.pack(side=TOP, fill=X, padx=10, pady=5)

        # Left controls
        mid_left = Frame(mid, bg="#0f172a")
        mid_left.pack(side=LEFT, padx=5)

        btn_style = {
            "font": ("Segoe UI", 10, "bold"),
            "relief": RAISED,
            "bd": 1,
            "width": 14,
        }

        btn_add = Button(
            mid_left,
            text="+ Add New",
            bg="#22c55e",
            fg="black",
            activebackground="#16a34a",
            **btn_style,
            command=self.open_add_window,
        )
        btn_add.pack(pady=2)

        btn_edit = Button(
            mid_left,
            text="✏ Edit Selected",
            bg="#f97316",
            fg="black",
            activebackground="#ea580c",
            **btn_style,
            command=self.open_edit_window_from_selection,
        )
        btn_edit.pack(pady=2)

        btn_delete = Button(
            mid_left,
            text="🗑 Delete",
            bg="#ef4444",
            fg="black",
            activebackground="#b91c1c",
            **btn_style,
            command=self.delete_selected_contact,
        )
        btn_delete.pack(pady=2)

        btn_stats = Button(
            mid_left,
            text="📊 Stats",
            bg="#38bdf8",
            fg="black",
            activebackground="#0ea5e9",
            **btn_style,
            command=self.show_stats,
        )
        btn_stats.pack(pady=2)

        # Middle search area
        mid_center = Frame(mid, bg="#0f172a")
        mid_center.pack(side=LEFT, expand=True, fill=X, padx=20)

        lbl_search = Label(
            mid_center,
            text="Search (Name / Contact):",
            font=("Segoe UI", 10),
            bg="#0f172a",
            fg="#e5e7eb",
        )
        lbl_search.grid(row=0, column=0, sticky=W, pady=2)

        entry_search = Entry(
            mid_center,
            textvariable=self.SEARCH_TERM,
            width=30,
            font=("Segoe UI", 10),
            relief=FLAT,
        )
        entry_search.grid(row=0, column=1, pady=2, padx=5)
        entry_search.config(highlightbackground="#334155", highlightthickness=1)

        btn_search = Button(
            mid_center,
            text="Search",
            command=self.on_search,
            width=10,
            font=("Segoe UI", 9, "bold"),
        )
        btn_search.grid(row=0, column=2, padx=5)

        btn_clear_search = Button(
            mid_center,
            text="Clear",
            command=self.on_clear_search,
            width=10,
            font=("Segoe UI", 9, "bold"),
        )
        btn_clear_search.grid(row=0, column=3, padx=5)

        # Table frame
        table_margin = Frame(self.root, width=800, bg="#020617")
        table_margin.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#020617",
            foreground="#e5e7eb",
            fieldbackground="#020617",
            rowheight=24,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            background="#111827",
            foreground="#e5e7eb",
            font=("Segoe UI", 9, "bold"),
        )
        style.map("Treeview", background=[("selected", "#1d4ed8")])

        scrollbarx = Scrollbar(table_margin, orient=HORIZONTAL)
        scrollbary = Scrollbar(table_margin, orient=VERTICAL)

        self.tree = ttk.Treeview(
            table_margin,
            columns=(
                "MemberID",
                "Firstname",
                "Lastname",
                "Gender",
                "Age",
                "Address",
                "Contact",
            ),
            height=10,
            selectmode="browse",
            yscrollcommand=scrollbary.set,
            xscrollcommand=scrollbarx.set,
        )

        scrollbarx.config(command=self.tree.xview)
        scrollbary.config(command=self.tree.yview)
        scrollbarx.pack(side=BOTTOM, fill=X)
        scrollbary.pack(side=RIGHT, fill=Y)

        # Tree headings
        self.tree.heading("MemberID", text="ID", anchor=W)
        self.tree.heading("Firstname", text="Firstname", anchor=W)
        self.tree.heading("Lastname", text="Lastname", anchor=W)
        self.tree.heading("Gender", text="Gender", anchor=W)
        self.tree.heading("Age", text="Age", anchor=W)
        self.tree.heading("Address", text="Address", anchor=W)
        self.tree.heading("Contact", text="Contact", anchor=W)

        self.tree.column("#0", stretch=NO, minwidth=0, width=0)
        self.tree.column("MemberID", stretch=NO, minwidth=40, width=50)
        self.tree.column("Firstname", stretch=NO, minwidth=90, width=120)
        self.tree.column("Lastname", stretch=NO, minwidth=90, width=120)
        self.tree.column("Gender", stretch=NO, minwidth=60, width=80)
        self.tree.column("Age", stretch=NO, minwidth=40, width=60)
        self.tree.column("Address", stretch=NO, minwidth=140, width=200)
        self.tree.column("Contact", stretch=NO, minwidth=100, width=140)

        self.tree.pack(fill=BOTH, expand=True)
        self.tree.bind("<Double-Button-1>", self.on_tree_double_click)

        # Status bar
        status_frame = Frame(self.root, bd=1, relief=SUNKEN, bg="#020617")
        status_frame.pack(side=BOTTOM, fill=X)
        self.status_label = Label(
            status_frame,
            text="Ready",
            anchor=W,
            padx=5,
            font=("Segoe UI", 9),
            bg="#020617",
            fg="#9ca3af",
        )
        self.status_label.pack(fill=X)

    # ============================ SEARCH ============================

    def on_search(self):
        term = self.SEARCH_TERM.get()
        self.load_contacts(term)

    def on_clear_search(self):
        self.SEARCH_TERM.set("")
        self.load_contacts()

    # ============================ TREE EVENTS ============================

    def get_selected_row(self):
        """Return selected row values or None."""
        cur_item = self.tree.focus()
        if not cur_item:
            return None
        contents = self.tree.item(cur_item)
        selected = contents.get("values")
        return selected

    def on_tree_double_click(self, event):
        self.open_edit_window_from_selection()

    # ============================ WINDOWS ============================

    def open_add_window(self):
        self.clear_form()

        win = Toplevel(self.root)
        win.title("Add New Contact")
        win.resizable(False, False)

        width = 420
        height = 330
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2) - 260
        y = (screen_height // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")
        win.config(bg="#020617")

        self.build_form(win, mode="add")

    def open_edit_window_from_selection(self):
        row = self.get_selected_row()
        if not row:
            tkMessageBox.showwarning("Warning", "Please select a contact first.")
            return

        # row layout: (mem_id, firstname, lastname, gender, age, address, contact)
        self.selected_mem_id = row[0]
        self.FIRSTNAME.set(row[1])
        self.LASTNAME.set(row[2])
        self.GENDER.set(row[3])
        self.AGE.set(row[4])
        self.ADDRESS.set(row[5])
        self.CONTACT.set(row[6])

        win = Toplevel(self.root)
        win.title("Update Contact")
        win.resizable(False, False)

        width = 420
        height = 330
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2) + 260
        y = (screen_height // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")
        win.config(bg="#020617")

        self.build_form(win, mode="edit")

    def build_form(self, win: Toplevel, mode: str = "add"):
        """Build Add/Edit form in a Toplevel window."""
        title_text = "Adding New Contact" if mode == "add" else "Updating Contact"
        title_bg = "#22c55e" if mode == "add" else "#f97316"

        form_title = Frame(win, bg="#020617")
        form_title.pack(side=TOP, fill=X)
        lbl_title = Label(
            form_title,
            text=title_text,
            font=("Segoe UI", 14, "bold"),
            bg=title_bg,
            fg="#020617",
            width=300,
        )
        lbl_title.pack(fill=X)

        contact_form = Frame(win, bg="#020617")
        contact_form.pack(side=TOP, pady=10, padx=12)

        label_style = {"font": ("Segoe UI", 10), "bg": "#020617", "fg": "#e5e7eb"}

        # Labels
        Label(contact_form, text="Firstname", **label_style).grid(
            row=0, column=0, sticky=W, pady=3
        )
        Label(contact_form, text="Lastname", **label_style).grid(
            row=1, column=0, sticky=W, pady=3
        )
        Label(contact_form, text="Gender", **label_style).grid(
            row=2, column=0, sticky=W, pady=3
        )
        Label(contact_form, text="Age", **label_style).grid(
            row=3, column=0, sticky=W, pady=3
        )
        Label(contact_form, text="Address", **label_style).grid(
            row=4, column=0, sticky=W, pady=3
        )
        Label(contact_form, text="Contact", **label_style).grid(
            row=5, column=0, sticky=W, pady=3
        )

        entry_style = {"font": ("Segoe UI", 10), "relief": FLAT}
        def styled_entry(row, var):
            e = Entry(contact_form, textvariable=var, **entry_style)
            e.grid(row=row, column=1, pady=3, padx=5, sticky="we")
            e.config(highlightbackground="#334155", highlightthickness=1)
            return e

        styled_entry(0, self.FIRSTNAME)
        styled_entry(1, self.LASTNAME)

        radio_group = Frame(contact_form, bg="#020617")
        radio_group.grid(row=2, column=1, sticky=W, pady=3)
        Radiobutton(
            radio_group,
            text="Male",
            variable=self.GENDER,
            value="Male",
            font=("Segoe UI", 9),
            bg="#020617",
            fg="#e5e7eb",
            selectcolor="#020617",
            activebackground="#020617",
        ).pack(side=LEFT)
        Radiobutton(
            radio_group,
            text="Female",
            variable=self.GENDER,
            value="Female",
            font=("Segoe UI", 9),
            bg="#020617",
            fg="#e5e7eb",
            selectcolor="#020617",
            activebackground="#020617",
        ).pack(side=LEFT)

        styled_entry(3, self.AGE)
        styled_entry(4, self.ADDRESS)
        styled_entry(5, self.CONTACT)

        # Buttons
        btn_text = "Save" if mode == "add" else "Update"
        btn_cmd = (
            lambda: self.on_save(win)
            if mode == "add"
            else lambda: self.on_update(win)
        )

        btn_submit = Button(
            contact_form,
            text=btn_text,
            width=30,
            command=btn_cmd,
            font=("Segoe UI", 10, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            relief=RAISED,
            bd=1,
        )
        btn_submit.grid(row=6, columnspan=2, pady=12)

    # ============================ FORM ACTIONS ============================

    def on_save(self, win: Toplevel):
        ok, msg = self.validate_contact_form()
        if not ok:
            tkMessageBox.showwarning("Validation Error", msg)
            return

        self.insert_contact(
            self.FIRSTNAME.get().strip(),
            self.LASTNAME.get().strip(),
            self.GENDER.get().strip(),
            self.AGE.get().strip(),
            self.ADDRESS.get().strip(),
            self.CONTACT.get().strip(),
        )
        tkMessageBox.showinfo("Success", "Contact saved successfully.")
        self.clear_form()
        win.destroy()
        self.load_contacts()

    def on_update(self, win: Toplevel):
        if self.selected_mem_id is None:
            tkMessageBox.showwarning("Warning", "No contact selected to update.")
            return

        ok, msg = self.validate_contact_form()
        if not ok:
            tkMessageBox.showwarning("Validation Error", msg)
            return

        self.update_contact(
            self.selected_mem_id,
            self.FIRSTNAME.get().strip(),
            self.LASTNAME.get().strip(),
            self.GENDER.get().strip(),
            self.AGE.get().strip(),
            self.ADDRESS.get().strip(),
            self.CONTACT.get().strip(),
        )
        tkMessageBox.showinfo("Success", "Contact updated successfully.")
        self.clear_form()
        win.destroy()
        self.load_contacts()

    def delete_selected_contact(self):
        row = self.get_selected_row()
        if not row:
            tkMessageBox.showwarning("Warning", "Please select a contact first.")
            return

        mem_id = row[0]
        answer = tkMessageBox.askquestion(
            "Confirm Delete",
            "Are you sure you want to delete this record?",
            icon="warning",
        )
        if answer == "yes":
            self.delete_contact_from_db(mem_id)
            self.load_contacts()
            tkMessageBox.showinfo("Deleted", "Contact deleted successfully.")

    # ============================ CSV IMPORT / EXPORT ============================

    def export_to_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        if not path:
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT firstname, lastname, gender, age, address, contact FROM member ORDER BY lastname ASC"
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["firstname", "lastname", "gender", "age", "address", "contact"]
            )
            writer.writerows(rows)

        tkMessageBox.showinfo(
            "Export", f"Exported {len(rows)} contacts to:\n{path}"
        )

    def import_from_csv(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not path:
            return

        path_obj = Path(path)
        if not path_obj.exists():
            tkMessageBox.showerror("Error", "File not found.")
            return

        inserted = 0
        skipped = 0

        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                tkMessageBox.showerror("Error", "CSV file is empty or invalid.")
                return

            headers_lower = [h.lower() for h in reader.fieldnames]
            required = ["firstname", "lastname", "gender", "age", "address", "contact"]
            if not all(col in headers_lower for col in required):
                tkMessageBox.showerror(
                    "Error",
                    "CSV must contain columns: firstname, lastname, gender, age, address, contact",
                )
                return

            conn = get_connection()
            cursor = conn.cursor()
            query = (
                f"INSERT INTO member (firstname, lastname, gender, age, address, contact) "
                f"VALUES ({PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER})"
            )

            for row in reader:
                try:
                    def get_val(key):
                        for k in row.keys():
                            if k.lower() == key:
                                return row[k]
                        return ""

                    firstname = (get_val("firstname") or "").strip()
                    lastname = (get_val("lastname") or "").strip()
                    gender = (get_val("gender") or "").strip()
                    age = str(get_val("age") or "").strip()
                    address = (get_val("address") or "").strip()
                    contact = str(get_val("contact") or "").strip()

                    if not firstname or not lastname or not contact:
                        skipped += 1
                        continue

                    cursor.execute(
                        query, (firstname, lastname, gender, age, address, contact)
                    )
                    inserted += 1
                except Exception:
                    skipped += 1

            conn.commit()
            cursor.close()
            conn.close()

        self.load_contacts()
        tkMessageBox.showinfo(
            "Import",
            f"Imported {inserted} contacts.\nSkipped: {skipped}",
        )

    # ============================ STATS ============================

    def show_stats(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM member")
        total_row = cursor.fetchone()
        total = total_row[0] if total_row else 0

        cursor.execute("SELECT gender, COUNT(*) FROM member GROUP BY gender")
        gender_rows = cursor.fetchall()
        cursor.close()
        conn.close()

        gender_text = ""
        for g, c in gender_rows:
            label = g if g else "Unknown"
            gender_text += f"{label}: {c}\n"
        if not gender_text:
            gender_text = "No data"

        msg = f"Total contacts: {total}\n\nBy gender:\n{gender_text}"
        tkMessageBox.showinfo("Statistics", msg)


# ============================ MAIN ============================

if __name__ == "__main__":
    root = Tk()
    app = ContactApp(root)
    root.mainloop()

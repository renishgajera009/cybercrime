import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import mysql.connector
import csv
import pandas as pd
import os
import datetime
from PIL import Image, ImageTk
from fpdf import FPDF



def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='tbl_data'
    )

class CyberCrimeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cyber Crime Branch | AI-Assisted Entry System")
        self.root.iconbitmap("crime_icon.ico")
        self.root.geometry("1250x750")
        self.root.configure(bg="#0d1117")

        # --------- Menu bar --------- #
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        home_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Home", menu=home_menu)
        home_menu.add_command(label="Go to Home", command=self.show_homepage)

        import_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Import", menu=import_menu)
        import_menu.add_command(label="Import Data", command=self.load_import_screen)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="View Database", command=self.view_data)

        filter_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Filter", menu=filter_menu)
        filter_menu.add_command(label="Filter Data", command=self.filter_by_database)

        # --------- Container --------- #
        self.container = tk.Frame(self.root, bg="#0d1117")
        self.container.pack(fill="both", expand=True)

        self.df_loaded = None
        self.mapping_vars = {}
        self.submitted_rows = set()

        self.show_homepage()

    def show_homepage(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        # Main homepage frame with dark background
        home_frame = tk.Frame(self.container, bg="#1e1e2f")  # dark indigo/navy tone
        home_frame.pack(fill="both", expand=True)
        home_frame.pack_propagate(0)

        try:
            image_path = "crime_poster.png"
            image = Image.open(image_path)
            image = image.resize((500, 500))  # Resize to fit UI
            photo = ImageTk.PhotoImage(image)

            # Poster label with image
            self.poster_label = tk.Label(
                home_frame, image=photo, bg="#1e1e2f", bd=2, relief="solid"
            )
            self.poster_label.image = photo  # prevent garbage collection
            self.poster_label.pack(pady=30)

            # Main title label with color options
            title_label = tk.Label(
                home_frame,
                text=" AI-ASSISTED SURAT CITY CYBER CRIME SYSTEM ",
                font=("Helvetica", 18, "bold"),
                fg="#FFD700",       # golden yellow text
                bg="#1e1e2f",       # match background
                wraplength=700,
                justify="center"
            )
            title_label.pack(pady=10)

            # Optional subtitle
            subtitle = tk.Label(
                home_frame,
                text="Empowering Enforcement with AI Intelligence",
                font=("Arial", 14, "italic"),
                fg="#00CED1",       # dark turquoise
                bg="#1e1e2f"
            )
            subtitle.pack()

        except Exception as e:
            tk.Label(
                home_frame,
                text=f"Error loading poster: {e}",
                font=("Arial", 20),
                fg="red",
                bg="#1e1e2f"
            ).pack(expand=True)

    def load_import_screen(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        self.left_frame = tk.LabelFrame(self.container, text="Database Fields", font=("Arial", 12, "bold"), fg="white", bg="#161b22")
        self.left_frame.place(x=100, y=20, width=350, height=660)
        self.left_listbox = tk.Listbox(self.left_frame, font=("Arial", 15), bg="white", fg="black", justify="center")
        self.left_listbox.pack(fill="both", expand=True)
        self.load_database_fields()

        self.center_frame = tk.LabelFrame(self.container, text="Field Mapping Panel", font=("Arial", 12, "bold"), fg="white", bg="#161b22")
        self.center_frame.place(x=500, y=20, width=450, height=660)

        self.scroll_canvas = tk.Canvas(self.center_frame, bg="#161b22", highlightthickness=0)
        self.scroll_frame = tk.Frame(self.scroll_canvas, bg="#161b22")
        self.scrollbar = ttk.Scrollbar(self.center_frame, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))

        self.right_frame = tk.LabelFrame(self.container, text="Actions", font=("Arial", 12, "bold"), fg="white", bg="#161b22")
        self.right_frame.place(x=1000, y=20, width=410, height=660)

        tk.Button(self.right_frame, text="Choose File", font=("Arial", 12), command=self.choose_file, bg="#00ADB5", fg="white").pack(pady=20, ipadx=10, ipady=5)
        tk.Button(self.right_frame, text="Submit to Database", font=("Arial", 12), command=self.submit_data, bg="#F94C66", fg="white").pack(pady=10, ipadx=10, ipady=5)

        self.progress = ttk.Progressbar(self.right_frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(pady=20)

        self.status = tk.Label(self.container, text="", fg="lime", bg="#0d1117", font=("Arial", 10))
        self.status.place(x=20, y=690)

    def load_database_fields(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DESCRIBE data_entry")
            columns = cursor.fetchall()
            self.left_listbox.delete(0, tk.END)
            self.db_fields = []
            for col in columns:
                if col[0].lower() != "data_id":
                    self.left_listbox.insert(tk.END, col[0])
                    self.db_fields.append(col[0])
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def choose_file(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Excel files", "*.xlsx *.xls"),
            ("CSV files", "*.csv")
        ])
        if not file_path:
            return

        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, dtype=str)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path, engine='openpyxl', dtype=str, header=0)
            elif file_path.endswith('.xls'):
                df = pd.read_excel(file_path, engine='xlrd', dtype=str, header=0)
            else:
                raise ValueError("Unsupported file type.")

            df.fillna('', inplace=True)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
            df = df.loc[:, df.columns.str.lower() != 'data_id']  # ✅ Remove data_id from file

            self.df_loaded = df.copy()
            self.mapping_vars.clear()

            for widget in self.scroll_frame.winfo_children():
                widget.destroy()

            tk.Label(self.scroll_frame, text=f"File Loaded: {os.path.basename(file_path)}", bg="#161b22", fg="white", font=("Arial", 12)).pack(pady=10)
            tk.Label(self.scroll_frame, text="--- Compulsory Fields ---", bg="#161b22", fg="red", font=("Arial", 11, "bold")).pack()

            compulsory_fields = ["Name", "Mobile", "Email_ID", "Unique_ID", "Type"]
            optional_fields = [f for f in self.db_fields if f not in compulsory_fields]

            for db_field in compulsory_fields:
                frame = tk.Frame(self.scroll_frame, bg="#161b22")
                frame.pack(pady=3, fill="x", padx=10)
                tk.Label(frame, text=db_field, bg="#161b22", fg="white", width=20, anchor="w").pack(side="left")

                var = tk.StringVar()
                if db_field.lower() == "type":  # ✅ Manually enter Type
                    entry = tk.Entry(frame, textvariable=var, width=30)
                    entry.pack(side="left", padx=5)
                else:
                    dropdown = ttk.Combobox(frame, textvariable=var, values=self.df_loaded.columns.tolist(), width=30, state="readonly")
                    dropdown.pack(side="left", padx=5)
                self.mapping_vars[db_field] = var

            ttk.Separator(self.scroll_frame, orient='horizontal').pack(fill='x', pady=10)
            tk.Label(self.scroll_frame, text="--- Optional Fields ---", bg="#161b22", fg="lightgreen", font=("Arial", 11, "bold")).pack()

            for db_field in optional_fields:
                frame = tk.Frame(self.scroll_frame, bg="#161b22")
                frame.pack(pady=3, fill="x", padx=10)
                tk.Label(frame, text=db_field, bg="#161b22", fg="white", width=20, anchor="w").pack(side="left")

                var = tk.StringVar()
                dropdown = ttk.Combobox(frame, textvariable=var, values=self.df_loaded.columns.tolist(), width=30, state="readonly")
                dropdown.pack(side="left", padx=5)
                self.mapping_vars[db_field] = var

            self.status.config(text=f"{os.path.basename(file_path)} loaded. Map DB to Excel fields and submit.", fg="yellow")

        except Exception as e:
            messagebox.showerror("File Error", str(e))

    def submit_data(self):
        if self.df_loaded is None or not self.mapping_vars:
            messagebox.showwarning("Missing Data", "Please load a file and map fields.")
            return

        compulsory_fields = ["Name", "Mobile", "Email_ID", "Unique_ID", "Type"]
        mapped = {db_field: var.get().strip() for db_field, var in self.mapping_vars.items() if var.get().strip()}
        mapped_keys = list(mapped.keys())

        # ✅ Ensure compulsory fields are present
        missing = [field for field in compulsory_fields if field not in mapped_keys]
        if missing:
            messagebox.showerror("Mapping Error", f"Missing compulsory fields: {', '.join(missing)}")
            return

        if len(mapped_keys) < 5:
            messagebox.showerror("Field Error", "Minimum 5 fields must be mapped.")
            return

        headers = list(mapped.keys())

        try:
            conn = get_connection()
            cursor = conn.cursor()
            total = len(self.df_loaded)
            inserted_count = 0

            for idx, (_, row) in enumerate(self.df_loaded.iterrows()):
                values = []
                row_key = []

                for field in headers:
                    if field.lower() == "type":
                        value = mapped[field]  # Direct input from Entry box
                    else:
                        col_name = mapped[field]
                        if col_name not in row:
                            raise ValueError(f"Column '{col_name}' not found in file.")
                        value = row[col_name]
                    values.append(value)
                    row_key.append(value)

                row_key = tuple(row_key)

                if row_key in self.submitted_rows:
                    continue

                placeholders = ','.join(['%s'] * len(values))
                query = f"INSERT INTO data_entry ({','.join(headers)}) VALUES ({placeholders})"

                try:
                    cursor.execute(query, values)
                    inserted_count += 1
                    self.submitted_rows.add(row_key)
                except Exception as e:
                    print("Row Error:", e)
                    continue

                self.progress['value'] = ((idx + 1) / total) * 100
                self.root.update_idletasks()

            conn.commit()
            cursor.close()
            conn.close()

            # ✅ Backup log file
            now = datetime.datetime.now().strftime("%Y%m%d")
            os.makedirs("logs", exist_ok=True)
            with open(f"logs/backup_{now}.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for _, row in self.df_loaded.iterrows():
                    row_values = []
                    for field in headers:
                        if field.lower() == "type":
                            row_values.append(mapped[field])
                        else:
                            row_values.append(row[mapped[field]])
                    writer.writerow(row_values)

            messagebox.showinfo("Success", f"Records Inserted Succesfully .")
            self.status.config(text=f"{inserted_count} inserted.", fg="lime")
            self.progress['value'] = 0

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def view_data(self):
        try:
            from fpdf import FPDF
            import os
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM data_entry")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            # ✅ Remove 'data_id' column
            if "data_id" in columns:
                idx = columns.index("data_id")
                columns.pop(idx)
                rows = [list(row[:idx] + row[idx + 1:]) for row in rows]

            view_window = tk.Toplevel(self.root)
            view_window.title("View All Data")
            view_window.geometry("1100x650")
            view_window.configure(bg="white")

            # 🔍 Search bar with placeholder
            search_var = tk.StringVar()
            search_entry = tk.Entry(view_window, textvariable=search_var, font=("Arial", 12), fg='grey')
            search_entry.insert(0, "Search here...")
            search_entry.pack(pady=10, padx=10, anchor="nw", fill="x")

            def on_entry_click(event):
                if search_entry.get() == "Search here...":
                    search_entry.delete(0, "end")
                    search_entry.config(fg="black")

            def on_focusout(event):
                if not search_entry.get():
                    search_entry.insert(0, "Search here...")
                    search_entry.config(fg="grey")

            search_entry.bind("<FocusIn>", on_entry_click)
            search_entry.bind("<FocusOut>", on_focusout)

            frame = tk.Frame(view_window)
            frame.pack(fill="both", expand=True, padx=10, pady=10)

            x_scroll = tk.Scrollbar(frame, orient='horizontal')
            y_scroll = tk.Scrollbar(frame, orient='vertical')

            tree = ttk.Treeview(
                frame,
                columns=columns,
                show="headings",
                xscrollcommand=x_scroll.set,
                yscrollcommand=y_scroll.set
            )

            x_scroll.config(command=tree.xview)
            y_scroll.config(command=tree.yview)
            x_scroll.pack(side='bottom', fill='x')
            y_scroll.pack(side='right', fill='y')

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor='center', width=150)

            for row in rows:
                tree.insert('', 'end', values=row)

            tree.pack(fill="both", expand=True)

            # ✅ Show data in messagebox on row double-click
            def on_row_double_click(event):
                selected = tree.focus()
                if selected:
                    values = tree.item(selected, 'values')
                    details = "\n".join([f"{columns[i]}: {values[i]}" for i in range(len(columns))])
                    messagebox.showinfo("Selected Record", f"{details}", icon='info')

            tree.bind("<Double-1>", on_row_double_click)

            # 🔍 Live filtering
            def filter_data(*args):
                query = search_var.get().lower()
                if query == "search here...":
                    return
                tree.delete(*tree.get_children())
                for row in rows:
                    if any(query in str(cell).lower() for cell in row):
                        tree.insert('', 'end', values=row)

            search_var.trace_add("write", filter_data)

            # 📤 Export to PDF (automatic save)

            def export_to_pdf():
                from fpdf import FPDF
                import os
                import datetime

                class PDF(FPDF):
                    def header(self):
                        self.set_font("Arial", 'B', 12)
                        self.cell(0, 10, "Cyber Crime Branch - Detailed Records", ln=True, align='C')
                        self.ln(3)

                pdf = PDF(format='A4')
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                pdf.set_font("Arial", '', 10)

                # Get visible headers and row data
                headers = [tree.heading(col)['text'] for col in tree["columns"]]
                data_rows = [tree.item(item, 'values') for item in tree.get_children()]

                row_height = 7
                label_width = 50
                value_width = 130
                line_spacing = 1.5

                for row_num, row in enumerate(data_rows, start=1):
                    pdf.set_font("Arial", 'B', 11)
                    pdf.cell(0, 8, f"Record {row_num}", ln=True, align='L')
                    pdf.set_font("Arial", '', 10)
                    pdf.ln(1)

                    for i in range(len(headers)):
                        pdf.set_font("Arial", 'B', 10)
                        pdf.cell(label_width, row_height, f"{headers[i]}:", border=0)
                        pdf.set_font("Arial", '', 10)
                        value = str(row[i])
                        pdf.multi_cell(value_width, row_height, value, border=0)
                    pdf.ln(4)
                    pdf.cell(0, 0, "-" * 120, ln=True)  # separator line
                    pdf.ln(3)

                # Save file automatically
                folder = "ExportedPDFs"
                os.makedirs(folder, exist_ok=True)
                filename = f"cyber_crime_vertical_view_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                path = os.path.join(folder, filename)
                pdf.output(path)

                messagebox.showinfo("Export Complete", f"Data exported successfully:\n{path}")

            # 📤 Export to PDF button
            export_btn = tk.Button(view_window, text="Export to PDF", command=export_to_pdf,
                                bg="#007acc", fg="white", font=("Arial", 11, "bold"))
            export_btn.pack(pady=10)

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("View Error", str(e))

    def filter_by_database(self):
        def search_from_database():
            keyword = entry.get().strip().lower()
            if not keyword or keyword == "search here...":
                messagebox.showwarning("Input Needed", "Please enter a keyword to search.")
                return

            try:
                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute("SHOW COLUMNS FROM data_entry")
                all_columns = [col[0] for col in cursor.fetchall()]
                if 'data_id' in all_columns:
                    all_columns.remove('data_id')

                columns_str = ", ".join(all_columns)
                query = f"""
                    SELECT {columns_str} FROM data_entry
                    WHERE LOWER(CONCAT_WS(' ', {columns_str})) LIKE %s
                """
                cursor.execute(query, ('%' + keyword + '%',))
                rows = cursor.fetchall()

                for item in tree.get_children():
                    tree.delete(item)

                if not rows:
                    messagebox.showinfo("No Results", "No records found matching your search.")
                    return

                for row in rows:
                    tree.insert('', 'end', values=row)

                cursor.close()
                conn.close()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        def on_row_double_click(event):
            selected_item = tree.selection()
            if selected_item:
                values = tree.item(selected_item, 'values')
                if values:
                    popup = tk.Toplevel(win)
                    popup.title("Detailed View")
                    popup.geometry("500x400")
                    frame = tk.Frame(popup)
                    frame.pack(expand=True, fill='both', padx=10, pady=10)

                    scroll = tk.Scrollbar(frame)
                    scroll.pack(side='right', fill='y')

                    text = tk.Text(frame, yscrollcommand=scroll.set, wrap='word')
                    text.pack(expand=True, fill='both')
                    scroll.config(command=text.yview)

                    bold_font = ("Arial", 11, "bold")
                    normal_font = ("Arial", 11)

                    for col, val in zip(tree["columns"], values):
                        text.insert(tk.END, f"{col}: ", ("bold",))
                        text.insert(tk.END, f"{val}\n\n", ("normal",))
                    text.tag_configure("bold", font=bold_font)
                    text.tag_configure("normal", font=normal_font)
                    text.config(state='disabled')

        def on_entry_focus_in(event):
            if entry.get() == "Search here...":
                entry.delete(0, tk.END)
                entry.config(fg="black")

        def on_entry_focus_out(event):
            if entry.get().strip() == "":
                entry.insert(0, "Search here...")
                entry.config(fg="gray")

        win = tk.Toplevel(self.root)
        win.title("Database Filter")
        win.geometry("1000x600")
        win.grab_set()

        tk.Label(win, text="Enter keyword:", font=("Arial", 12)).pack(pady=10)
        entry = tk.Entry(win, font=("Arial", 12), width=60, fg="gray")
        entry.insert(0, "Search here...")
        entry.pack(pady=5)
        entry.bind("<FocusIn>", on_entry_focus_in)
        entry.bind("<FocusOut>", on_entry_focus_out)
        entry.bind("<Return>", lambda e: search_from_database())

        tk.Button(win, text="Search Now", font=("Arial", 12), command=search_from_database).pack(pady=10)

        frame = tk.Frame(win)
        frame.pack(expand=True, fill='both')

        x_scroll = tk.Scrollbar(frame, orient='horizontal')
        y_scroll = tk.Scrollbar(frame, orient='vertical')
        tree = ttk.Treeview(frame, xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
        tree.pack(expand=True, fill='both')
        x_scroll.pack(side='bottom', fill='x')
        y_scroll.pack(side='right', fill='y')
        x_scroll.config(command=tree.xview)
        y_scroll.config(command=tree.yview)

        tree.bind("<Double-1>", on_row_double_click)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SHOW COLUMNS FROM data_entry")
            columns = [col[0] for col in cursor.fetchall()]
            if 'data_id' in columns:
                columns.remove('data_id')

            tree["columns"] = columns
            tree["show"] = "headings"
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor='center')

            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap("crime_icon.ico")
    app = CyberCrimeGUI(root)
    root.mainloop()

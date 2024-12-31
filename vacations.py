import customtkinter as ctk
import sqlite3
from tkinter import messagebox
from tkinter import *
import fpdf
from tkcalendar import Calendar
from tkinter import Toplevel
from tkinter import filedialog
import os


# Initialize the database
conn = sqlite3.connect('vacation_request.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY,
                name TEXT,
                department TEXT,
                vacation_days INTEGER,
                status TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY,
                worker_id INTEGER,
                days_requested INTEGER,
                start_date TEXT,
                end_date TEXT,
                status TEXT,
                FOREIGN KEY (worker_id) REFERENCES workers (id))''')

conn.commit()

class VacationRequestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vacation Request")
        self.root.geometry("1280x420")

        # Admin Login
        self.admin_login()

    def admin_login(self):
        self.login_frame = ctk.CTkFrame(self.root)
        self.login_frame.pack(pady=20)

        self.username_label = ctk.CTkLabel(self.login_frame, text="Username:")
        self.username_label.grid(row=0, column=0, padx=10, pady=10)
        self.username_entry = ctk.CTkEntry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.password_label = ctk.CTkLabel(self.login_frame, text="Password:")
        self.password_label.grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.password_entry.bind("<Return>", lambda event: self.check_login())

        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.check_login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # For simplicity, using hardcoded admin credentials
        if username == "admin" and password == "admin":
            self.login_frame.pack_forget()
            self.main_screen()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def main_screen(self):
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.workers_button = ctk.CTkButton(self.main_frame, text="Workers List", command=self.show_workers)
        self.workers_button.grid(row=0, column=0, padx=20, pady=20)

        self.requests_button = ctk.CTkButton(self.main_frame, text="Vacation Request", command=self.show_requests)
        self.requests_button.grid(row=1, column=0, padx=20, pady=20)

        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.grid(row=0, column=1, rowspan=2, padx=20, pady=20)

    def show_workers(self):
        self.workers_button.configure(fg_color="green")
        self.requests_button.configure(fg_color="blue")
        self.clear_content_frame()

        self.add_worker_button = ctk.CTkButton(self.content_frame, text="Add Worker", command=self.add_worker)
        self.add_worker_button.grid(row=0, column=0, padx=10, pady=10)

        self.workers_list = ctk.CTkFrame(self.content_frame)
        self.workers_list.grid(row=1, column=0, padx=10, pady=10)

        c.execute("SELECT * FROM workers")
        workers = c.fetchall()

        headers = ["ID", "Name", "Department", "Vacation Days", "Status", "Actions"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.workers_list, text=header)
            label.grid(row=0, column=i, padx=5, pady=5)

        for i, worker in enumerate(workers):
            for j, value in enumerate(worker):
                label = ctk.CTkLabel(self.workers_list, text=value)
                label.grid(row=i + 1, column=j, padx=5, pady=5)

            edit_button = ctk.CTkButton(self.workers_list, text="Edit", command=lambda w=worker: self.edit_worker(w))
            edit_button.grid(row=i + 1, column=len(worker), padx=5, pady=5)
            delete_button = ctk.CTkButton(self.workers_list, text="Delete", command=lambda w=worker[0]: self.delete_worker(w))
            delete_button.grid(row=i + 1, column=len(worker) + 1, padx=5, pady=5)

    def show_requests(self):
        self.workers_button.configure(fg_color="blue")
        self.requests_button.configure(fg_color="green")
        self.clear_content_frame()

        # Add Request Button
        self.add_request_button = ctk.CTkButton(self.content_frame, text="Add Request", command=self.add_request)
        self.add_request_button.grid(row=0, column=0, padx=10, pady=10)

        # Requests List Frame
        self.requests_list = ctk.CTkFrame(self.content_frame)
        self.requests_list.grid(row=1, column=0, padx=10, pady=10)

        # Query all vacation requests
        c.execute('''SELECT r.id, w.name, w.department, w.vacation_days, r.days_requested, r.start_date, r.end_date, r.status
                    FROM requests r JOIN workers w ON r.worker_id = w.id''')
        requests = c.fetchall()

        # Table Headers
        headers = ["ID", "Name", "Department", "Vacation Days", "Days Requested", "Start Date", "End Date", "Status", "Actions"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self.requests_list, text=header)
            label.grid(row=0, column=i, padx=5, pady=5)

        # Render Each Request with Independent Buttons
        for i, request in enumerate(requests):
            for j, value in enumerate(request):
                label = ctk.CTkLabel(self.requests_list, text=value)
                label.grid(row=i + 1, column=j, padx=5, pady=5)

            # Edit Button
            edit_button = ctk.CTkButton(
                self.requests_list,
                text="Edit",
                command=lambda r=request: self.edit_request(r)  # Link to this specific request
            )
            edit_button.grid(row=i + 1, column=len(request), padx=5, pady=5)

            # Delete Button
            delete_button = ctk.CTkButton(
                self.requests_list,
                text="Delete",
                command=lambda r=request[0]: self.delete_request(r)  # Link to this specific request ID
            )
            delete_button.grid(row=i + 1, column=len(request) + 1, padx=5, pady=5)

            # Add "Print Request" Button at the Bottom
        self.print_button = ctk.CTkButton(self.content_frame, text="Print Request", command=self.print_request)
        self.print_button.grid(row=2, column=0, columnspan=2, pady=20)

    def edit_request(self, request):
            # Open a new edit window
            self.edit_window = ctk.CTkToplevel(self.root)
            self.edit_window.title("Edit Request")

            request_id = request[0]
            worker_name = request[1]
            days_requested = request[4]
            start_date = request[5]
            end_date = request[6]
            status = request[7]

            # Fields for editing
            self.edit_days_label = ctk.CTkLabel(self.edit_window, text="Days Requested:")
            self.edit_days_label.grid(row=0, column=0, padx=10, pady=10)
            self.edit_days_entry = ctk.CTkEntry(self.edit_window)
            self.edit_days_entry.insert(0, str(days_requested))
            self.edit_days_entry.grid(row=0, column=1, padx=10, pady=10)

            self.edit_start_date_label = ctk.CTkLabel(self.edit_window, text="Start Date:")
            self.edit_start_date_label.grid(row=1, column=0, padx=10, pady=10)
            self.edit_start_date_entry = ctk.CTkEntry(self.edit_window)
            self.edit_start_date_entry.insert(0, start_date)
            self.edit_start_date_entry.grid(row=1, column=1, padx=10, pady=10)

            self.edit_end_date_label = ctk.CTkLabel(self.edit_window, text="End Date:")
            self.edit_end_date_label.grid(row=2, column=0, padx=10, pady=10)
            self.edit_end_date_entry = ctk.CTkEntry(self.edit_window)
            self.edit_end_date_entry.insert(0, end_date)
            self.edit_end_date_entry.grid(row=2, column=1, padx=10, pady=10)

            self.edit_status_label = ctk.CTkLabel(self.edit_window, text="Status:")
            self.edit_status_label.grid(row=3, column=0, padx=10, pady=10)
            self.edit_status_menu = ctk.CTkOptionMenu(self.edit_window, values=["In Work", "Not in Work"])
            self.edit_status_menu.set(status)
            self.edit_status_menu.grid(row=3, column=1, padx=10, pady=10)

            # Save Button
            self.save_edit_button = ctk.CTkButton(
                self.edit_window,
                text="Save",
                command=lambda: self.confirm_edit(request_id)
            )
            self.save_edit_button.grid(row=4, column=0, columnspan=2, pady=10)

    def confirm_edit(self, request_id):
        """Show a confirmation box before saving edits."""
        confirm = messagebox.askyesno("Confirm Edit", "Do you want to save changes?")
        if confirm:
            # Save edits to the database
            days_requested = int(self.edit_days_entry.get())
            start_date = self.edit_start_date_entry.get()
            end_date = self.edit_end_date_entry.get()
            status = self.edit_status_menu.get()

            c.execute(
                "UPDATE requests SET days_requested=?, start_date=?, end_date=?, status=? WHERE id=?",
                (days_requested, start_date, end_date, status, request_id)
            )
            conn.commit()
            self.edit_window.destroy()
            self.show_requests()

    def delete_request(self, request_id):
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this request?")
        if confirm:
            c.execute("DELETE FROM requests WHERE id=?", (request_id,))
            conn.commit()
            self.show_requests()



    def add_worker(self):
        self.worker_window = ctk.CTkToplevel(self.root)
        self.worker_window.title("Add Worker")

        self.name_label = ctk.CTkLabel(self.worker_window, text="Name:")
        self.name_label.grid(row=0, column=0, padx=10, pady=10)
        self.name_entry = ctk.CTkEntry(self.worker_window)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        self.dept_label = ctk.CTkLabel(self.worker_window, text="Department:")
        self.dept_label.grid(row=1, column=0, padx=10, pady=10)
        self.dept_entry = ctk.CTkEntry(self.worker_window)
        self.dept_entry.grid(row=1, column=1, padx=10, pady=10)

        self.days_label = ctk.CTkLabel(self.worker_window, text="Vacation Days:")
        self.days_label.grid(row=2, column=0, padx=10, pady=10)
        self.days_entry = ctk.CTkEntry(self.worker_window)
        self.days_entry.grid(row=2, column=1, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(self.worker_window, text="Status:")
        self.status_label.grid(row=3, column=0, padx=10, pady=10)
        self.status_menu = ctk.CTkOptionMenu(self.worker_window, values=["In Work", "Not in Work"])
        self.status_menu.grid(row=3, column=1, padx=10, pady=10)

        self.save_button = ctk.CTkButton(self.worker_window, text="Save", command=self.save_worker)
        self.save_button.grid(row=4, column=0, columnspan=2, pady=10)

    def save_worker(self):
        name = self.name_entry.get()
        dept = self.dept_entry.get()
        days = int(self.days_entry.get())
        status = self.status_menu.get()

        c.execute("INSERT INTO workers (name, department, vacation_days, status) VALUES (?, ?, ?, ?)",
                  (name, dept, days, status))
        conn.commit()

        self.worker_window.destroy()
        self.show_workers()

    def edit_worker(self, worker):
        self.worker_window = ctk.CTkToplevel(self.root)
        self.worker_window.title("Edit Worker")

        self.name_label = ctk.CTkLabel(self.worker_window, text="Name:")
        self.name_label.grid(row=0, column=0, padx=10, pady=10)
        self.name_entry = ctk.CTkEntry(self.worker_window)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)
        self.name_entry.insert(0, worker[1])

        self.dept_label = ctk.CTkLabel(self.worker_window, text="Department:")
        self.dept_label.grid(row=1, column=0, padx=10, pady=10)
        self.dept_entry = ctk.CTkEntry(self.worker_window)
        self.dept_entry.grid(row=1, column=1, padx=10, pady=10)
        self.dept_entry.insert(0, worker[2])

        self.days_label = ctk.CTkLabel(self.worker_window, text="Vacation Days:")
        self.days_label.grid(row=2, column=0, padx=10, pady=10)
        self.days_entry = ctk.CTkEntry(self.worker_window)
        self.days_entry.grid(row=2, column=1, padx=10, pady=10)
        self.days_entry.insert(0, worker[3])

        self.status_label = ctk.CTkLabel(self.worker_window, text="Status:")
        self.status_label.grid(row=3, column=0, padx=10, pady=10)
        self.status_menu = ctk.CTkOptionMenu(self.worker_window, values=["In Work", "Not in Work"])
        self.status_menu.grid(row=3, column=1, padx=10, pady=10)
        self.status_menu.set(worker[4])

        self.save_button = ctk.CTkButton(self.worker_window, text="Save", command=lambda: self.update_worker(worker[0]))
        self.save_button.grid(row=4, column=0, columnspan=2, pady=10)

    def update_worker(self, worker_id):
        name = self.name_entry.get()
        dept = self.dept_entry.get()
        days = int(self.days_entry.get())
        status = self.status_menu.get()

        c.execute("UPDATE workers SET name=?, department=?, vacation_days=?, status=? WHERE id=?",
                  (name, dept, days, status, worker_id))
        conn.commit()

        self.worker_window.destroy()
        self.show_workers()

    def delete_worker(self, worker_id):

        # Delete associated requests first
        c.execute("DELETE FROM requests WHERE worker_id=?", (worker_id,))
        conn.commit()

        # Then delete the worker
        c.execute("DELETE FROM workers WHERE id=?", (worker_id,))
        conn.commit()

        self.show_workers()

    def create_date_input(self, parent, row, column, label_text):
        """Creates a date entry with an optional calendar popup."""
        # Label
        date_label = ctk.CTkLabel(parent, text=label_text)
        date_label.grid(row=row, column=column, padx=10, pady=10)

        # Entry Widget
        date_entry = ctk.CTkEntry(parent)
        date_entry.grid(row=row, column=column + 1, padx=10, pady=10)

        # Add formatting logic
        def format_date(event):
            text = date_entry.get()
            # Format as dd/mm/yyyy
            if len(text) == 2 or len(text) == 5:
                date_entry.insert(len(text), "/")
            elif len(text) > 10:
                date_entry.delete(10, 'end')  # Ensure the date doesn't exceed 10 characters (dd/mm/yyyy)

        date_entry.bind("<KeyRelease>", format_date)  # Format date as the user types

        # Calendar Popup
        def open_calendar():
            calendar_window = Toplevel(self.request_window)
            calendar_window.title("Select Date")
            calendar = Calendar(calendar_window, selectmode='day', date_pattern='dd/mm/yyyy')  # Corrected pattern

            # Place Calendar
            calendar.pack(pady=10)

            # Function to set date from calendar
            def select_date():
                selected_date = calendar.get_date()  # Returns dd/mm/yyyy due to the pattern
                date_entry.delete(0, 'end')
                date_entry.insert(0, selected_date)  # Set the selected date in the entry
                calendar_window.destroy()

            # Select Button
            select_button = ctk.CTkButton(calendar_window, text="Select", command=select_date)
            select_button.pack(pady=10)

        # Calendar Icon Button
        calendar_button = ctk.CTkButton(parent, text="📅", command=open_calendar, width=30)
        calendar_button.grid(row=row, column=column + 2, padx=10, pady=10)

        return date_entry

    def add_request(self):
        self.request_window = ctk.CTkToplevel(self.root)
        self.request_window.title("Add Request")

        # Worker Selection Dropdown
        self.worker_id_label = ctk.CTkLabel(self.request_window, text="Select Worker:")
        self.worker_id_label.grid(row=0, column=0, padx=10, pady=10)
        
        # Fetch workers and display ID + Name
        c.execute("SELECT id, name FROM workers")
        workers = c.fetchall()
        worker_options = [f"{worker[0]} - {worker[1]}" for worker in workers]
        self.worker_menu = ctk.CTkOptionMenu(self.request_window, values=worker_options, command=self.autofill_worker_info)
        self.worker_menu.grid(row=0, column=1, padx=10, pady=10)

        # Worker Info Fields
        self.name_label = ctk.CTkLabel(self.request_window, text="Name:")
        self.name_label.grid(row=1, column=0, padx=10, pady=10)
        self.name_entry = ctk.CTkEntry(self.request_window)
        self.name_entry.grid(row=1, column=1, padx=10, pady=10)

        self.dept_label = ctk.CTkLabel(self.request_window, text="Department:")
        self.dept_label.grid(row=2, column=0, padx=10, pady=10)
        self.dept_entry = ctk.CTkEntry(self.request_window)
        self.dept_entry.grid(row=2, column=1, padx=10, pady=10)

        self.days_label = ctk.CTkLabel(self.request_window, text="Vacation Days:")
        self.days_label.grid(row=3, column=0, padx=10, pady=10)
        self.days_entry = ctk.CTkEntry(self.request_window)
        self.days_entry.grid(row=3, column=1, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(self.request_window, text="Status:")
        self.status_label.grid(row=4, column=0, padx=10, pady=10)
        self.status_menu = ctk.CTkOptionMenu(self.request_window, values=["In Work", "Not in Work"])
        self.status_menu.grid(row=4, column=1, padx=10, pady=10)

        # Request Details
        self.days_requested_label = ctk.CTkLabel(self.request_window, text="Days Requested:")
        self.days_requested_label.grid(row=5, column=0, padx=10, pady=10)
        self.days_requested_entry = ctk.CTkEntry(self.request_window)
        self.days_requested_entry.grid(row=5, column=1, padx=10, pady=10)
        
        # Start Date Calendar
        self.start_date_label = ctk.CTkLabel(self.request_window, text="Start Date:")
        self.start_date_label.grid(row=6, column=0, padx=10, pady=10)
        self.start_date_entry = self.create_date_input(self.request_window, 6, 0, "Start Date:")
        self.start_date_entry.grid(row=6, column=1, padx=10, pady=10)

        # End Date Calendar
        self.end_date_label = ctk.CTkLabel(self.request_window, text="End Date:")
        self.end_date_label.grid(row=7, column=0, padx=10, pady=10)
        self.end_date_entry = self.create_date_input(self.request_window, 7, 0, "End Date:")
        self.end_date_entry.grid(row=7, column=1, padx=10, pady=10)

        # Save Button
        self.save_button = ctk.CTkButton(self.request_window, text="Save", command=self.save_request)
        self.save_button.grid(row=8, column=0, columnspan=2, pady=10)

    def autofill_worker_info(self, selected_worker):
        # Extract worker ID from the selected option
        worker_id = int(selected_worker.split(" - ")[0])

        # Fetch worker details from the database
        c.execute("SELECT name, department, vacation_days, status FROM workers WHERE id=?", (worker_id,))
        worker = c.fetchone()

        if worker:
            self.name_entry.delete(0, END)
            self.name_entry.insert(0, worker[0])

            self.dept_entry.delete(0, END)
            self.dept_entry.insert(0, worker[1])

            self.days_entry.delete(0, END)
            self.days_entry.insert(0, worker[2])

            self.status_menu.set(worker[3])


    def save_request(self):

        worker_id = int(self.worker_menu.get().split(" - ")[0])

        name = self.name_entry.get()
        department = self.dept_entry.get()
        vacation_days = int(self.days_entry.get())
        status = self.status_menu.get()

        # Update worker profile
        c.execute("UPDATE workers SET name=?, department=?, vacation_days=?, status=? WHERE id=?",
        (name, department, vacation_days, status, worker_id))


        # Save the vacation request
        days_requested = int(self.days_requested_entry.get())
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        c.execute("INSERT INTO requests (worker_id, days_requested, start_date, end_date, status) VALUES (?, ?, ?, ?, ?)",
                  (worker_id, days_requested, start_date, end_date, status))
        conn.commit()

        self.request_window.destroy()
        self.show_requests()

    def print_request(self):
        # Fetch requests from the database
        c.execute('''SELECT r.id, w.name, w.department, w.vacation_days, r.days_requested, r.start_date, r.end_date, r.status
                    FROM requests r JOIN workers w ON r.worker_id = w.id''')
        requests = c.fetchall()

        if not requests:
            messagebox.showwarning("Warning", "No requests to print.")
            return

        for request in requests:
            request_id = request[0]
            employee_name = request[1].replace(" ", "_")  # Replace spaces with underscores for filename
            default_filename = f"{employee_name}_Vacation.pdf"

            # Open Save Dialog
            save_path = filedialog.asksaveasfilename(
                initialfile=default_filename, 
                defaultextension=".pdf", 
                filetypes=[("PDF files", "*.pdf")],
                title="Save Vacation Request PDF"
            )

            if save_path:
                # Create the PDF
                pdf = fpdf.FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                # Title
                pdf.cell(200, 10, txt="Vacation Request Details", ln=True, align='C')

                # Request Details
                details = [
                    ("Request ID", request_id),
                    ("Employee Name", employee_name.replace("_", " ")),  # Show normal name
                    ("Department", request[2]),
                    ("Vacation Days", request[3]),
                    ("Days Requested", request[4]),
                    ("Start Date", request[5]),
                    ("End Date", request[6]),
                    ("Status", request[7]),
                ]

                for label, value in details:
                    pdf.cell(50, 10, txt=f"{label}: ", border=0)
                    pdf.cell(100, 10, txt=str(value), border=0, ln=True)

                # Add Signature Section
                pdf.ln(20)
                pdf.cell(200, 10, txt="____________________________", ln=True, align='C')
                pdf.cell(200, 10, txt="Director's Signature", ln=True, align='C')

                # Save the PDF to the chosen path
                try:
                    pdf.output(save_path)
                    messagebox.showinfo("Success", f"PDF saved as '{os.path.basename(save_path)}'")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save PDF: {e}")

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = VacationRequestApp(root)
    root.mainloop()

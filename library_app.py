import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import time

conn = sqlite3.connect('database.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS library (
            isbn TEXT PRIMARY KEY,
            bookname TEXT,
            bookyear INTEGER,
            author TEXT);''')
conn.commit()

window = tk.Tk()
window.title('Library Management')
window.geometry('550x400')

#Modern Theme
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", padding=6, font=("Segoe UI", 10, "bold"))
style.configure("TLabel", foreground="#1a1a1a", background="#f8f9fa", font=("Segoe UI", 10))
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
style.configure("Treeview", rowheight=25)
window.configure(bg="#f8f9fa")

E1V = tk.StringVar()
E2V = tk.StringVar()
E3V = tk.StringVar()
E4V = tk.StringVar()

def display_all():
    for item in table.get_children():
        table.delete(item)

    cur.execute('SELECT * FROM library;')
    booklist = cur.fetchall()
    for book in booklist:
        table.insert('', tk.END, values=book)

def clear_display():
    for item in table.get_children():
        table.delete(item)
    status_label.config(text="Display cleared")

def search():
    name = E1V.get()
    year = E2V.get()
    author = E3V.get()
    isbn = E4V.get()
    if name == '' and year == '' and author == '' and isbn == '':
        messagebox.showerror('Error', 'Please fill at least one field.')
    else:
        cur.execute('SELECT * FROM library WHERE isbn=? OR bookname=? OR bookyear=? OR author=?',
                    (isbn, name, year, author))
        res = cur.fetchall()

        for item in table.get_children():
            table.delete(item)

        if res:
            for row in res:
                table.insert('', tk.END, values=row)
        else:
            messagebox.showinfo('Result', 'No book found.')

        E1V.set('')
        E2V.set('')
        E3V.set('')
        E4V.set('')


def add():
    name = E1V.get()
    year = E2V.get()
    author = E3V.get()
    isbn = E4V.get()
    if name == '' or year == '' or author == '' or isbn == '':
        messagebox.showerror('Error', 'Please fill all required fields.')
    else:
        try:
            cur.execute('INSERT INTO library VALUES (?, ?, ?, ?);', (isbn, name, year, author))
            conn.commit()
            messagebox.showinfo('Success', 'Book added successfully.')
        except sqlite3.IntegrityError:
            messagebox.showerror('Error', 'A book with this ISBN already exists.')
        finally:
            E1V.set('')
            E2V.set('')
            E3V.set('')
            E4V.set('')

def update():
    isbn = E4V.get()
    name = E1V.get()
    year = E2V.get()
    author = E3V.get()
    if isbn == '':
        messagebox.showerror('Error', 'Please enter the ISBN of the book to update.')
        return
    cur.execute('UPDATE library SET bookname=?, bookyear=?, author=? WHERE isbn=?;',
                (name, year, author, isbn))
    conn.commit()
    display_all()
    clear_entries()
    messagebox.showinfo('Success', 'Book updated successfully!')

def delete():
    isbn = E4V.get()
    if isbn == '':
        messagebox.showerror('Error', 'Please enter an ISBN to delete.')
    else:
        cur.execute('SELECT * FROM library WHERE isbn = ?', (isbn,))
        res = cur.fetchone()
        if not res:
            messagebox.showerror('Error', 'No book found with this ISBN.')
        else:
            cur.execute('DELETE FROM library WHERE isbn = ?', (isbn,))
            conn.commit()
            messagebox.showinfo('Success', 'Book deleted successfully.')
    E1V.set('')
    E2V.set('')
    E3V.set('')
    E4V.set('')

def del_items(event=None):
    selection = table.selection()
    if not selection:
        messagebox.showerror('Error', 'Please select at least one book to delete.')
        return

    for item in selection:
        isbn = table.item(item, 'values')[0]
        cur.execute('DELETE FROM library WHERE isbn=?', (isbn,))
        table.delete(item)
    conn.commit()
    messagebox.showinfo('Success', 'Selected book(s) deleted successfully.')

def clear_fields():
    E1V.set('')
    E2V.set('')
    E3V.set('')
    E4V.set('')
    status_label.config(text="Fields cleared")

def save_as_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if file_path:
        with open(file_path, "w") as f:
            f.write(f"Title: {E1V.get()}\n")
            f.write(f"Year: {E2V.get()}\n")
            f.write(f"Author: {E3V.get()}\n")
            f.write(f"ISBN: {E4V.get()}\n")
        status_label.config(text="File saved successfully!")

def update_clock():
    current_time = time.strftime("%H:%M:%S")
    clock_label.config(text=current_time)
    window.after(1000, update_clock)

def export_csv():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return
    cur.execute('SELECT * FROM library')
    rows = cur.fetchall()
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ISBN', 'Book Name', 'Year', 'Author'])
        writer.writerows(rows)
    messagebox.showinfo('Success', 'Books exported successfully!')

def fill_fields(event):
    selected = table.selection()
    if selected:
        values = table.item(selected[0], 'values')
        E4V.set(values[0])
        E1V.set(values[1])
        E2V.set(values[2])
        E3V.set(values[3])

def clear_entries():
    E1V.set('')
    E2V.set('')
    E3V.set('')
    E4V.set('')

def close():
    window.destroy()

# ---------- UI Layout ----------

ttk.Label(window, text='Title').place(x=20, y=20)
ttk.Label(window, text='Year').place(x=20, y=45)
ttk.Label(window, text='Author').place(x=280, y=20)
ttk.Label(window, text='ISBN').place(x=280, y=45)

ttk.Entry(window, textvariable=E1V).place(x=80, y=20)
ttk.Entry(window, textvariable=E2V).place(x=80, y=45)
ttk.Entry(window, textvariable=E3V).place(x=340, y=20)
ttk.Entry(window, textvariable=E4V).place(x=340, y=45)

table = ttk.Treeview(window, columns=('isbn', 'name', 'year', 'author'), show='headings')
table.heading('isbn', text='ISBN')
table.heading('name', text='Book Name')
table.heading('year', text='Year')
table.heading('author', text='Author')
table.column('isbn', width=60)
table.column('name', width=120)
table.column('year', width=60)
table.column('author', width=120)
table.place(x=20, y=80, width=350, height=220)
table.bind("<<TreeviewSelect>>", fill_fields)
table.bind('<Delete>', del_items)

# Scrollbar
scrollbar = ttk.Scrollbar(window, orient="vertical", command=table.yview)
table.configure(yscrollcommand=scrollbar.set)
scrollbar.place(x=370, y=80, height=220)

button_frame = ttk.Frame(window)
button_frame.pack(side="bottom", pady=10)

status_label = tk.Label(window, text="Ready", anchor="w", relief="sunken", bd=1, bg="#e9ecef")
status_label.pack(side="bottom", fill="x")

clock_label = tk.Label(window, text="", anchor="e", bg="#e9ecef")
clock_label.pack(side="bottom", fill="x")

# Buttons
ttk.Button(window, text='Show All', command=display_all).place(x=410, y=80, width=110)
ttk.Button(window, text='Clear Display', command=clear_display).place(x=410, y=110, width=110)
ttk.Button(window, text='Search', command=search).place(x=410, y=140, width=110)
ttk.Button(window, text='Add', command=add).place(x=410, y=170, width=110)
ttk.Button(window, text='Update', command=update).place(x=410, y=200, width=110)
ttk.Button(window, text='Delete', command=delete).place(x=410, y=230, width=110)
ttk.Button(window, text='Export CSV', command=export_csv).place(x=410, y=260, width=110)
ttk.Button(button_frame, text="Clear", command=clear_fields).pack(side="left", padx=5)
ttk.Button(button_frame, text="Save As", command=save_as_file).pack(side="left", padx=5)
ttk.Button(button_frame, text="Exit", command=window.quit).pack(side="left", padx=5)

ttk.Separator(window, orient='horizontal').pack(fill='x', pady=5)

update_clock()
window.mainloop()
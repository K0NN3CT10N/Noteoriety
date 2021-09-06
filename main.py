import mysql.connector
from tkinter import *
import tkinter as tk
from tkinter import messagebox

# Code originally taken from github.com/effiongcharles and then adapted to current versions
# of tkinter and MySQL, as well as augmented for additional features/different frontend design

# Uses XAMPP and phpMyAdmin to host backend
# Uses tk to create GUI
# Local host on port 3306

# Establishing initial tools through Tkinter that will be used throughout frontend and backend development

conn = mysql.connector.connect(host="localhost", port=3306, user="root", passwd="")

notes_ids = []
selected_index = 0

window = tk.Tk()
window.title("Noteoriety")

top_frame = tk.Frame(window)
scroll_list = tk.Scrollbar(top_frame)
scroll_list.pack(side=tk.RIGHT, fill=tk.Y)

list_notes = Listbox(top_frame, height=15, width=40)
list_notes.bind('<<ListBoxSelect>>')
list_notes.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0), pady=(10, 0))

scroll_list.config(command=list_notes.yview)
list_notes.config(yscrollcommand=scroll_list.set, cursor="hand2", background="#fff5e6",
                  highlightbackground="grey", bd=0, selectbackground="#c9b922")
top_frame.pack(side=tk.TOP, padx=(0, 5))

text_frame = tk.Frame(window)
note_title = tk.Entry(text_frame, width=39, font="Helvetica 13")
note_title.insert(tk.END, "Title")
note_title.config(background="#F4F6F7", highlightbackground="grey")
note_title.pack(side=tk.TOP, pady=(0, 5), padx=(0, 10))

scroll_text = tk.Scrollbar(text_frame)
scroll_text.pack(side=tk.RIGHT, fill=tk.Y)
note_text = tk.Text(text_frame, height=7, width=40, font="Helvetica 13")
note_text.pack(side=tk.TOP, fill=tk.Y, padx=(5, 0), pady=(0, 5))
note_text.tag_config("tag your message", foreground="blue")
note_text.insert(tk.END, "Notes")
scroll_text.config(command=note_text.yview)
note_text.config(yscrollcommand=scroll_text.set, background="#F4F6F7", highlightbackground="grey")

text_frame.pack(side=tk.TOP)

button_frame = tk.Frame(window)
# photo_add = PhotoImage(file="add.gif")
# photo_edit = PhotoImage(file="edit.gif")
# photo_delete = PhotoImage(file="delete.gif")

btn_save = tk.Button(button_frame, text="Add", command=lambda: update_note())
btn_edit = tk.Button(button_frame, text="Update", command=lambda: update_note())
btn_delete = tk.Button(button_frame, text="Delete", command=lambda: delete_note())

btn_save.grid(row=0, column=1)
btn_edit.grid(row=0, column=2)
btn_delete.grid(row=0, column=3)

button_frame.pack(side=tk.TOP)


# From here, CRUD functions are created for the backend


def db_create_db(con):
    curs = con.cursor()
    query = "CREATE DATABASE IF NOT EXISTS db_notes"
    curs.execute(query)
    # Creates database of notes if there isn't one already


# Creates a table if it doesn't exist already
def db_create_table(con):
    db_create_db(con)
    con.database = "db_notes"
    curs = con.cursor()
    query = "CREATE TABLE IF NOT EXISTS tb_notes (note_id INT AUTO_INCREMENT PRIMARY KEY, " \
            "title VARCHAR(255) NOT NULL, note VARCHAR(2000) NOT NULL)"
    # Tells the server to create a unique ID for each table row
    # Creates each table row with an editable title and space to write notes
    curs.execute(query)


db_create_table(conn)


# Prepares title and note data so they can be modified
def db_insert_note(con, title, note):
    con.database = "db_notes"
    curs = con.cursor()
    query = "INSERT INTO tb_notes (title, note) VALUES (%s, %s)"
    val = (title, note)
    curs.execute(query, val)
    con.commit()
    return curs.lastrowid


# Array of key-value pairs as a base to call db_insert_note over
records = [
    ('My first title', 'This is my first awesome note'),
    ('My second title', 'This is my second awesome note'),
    ('My third title', 'This is my third awesome note'),
    ('My fourth title', 'This is my fourth awesome note'),
    ('My fifth title', 'This is my fifth awesome note')
]

for v in records:
    db_insert_note(conn, v[0], v[1])


def db_select_all_notes(con):
    con.database = "db_notes"
    curs = con.cursor()
    curs.execute("SELECT * from tb_notes")
    return curs.fetchall()


def db_select_specific_note(con, note_id):
    con.database = "db_notes"
    curs = con.cursor()
    curs.execute("SELECT title, note FROM tb_notes WHERE note_id = " + str(note_id))
    return curs.fetchone()


# Invoking the functions
print("======Selecting all records=====")
db_select_all_notes(conn)

print("===Selecting the record where the note_id is 2===")
print(db_select_specific_note(conn, 2))


def db_update_note(con, title, note, note_id):
    con.database = "db_notes"
    curs = con.cursor()
    val = (title, note, note_id)
    curs.execute("UPDATE tb_notes SET title = %s, note = %s WHERE note_id = %s", val)
    con.commit()


def db_delete_note(con, note_id):
    con.database = "db_notes"
    curs = con.cursor()
    query = "DELETE FROM tb_notes WHERE note_id = %s"
    adr = (note_id,)
    curs.execute(query, adr)
    con.commit()


db_delete_note(conn, "3")

# From here, frontend UI creation is done


def init(con):
    db_create_db(con)  # Creates database if it doesn't exist
    db_create_table(con)  # Creates a table if it doesn't exist

    # Select appropriate data
    notes = db_select_all_notes(con)

    for note in notes:
        list_notes.insert(tk.END, note[1])
        notes_ids.append(note[0])  # Saves the id of the note


init(conn)


def on_select(evt):
    global selected_index
    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    selected_index = index
    display_note(index, value)


def display_note(index, value):
    global notes_ids, conn
    # Clear the fields
    note_title.delete(0, tk.END)
    note_text.delete('1.0', tk.END)

    data = db_select_specific_note(conn, notes_ids[index])

    # Insert data
    note_title.insert(tk.END, data[0])
    note_text.insert(tk.END, data[1])

    # Enable delete and edit button
    btn_delete.config(state=tk.NORMAL)
    btn_edit.config(state=tk.NORMAL)


def save_note():
    global conn
    title = note_title.get()
    if len(title) < 1:
        tk.messagebox.showerror(title="Error", message="You must enter the note title")
        return

    note = note_text.get()
    if len(note.rstrip()) < 1:
        tk.messagebox.showerror(title="Error", message="You must enter the note")
        return

    # Check if title exists
    title_exist = False
    existing_titles = list_notes.get(0, tk.END)

    for t in existing_titles:
        if t == title:
            title_exist = True
            break

    if title_exist is True:
        tk.messagebox.showerror(title="Error", message="Note title already exists. You must choose a new title")
        return

    # Save in database
    inserted_id = db_insert_note(conn, title, note)
    print("Last inserted id is: " + str(inserted_id))

    # Insert into listbox
    list_notes.insert(tk.END, title)
    notes_ids.append(inserted_id)  # Save the id

    # Clear UI
    note_title.delete(0, tk.END)
    note_text.delete('1.0', tk.END)


def update_note():
    global selected_index, conn
    title = note_title.get()

    if len(title) < 1:
        tk.messagebox.showerror(title="Error", message="You must enter a title")
        return

    note = note_text.get("1.0", tk.END)
    if len(note.rstrip()) < 1:
        tk.messagebox.showerror(title="Error", message="You must enter a note")
        return

    note_id = notes_ids[selected_index]  # Get the id of the selected note

    # Save in database
    db_update_note(conn, title, note, note_id)

    # Update list_notes
    list_notes.delete(selected_index)
    list_notes.insert(selected_index, title)

    # Clear UI
    note_title.delete(0, tk.END)
    note_text.delete('1.0', tk.END)


def delete_note():
    global selected_index, conn, notes_ids
    title = note_title.get()
    notes = note_text.get('1.0', tk.END)

    print("Selected note is: " + str(selected_index))

    if len(title) < 1 or len(notes.rstrip()) < 1:
        tk.messagebox.showerror(title="Error", message="Please select a note to delete")
        return

    result = tk.messagebox.askquestion("Delete", "Are you sure you want to delete?", icon='warning')

    if result == 'yes':
        # Remove note from db
        note_id = notes_ids[selected_index]
        db_delete_note(conn, note_id)

        # Remove note from UI
        note_title.delete(0, tk.END)
        note_text.delete('1.0', tk.END)
        list_notes.delete(selected_index)


window.mainloop()

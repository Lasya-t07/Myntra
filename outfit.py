import tkinter as tk
from tkinter import messagebox
import sqlite3
import re

class User:
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password
        self.clothes_collection = []
        self.current_outfit = None  # Burada None olarak başlatıyoruz, çünkü henüz bir outfit oluşturmadık.

    def authenticate(self, entered_username, entered_password):
        return self.username == entered_username and self.password == entered_password

class ClothingAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Clothing App")

        self.current_user = None

        # Database connection
        self.conn = sqlite3.connect('user_data.db')
        self.create_tables()

        # Labels
        self.label_username = tk.Label(root, text="Username:")
        self.label_password = tk.Label(root, text="Password:")

        # Entry widgets
        self.entry_username = tk.Entry(root)
        self.entry_password = tk.Entry(root, show="*")

        # Buttons
        self.button_login = tk.Button(root, text="Log In", command=self.login)
        self.button_register = tk.Button(root, text="Register", command=self.register)
        self.button_add_clothes = tk.Button(root, text="Add Clothes", command=self.add_clothes)
        self.button_select_clothes = tk.Button(root, text="Select Clothes for Outfit", command=self.select_clothes_for_outfit)
        self.button_save_outfit = tk.Button(root, text="Save the Created Outfit", command=self.save_created_outfit)
        self.button_exit = tk.Button(root, text="Exit", command=self.root.destroy)

        # Grid layout
        self.label_username.grid(row=0, column=0, sticky=tk.E)
        self.label_password.grid(row=1, column=0, sticky=tk.E)
        self.entry_username.grid(row=0, column=1)
        self.entry_password.grid(row=1, column=1)
        self.button_login.grid(row=2, column=1, pady=10)
        self.button_register.grid(row=3, column=1, pady=10)
        self.button_add_clothes.grid(row=4, column=1, pady=10)
        self.button_select_clothes.grid(row=5, column=1, pady=10)
        self.button_save_outfit.grid(row=6, column=1, pady=10)
        self.button_exit.grid(row=7, column=1, pady=10)

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clothes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                color TEXT NOT NULL,
                size TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outfits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS selected_clothes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                outfit_id INTEGER NOT NULL,
                cloth_id INTEGER NOT NULL,
                FOREIGN KEY (outfit_id) REFERENCES outfits (id),
                FOREIGN KEY (cloth_id) REFERENCES clothes (id)
            )
        ''')
        self.conn.commit()

    def register_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        self.conn.commit()

    def login(self):
        entered_username = self.entry_username.get()
        entered_password = self.entry_password.get()

        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (entered_username, entered_password))
        user_data = cursor.fetchone()

        if user_data:
            user_id, _, _ = user_data
            self.current_user = User(user_id, entered_username, entered_password)
            messagebox.showinfo("Success", f"Welcome, {self.current_user.username}!")
        else:
            messagebox.showerror("Error", "Invalid username or password. Please try again.")

    def register(self):
        entered_username = self.entry_username.get()
        entered_password = self.entry_password.get()

        if entered_username and entered_password:
            self.register_user(entered_username, entered_password)
            messagebox.showinfo("Success", "Registration successful. You can now log in.")
        else:
            messagebox.showerror("Error", "Please enter both username and password.")

    def add_clothes(self):
        # Create a new window
        add_clothes_window = tk.Toplevel(self.root)
        add_clothes_window.title("Add Clothes")

        # Labels
        label_name = tk.Label(add_clothes_window, text="Name:")
        label_category = tk.Label(add_clothes_window, text="Category:")
        label_color = tk.Label(add_clothes_window, text="Color:")
        label_size = tk.Label(add_clothes_window, text="Size:")

        # Entry widgets
        entry_name = tk.Entry(add_clothes_window)
        entry_category = tk.Entry(add_clothes_window)
        entry_color = tk.Entry(add_clothes_window)
        entry_size = tk.Entry(add_clothes_window)

        # Save button
        button_save_clothes = tk.Button(add_clothes_window, text="Save", command=lambda: self.save_clothes(entry_name.get(), entry_category.get(), entry_color.get(), entry_size.get(), add_clothes_window))

        # Grid layout
        label_name.grid(row=0, column=0, sticky=tk.E)
        label_category.grid(row=1, column=0, sticky=tk.E)
        label_color.grid(row=2, column=0, sticky=tk.E)
        label_size.grid(row=3, column=0, sticky=tk.E)
        entry_name.grid(row=0, column=1)
        entry_category.grid(row=1, column=1)
        entry_color.grid(row=2, column=1)
        entry_size.grid(row=3, column=1)
        button_save_clothes.grid(row=4, column=1, pady=10)

    def save_clothes(self, name, category, color, size, window):
        # Add clothing information to the database
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO clothes (user_id, name, category, color, size) VALUES (?, ?, ?, ?, ?)",
                       (self.current_user.id, name, category, color, size))
        self.conn.commit()

        messagebox.showinfo("Success", "Clothes added successfully!")

        # Close the window
        window.destroy()

    def display_user_clothes(self):
        # Create a new window
        self.display_clothes_window = tk.Toplevel(self.root)
        self.display_clothes_window.title("User Clothes")

        # Listbox
        self.clothes_listbox = tk.Listbox(self.display_clothes_window)
        
        # Retrieve clothing information from the database
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name FROM clothes WHERE user_id=?', (self.current_user.id,))
        clothes_data = cursor.fetchall()

        # Add clothing information to the listbox
        for cloth_id, cloth_name in clothes_data:
            self.clothes_listbox.insert(tk.END, f"{cloth_name} (ID: {cloth_id})")

        # Select button
        button_select = tk.Button(self.display_clothes_window, text="Select", command=self.select_clothes_for_outfit)

        # Grid layout
        self.clothes_listbox.grid(row=0, column=0, pady=10)
        button_select.grid(row=1, column=0)

    def select_clothes_for_outfit(self):
        # Create a new window
        select_clothes_window = tk.Toplevel(self.root)
        select_clothes_window.title("Select Clothes for Outfit")

        # Listbox
        clothes_listbox = tk.Listbox(select_clothes_window, selectmode=tk.MULTIPLE)
        
        # Retrieve clothing information from the database
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name FROM clothes WHERE user_id=?', (self.current_user.id,))
        clothes_data = cursor.fetchall()

        # Add clothing information to the listbox
        for cloth_id, cloth_name in clothes_data:
            clothes_listbox.insert(tk.END, f"{cloth_name} (ID: {cloth_id})")

        # Select button
        button_select = tk.Button(select_clothes_window, text="Select", command=lambda: self.save_selected_clothes(clothes_listbox.curselection(), clothes_listbox, select_clothes_window))

        # Grid layout
        clothes_listbox.grid(row=0, column=0, pady=10)
        button_select.grid(row=1, column=0)

    def save_selected_clothes(self, selected_indices, clothes_listbox, window):
        # Get the IDs of the selected clothes
        selected_clothes_ids = [re.findall(r'\d+', clothes_listbox.get(index))[0] for index in selected_indices]

        # Check if an outfit exists for the user, if not, create one
        if not self.current_user.current_outfit:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO outfits (user_id, name) VALUES (?, ?)",
                           (self.current_user.id, "Unnamed Outfit"))
            self.conn.commit()
            self.current_user.current_outfit = cursor.lastrowid

        # Add the selected clothes to the database
        cursor = self.conn.cursor()
        for cloth_id in selected_clothes_ids:
            cursor.execute("INSERT INTO selected_clothes (outfit_id, cloth_id) VALUES (?, ?)",
                           (self.current_user.current_outfit, cloth_id))
        self.conn.commit()

        messagebox.showinfo("Success", "Clothes selected successfully!")

        # Close the window
        window.destroy()

    def save_created_outfit(self):
        # Create a new window
        save_outfit_window = tk.Toplevel(self.root)
        save_outfit_window.title("Save the Created Outfit")

        # Name label
        label_outfit_name = tk.Label(save_outfit_window, text="Outfit Name:")

        # Name entry
        entry_outfit_name = tk.Entry(save_outfit_window)

        # Save button
        button_save_outfit = tk.Button(save_outfit_window, text="Save", command=lambda: self.save_outfit_entry(entry_outfit_name.get(), save_outfit_window))

        # Grid layout
        label_outfit_name.grid(row=0, column=0, sticky=tk.E)
        entry_outfit_name.grid(row=0, column=1)
        button_save_outfit.grid(row=1, column=1, pady=10)

    def save_outfit_entry(self, outfit_name, window):
        # Update the outfit name in the database
        cursor = self.conn.cursor()
        cursor.execute("UPDATE outfits SET name=? WHERE id=?", (outfit_name, self.current_user.current_outfit))
        self.conn.commit()

        messagebox.showinfo("Success", "Outfit saved successfully!")

        # Close the window
        window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClothingAppGUI(root)
    root.mainloop()
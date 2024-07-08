from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'user_data.db'

class User:
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password
        self.clothes_collection = []
        self.current_outfit = None

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                            (username, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                     (username, password))
        conn.commit()
        conn.close()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/add_clothes', methods=['GET', 'POST'])
def add_clothes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        color = request.form['color']
        size = request.form['size']

        conn = get_db_connection()
        conn.execute('INSERT INTO clothes (user_id, name, category, color, size) VALUES (?, ?, ?, ?, ?)', 
                     (session['user_id'], name, category, color, size))
        conn.commit()
        conn.close()
        flash('Clothes added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_clothes.html')

@app.route('/select_clothes', methods=['GET', 'POST'])
def select_clothes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    clothes = conn.execute('SELECT id, name FROM clothes WHERE user_id = ?', 
                           (session['user_id'],)).fetchall()
    conn.close()

    if request.method == 'POST':
        selected_clothes_ids = request.form.getlist('clothes')
        conn = get_db_connection()

        if 'current_outfit' not in session or session['current_outfit'] is None:
            conn.execute("INSERT INTO outfits (user_id, name) VALUES (?, ?)",
                         (session['user_id'], "Unnamed Outfit"))
            session['current_outfit'] = conn.execute('SELECT last_insert_rowid()').fetchone()[0]

        for cloth_id in selected_clothes_ids:
            conn.execute("INSERT INTO selected_clothes (outfit_id, cloth_id) VALUES (?, ?)",
                         (session['current_outfit'], cloth_id))
        conn.commit()
        conn.close()

        flash('Clothes selected successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('select_clothes.html', clothes=clothes)

@app.route('/save_outfit', methods=['GET', 'POST'])
def save_outfit():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        outfit_name = request.form['outfit_name']

        conn = get_db_connection()
        conn.execute("UPDATE outfits SET name = ? WHERE id = ?",
                     (outfit_name, session['current_outfit']))
        conn.commit()
        conn.close()
        flash('Outfit saved successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('save_outfit.html')

@app.route('/user_clothes')
def user_clothes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    clothes = conn.execute('SELECT id, name FROM clothes WHERE user_id = ?', 
                           (session['user_id'],)).fetchall()
    conn.close()
    return render_template('user_clothes.html', clothes=clothes)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

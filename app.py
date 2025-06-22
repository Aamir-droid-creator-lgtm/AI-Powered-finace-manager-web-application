# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3, hashlib, pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import plotly.express as px

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DB_PATH = 'expense_tracker.db'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT id, username FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return User(id=row[0], username=row[1]) if row else None

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Registered successfully. Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
        conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        conn = get_db()
        row = conn.execute("SELECT id, username FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if row:
            login_user(User(id=row['id'], username=row['username']))
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    amount = float(request.form['amount'])
    category = request.form['category']
    description = request.form['description']
    conn = get_db()
    conn.execute("INSERT INTO expenses (username, amount, category, description, date) VALUES (?, ?, ?, ?, DATE('now'))",
                 (current_user.username, amount, category, description))
    conn.commit()
    conn.close()
    flash('Expense added.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add_income', methods=['POST'])
@login_required
def add_income():
    amount = float(request.form['amount'])
    conn = get_db()
    conn.execute("INSERT INTO income (username, amount, date) VALUES (?, ?, DATE('now'))", (current_user.username, amount))
    conn.commit()
    conn.close()
    flash('Income added.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/set_goal', methods=['POST'])
@login_required
def set_goal():
    goal = float(request.form['goal'])
    conn = get_db()
    row = conn.execute("SELECT 1 FROM goals WHERE username=?", (current_user.username,)).fetchone()
    if row:
        conn.execute("UPDATE goals SET goal=? WHERE username=?", (goal, current_user.username))
    else:
        conn.execute("INSERT INTO goals (username, goal) VALUES (?, ?)", (current_user.username, goal))
    conn.commit()
    conn.close()
    flash('Goal updated.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/export_excel')
@login_required
def export_excel():
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM expenses WHERE username=?", conn, params=(current_user.username,))
    conn.close()
    buf = BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='expenses.xlsx')

@app.route('/export_pdf')
@login_required
def export_pdf():
    conn = get_db()
    rows = conn.execute("SELECT date, category, amount, description FROM expenses WHERE username=?", (current_user.username,)).fetchall()
    conn.close()
    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=letter)
    p.setFont("Helvetica", 12)
    y = 750
    p.drawString(30, y, "Expense Report")
    y -= 30
    for r in rows:
        p.drawString(30, y, f"{r['date']} | {r['category']} | ₹{r['amount']} | {r['description']}")
        y -= 20
    p.save()
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='expenses.pdf')

@app.route('/visuals')
@login_required
def visuals():
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM expenses WHERE username=?", conn, params=(current_user.username,))
    conn.close()
    if df.empty:
        flash('No data to visualize.', 'warning')
        return redirect(url_for('dashboard'))
    pie = px.pie(df, values='amount', names='category', title='Expenses by Category')
    bar = px.bar(df, x='category', y='amount', title='Category-wise Expense')
    df['date'] = pd.to_datetime(df['date'])
    daily = df.groupby('date')['amount'].sum().reset_index()
    line = px.line(daily, x='date', y='amount', title='Daily Expense Trend')
    for fig in (pie, bar, line):
        fig.update_layout(template='plotly_dark')
    return render_template('charts.html',
                           pie_html=pie.to_html(full_html=False),
                           bar_html=bar.to_html(full_html=False),
                           line_html=line.to_html(full_html=False))

@app.route('/add_recurring', methods=['POST'])
@login_required
def add_recurring():
    amount, description, frequency = float(request.form['amount']), request.form['description'], request.form['frequency']
    conn = get_db()
    conn.execute("INSERT INTO recurring_expenses (username, amount, description, frequency) VALUES (?, ?, ?, ?)",
                 (current_user.username, amount, description, frequency))
    conn.commit()
    conn.close()
    flash('Recurring expense added.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/edit_recurring/<int:id>', methods=['GET','POST'])
@login_required
def edit_recurring(id):
    conn = get_db()
    row = conn.execute("SELECT * FROM recurring_expenses WHERE id=? AND username=?", (id, current_user.username)).fetchone()
    if not row:
        conn.close()
        flash('Not found.', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        conn.execute("UPDATE recurring_expenses SET amount=?, description=?, frequency=? WHERE id=? AND username=?",
                     (float(request.form['amount']), request.form['description'], request.form['frequency'], id, current_user.username))
        conn.commit()
        conn.close()
        flash('Recurring updated.', 'success')
        return redirect(url_for('dashboard'))
    conn.close()
    return render_template('edit_recurring.html', recurring=row)

@app.route('/delete_recurring/<int:id>')
@login_required
def delete_recurring(id):
    conn = get_db()
    conn.execute("DELETE FROM recurring_expenses WHERE id=? AND username=?", (id, current_user.username))
    conn.commit()
    conn.close()
    flash('Recurring deleted.', 'warning')
    return redirect(url_for('dashboard'))

@app.route('/delete_all_expenses')
@login_required
def delete_all_expenses():
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE username=?", (current_user.username,))
    conn.commit()
    conn.close()
    flash('All expenses cleared.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/delete_income')
@login_required
def delete_income():
    conn = get_db()
    conn.execute("DELETE FROM income WHERE username=?", (current_user.username,))
    conn.commit()
    conn.close()
    flash('All income cleared.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/delete_goal')
@login_required
def delete_goal():
    conn = get_db()
    conn.execute("DELETE FROM goals WHERE username=?", (current_user.username,))
    conn.commit()
    conn.close()
    flash('Goal deleted.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/')
@login_required
def dashboard():
    conn = get_db()
    expenses = conn.execute("SELECT * FROM expenses WHERE username=? ORDER BY date DESC", (current_user.username,)).fetchall()
    total_exp = sum(r['amount'] for r in expenses)
    row_income = conn.execute("SELECT SUM(amount) as total FROM income WHERE username=?", (current_user.username,)).fetchone()
    income = row_income['total'] or 0
    row_goal = conn.execute("SELECT goal FROM goals WHERE username=?", (current_user.username,)).fetchone()
    goal = row_goal['goal'] if row_goal else 0
    recurring = conn.execute("SELECT * FROM recurring_expenses WHERE username=?", (current_user.username,)).fetchall()
    conn.close()
    if total_exp > goal and goal > 0:
        alert = True
    elif income == 0 and total_exp == 0:
        alert = None
    else:
        alert = False
    return render_template('dashboard.html',
                           expenses=expenses, total=total_exp,
                           income=income, goal=goal,
                           alert=alert, recurring=recurring)

if __name__ == '__main__':
    app.run(debug=True)

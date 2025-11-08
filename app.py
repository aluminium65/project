from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


# Ensure the static folder exists
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
os.makedirs(static_folder, exist_ok=True)


app = Flask(__name__)
app.secret_key = 'secretkey'

# ---- Configure Database ----
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'voting_app'
mysql = MySQL(app)

# ---- ROUTES ----
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def voter_login():
    roll = request.form['roll']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM voters WHERE roll_num = %s", [roll])
    user = cursor.fetchone()

    if user and not user['has_voted']:
        session['roll'] = roll
        return redirect(url_for('vote'))
    else:
        flash('Invalid roll number or vote already casted!')
        return redirect(url_for('login'))

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'roll' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()

    # Organize candidates by rows
    rows = {1: [], 2: [], 3: []}
    for c in candidates:
        rows[c['row_num']].append(c)

    if request.method == 'POST':
        for row in range(1, 4):
            candidate_id = request.form.get(f'row{row}')
            if candidate_id:
                cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE id = %s", [candidate_id])
                cursor.execute("INSERT INTO votes (roll_num, candidate_id) VALUES (%s, %s)", (session['roll'], candidate_id))

        cursor.execute("UPDATE voters SET has_voted = TRUE WHERE roll_num = %s", [session['roll']])
        mysql.connection.commit()
        session.pop('roll', None)
        flash('Vote has been successfully submitted!')
        return redirect(url_for('login'))

    return render_template('vote.html', rows=rows)

@app.route('/admin')
def admin_login_page():
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == 'password':
        session['admin'] = True
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid credentials')
        return redirect(url_for('admin_login_page'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login_page'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM candidates")
    data = cursor.fetchall()

    charts = []
    for row in [1, 2, 3]:
        row_data = [c for c in data if c['row_num'] == row]
        names = [c['name'] for c in row_data]
        votes = [c['votes'] for c in row_data]
        plt.bar(names, votes)
        charts = []
        for row in [1, 2, 3]:
            row_data = [c for c in data if c['row_num'] == row]
            names = [c['name'] for c in row_data]
            votes = [c['votes'] for c in row_data]

            if not row_data:
                continue  # Skip empty rows

            plt.figure(figsize=(5, 4))
            plt.bar(names, votes, color='skyblue')
            plt.title(f'Row {row} Voting Results')
            plt.ylabel('Votes')

            chart_filename = f'chart_row{row}.png'
            chart_path = os.path.join(static_folder, chart_filename)
            plt.tight_layout()
            plt.savefig(chart_path)
            plt.close()

            charts.append(chart_filename)


    return render_template('admin_dashboard.html', charts=charts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

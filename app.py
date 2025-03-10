from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure random value

# MySQL database connection details
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '2112',  # Your MySQL password
    'database': 'voting_system'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            return conn
        else:
            raise Exception("Failed to connect to the database.")
    except Exception as e:
        print("Database connection error:", e)
        return None

# Simulated Quantum Key Distribution (QKD)
def generate_qkd_key(length=8):
    return ''.join(random.choices('01', k=length))

# Encrypt vote using XOR with QKD key
def encrypt_vote(vote, qkd_key):
    return ''.join(chr(ord(c) ^ int(qkd_key[i % len(qkd_key)])) for i, c in enumerate(vote))

# Decrypt vote using XOR with QKD key
def decrypt_vote(encrypted_vote, qkd_key):
    return ''.join(chr(ord(c) ^ int(qkd_key[i % len(qkd_key)])) for i, c in enumerate(encrypted_vote))

# Home Page: Choose Voter Login or Admin Login
@app.route('/')
def home():
    return render_template('home.html')

# Voter Login Page
@app.route('/voter_login', methods=['GET', 'POST'])
def voter_login():
    if request.method == 'POST':
        voter_id_number = request.form['voter_id_number']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM voters WHERE voter_id_number = %s", (voter_id_number,))
        voter = cursor.fetchone()
        conn.close()
        if voter:
            session['voter_id_number'] = voter_id_number
            return redirect(url_for('voting_ballot'))
        else:
            return "Invalid Voter ID. Please try again."
    return render_template('voter_login.html')

# Voting Ballot Page for Voters
@app.route('/voting_ballot', methods=['GET', 'POST'])
def voting_ballot():
    if 'voter_id_number' not in session:
        return redirect(url_for('voter_login'))
    
    if request.method == 'POST':
        selected_party = request.form['party']
        qkd_key = generate_qkd_key()
        encrypted_vote = encrypt_vote(selected_party, qkd_key)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO votes (voter_id_number, encrypted_vote, qkd_key) VALUES (%s, %s, %s)",
                       (session['voter_id_number'], encrypted_vote, qkd_key))
        conn.commit()
        conn.close()
        
        return render_template('voting_success.html')
    
    return render_template('voting_ballot.html')

# Admin Login Page
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
        admin = cursor.fetchone()
        conn.close()
        if admin:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid admin credentials. Please try again."
    return render_template('admin_login.html')

# Admin Dashboard: Add Voters & View Voting Results
@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    # Handle adding new voter if form submitted
    if request.method == 'POST':
        if 'voter_name' in request.form and 'voter_id_number' in request.form:
            voter_name = request.form['voter_name']
            voter_id_number = request.form['voter_id_number']
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO voters (voter_id_number, name) VALUES (%s, %s)", (voter_id_number, voter_name))
            conn.commit()
            conn.close()
            return redirect(url_for('admin_dashboard'))
    
    # Retrieve voting results
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM votes")
    votes = cursor.fetchall()
    conn.close()
    
    # Process votes: decrypt each vote and count per party
    decrypted_votes = []
    party_counts = {"YSRCP": 0, "TDP": 0, "BJP": 0, "Janasena": 0}
    for vote in votes:
        # vote: (voter_id_number, encrypted_vote, qkd_key)
        encrypted_vote = vote[1]
        qkd_key = vote[2]
        decrypted = decrypt_vote(encrypted_vote, qkd_key)
        decrypted_votes.append({
            'voter_id_number': vote[0],
            'encrypted_vote': encrypted_vote,
            'decrypted_vote': decrypted,
            'qkd_key': qkd_key
        })
        if decrypted in party_counts:
            party_counts[decrypted] += 1
    
    winner = max(party_counts, key=party_counts.get) if votes else "No votes"
    
    return render_template('admin_dashboard.html',
                           vote_results=decrypted_votes,
                           vote_count=party_counts,
                           winner=winner)

if __name__ == '__main__':
    app.run(debug=True)

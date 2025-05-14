from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flashing messages

# Database connection
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="A-081416",
        database="Sentiment_analysis"
    )

# Insert user data into the database
def insert_user(name, contact, email, birth_date, username, password):
    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO users (name, contact_number, email, birth_date, username, password)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, contact, email, birth_date, username, password))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

# Function to verify login credentials
def verify_login(username, password):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return result and result[0] == password

# Function to perform sentiment analysis
def analyze_sentiment(input_text, username):
    # Simple sentiment analysis (Replace with actual ML model or service)
    positive_keywords = ['happy', 'good', 'love', 'great', 'awesome']
    negative_keywords = ['sad', 'bad', 'hate', 'angry', 'terrible']

    sentiment_score = 0

    for word in positive_keywords:
        if word in input_text.lower():
            sentiment_score += 1

    for word in negative_keywords:
        if word in input_text.lower():
            sentiment_score -= 1

    if sentiment_score > 0:
        return 'Positive'
    elif sentiment_score < 0:
        return 'Negative'
    else:
        return 'Neutral'

# Insert feedback into the database
def insert_feedback(opinion, category, feedback):
    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO feedback (opinion, category, feedback)
        VALUES (%s, %s, %s)
        """, (opinion, category, feedback))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

# Home Page (First Page)
@app.route('/')
def index():
    return render_template('index.html')  # First page of the project

# Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        email = request.form['email']
        birth_date = request.form['birth_date']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('signup'))

        if insert_user(name, contact, email, birth_date, username, password):
            flash("Signup successful! Please login.", "success")
            return redirect(url_for('login'))
        else:
            flash("An error occurred. Try a different username or email.", "error")
            return redirect(url_for('signup'))

    return render_template('signup.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if verify_login(username, password):
            session['username'] = username  # Store session data
            flash("Login successful!", "success")
            return redirect(url_for('main'))
        else:
            flash("Invalid username or password. Please try again.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

# Main Page (After login)
@app.route('/main')
def main():
    if 'username' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    return render_template('main.html', username=session['username'])

# Feedback Page
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        opinion = request.form['opinion']
        category = request.form['category']
        feedback_text = request.form['feedback']

        if insert_feedback(opinion, category, feedback_text):
            flash("Feedback submitted successfully!", "success")
            return redirect(url_for('feedback'))
        else:
            flash("An error occurred while submitting feedback.", "error")
            return redirect(url_for('feedback'))

    return render_template('feedback.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# Sentiment Analysis Route
@app.route('/analyze', methods=['POST'])
def analyze():
    input_text = request.form.get('input_text')
    username = request.form.get('username')

    # Analyze sentiment based on input_text
    sentiment = analyze_sentiment(input_text, username)

    return jsonify({
        'sentiment': sentiment
    })

if __name__ == '__main__':
    app.run(debug=True)

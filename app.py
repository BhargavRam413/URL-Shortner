from flask import Flask, render_template, request, jsonify, redirect
import string
import random
import psycopg2

app = Flask(__name__, template_folder='templates')

# Configuration
myip = 'http://localhost:5000'
DB_HOST = 'localhost'
DB_NAME = 'url_shortner'
DB_USER = 'postgres'
DB_PASS = '1234'

# Database Connection
def db_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST
    )
    return conn

@app.route('/shortened_url', methods=['POST'])
def shortened_url():
    data = request.get_json()
    long_url = data.get('url')
    short = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    shortened_url = f"{myip}/{short}"

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO url (original_url, shortened_url, click_count) VALUES (%s, %s, %s)", 
                (long_url, short, 0))  
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'shortened_url': shortened_url})


@app.route('/<short_path>')
def redirect_originalurl(short_path):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT original_url FROM url WHERE shortened_url = %s", (short_path,))
    url_data = cur.fetchone()

    if not url_data:
        return "URL not found", 404

    long_url = url_data[0]

   
    cur.execute("UPDATE url SET click_count = click_count + 1 WHERE shortened_url = %s", (short_path,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(long_url)


@app.route('/clicks/<short_path>', methods=['GET'])
def get_click_count(short_path):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT click_count FROM url WHERE shortened_url = %s", (short_path,))
    count_data = cur.fetchone()

    cur.close()
    conn.close()

    if count_data:
        return jsonify({'click_count': count_data[0]})
    else:
        return jsonify({'error': 'Shortened URL not found'}), 404


# Home Page
@app.route('/')
def index():
    return render_template('shorten_url.html')  


if __name__ == '__main__':
    app.run(debug=True)

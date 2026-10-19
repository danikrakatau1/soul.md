from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "test_vuln.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'SuperSecretAdminPassword123')")
    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (2, 'user', 'password123')")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return '''
    <h2>Firing Range - Vulnerable Lab</h2>
    <p>1. <a href="/sqli?id=1">SQL Injection Test</a></p>
    <p>2. <a href="/xss?name=Hacker">XSS Test</a></p>
    <p>3. <a href="/eval?code=2+2">RCE / Eval Test</a></p>
    '''

# 1. SQL Injection Vulnerability
@app.route('/sqli')
def sqli():
    user_id = request.args.get('id', '1')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # VULNERABLE SQL QUERY
    query = f"SELECT username, password FROM users WHERE id = {user_id}"
    try:
        c.execute(query)
        result = c.fetchall()
        html = f"<h3>Query: {query}</h3><p>Results: {result}</p>"
    except Exception as e:
        html = f"<h3>Query: {query}</h3><p>Error: {e}</p>"
    conn.close()
    return html

# 2. XSS Vulnerability
@app.route('/xss')
def xss():
    name = request.args.get('name', 'Guest')
    # VULNERABLE REFLECTED XSS
    return f"<h3>Hello, {name}</h3><form><input name='name' value=''><button>Submit</button></form>"

# 3. Insecure Eval / RCE Vulnerability
@app.route('/eval')
def eval_code():
    code = request.args.get('code', '1+1')
    try:
        # VULNERABLE EVAL
        res = eval(code)
        return f"<h3>Result of eval({code}) = {res}</h3>"
    except Exception as e:
        return f"<h3>Error: {e}</h3>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

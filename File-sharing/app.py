from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, send_from_directory
import os
import sqlite3
from flask import g
from werkzeug.utils import secure_filename
from wtforms import Form, TextAreaField, validators, StringField, SubmitField

# Upload folder (relative path for portability)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'files')

app = Flask(__name__)
app.secret_key = "James Bond"

# Function to show files of a user
def show_files(username):
    return os.listdir(os.path.join(UPLOAD_FOLDER, username))

# Fetch existing users from the DB
def get_user():
    lst = []
    conn = sqlite3.connect("base.db")
    c = conn.cursor()
    for row in c.execute('SELECT * FROM data'):
        lst.append(row[0])
    conn.commit()
    return lst

l = get_user()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/', methods=['POST'])
def reg():
    return validate()

@app.route('/home', methods=['POST'])
def do_login():
    conn = sqlite3.connect("base.db")
    c = conn.cursor()
    session['username'] = request.form['username']
    password = request.form['password']
    error1 = None

    for row in c.execute('SELECT * FROM data'):
        if row[0] == session['username'] and row[1] == password:
            error2 = "Welcome, " + session['username'] + "!"
            return render_template('home.html', error2=error2)
        elif row[0] != session['username'] or row[1] != password:
            error1 = "Wrong username or password! Please, try again."

    conn.commit()
    return render_template('login.html', error1=error1)

@app.route('/home', methods=['GET'])
def home_page():
    error2 = "Welcome, " + session['username'] + "!"
    return render_template('home.html', error2=error2)

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

def add_value(username, password, folder_password):
    conn = sqlite3.connect("base.db")
    c = conn.cursor()
    data1 = [(username, password, folder_password)]
    c.executemany("INSERT INTO data VALUES (?,?,?)", data1)
    conn.commit()

def validate():
    error = None
    error1 = None
    user = request.form['user']
    password = request.form['pass']
    repeat_password = request.form['repeat_password']

    if user != "" and password != "" and repeat_password != "":
        if user in l:
            error = "This username is already used. Please, enter another username!"
        elif user not in l and (password != repeat_password or len(password) < 6):
            error = "The passwords aren’t the same or password is too short!"
        else:
            add_value(user, password, None)
            os.mkdir(os.path.join(UPLOAD_FOLDER, user))
            error1 = "You are successfully registered :)"
            return render_template('login.html', error1=error1)
    else:
        error = "The fields cannot be empty!"

    return render_template('register.html', error=error)

@app.route("/logout", methods=['POST'])
def logout():
    session.pop('users name', None)
    session.pop('username', None)
    return home()

@app.route("/home/directory", methods=['POST'])
def directory():
    files = show_files(session.get('username', None))
    return render_template("directory.html", files=files)

@app.route("/back", methods=['POST'])
def back():
    return redirect("http://127.0.0.1:4000/home", code=302)

@app.route("/delete", methods=['GET', 'POST'])
def delete():
    if request.method == 'GET':
        lst = show_files(session.get('username'))
        return render_template("delete.html", lst=lst)
    elif request.method == 'POST':
        choose = str(request.form.get('choose'))
        os.remove(os.path.join(UPLOAD_FOLDER, session.get('username', None), choose))
        return redirect("http://127.0.0.1:4000/home", code=302)

@app.route("/change", methods=['GET', 'POST'])
def change():
    if request.method == 'GET':
        return render_template("change.html")
    elif request.method == 'POST':
        conn = sqlite3.connect("base.db")
        c = conn.cursor()
        if request.form['new password'] == request.form['repeat password']:
            c.execute("UPDATE data SET folder_password = ? WHERE username = ?", 
                      [request.form['new password'], session.get('username', None)])
            error1 = "Password refreshed successfully!"
        else:
            error1 = "Passwords aren’t the same!"
        conn.commit()
        return render_template("change.html", error1=error1)

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    return render_template('upload.html')

@app.route('/uploader', methods=['GET', 'POST'])
def uploadd_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join(UPLOAD_FOLDER, session.get('username', None), secure_filename(f.filename)))
        return render_template("uploader.html")

@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == 'GET':
        return render_template("download.html")
    elif request.method == 'POST':
        conn = sqlite3.connect("base.db")
        c = conn.cursor()
        for row in c.execute('SELECT * FROM data'):
            if request.form['users name'] == row[0] and request.form['folder password'] == row[2]:
                session['users name'] = request.form['users name']
                spisok = show_files(request.form['users name'])
                return render_template("downloading.html", spisok=spisok)

        error1 = "Invalid data!"
        return render_template("download.html", error1=error1)

@app.route('/downloading', methods=['POST'])
def downloading():
    filename = request.form.get('todownload')
    return send_from_directory(os.path.join(UPLOAD_FOLDER, session.get('users name', None)), filename)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4000)

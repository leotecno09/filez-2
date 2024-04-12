import os
import psycopg2
import flask_login
import random
import json
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from psycopg2 import Error
from flask import Flask, render_template, request, jsonify, url_for, redirect
from datetime import date

app = Flask(__name__)
#bcrypt = Bcrypt(app)

#FLASK CONFIGURATIONS
app.config['SECRET_KEY'] = 'ZJ48dnJD85jAL93jADn398!73nDS38@nfd38'

# VARIABLES
FILES_ROOT = "./users/uploads"

#LOGIN MANAGER

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(id):
    try:
        cur.execute("SELECT * FROM users WHERE id = %s", (id,))
        result = cur.fetchone()

        username = result[1]
        email = result[2]

        user = User(id)
        user.username = username
        user.email = email
        
        return user
    
    except Error as e:
        return e

#DATABASE
conn = psycopg2.connect(host = "192.168.0.199", database = "filez", user = "postgres", password = "1")
cur = conn.cursor()

@app.route('/dashboard')
def root():
    return render_template('dashboard-ok.html')

@app.route('/account/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        passwordConfirm = request.form['passwordConfirm']

        try:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            result = cur.fetchone()

        except Error as e:
            return e

        if result:
            return jsonify({"result": "error", "error_text": "This email is already registered."})

        elif password != passwordConfirm:
            return jsonify({"result": "error", "error_text": "The passwords doest not match."})
        
        elif len(password) < 7:
            return jsonify({"result": "error", "error_text": "The password needs to be at least 7 characters long."})
        
        else:
            hashed_password = generate_password_hash(password, method='sha256')

            today = date.today()
            user_id = ''.join([str(random.randint(0, 9)) for _ in range(9)])

            try:
                cur.execute("INSERT INTO users (id, username, email, password, register_date)" "VALUES (%s, %s, %s, %s, %s)", (int(user_id), format(username), format(email), format(hashed_password), format(today)))
                conn.commit()
            
            except Error as e:
                return e


            return jsonify({"result": "success"})

    else:
        return render_template('register.html')

@app.route('/account/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (format(username), format(username)))
            result = cur.fetchone()

            if result:
                user_id = result[0]
                storedUsername = result[1]
                storedEmail = result[2]
                storedPassword = result[3]
                register_date = result[4]

                if not check_password_hash(storedPassword, password):
                    return jsonify({"result": "error", "error_text": "Wrong password."})
                
                else:
                    user = User(id=user_id)
                    user.username = storedUsername
                    user.email = storedEmail
                    login_user(user)

                    return jsonify({"result": "success"})
        
            else:
                return jsonify({"result": "error", "error_text": "Account not found."})
        
        except Error as e:
            return e
    
    else:
        return render_template('login.html')

@app.route('/account/logout')
@login_required
def logout():
    logout_user()

@app.route('/api/get_files')
@login_required
def get_files():
    location = request.args.get('location', default='my_files')
    session_username = current_user.username

    if location == 'my_files':
        user_dir = FILES_ROOT + '/' + str(session_username)
        print(user_dir)
        user_folders = [f for f in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, f))]
        print(user_folders)

        all_files = []

        for folder in user_folders:
            folder_path = os.path.join(user_dir, folder)
            if os.path.isdir(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    for filename in files:
                        if filename.endswith('.json'):
                            continue
                        
                        file_path = os.path.join(root, filename)

                        #Read the .json
                        json_filename = os.path.splitext(filename)[0] + '.json'
                        json_file_path = os.path.join(root, json_filename)
                        if os.path.exists(json_file_path):
                            with open(json_file_path, 'r') as json_file:
                                file_info = json.load(json_file)
                        
                        else:
                            file_info = {}

                        all_files.append(file_info)
        
        return jsonify(all_files)
    
    else:
        folder_path = f"./users/tester/files/{location}"
        if os.path.isdir(folder_path):
            files = []
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    file_info = {
                        "name": filename,
                        "upload_date": "DATA DI CARICAMENTO",
                        "owner": "sempre io",
                        "location": location,
                        "url": f"/users/tester/files/{location}/{filename}"
                    }
                    files.append(file_info)
                
            return jsonify(files)
        else:
            return jsonify([])

@app.route('/api/upload_files', methods=['POST'])
def upload():
    #if 'file' not in request.files:
    #    return jsonify({"status": "error", "error_text": "No files selected."}), 400

    files = request.files.getlist('files')
    location = request.form['location']

    if location == "":
        location = "my_files"

    for file in files:
        if file.filename == '':
            return jsonify({"status": "error", "error_text": "No files selected."})

    session_username = current_user.username

    if not session_username:
        return jsonify({"status": "error", "error_text": "User not logged in."})
        
    upload_folder = os.path.join(FILES_ROOT, str(session_username), location)
    print(upload_folder)

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    for file in files:
        file.save(os.path.join(upload_folder, file.filename))

        upload_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #Location adjustments
        if location == "my_files":
            location = "My files"
        elif location == "shared":
            location = "Shared"
        elif location == "trash":
            location = "Trash"

        file_data = {                       # AGGIUNGERE RAW
            "filename": file.filename,
            "owner": session_username,
            "upload_date": upload_date,
            "location": location,
            "shared": False,
            "shared_with": None
        }

        json_filename = os.path.splitext(file.filename)[0] + '.json'
        json_path = os.path.join(upload_folder, json_filename)
        with open(json_path, 'w') as json_file:
            json_file.write(json.dumps(file_data))
    
    return jsonify({"status": "success"})

        
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=True)
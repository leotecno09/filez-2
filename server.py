import os
import psycopg2
import flask_login
import random
import json
import datetime
import shutil
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from psycopg2 import Error
from flask import Flask, render_template, request, jsonify, url_for, redirect, send_file
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
login_manager.login_view = '/account/login'

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

#FUNZIONI BELLE A CASO (pt.2)
#def find_json_file(folder_path, filecode):
#    for root, dirs, files in os.walk(folder_path):
#        for file_name in files:
#            if file_name == f"{filecode}.json":
#                return os.path.join(root, file_name)
#    return None

def calcUserArchiveSize(folder):
    suffix = ['B', 'KB', 'MB', 'GB']
    suffixIndex = 0
    size = 0

    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            size += os.path.getsize(file_path)

    while size >= 1024 and suffixIndex < len(suffix) - 1:
        size /= 1024.0
        suffixIndex += 1
    
    return "{:.2f} {}".format(size, suffix[suffixIndex])

# ERROR HANDLER
@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("general_error.html", error="Method not allowed.<br>Are you trying to use our APIs? See this guide: <a href='https://filez.leotecno.it/doc/using_api'>How to use our APIs</a>", error_code="405")

@app.route('/')
def welcome():
    if current_user.is_authenticated:
        return redirect('/dashboard?location=my_files')
    else:
        return render_template('welcome.html')

@app.route('/dashboard')
@login_required
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
        #next = request.args.get("next")

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
    return redirect(url_for('login'))

@app.route('/account/settings')
@login_required
def user_settings():
    return render_template("user-settings.html")

@app.route('/api/get_files')
@login_required                                      
def get_files():
    location = request.args.get('location', default='my_files')
    print(location)
    session_username = current_user.username
    print(session_username)

    files = []

    if location == "my_files":
        try:
            cur.execute('SELECT * FROM files WHERE owner = %s', (format(session_username),))
            rows = cur.fetchall()
        except Error as e:
            print("Error during SQL query: ", e)
            return jsonify({"result": "error", "error_text": e})

        for row in rows:                                        
            if row[3] == "trash":
                continue 

            files.append({
                'filename': row[0],
                'owner': row[1],
                'upload_date': row[2],
                'location': row[3],
                'file_code': row[4],
                'original_path': row[5],
                'shared': row[6],
            })

        archive_size = calcUserArchiveSize(f'users/uploads/{session_username}')    

        return jsonify(files=files, archive_size=calcUserArchiveSize(f'users/uploads/{session_username}'))

    elif location == "folders":
        folders = []

        try:
            cur.execute('SELECT * FROM folders WHERE owner = %s', (format(session_username),))
            rows = cur.fetchall()
        except Error as e:
            print("Error during SQL query: ", e)
            return jsonify({"result": "error", "error_text": e})

        for column in rows:
            folders.append({
                'folder_name': column[0],
                'owner': column[1],
                'creation_date': column[2],
                'shared': column[3],
                'foldercode': column[4]
            })

        return jsonify(files=folders, archive_size=calcUserArchiveSize(f'users/uploads/{session_username}'))

    elif location == "shared":
        try:
            print("HO CHIAMATO IL DB")
            cur.execute('SELECT * FROM files WHERE shared = %s AND owner = %s', (format("True"), format(session_username)))
            rows = cur.fetchall()
        except Error as e:
            print("Error during SQL query: ", e)
            return jsonify({"result": "error", "error_text": e})
        
        for row in rows:
            files.append({
                'filename': row[0],
                'owner': row[1],
                'upload_date': row[2],
                'location': row[3],
                'file_code': row[4],
                'original_path': row[5],
                'shared': row[6],       
            })
        
        return jsonify(files=files, archive_size=calcUserArchiveSize(f'users/uploads/{session_username}'))       

    else:
        try:
            cur.execute('SELECT * FROM files WHERE location = %s AND owner = %s', (format(location), format(session_username)))
            rows = cur.fetchall()
        except Error as e:
            print("Error during SQL query: ", e)
            return jsonify({"result": "error", "error_text": e})
        
        for row in rows:
            files.append({
                'filename': row[0],
                'owner': row[1],
                'upload_date': row[2],
                'location': row[3],
                'file_code': row[4],
                'original_path': row[5],
                'shared': row[6],      
            })
        
        return jsonify(files=files, archive_size=calcUserArchiveSize(f'users/uploads/{session_username}'))


        

@app.route('/api/upload_files', methods=['POST'])
def upload():
    #if 'file' not in request.files:
    #    return jsonify({"status": "error", "error_text": "No files selected."}), 400

    files = request.files.getlist('files')
    location = request.form['location']
    location_viewed = ""

    if location == "":
        location = "my_files"

    if location == "trash":
        return jsonify({"status": "error", "error_text": "You cannot upload files here."})

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
        filecode = ''.join([str(random.randint(0, 9)) for _ in range(15)])
        #file_extension = os.path.splitext(file.filename)[1]
        #filename_ok = filecode + file_extension

        upload_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #Location adjustments
        #if location == "my_files":
        #    location_viewed = "My files"
        #elif location == "shared":
        #    location_viewed = "Shared"
        #elif location == "trash":
        #    location_viewed = "Trash"


        '''file_data = {                       # AGGIUNGERE RAW
            "filename": file.filename,
            "owner": session_username,
            "upload_date": upload_date,
            "location": location_viewed,
            "file_code": filecode,
            "original_path": f"users/uploads/{session_username}/{location}/{filecode}{file_extension}",
            "raw_url": f"/r/{filecode}",
            "shared": False,
            "shared_with": None
        }'''

        shared = "False"
        original_path = f"users/uploads/{session_username}/{location}/{file.filename}"

        #json_filename = filecode + '.json'
        #json_path = os.path.join(upload_folder, json_filename)
        #with open(json_path, 'w') as json_file:
        #    json_file.write(json.dumps(file_data))

        cur.execute('INSERT INTO files (filename, owner, upload_date, location, file_code, original_path, shared)' 'VALUES (%s, %s, %s, %s, %s, %s, %s)', (format(file.filename), format(session_username), format(upload_date), format(location), int(filecode), format(original_path), format(shared)))
        conn.commit()

        file.save(os.path.join(upload_folder, file.filename))
    
    return jsonify({"status": "success"})

@app.route('/api/share_file', methods=['POST'])
@login_required
def share_file():
    filecode = request.form['filecode']
    shareUsersList = request.form['shareUsers']

    if shareUsersList:
        array_shareUsers = shareUsersList.split(",")
        array_shareUsers = [element.strip() for element in array_shareUsers]
        #print(array_shareUsers)

        if current_user.email in array_shareUsers:
            return jsonify({"result": "error", "error_text": "You cannot share a file with yourself."})

        shareUsers_id = []

        for user in array_shareUsers:   # Take users id from db
            try:
                cur.execute("SELECT id FROM users WHERE email = %s", (format(user),))
                results = cur.fetchone()
                if results:
                    shareUsers_id.append(results)
                    print(shareUsers_id)
                else:
                    return jsonify({"result": "error", "error_text": "A user on the list was not found."})
            except Error as e:
                print("Error during SQL query: ", e)
                return jsonify({"result": "error", "error_text": e})

        for user_id_tuple in shareUsers_id:
            user_id = user_id_tuple[0]
            print(user_id)
            try:
                cur.execute("INSERT INTO file_user_shared (file_code, user_id)" "VALUES (%s, %s)", (int(filecode), int(user_id)))
                conn.commit()
            except Error as e:
                print("Error during SQL query: ", e)
                return jsonify({"result": "error", "error_text": e})

    else:
        print("No users list.")

    cur.execute("UPDATE files SET shared = %s WHERE file_code = %s", (format("True"), int(filecode)))
    conn.commit()

    return jsonify({"result": "success"})

@app.route('/api/unshare_file', methods=['POST'])
@login_required
def unshare_file():
    filecode = request.form['filecode']
    #print(int(filecode))

    try:
        cur.execute("UPDATE files SET shared = %s WHERE file_code = %s", (format("False"), int(filecode)))
        conn.commit()
    except Error as e:
        print("Error during SQL query: ", e)
        return jsonify({"result": "error", "error_text": e})

    try:
        cur.execute("DELETE FROM file_user_shared WHERE file_code = %s", (filecode,))
        conn.commit()
    except Error as e:
        print("Error during SQL query: ", e)
        return jsonify({"result": "error", "error_text": e})
    
    return jsonify({"result": "success"})

@app.route('/api/move_to_trash', methods=['POST'])
def moveToTrash():
    filecode = request.form['filecode']
    filename = request.form['filename']
    trash_path = f"users/uploads/{current_user.username}/trash/"

    try:
        cur.execute("SELECT * FROM files WHERE file_code = %s", (filecode,))
        result = cur.fetchall()
        cur.execute("SELECT * FROM file_user_shared WHERE file_code = %s", (filecode,))
        resultShares = cur.fetchall()
    except Error as e:
        print("Error during SQL query: ", e)
        return jsonify({"result": "error", "error_text": e})
    
    for row in result:
        original_path = row[5]

    if not os.path.exists(trash_path):
        os.makedirs(trash_path)

    if resultShares:
        try:
            cur.execute("DELETE FROM file_user_shared WHERE file_code = %s", (filecode,))
            conn.commit()
        except Error as e:
            print("Error during SQL query: ", e)
            return jsonify({"result": "error", "error_text": e})

    
    try:
        cur.execute("UPDATE files SET location = %s WHERE file_code = %s", (format("trash"), int(filecode)))
        conn.commit()
    except Error as e:
        print("Error during SQL query: ", e)
        return jsonify({"result": "error", "error_text": e})

    shutil.move(original_path, trash_path)

    return jsonify({"status": "success"})

@app.route('/api/restore_file', methods=['POST'])
@login_required
def restore_file():
    filecode = request.form['filecode']
    filename = request.form['filename']

    my_files_path = f"users/uploads/{current_user.username}/my_files/"
    trash_path = f"users/uploads/{current_user.username}/trash/{filename}"

    try:
        cur.execute("UPDATE files SET location = %s WHERE file_code = %s", (format("my_files"), int(filecode)))
        conn.commit()
    except Error as e:
        print("Error during SQL query: ", e)
        return jsonify({"result": "error", "error_text": e})

    shutil.move(trash_path, my_files_path)

    return jsonify({"status": "success"})

@app.route('/api/delete_file', methods=['POST'])
@login_required
def delete_file():
    thing_type = request.form['type']
    filecode = request.form['filecode']
    filename = request.form['filename']
    password = request.form['password']

    user_id = current_user.id

    print(thing_type)
    
    try:
        cur.execute("SELECT * FROM users WHERE id = %s", (int(user_id),))
        result = cur.fetchall()
    except Error as e:
        print("Error during SQL query: ", e)
        return jsonify({"result": "error", "error_text": e})

    for column in result:           # oh, e funziona solo così
        storedPassword = column[3]

    if not check_password_hash(storedPassword, password):
        return jsonify({"result": "error", "error_text": "Wrong password."})
    
    else:
        
        if thing_type == "folder":
            thing_to_delete = f"users/uploads/{current_user.username}/{filename}"

            try:
                cur.execute("DELETE FROM folders WHERE foldercode = %s", (filecode,))
                cur.execute("DELETE FROM files WHERE location = %s", (filename,))
                conn.commit()
            except Error as e:
                print("Error during SQL query: ", e)
                return jsonify({"result": "error", "error_text": e})

            shutil.rmtree(thing_to_delete)

            return jsonify({"result": "success"})
        else:
            thing_to_delete = f"users/uploads/{current_user.username}/trash/{filename}"

            try:
                cur.execute("DELETE FROM files WHERE file_code = %s", (filecode,))
                conn.commit()
            except Error as e:
                print("Error during SQL query: ", e)
                return jsonify({"result": "error", "error_text": e})

            os.remove(thing_to_delete)

            return jsonify({"result": "success"})

@app.route('/api/create_folder', methods=['POST'])
@login_required
def create_folder():
    folder_name = request.form['folder_name']

    new_folder = f"users/uploads/{current_user.username}/{folder_name}" 

    if os.path.exists(new_folder):
        return jsonify({"result": "error", "error_text": "A folder with this name already exists."})
    
    else:
        creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        foldercode = ''.join([str(random.randint(0, 9)) for _ in range(13)])

        shared = "False"

        try:
            cur.execute('INSERT INTO folders (folder_name, owner, creation_date, shared, foldercode)' 'VALUES (%s, %s, %s, %s, %s)', (format(folder_name), format(current_user.username), format(creation_date), format(shared), int(foldercode),))
            conn.commit()
        except Error as e:
            print("Error during SQL query: ", e)
            return jsonify({"result": "error", "error_text": e})
                    
        os.mkdir(new_folder)
        return jsonify({"result": "success"})

@app.route('/r/<filecode>')
def get_raw_file(filecode):
    attachment = request.args.get('a')
    #session_username = current_user.username
    #session_id = current_user.id

    if attachment == "False":
        attachment = False
    else:
        attachment = True

    try:
        cur.execute("SELECT * FROM files WHERE file_code = %s", (int(filecode),))
        result = cur.fetchall()
    except Error as e:
        print("Error during SQL query: ", e)
        return jsonify({"result": "error", "error_text": e})
    
    if result:
        for row in result:
            filename = row[0]
            shared = row[6]
            owner = row[1]
            original_path = row[5]

        if current_user.is_authenticated:
            if owner == current_user.username:
                return send_file(original_path, as_attachment=attachment)

        if shared == "True":
                    
                    # CHECK IF THE USER CAN ACCESS IT
            try:
                cur.execute("SELECT * FROM file_user_shared WHERE file_code = %s", (int(filecode),))
                result = cur.fetchall()
            except Error as e:
                print("Error during SQL query: ", e)
                return jsonify({"result": "error", "error_text": e})

            if result:
                whoHasAccess = []
                for row in result:
                    user_id = row[1]
                    #print(user_id)
                    whoHasAccess.append(user_id)
                    #whoHasAccess.append("fakeuser")
                if current_user.is_authenticated:       
                    if int(current_user.id) in whoHasAccess:
                        #return "Hai l'accesso"
                        #return render_template('view_shared_file.html', filename=filename, filecode=filecode)
                        return send_file(original_path, as_attachment=attachment)
                    else:
                        return render_template("general_error.html", error="Cannot access this file", error_code="403")
                else:
                    return redirect(url_for('login'))
            else:
                return send_file(original_path, as_attachment=attachment)
        else:
            return render_template("general_error.html", error="File not shared", error_code="403")
    
    else:
        return render_template("general_error.html", error="File not found", error_code="404")
            
@app.route('/s/<filecode>')
def get_share(filecode):
    #session_username = current_user.username
    #session_id = current_user.id

    try:
        cur.execute("SELECT * FROM files WHERE file_code = %s", (int(filecode),))
        result = cur.fetchall()
    except Error as e:
        print("Error during SQL query: ", e)
        return jsonify({"result": "error", "error_text": e})
    
    if result:
        for row in result:
            filename = row[0]
            shared = row[6]
            owner = row[1]
        
        file_ext = filename.split('.')
        file_ext = file_ext[1].upper()
        print(file_ext)

        if shared == "True":
            if current_user.is_authenticated:
                if owner == current_user.username:
                    return render_template('view_shared_file.html', filename=filename, filecode=filecode, type=file_ext)
                
            # CHECK IF THE USER CAN ACCESS IT
            try:
                cur.execute("SELECT * FROM file_user_shared WHERE file_code = %s", (int(filecode),))
                result = cur.fetchall()
            except Error as e:
                print("Error during SQL query: ", e)
                return jsonify({"result": "error", "error_text": e})

            if result:
                whoHasAccess = []
                for row in result:
                    user_id = row[1]
                    #print(user_id)
                    whoHasAccess.append(user_id)
                    #whoHasAccess.append("fakeuser")
                if current_user.is_authenticated:    
                    if int(current_user.id) in whoHasAccess:
                        #return "Hai l'accesso"
                        return render_template('view_shared_file.html', filename=filename, filecode=filecode, type=file_ext)
                
                    else:
                        return render_template("general_error.html", error="Cannot access this file", error_code="403")
                else:
                    return redirect(url_for('login'))
            else:
                return render_template('view_shared_file.html', filename=filename, filecode=filecode, type=file_ext)
        else:
            return render_template("general_error.html", error="File not shared", error_code="403")
    
    else:
        return render_template("general_error.html", error="File not found", error_code="404")
    
        
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=True)
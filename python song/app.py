from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
PLAYLIST_FILE = 'playlist.json'
ALLOWED_EXTENSIONS = {'mp3'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_playlist(playlist):
    with open(PLAYLIST_FILE, 'w') as f:
        json.dump(playlist, f)

def load_playlist():
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, 'r') as f:
            return json.load(f)
    return []

@app.route('/')
def index():
    playlist = load_playlist()
    return render_template('index.html', playlist=playlist)

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            playlist = load_playlist()
            playlist.append({'name': filename, 'path': file_path})
            save_playlist(playlist)
            return jsonify({'success': 'File uploaded successfully'})
        else:
            return jsonify({'error': 'File type not allowed'})

@app.route('/playlist')
def playlist():
    playlist = load_playlist()
    return jsonify(playlist)

@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete', methods=['POST'])
def delete_file():
    if request.method == 'POST':
        data = request.get_json()
        file_path = data.get('path')
        if file_path:
            try:
                os.remove(file_path)
                playlist = load_playlist()
                updated_playlist = [track for track in playlist if track['path'] != file_path]
                save_playlist(updated_playlist)
                return jsonify({'success': 'File deleted successfully'})
            except OSError as e:
                return jsonify({'error': str(e)})
        else:
            return jsonify({'error': 'File path not provided'})

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)

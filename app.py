#!/usr/bin/env python3
"""
Flask File Explorer Web Server
Access, upload, download, and preview files from all storage drives
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from pathlib import Path
import os
import mimetypes
import json
from datetime import datetime
import subprocess
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this-in-production')

# Configuration
FLASK_PASSWORD = os.getenv('FLASK_PASSWORD', 'admin')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/mnt/storage_1/uploads')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 5368709120))  # 5GB default

# Storage drive mounts
STORAGE_DRIVES = {
    'storage_1': '/mnt/storage_1',
    'storage_2': '/mnt/storage_2',
    'storage_3': '/mnt/storage_3',
    'storage_4': '/mnt/storage_4',
    'sde3_docs': '/mnt/sde3_docs',
    'sde5_docs': '/mnt/sde5_docs',
}

# File preview extensions
PREVIEW_EXTENSIONS = {
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'],
    'videos': ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv'],
    'text': ['.txt', '.md', '.log', '.csv', '.json', '.xml', '.html', '.py', '.js', '.sh', '.conf'],
    'pdf': ['.pdf'],
}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper Functions
def get_file_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def get_file_icon(filename):
    """Get appropriate icon for file type"""
    ext = Path(filename).suffix.lower()
    
    if ext in PREVIEW_EXTENSIONS['images']:
        return '🖼️'
    elif ext in PREVIEW_EXTENSIONS['videos']:
        return '🎥'
    elif ext in PREVIEW_EXTENSIONS['pdf']:
        return '📄'
    elif ext in PREVIEW_EXTENSIONS['text']:
        return '📝'
    elif ext in ['.zip', '.tar', '.gz', '.rar', '.7z']:
        return '📦'
    elif ext in ['.mp3', '.wav', '.flac', '.aac']:
        return '🎵'
    else:
        return '📁'

def can_preview(filename):
    """Check if file can be previewed in browser"""
    ext = Path(filename).suffix.lower()
    all_previewable = (PREVIEW_EXTENSIONS['images'] + 
                       PREVIEW_EXTENSIONS['videos'] + 
                       PREVIEW_EXTENSIONS['text'] + 
                       PREVIEW_EXTENSIONS['pdf'])
    return ext in all_previewable

def get_drive_info(drive_path):
    """Get storage info for a drive"""
    try:
        result = subprocess.run(
            ['df', drive_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            total = int(parts[1]) * 1024
            used = int(parts[2]) * 1024
            available = int(parts[3]) * 1024
            percent = int(parts[4].rstrip('%'))
            
            return {
                'total': get_file_size(total),
                'used': get_file_size(used),
                'available': get_file_size(available),
                'percent': percent,
                'raw_total': total,
                'raw_used': used,
                'raw_available': available,
            }
    except Exception as e:
        return None
    return None

def is_safe_path(base_path, target_path):
    """Prevent directory traversal attacks"""
    base = Path(base_path).resolve()
    target = Path(target_path).resolve()
    try:
        target.relative_to(base)
        return True
    except ValueError:
        return False

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == FLASK_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Main dashboard"""
    drives_info = {}
    for drive_name, drive_path in STORAGE_DRIVES.items():
        if os.path.exists(drive_path):
            drives_info[drive_name] = {
                'path': drive_path,
                'info': get_drive_info(drive_path)
            }
    
    return render_template('index.html', drives=drives_info)

@app.route('/api/browse', methods=['GET'])
@login_required
def browse():
    """Browse files and folders"""
    drive = request.args.get('drive', 'storage_1')
    path = request.args.get('path', '')
    
    # Validate drive
    if drive not in STORAGE_DRIVES:
        return jsonify({'error': 'Invalid drive'}), 400
    
    base_path = STORAGE_DRIVES[drive]
    full_path = os.path.join(base_path, path) if path else base_path
    
    # Security check
    if not is_safe_path(base_path, full_path):
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if path exists
    if not os.path.exists(full_path):
        return jsonify({'error': 'Path not found'}), 404
    
    try:
        items = []
        for item in sorted(os.listdir(full_path)):
            item_path = os.path.join(full_path, item)
            try:
                if os.path.isdir(item_path):
                    items.append({
                        'name': item,
                        'type': 'folder',
                        'icon': '📁',
                        'path': os.path.join(path, item) if path else item,
                        'modified': datetime.fromtimestamp(os.path.getmtime(item_path)).isoformat(),
                    })
                else:
                    size = os.path.getsize(item_path)
                    items.append({
                        'name': item,
                        'type': 'file',
                        'size': size,
                        'size_human': get_file_size(size),
                        'icon': get_file_icon(item),
                        'can_preview': can_preview(item),
                        'path': os.path.join(path, item) if path else item,
                        'modified': datetime.fromtimestamp(os.path.getmtime(item_path)).isoformat(),
                    })
            except (OSError, IOError) as e:
                continue
        
        return jsonify({
            'items': items,
            'path': path,
            'drive': drive,
            'full_path': full_path,
        })
    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    """Upload file to storage"""
    drive = request.form.get('drive', 'storage_1')
    path = request.form.get('path', '')
    file = request.files.get('file')
    
    if not file:
        return jsonify({'error': 'No file provided'}), 400
    
    # Validate drive
    if drive not in STORAGE_DRIVES:
        return jsonify({'error': 'Invalid drive'}), 400
    
    base_path = STORAGE_DRIVES[drive]
    upload_path = os.path.join(base_path, path) if path else base_path
    
    # Security check
    if not is_safe_path(base_path, upload_path):
        return jsonify({'error': 'Access denied'}), 403
    
    # Create directory if needed
    os.makedirs(upload_path, exist_ok=True)
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_path, filename)
    
    try:
        file.save(file_path)
        return jsonify({
            'success': True,
            'message': f'File uploaded: {filename}',
            'filename': filename,
            'size': os.path.getsize(file_path),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download')
@login_required
def download_file():
    """Download file"""
    drive = request.args.get('drive', 'storage_1')
    path = request.args.get('path', '')
    
    if not drive or not path:
        return jsonify({'error': 'Missing parameters'}), 400
    
    # Validate drive
    if drive not in STORAGE_DRIVES:
        return jsonify({'error': 'Invalid drive'}), 400
    
    base_path = STORAGE_DRIVES[drive]
    file_path = os.path.join(base_path, path)
    
    # Security check
    if not is_safe_path(base_path, file_path):
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if file exists and is a file
    if not os.path.isfile(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preview')
@login_required
def preview_file():
    """Get file for preview"""
    drive = request.args.get('drive', 'storage_1')
    path = request.args.get('path', '')
    
    if not drive or not path:
        return jsonify({'error': 'Missing parameters'}), 400
    
    if drive not in STORAGE_DRIVES:
        return jsonify({'error': 'Invalid drive'}), 400
    
    base_path = STORAGE_DRIVES[drive]
    file_path = os.path.join(base_path, path)
    
    if not is_safe_path(base_path, file_path):
        return jsonify({'error': 'Access denied'}), 403
    
    if not os.path.isfile(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    if not can_preview(file_path):
        return jsonify({'error': 'Preview not supported'}), 400
    
    try:
        return send_file(file_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete', methods=['POST'])
@login_required
def delete_item():
    """Delete file or folder"""
    data = request.get_json()
    drive = data.get('drive', 'storage_1')
    path = data.get('path', '')
    
    if not drive or not path:
        return jsonify({'error': 'Missing parameters'}), 400
    
    if drive not in STORAGE_DRIVES:
        return jsonify({'error': 'Invalid drive'}), 400
    
    base_path = STORAGE_DRIVES[drive]
    item_path = os.path.join(base_path, path)
    
    if not is_safe_path(base_path, item_path):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            import shutil
            shutil.rmtree(item_path)
        else:
            return jsonify({'error': 'Item not found'}), 404
        
        return jsonify({'success': True, 'message': 'Item deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mkdir', methods=['POST'])
@login_required
def mkdir():
    """Create new folder"""
    data = request.get_json()
    drive = data.get('drive', 'storage_1')
    path = data.get('path', '')
    folder_name = data.get('folder_name', '')
    
    if not drive or not folder_name:
        return jsonify({'error': 'Missing parameters'}), 400
    
    if drive not in STORAGE_DRIVES:
        return jsonify({'error': 'Invalid drive'}), 400
    
    folder_name = secure_filename(folder_name)
    
    base_path = STORAGE_DRIVES[drive]
    folder_path = os.path.join(base_path, path, folder_name) if path else os.path.join(base_path, folder_name)
    
    if not is_safe_path(base_path, folder_path):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        os.makedirs(folder_path, exist_ok=True)
        return jsonify({'success': True, 'message': 'Folder created'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large"""
    return jsonify({'error': f'File too large. Maximum size: {get_file_size(MAX_FILE_SIZE)}'}), 413

if __name__ == '__main__':
    print(f"🚀 File Explorer Server starting...")
    print(f"📁 Storage drives: {list(STORAGE_DRIVES.keys())}")
    print(f"🔐 Password protected: Yes")
    print(f"📤 Max upload size: {get_file_size(MAX_FILE_SIZE)}")
    print(f"🌐 Access at: http://0.0.0.0:1234")
    print(f"⚠️  Change FLASK_PASSWORD in .env file!")
    
    app.run(host='0.0.0.0', port=1234, debug=False)

# “””
Wall Verification System - Backend

Flask app for managing wall JSONs and photo analysis.

Features:

- Upload expected JSON for a wall (persists)
- List saved walls
- Delete walls
- Analyze photos against saved walls
- Return PASS/WARNING/FAIL results

Run locally:
pip install flask flask-cors opencv-python numpy pillow
python app.py

Then visit: http://localhost:5000
“””

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import shutil
from pathlib import Path
from datetime import datetime

# ============================================================

# SETUP

# ============================================================

app = Flask(**name**)
CORS(app)

# Storage paths

STORAGE_DIR = Path(’./wall_storage’)
WALLS_DB = STORAGE_DIR / ‘walls.json’

# Create storage directory

STORAGE_DIR.mkdir(exist_ok=True)

# Initialize walls database if it doesn’t exist

if not WALLS_DB.exists():
WALLS_DB.write_text(json.dumps({}))

def load_walls_db():
“”“Load all walls from storage”””
return json.loads(WALLS_DB.read_text())

def save_walls_db(data):
“”“Save walls to storage”””
WALLS_DB.write_text(json.dumps(data, indent=2))

# ============================================================

# ROUTES

# ============================================================

@app.route(’/’, methods=[‘GET’])
def index():
“”“Serve the frontend HTML”””
html = “””

<!DOCTYPE html>

<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wall Verification System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

```
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #f5f5f5;
        padding: 20px;
    }
    
    .container {
        max-width: 600px;
        margin: 0 auto;
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    h1 {
        color: #1f77b4;
        margin-bottom: 8px;
        font-size: 28px;
    }
    
    .subtitle {
        color: #666;
        margin-bottom: 24px;
        font-size: 14px;
    }
    
    .section {
        margin-bottom: 32px;
    }
    
    .section-title {
        color: #333;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .upload-area {
        border: 2px dashed #1f77b4;
        border-radius: 8px;
        padding: 24px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
        background: #f9f9f9;
    }
    
    .upload-area:hover {
        background: #f0f5ff;
        border-color: #0d47a1;
    }
    
    .upload-area input {
        display: none;
    }
    
    .upload-button {
        background: #1f77b4;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 6px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        width: 100%;
    }
    
    .upload-button:hover {
        background: #0d47a1;
    }
    
    .upload-button:active {
        transform: scale(0.98);
    }
    
    .walls-list {
        list-style: none;
    }
    
    .wall-item {
        background: #f9f9f9;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .wall-info {
        flex: 1;
    }
    
    .wall-id {
        font-weight: 600;
        color: #333;
        font-size: 16px;
    }
    
    .wall-meta {
        font-size: 12px;
        color: #999;
        margin-top: 4px;
    }
    
    .wall-actions {
        display: flex;
        gap: 8px;
    }
    
    .btn-select {
        background: #2ecc71;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .btn-select:hover {
        background: #27ae60;
    }
    
    .btn-delete {
        background: #e74c3c;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .btn-delete:hover {
        background: #c0392b;
    }
    
    .empty-state {
        text-align: center;
        color: #999;
        padding: 32px 16px;
    }
    
    .empty-state-icon {
        font-size: 48px;
        margin-bottom: 12px;
    }
    
    .message {
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 16px;
        font-size: 14px;
    }
    
    .message.success {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .message.error {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .message.loading {
        background: #cfe2ff;
        color: #084298;
        border: 1px solid #b6d4fe;
    }
</style>
```

</head>
<body>
    <div class="container">
        <h1>🏗️ Wall Verification</h1>
        <p class="subtitle">Upload expected wall JSONs and select to analyze photos</p>

```
    <div id="message"></div>
    
    <!-- SECTION 1: Upload JSON -->
    <div class="section">
        <div class="section-title">Step 1: Upload Wall JSON</div>
        <div class="upload-area" onclick="document.getElementById('jsonInput').click()">
            <input type="file" id="jsonInput" accept=".json" />
            <button class="upload-button">📁 Choose Expected JSON File</button>
            <p style="margin-top: 12px; color: #999; font-size: 13px;">
                Select a wall's expected JSON file
            </p>
        </div>
    </div>
    
    <!-- SECTION 2: Saved Walls -->
    <div class="section">
        <div class="section-title">Step 2: Select Wall to Analyze</div>
        <ul id="wallsList" class="walls-list"></ul>
        <div id="emptyState" class="empty-state">
            <div class="empty-state-icon">📄</div>
            <p>No walls uploaded yet.<br>Upload a wall JSON to get started.</p>
        </div>
    </div>
</div>

<script>
    // File input handler
    document.getElementById('jsonInput').addEventListener('change', handleJsonUpload);
    
    // Load walls on page load
    loadWalls();
    
    async function handleJsonUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        showMessage('⏳ Uploading...', 'loading');
        
        const formData = new FormData();
        formData.append('json_file', file);
        
        try {
            const response = await fetch('/api/walls', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showMessage(`✅ Wall saved: ${result.wall_id}`, 'success');
                document.getElementById('jsonInput').value = '';
                loadWalls();
            } else {
                showMessage(`❌ Error: ${result.error}`, 'error');
            }
        } catch (error) {
            showMessage(`❌ Error: ${error.message}`, 'error');
        }
    }
    
    async function loadWalls() {
        try {
            const response = await fetch('/api/walls');
            const data = await response.json();
            
            const wallsList = document.getElementById('wallsList');
            const emptyState = document.getElementById('emptyState');
            
            wallsList.innerHTML = '';
            
            if (data.walls.length === 0) {
                emptyState.style.display = 'block';
            } else {
                emptyState.style.display = 'none';
                
                data.walls.forEach(wall => {
                    const li = document.createElement('li');
                    li.className = 'wall-item';
                    li.innerHTML = `
                        <div class="wall-info">
                            <div class="wall-id">${wall.room || wall.wall_name || wall.wall_id}</div>
                            <div class="wall-meta">
                                ${wall.openings_count || '?'} opening(s) expected
                                · uploaded ${new Date(wall.uploaded_at).toLocaleDateString()}
                            </div>
                        </div>
                        <div class="wall-actions">
                            <button class="btn-select" onclick="selectWall('${wall.wall_id}')">
                                📸 Analyze
                            </button>
                            <button class="btn-delete" onclick="deleteWall('${wall.wall_id}')">
                                🗑️
                            </button>
                        </div>
                    `;
                    wallsList.appendChild(li);
                });
            }
        } catch (error) {
            showMessage(`❌ Error loading walls: ${error.message}`, 'error');
        }
    }
    
    function selectWall(wallId) {
        // TODO: Navigate to photo upload screen (Step B)
        alert(`Selected wall: ${wallId}\n\nStep B (photo upload) coming soon!`);
    }
    
    async function deleteWall(wallId) {
        if (!confirm(`Delete this wall?`)) return;
        
        try {
            const response = await fetch(`/api/walls/${wallId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showMessage('✅ Wall deleted', 'success');
                loadWalls();
            } else {
                showMessage(`❌ Error: ${result.error}`, 'error');
            }
        } catch (error) {
            showMessage(`❌ Error: ${error.message}`, 'error');
        }
    }
    
    function showMessage(text, type) {
        const messageEl = document.getElementById('message');
        messageEl.textContent = text;
        messageEl.className = `message ${type}`;
        messageEl.style.display = 'block';
        
        if (type !== 'loading') {
            setTimeout(() => {
                messageEl.style.display = 'none';
            }, 4000);
        }
    }
</script>
```

</body>
</html>
    """
    return html

@app.route(’/api/walls’, methods=[‘GET’])
def list_walls():
“”“List all saved walls”””
walls_db = load_walls_db()
walls_list = []

```
for wall_id, wall_data in walls_db.items():
    walls_list.append({
        'wall_id': wall_id,
        'room': wall_data.get('room', ''),
        'wall_name': wall_data.get('wall_name', ''),
        'openings_count': len(wall_data.get('openings', [])),
        'uploaded_at': wall_data.get('uploaded_at', ''),
    })

return jsonify({'walls': walls_list}), 200
```

@app.route(’/api/walls’, methods=[‘POST’])
def upload_wall_json():
“”“Upload a new wall JSON”””
if ‘json_file’ not in request.files:
return jsonify({‘error’: ‘No JSON file provided’}), 400

```
file = request.files['json_file']
if file.filename == '':
    return jsonify({'error': 'No file selected'}), 400

try:
    # Read and parse JSON
    expected_data = json.load(file)
    wall_id = expected_data.get('wall_id')
    
    if not wall_id:
        return jsonify({'error': 'JSON must contain "wall_id" field'}), 400
    
    # Add upload timestamp
    expected_data['uploaded_at'] = datetime.now().isoformat()
    
    # Save to database
    walls_db = load_walls_db()
    walls_db[wall_id] = expected_data
    save_walls_db(walls_db)
    
    return jsonify({
        'success': True,
        'wall_id': wall_id,
        'message': f'Wall "{wall_id}" saved successfully'
    }), 200

except json.JSONDecodeError:
    return jsonify({'error': 'Invalid JSON file'}), 400
except Exception as e:
    return jsonify({'error': str(e)}), 500
```

@app.route(’/api/walls/<wall_id>’, methods=[‘DELETE’])
def delete_wall(wall_id):
“”“Delete a wall”””
walls_db = load_walls_db()

```
if wall_id not in walls_db:
    return jsonify({'error': 'Wall not found'}), 404

del walls_db[wall_id]
save_walls_db(walls_db)

return jsonify({'success': True, 'message': 'Wall deleted'}), 200
```

# ============================================================

# RUN

# ============================================================

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Wall Verification System starting...")
    print(f"📍 http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)

from flask import Flask, render_template, request, jsonify
import os, shutil
from multimodal_gemini import PrescriptionBot
from markdown import markdown

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/tmp_uploads'

@app.route('/')
def home():
    global bot
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        shutil.rmtree(app.config['UPLOAD_FOLDER'])
    os.makedirs(app.config['UPLOAD_FOLDER'])
    bot = PrescriptionBot()
    return render_template('index.html')
# Only create interface to upload photo
@app.route('/upload_media', methods=['POST'])
def upload_media():
    if 'media' not in request.files:
        return jsonify({'error': 'No media part'}), 400
    file = request.files['media']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = file.filename
        file_address = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_address)
        # Analyze the uploaded prescription image
        response = bot.process_file(file_address)
        # Format response into readable output
        prescription_details = "# Prescription Details\n\n" + "\n\n".join(
            [f"## {key.replace('_', ' ')}\n\n{value}" for key, value in response.items()]
        )
        return jsonify({'message': markdown(prescription_details)}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

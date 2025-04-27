import os
from datetime import datetime
import logging
from flask import Flask, render_template, send_file, request, abort
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from utils import network, storage

# Initialize storage and network components
storage_dir_name, storage_path = storage.init()
ip_addr = network.get_local_ipv4()
port = 8000

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))  # Set a secure secret key via env var

# Allowed file extensions for image and video files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'mp4', 'mov', 'avi', 'mkv', 'flv'}
MAX_CONTENT_LENGTH = 256 * 1024 * 1024  # 16MB file size limit
app.config['UPLOAD_FOLDER'] = storage_path
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
@app.route("/up")
def upload_func():
    return render_template("upload.html", ip_addr=ip_addr, port=port, files_dir_name=storage_dir_name)


@app.route("/uploader", methods=["GET", "POST"])
def uploader():
    if request.method == "POST":
        # Ensure file exists in the request
        if 'file' not in request.files:
            return render_template("upload.html", message="No selected file", ip_addr=ip_addr, port=port)

        file = request.files["file"]

        # If no file selected
        if file.filename == "":
            return render_template("upload.html", message="No selected file", ip_addr=ip_addr, port=port)

        # Ensure file type is allowed
        if not allowed_file(file.filename):
            return render_template("upload.html", message="Invalid file type", ip_addr=ip_addr, port=port)

        # Secure and save the file
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(storage_path, filename)

            # Save the file securely
            file.save(file_path)
            logger.info(f"File {filename} saved successfully.")

            return render_template("up_done.html", ip_addr=ip_addr, port=port, files_dir_name=storage_dir_name)

        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return render_template("upload.html", message=f"Error: {str(e)}", ip_addr=ip_addr, port=port)

    return render_template("upload.html", ip_addr=ip_addr, port=port)


@app.route('/save-text', methods=['POST'])
def save_text():
    user_text = request.form.get('user_text')
    if user_text:
        file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path = os.path.join(storage_path, file_name)
        with open(file_path, 'w') as f:
            f.write(user_text)
        return render_template("up_done.html", ip_addr=ip_addr, port=port, files_dir_name=storage_dir_name)
    
    e = "No text is provided"
    logger.error(e)
    return render_template("upload.html", message=f"Error: {e}", ip_addr=ip_addr, port=port)


@app.route("/<path:req_path>")
def index_files_func(req_path):
    base_dir = "./"
    abs_path = os.path.join(base_dir, req_path)

    # Check if file path exists
    if not os.path.exists(abs_path):
        return abort(404, description="File not found")

    # If it's a file, serve it
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # If it's a directory, list files
    files = os.listdir(abs_path)
    return render_template("index_files.html", files=files)


# Custom error handler for 413 (Request Entity Too Large)
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    return render_template("upload.html", message="File is too large. Please upload a smaller file.", ip_addr=ip_addr, port=port)


if __name__ == "__main__":
    app.run(host=ip_addr, port=port, debug=True)

import os
from flask import Flask, render_template, send_file, request
from werkzeug.utils import secure_filename

from utils import network, storage


storage_dir_name, storage_path = storage.init()
ip_addr = network.get_local_ipv4()
port = network.port

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route("/")
@app.route("/up")
def upload_func():
    return render_template("upload.html", ip_addr=ip_addr, port=port, files_dir_name=storage_dir_name)


@app.route("/uploader", methods=["GET", "POST"])
def uploader():
    if request.method == "POST":

        if 'file' not in request.files:
            return render_template("upload.html", message="No selected file", ip_addr=ip_addr, port=port)

        file = request.files["file"]

        if file.filename == "":
            return render_template("upload.html", message="No selected file", ip_addr=ip_addr, port=port)

        if file:
            try:
                print("Started saving file ... ")

                # Use a streaming approach to save the file in chunks
                file_path = os.path.join(storage_path, file.filename)
                with open(file_path, "wb") as f:
                    while True:
                        chunk = file.stream.read(1024)  # Read 1KB at a time
                        if not chunk:
                            break
                        f.write(chunk)

                print("File saved successfully.")

            except Exception as e:
                return render_template("upload.html", message=f"Error: {str(e)}", ip_addr=ip_addr, port=port)

    return render_template("up_done.html", ip_addr=ip_addr, port=port)


@app.route("/<path:req_path>")
def index_files_func(req_path):
    base_dir = "./"
    abs_path = os.path.join(base_dir, req_path)

    if not os.path.exists(abs_path):
        return f"{abs_path}"
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    files = os.listdir(abs_path)
    return render_template("index_files.html", files=files)


if __name__ == "__main__":
    app.run(host=ip_addr, port=port, debug=True)

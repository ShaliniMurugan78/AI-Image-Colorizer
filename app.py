from flask import Flask, render_template, request, send_from_directory
import os
import cv2
import numpy as np
from cv2 import dnn
import gdown

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------------------------------
# AUTO DOWNLOAD MODEL (GOOGLE DRIVE SAFE)
# ---------------------------------------
def download_model():
    model_path = "Models/colorization_release_v2.caffemodel"
    file_id = "1iGCjwOe0N5A1KdJ988gX9tXoFut3tyFk"

    if os.path.exists(model_path) and os.path.getsize(model_path) > 100_000_000:
        print("Model already exists. Skipping download.")
        return

    print("Downloading model from Google Drive...")
    os.makedirs("Models", exist_ok=True)

    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, model_path, quiet=False)

    print("Model downloaded successfully.")

# ---------------------------------------
# LOAD MODEL
# ---------------------------------------
proto = "Models/colorization_deploy_v2.prototxt"
model = "Models/colorization_release_v2.caffemodel"
pts = "Models/pts_in_hull.npy"

download_model()

net = dnn.readNetFromCaffe(proto, model)

pts_in_hull = np.load(pts)
class8 = net.getLayerId("class8_ab")
conv8 = net.getLayerId("conv8_313_rh")

pts_in_hull = pts_in_hull.transpose().reshape(2, 313, 1, 1)
net.getLayer(class8).blobs = [pts_in_hull.astype(np.float32)]
net.getLayer(conv8).blobs = [np.full((1, 313), 2.606, np.float32)]

# ---------------------------------------
# COLORIZE FUNCTION
# ---------------------------------------
def colorize(img_path):
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError("Image not found")

    h, w = img.shape[:2]

    img_rgb = img.astype("float32") / 255.0
    lab = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2LAB)

    L = lab[:, :, 0]
    L_resized = cv2.resize(L, (224, 224))
    L_resized -= 50

    blob = np.zeros((1, 1, 224, 224), dtype=np.float32)
    blob[0, 0, :, :] = L_resized

    net.setInput(blob)
    ab = net.forward()[0].transpose((1, 2, 0))

    ab = cv2.resize(ab, (w, h))
    lab_out = np.concatenate((L[:, :, np.newaxis], ab), axis=2)

    colorized = cv2.cvtColor(lab_out, cv2.COLOR_LAB2BGR)
    colorized = np.clip(colorized, 0, 1)

    return (colorized * 255).astype("uint8")

# ---------------------------------------
# FILTERS
# ---------------------------------------
def apply_filter(img, filter_type):
    if filter_type == "warm":
        img[:, :, 2] = cv2.add(img[:, :, 2], 30)
    elif filter_type == "cool":
        img[:, :, 0] = cv2.add(img[:, :, 0], 30)
    elif filter_type == "vintage":
        img = cv2.applyColorMap(img, cv2.COLORMAP_PINK)
    elif filter_type == "hdr":
        img = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.25)
    return img

# ---------------------------------------
# ROUTES
# ---------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["image"]
    filter_type = request.form.get("filter", "none")

    filename = file.filename
    name, _ = os.path.splitext(filename)

    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    colorized = colorize(input_path)

    if filter_type != "none":
        colorized = apply_filter(colorized, filter_type)

    out_name = f"colorized_{name}.jpg"
    out_path = os.path.join(UPLOAD_FOLDER, out_name)
    cv2.imwrite(out_path, colorized)

    return render_template("index.html", output_image=out_name)

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

# ---------------------------------------
# MAIN
# ---------------------------------------
if __name__ == "__main__":
    app.run()

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from pymongo import MongoClient
from dotenv import load_dotenv

from extractor import extract_contact_details

# -------------------------------
# Load ENV
# -------------------------------
load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------------
# MongoDB Setup (FIXED)
# -------------------------------
client = MongoClient(
    os.getenv("MONGO_URI"),
    tls=True,
    tlsAllowInvalidCertificates=True
)

db = client["visiting_cards"]
collection = db["contacts"]

# -------------------------------
# API Route
# -------------------------------
@app.route("/upload", methods=["POST"])
def upload_image():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    # 🔥 Extract data
    data = extract_contact_details(filepath)
    print(data)

    if not data:
        return jsonify({"error": "Extraction failed"}), 500

    # 🔥 Store in MongoDB
    result = collection.insert_one(data)

    # ✅ Fix ObjectId
    data["_id"] = str(result.inserted_id)

    # ✅ Optional: delete file after processing
    os.remove(filepath)

    response_data = {
        "message": "Success",
        "data": data
    }

    return jsonify(response_data)

# -------------------------------
# Health Check (optional)
# -------------------------------
@app.route("/")
def home():
    return jsonify({"message": "API is running 🚀"})

# -------------------------------
# Run Server
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import json
import os
import subprocess
from datetime import datetime
 
app = Flask(__name__)
CORS(app)
 
DATA_FILE = "berkeley_lost.json"
 
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"scraped_at": None, "posts": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)
 
@app.route("/")
def index():
    return render_template("index.html")
 
@app.route("/api/posts")
def get_posts():
    data = load_data()
    return jsonify(data)
 
@app.route("/api/refresh", methods=["POST"])
def refresh():
    try:
        subprocess.run(["python", "scraper.py"], timeout=120)
        data = load_data()
        return jsonify({"success": True, "count": len(data["posts"]), "scraped_at": data["scraped_at"]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
 
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
 
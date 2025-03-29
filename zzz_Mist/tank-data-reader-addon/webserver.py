from flask import Flask, jsonify
import os, json

app = Flask(__name__)
DATA_DIR = "/tmp/tank_data"

@app.route("/")
def index():
    return open("/www/index.html").read()

@app.route("/api/transactions")
def api():
    results = []
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".json"):
            with open(os.path.join(DATA_DIR, fname)) as f:
                try:
                    results.append(json.load(f))
                except:
                    continue
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

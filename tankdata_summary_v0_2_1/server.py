
from flask import Flask, render_template_string
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    dummy_data = [
        {"timestamp": "27.03.2025 16:11:05", "column": "2", "article": "MOGAS", "amount": "30.04", "plate": "OE-ALJ"},
        {"timestamp": "26.03.2025 14:21:09", "column": "2", "article": "MOGAS", "amount": "36.00", "plate": "OE-DKT"}
    ]
    with open("www/index.html") as f:
        template = f.read()
    return render_template_string(template, data=dummy_data, update_time=datetime.now().strftime("%d.%m.%Y, %H:%M:%S"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

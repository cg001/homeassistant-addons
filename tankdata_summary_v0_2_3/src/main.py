
from flask import Flask, render_template_string
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    dummy = [{
        "filename": "Transactions_20250328_163042.XML",
        "rows": [
            {"id": "1", "amount": "50", "timestamp": "2025-03-28 10:00"},
            {"id": "2", "amount": "20", "timestamp": "2025-03-28 11:00"}
        ]
    }]
    template_html = open("www/index.html").read()
    return render_template_string(template_html, data=dummy)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

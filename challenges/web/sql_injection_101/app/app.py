from flask import Flask, request, render_template_string
import os

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "CTF{4b3901cc21097ac7b8fab05e}")

INDEX = """<!DOCTYPE html>
<html><head><title>SQL Injection 101</title></head>
<body><h1>SQL Injection 101</h1><p>Find the flag!</p></body></html>"""

@app.route("/")
def index():
    return render_template_string(INDEX)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, request, render_template_string
import os

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "CTF{8c231da0a491b6818af83fe1}")

INDEX = """<!DOCTYPE html>
<html><head><title>JWT Bypass</title></head>
<body><h1>JWT Bypass</h1><p>Find the flag!</p></body></html>"""

@app.route("/")
def index():
    return render_template_string(INDEX)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, flash, request, redirect, url_for
from hide_faces import hide_faces

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello!'

@app.route('/hide', methods=['POST'])
def hide():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('no file part')
            return redirect(request.url)
    return 'hide faces here'
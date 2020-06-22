from flask import Flask 
from hide_faces import hide_faces

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello!'

@app.route('/hide')
def hide():
    return 'hide faces here'
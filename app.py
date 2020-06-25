import os
from flask import Flask, flash, request, redirect, url_for
import imghdr
from werkzeug.utils import secure_filename

from hide_faces import hide_faces

app = Flask(__name__)
app.config['TEMP_FOLDER'] = 'tmp/'
app.config['OUTPUT_FOLDER'] = 'out/'

@app.route('/')
def hello():
    return 'Hello!'

@app.route('/hide', methods=['POST'])
def hide():
    if 'file' not in request.files:
        return 'y no file'
    
    file = request.files['file']

    if file.filename == '':
        return 'no selected file'
    
    if file:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['TEMP_FOLDER'], filename)
        file.save(path)
        output_string = 'yes, it image' if imghdr.what(path) is not None else 'oops not image'
        os.remove(path) 
        return output_string 
    

    # check if image

    # save image to temp directory

    # process image to output directory

    # delete temp image

    # save output image name/id to db

    # return url to user
    
    return 'hide faces here'
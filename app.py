import os
from datetime import datetime, timedelta 
import uuid 
from flask import Flask, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 
import imghdr
from werkzeug.utils import secure_filename

from hide_faces import hide_faces


cascades = [
    'data/haarcascades/haarcascade_profileface.xml',
    'data/haarcascades/haarcascade_frontalface_default.xml',
    'data/lbpcascades/lbpcascade_frontalface_improved.xml'
]


app = Flask(__name__)
app.config['TEMP_FOLDER'] = 'tmp_data/'
app.config['OUTPUT_FOLDER'] = 'out/'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hidden_faces.db"
db = SQLAlchemy(app)



class ProcessedImage(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    filename = db.Column(db.String, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False)
    exp_date = db.Column(db.DateTime, nullable=False)


@app.route('/')
def hello():
    return 'Hello!'

@app.route('/hide', methods=['POST'])
def hide():
    if 'file' not in request.files:
        return 'y no file'
    
    file = request.files['file']

    if file.filename == '':
        return {'message': 'no selected file'}, 400
    
    payload = {}
    status = 200

    if file:
        filename = str(uuid.uuid4()) + secure_filename(file.filename)
        input_path = os.path.join(app.config['TEMP_FOLDER'], filename)

        # save image to temp directory
        file.save(input_path)

        # check if image
        if imghdr.what(input_path):

            # process image to output directory 
            filename_split = os.path.splitext(input_path)
            basename = os.path.basename(os.path.splitext(input_path)[0])
            ext = os.path.splitext(input_path)[1]
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], basename + '_processed' + ext)
            hide_faces(input_path, output_path, cascades)
            
            # save output image name/id to db
            db_id = uuid.uuid4().hex
            db_filename = os.path.basename(output_path)
            db_pub_date = datetime.utcnow()
            db_exp_date = db_pub_date + timedelta(hours=2)
            db.session.add(ProcessedImage(id=db_id, filename=db_filename, pub_date=db_pub_date, exp_date=db_exp_date))
            db.session.commit()
            
            # return url to user, if success
            payload['url'] = request.base_url + '/images/' + db_id + ext
            payload['message'] = 'successfully processed'
        else:
            payload['message'] = 'invalid file'
            status = 400

        # delete temp image
        os.remove(input_path)

    return payload, status 
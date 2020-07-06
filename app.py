import os
from datetime import datetime, timedelta 
import uuid 
import mimetypes 
import click 
from flask import Flask, flash, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy 
import imghdr
from werkzeug.utils import secure_filename

from hide_faces import hide_faces
import configs 


cascades = [
    'data/haarcascades/haarcascade_profileface.xml',
    'data/haarcascades/haarcascade_frontalface_default.xml',
    'data/lbpcascades/lbpcascade_frontalface_improved.xml'
]


app = Flask(__name__)
app.config.from_object('configs.ProductionConfig')
db = SQLAlchemy(app)

class ProcessedImage(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    filename = db.Column(db.String, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False)
    exp_date = db.Column(db.DateTime, nullable=False)

    def extension(self):
        return os.path.splitext(self.filename)[1]

    def mimetype(self):
        if self.extension() in mimetypes.types_map:
            return mimetypes.types_map[self.extension()]
        else:
            return 'image/' + self.extension()[1:]
    
    def dict(self):
        return {
            '_id': self.id,
            'filename': self.filename,
            'pub_date': self.pub_date.isoformat(),
            'exp_date': self.exp_date.isoformat()
        }

@app.cli.command('setup')
def setup():
    # create tmp directory if not exists
    if not os.path.exists(app.config['TEMP_FOLDER']):
        print('creating temp folder')
        os.makedirs(app.config['TEMP_FOLDER'])

    # create out directory if not exists
    if not os.path.exists(app.config['OUTPUT_FOLDER']):
        print('creating output folder')
        os.makedirs(app.config['OUTPUT_FOLDER'])

    # create db if not exists
    if not db.engine.has_table(ProcessedImage.__tablename__):
        print('creating db')
        db.create_all()


@app.route('/')
def hello():
    return 'Hello!'

@app.route('/processed/all')
def get_all_processed_images():
    return {
        'images': [i.dict() for i in ProcessedImage.query.all()]
    }

@app.route('/processed/<id>.<ext>')
def get_processed_image(id, ext):
    result = ProcessedImage.query.filter_by(id=id).first()
    if result and result.extension()[1:] == ext:
        # get file to return 
        
        return send_file(os.path.join(app.config['OUTPUT_FOLDER'], result.filename),
            mimetype=result.mimetype(),
            as_attachment=True,
            attachment_filename=id + '.'  + ext)

    return {'message': 'image not found'}, 404

@app.route('/hide', methods=['POST'])
def hide():
    if 'file' not in request.files:
        return {
            'message': 'no file uploaded'
        }, 400
    
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
            faces_processed = hide_faces(input_path, output_path, cascades)

            # check if processed
            if faces_processed > 0:
                # save output image name/id to db
                db_id = uuid.uuid4().hex
                db_filename = os.path.basename(output_path)
                db_pub_date = datetime.utcnow()
                db_exp_date = db_pub_date + timedelta(hours=2)
                db.session.add(ProcessedImage(id=db_id, filename=db_filename, pub_date=db_pub_date, exp_date=db_exp_date))
                db.session.commit()
                
                # return url to user, if success
                payload['url'] = request.url_root + 'processed/' + db_id + ext
                payload['message'] = 'successfully processed'
            
            else:
                payload['message'] = 'no faces detected to process'
        else:
            payload['message'] = 'invalid file'
            status = 400

        # delete temp image
        os.remove(input_path)

    return payload, status 
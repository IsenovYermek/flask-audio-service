from flask import Flask, request
from models import db
import uuid
from models import db, User
from flask_restful import Resource, Api, reqparse
import os
from models import db, User, Record
from flask_restful import Resource, Api, reqparse
from werkzeug.utils import secure_filename
from flask import send_from_directory

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mypassword@localhost:5432/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mypassword@localhost:5432/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


class CreateUser(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, help='User name is required', required=True)
        args = parser.parse_args()

        token = str(uuid.uuid4())
        user = User(name=args['name'], token=token)
        db.session.add(user)
        db.session.commit()

        return {'id': user.id, 'token': user.token}


api.add_resource(CreateUser, '/user')

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mypassword@localhost:5432/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/'

ALLOWED_EXTENSIONS = {'wav', 'mp3'}

db.init_app(app)

class RecordUpload(Resource):
    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='User id is required', required=True)
        parser.add_argument('token', type=str, help='Token is required', required=True)
        parser.add_argument('file', type=str, location='files', help='Audio file is required', required=True)
        args = parser.parse_args()

        user = User.query.get(args['id'])
        if not user:
            return {'message': 'User not found'}, 404

        if user.token != args['token']:
            return {'message': 'Invalid token'}, 403

        file = args['file']
        if file and self.allowed_file(file.filename):
            file_format = file.filename.split('.')[-1]
            uuid = str(uuid.uuid4())
            filename = secure_filename(uuid + '.' + file_format)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            record = Record(uuid=uuid, user=user, file_format=file_format)
            db.session.add(record)
            db.session.commit()

            return {'url': f'http://localhost:5000/record?id={uuid}&user={user.id}'}, 201
        else:
            return {'message': 'Invalid file'}, 400


api.add_resource(RecordUpload, '/record')

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mypassword@localhost:5432/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/'

db.init_app(app)


class RecordDownload(Resource):
    def get(self):
        record_uuid = request.args.get('id')
        user_id = request.args.get('user')

        record = Record.query.filter_by(uuid=record_uuid, user_id=user_id).first()
        if not record:
            return {'message': 'Record not found'}, 404

        return send_from_directory(app.config['UPLOAD_FOLDER'], f"{record.uuid}.{record.file_format}")


api.add_resource(RecordDownload, '/record/download')
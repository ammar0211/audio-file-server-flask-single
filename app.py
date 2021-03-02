from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validates
from werkzeug.utils import secure_filename
import os, datetime, ast

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)

# song Class/Model
class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.Integer,primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False)
    file_name = db.Column(db.String(100), nullable=False)

    def __init__(self, name, duration, upload_time, file_name):
        self.name = name
        self.duration = duration
        self.upload_time = upload_time
        self.file_name = file_name

# podcast Class/Model
class Podcast(db.Model):
    __tablename__ = 'podcasts'

    id = db.Column(db.Integer,primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False)
    host = db.Column(db.String(100), nullable=False)
    participants = db.Column(db.String(1030), nullable=True)
    file_name = db.Column(db.String(100), nullable=False)

    def __init__(self, name, duration, upload_time, host, participants, file_name):
        self.name = name
        self.duration = duration
        self.upload_time = upload_time
        self.host = host
        self.participants = participants
        self.file_name = file_name


# audiobooks Class/Model
class Audiobook(db.Model):
    id = db.Column(db.Integer,primary_key=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    narrator = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False)
    file_name = db.Column(db.String(100), nullable=False)

    def __init__(self, title, author, narrator, duration, upload_time, file_name):
        self.title = title
        self.author = author
        self.narrator = narrator
        self.duration = duration
        self.upload_time = upload_time
        self.file_name = file_name


# Table Schema
class SongSchema(Schema):
    id = fields.Int(strict=True, required=True, validate=(lambda x: x>0))
    name = fields.String(required=True, validate=(lambda x: len(x)<=100))
    duration = fields.Int(strict=True, required=True)
    upload_time = fields.DateTime(strict=True, required=True)

class PodcastSchema(Schema):
    id = fields.Int(strict=True, required=True, validate=(lambda x: x>0))
    name = fields.String(required=True, validate=(lambda x: len(x)<=100))
    duration = fields.Int(strict=True, required=True)
    upload_time = fields.DateTime(strict=True, required=True)
    host = fields.String(required=True, validate=(lambda x: len(x)<=100))
    # participants = fields.String(required=False, validate=(lambda x: len(x)<=1030))
    participants = fields.List(fields.String(validate=(lambda x: len(x)<=100)),validate=(lambda x: len(x)<=10))

class AudiobookSchema(Schema):
    id = fields.Int(strict=True, required=True, validate=(lambda x: x>0))
    title = fields.String(required=True, validate=(lambda x: len(x)<=100))
    author = fields.String(required=True, validate=(lambda x: len(x)<=100))
    narrator = fields.String(required=True, validate=(lambda x: len(x)<=100))
    duration = fields.Int(strict=True, required=True)
    upload_time = fields.DateTime(strict=True, required=True)

# Init schema
song_schema = SongSchema()
songs_schema = SongSchema(many=True)

podcast_schema = PodcastSchema()
podcasts_schema = PodcastSchema(many=True)

audiobook_schema = AudiobookSchema()
audiobooks_schema = AudiobookSchema(many=True)



#CREATE ROUTE
@app.route('/create', methods=['POST'])
def create():
    try:
        audioFileType=request.form['audioFileType']
        audioFileMetadata=request.form['audioFileMetadata']
        audioFileMetadata=ast.literal_eval(audioFileMetadata)
        uploadedFile=request.files['audioFile']

        if audioFileType.lower()=='song':
            try:
                name=audioFileMetadata['name']
                duration=audioFileMetadata['duration']
            except:
                return "The request is invalid: 400 bad request",400

            #VALIDATION
            if len(name)>100 or not str(duration).isdigit() :
                return "The request is invalid: 400 bad request",400

            uploadTime=datetime.datetime.utcnow()
            fileName = secure_filename(uploadedFile.filename)
            filePath = "./song/"+fileName
            uploadedFile.save(filePath)

            new_song = Song(name,duration,uploadTime,fileName)
            db.session.add(new_song)
            db.session.commit()

        elif audioFileType.lower()=='podcast':
            try:
                name=audioFileMetadata['name']
                duration=audioFileMetadata['duration']
                host=audioFileMetadata['host']
            except:
                return "The request is invalid: 400 bad request",400
            try:
                participants=audioFileMetadata['participants']
                if len(participants)>10 or any(len(participants) > 100 for participant in participants):
                    return "The request is invalid: 400 bad request",400
            except:
                participants=None

            #VALIDATION
            if len(name)>100 or len(host)>100 or not str(duration).isdigit():
                return "The request is invalid: 400 bad request",400

            uploadTime=datetime.datetime.utcnow()
            fileName = secure_filename(uploadedFile.filename)
            filePath = "./podcast/"+fileName
            uploadedFile.save(filePath)

            new_podcast = Podcast(name,duration,uploadTime,host,str(participants),fileName)
            db.session.add(new_podcast)
            db.session.commit()

        elif audioFileType.lower()=='audiobook':
            try:
                title=audioFileMetadata['title']
                duration=audioFileMetadata['duration']
                author=audioFileMetadata['author']
                narrator=audioFileMetadata['narrator']
            except:
                return "The request is invalid: 400 bad request",400

            #VALIDATION
            if len(title)>100 or len(author)>100 or len(narrator)>100 or not str(duration).isdigit():
                return "The request is invalid: 400 bad request",400

            uploadTime=datetime.datetime.utcnow()
            fileName = secure_filename(uploadedFile.filename)
            filePath = "./audiobook/"+fileName
            uploadedFile.save(filePath)

            new_podcast = Audiobook(title, author, narrator, duration, uploadTime, fileName)
            db.session.add(new_podcast)
            db.session.commit()

        else:
            return "The request is invalid: 400 bad request",400

        return "Action is successful: 200 OK",200
    except Exception as e:
        print (e)
        return "500 internal server error", 500


#GET ROUTE
@app.route('/get/<audioFileType>',defaults={'audioFileID': None} ,methods=['GET'])
@app.route('/get/<audioFileType>/<audioFileID>', methods=['GET'])
def get(audioFileType,audioFileID):
    try:
        if audioFileID==None:
            if audioFileType=='song':
                all_files=Song.query.all()
                result = songs_schema.dump(all_files)
                return jsonify(result),200
            elif audioFileType=='audiobook':
                all_files=Audiobook.query.all()
                result = audiobooks_schema.dump(all_files)
                return jsonify(result),200
            elif audioFileType=='podcast':
                all_files=Podcast.query.all()
                result = podcasts_schema.dump(all_files)
                return jsonify(result),200
            else:
                return "The request is invalid: 400 bad request", 400
        else:
            if audioFileType=='song':
                all_files=Song.query.get(audioFileID)
                if all_files==None:
                    return "The request is invalid: 400 bad request", 400
                result = song_schema.dump(all_files)
                return jsonify(result),200
            elif audioFileType=='audiobook':
                all_files=Audiobook.query.get(audioFileID)
                if all_files==None:
                    return "The request is invalid: 400 bad request", 400
                result = audiobook_schema.dump(all_files)
                return jsonify(result),200
            elif audioFileType=='podcast':
                all_files=Podcast.query.get(audioFileID)
                if all_files==None:
                    return "The request is invalid: 400 bad request", 400
                result = podcast_schema.dump(all_files)
                return jsonify(result),200
            else:
                return "The request is invalid: 400 bad request", 400
    except:
        return "500 internal server error", 500


#UPDATE ROUTE
@app.route('/update/<audioFileType>/<audioFileID>', methods=['PUT'])
def update(audioFileType,audioFileID):
    try:

        audioFileMetadata=request.form['audioFileMetadata']
        audioFileMetadata=ast.literal_eval(audioFileMetadata)
        uploadedFile=request.files['audioFile']

        if audioFileType.lower()=='song':
            try:
                update_file=Song.query.get(audioFileID)

                name=audioFileMetadata['name']
                duration=audioFileMetadata['duration']
            except:
                return "The request is invalid: 400 bad request",400

            #VALIDATION
            if len(name)>100 or not str(duration).isdigit() :
                return "The request is invalid: 400 bad request",400

            uploadTime=datetime.datetime.utcnow()
            fileName = secure_filename(uploadedFile.filename)
            filePath = "./song/"+fileName
            os.remove("./song/"+update_file.file_name)

            #UPDATING DATA
            update_file.name = name
            update_file.duration = duration
            update_file.upload_time = uploadTime
            update_file.file_name = fileName
            uploadedFile.save(filePath)

            db.session.commit()

        elif audioFileType.lower()=='podcast':
            try:
                update_file=Podcast.query.get(audioFileID)

                name=audioFileMetadata['name']
                duration=audioFileMetadata['duration']
                host=audioFileMetadata['host']
            except:
                return "The request is invalid: 400 bad request",400
            try:
                participants=audioFileMetadata['participants']
                if len(participants)>10 or any(len(participants) > 100 for participant in participants):
                    return "The request is invalid: 400 bad request",400
            except:
                participants=None

            #VALIDATION
            if len(name)>100 or len(host)>100 or not str(duration).isdigit():
                return "The request is invalid: 400 bad request",400

            uploadTime=datetime.datetime.utcnow()
            fileName = secure_filename(uploadedFile.filename)
            filePath = "./podcast/"+fileName
            os.remove("./podcast/"+update_file.file_name)

            #UPDATING DATA
            update_file.name = name
            update_file.duration = duration
            update_file.host = host
            update_file.participants = str(participants)
            update_file.upload_time = uploadTime
            update_file.file_name = fileName
            uploadedFile.save(filePath)

            db.session.commit()

        elif audioFileType.lower()=='audiobook':
            try:
                update_file=Audiobook.query.get(audioFileID)

                title=audioFileMetadata['title']
                duration=audioFileMetadata['duration']
                author=audioFileMetadata['author']
                narrator=audioFileMetadata['narrator']
            except:
                return "The request is invalid: 400 bad request",400

            #VALIDATION
            if len(title)>100 or len(author)>100 or len(narrator)>100 or not str(duration).isdigit():
                return "The request is invalid: 400 bad request",400

            uploadTime=datetime.datetime.utcnow()
            fileName = secure_filename(uploadedFile.filename)
            filePath = "./audiobook/"+fileName
            os.remove("./audiobook/"+update_file.file_name)

            #UPDATING DATA
            update_file.title = title
            update_file.duration = duration
            update_file.author = author
            update_file.narrator = narrator
            update_file.upload_time = uploadTime
            update_file.file_name = fileName
            uploadedFile.save(filePath)

            db.session.commit()

        else:
            return "The request is invalid: 400 bad request",400

        return "Action is successful: 200 OK",200
    except:
        return "500 internal server error", 500


#DELETE ROUTE
@app.route('/delete/<audioFileType>/<audioFileID>', methods=['DELETE'])
def delete(audioFileType,audioFileID):
    try:
        if audioFileType.lower()=='song':
            try:
                delete_file=Song.query.get(audioFileID)
                db.session.delete(delete_file)
            except:
                return "The request is invalid: 400 bad request",400

        elif audioFileType.lower()=='podcast':
            try:
                delete_file=Podcast.query.get(audioFileID)
                db.session.delete(delete_file)
            except:
                return "The request is invalid: 400 bad request",400

        elif audioFileType.lower()=='audiobook':
            try:
                delete_file=Audiobook.query.get(audioFileID)
                db.session.delete(delete_file)
            except:
                return "The request is invalid: 400 bad request",400
        else:
            return "The request is invalid: 400 bad request",400

        db.session().commit()
        return "Action is successful: 200 OK",200

    except:
        return "500 internal server error", 500


if __name__ == '__main__':
    if not os.path.exists("./song"):
        os.makedirs("./song")
    if not os.path.exists("./audiobook"):
        os.makedirs("./audiobook")
    if not os.path.exists("./podcast"):
        os.makedirs("./podcast")
    app.run(debug=True)

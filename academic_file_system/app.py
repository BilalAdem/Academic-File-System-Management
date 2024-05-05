from datetime import datetime
import re
from flask import Flask, request, render_template, redirect, url_for
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
from flask import current_app, g
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
import gridfs


import os
from bson import ObjectId
from flask import Response
from flask import make_response
from sqlalchemy import text


application = Flask(__name__)


app = application

# Configuration settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345678@localhost/files_db'
# Replace with your connection string
app.config["MONGO_URI"] = "mongodb://localhost:27017/files"


db = SQLAlchemy(app)
mongo = PyMongo(app)
migrate = Migrate(app, db)

fs = gridfs.GridFS(mongo.db)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    repository = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    pathname = db.Column(db.String(100), nullable=True)
    mongo_file_id = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"File('{self.name}', '{self.type}', '{self.repository} , '{self.created_at}, '{self.pathname} , '{self.mongo_file_id}')"

    def __init__(self, name, type, repository, pathname, created_at, mongo_file_id):
        self.name = name
        self.type = type
        self.repository = repository
        self.pathname = pathname
        self.created_at = created_at
        self.mongo_file_id = mongo_file_id


@app.route('/')
def index():
    # fecth from the database
    files = db.session.query(File).all()
    # get the distinct repositories that are different from the default Analyse, Algebre, Programmation,Reseau,Systeme
    repos = db.session.query(File.repository).filter(
        File.repository != 'Analyse').filter(File.repository != 'Algebre').filter(File.repository != 'Programmation').filter(File.repository != 'Reseau').filter(File.repository != 'Systeme').distinct().all()
    # get the distinct file types that are different from Cours, TP, TD
    types = db.session.query(File.type).filter(
        File.type != 'Cours').filter(File.type != 'TP').filter(File.type != 'TD').distinct().all()

    # ellininates all special characters using regex for the repository names and capitalizes the first letter of each repository name
    repos = [repo[0].capitalize() for repo in repos]
    repos = [re.sub(r'\W+', '', repo) for repo in repos]

    types = [type[0].capitalize() for type in types]
    types = [re.sub(r'\W+', '', type) for type in types]

    # verify if mysql db and ESITN folder contains the same files
    for file in files:
        if not os.path.exists(file.pathname):
            db.session.delete(file)
            db.session.commit()

    # if Ids are not organized, reorganize them
    db.session.execute(text('SET @count = 0'))
    db.session.execute(text('UPDATE file SET file.id = @count:= @count + 1'))
    db.session.commit()

    # if database is empty, then drop folder ESTIN and delete all files in the GridFS
    if not files:
        estin_repo_path = os.path.join('C:\\', 'ESTIN')
        if os.path.exists(estin_repo_path):
            os.system(f'rmdir /S /Q {estin_repo_path}')
        for file in fs.find():
            fs.delete(ObjectId(file._id))

    # when finished refetch the files
    files = db.session.query(File).all()
    repos = db.session.query(File.repository).filter(
        File.repository != 'Analyse').filter(File.repository != 'Algebre').filter(File.repository != 'Programmation').filter(File.repository != 'Reseau').filter(File.repository != 'Systeme').distinct().all()
    # get the distinct file types that are different from Cours, TP, TD
    types = db.session.query(File.type).filter(
        File.type != 'Cours').filter(File.type != 'TP').filter(File.type != 'TD').distinct().all()

    # ellininates all special characters using regex for the repository names and capitalizes the first letter of each repository name
    repos = [repo[0].capitalize() for repo in repos]
    repos = [re.sub(r'\W+', '', repo) for repo in repos]

    types = [type[0].capitalize() for type in types]
    types = [re.sub(r'\W+', '', type) for type in types]

    return render_template('index.html', files=files, repos=repos, types=types)


@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    file_type = request.form['options'] if 'options' in request.form else None
    existing_repo = request.form.get(
        'reps') if 'reps' in request.form else None
    new_repo = request.form.get('new_rep')
    new_type = request.form.get('new_type')

    allowed_extensions = {'txt', 'pdf', 'docx', 'xlsm', 'xlsx', 'pptx', 'ppt', 'doc',
                          'jpeg', 'png', 'gif', 'zip', 'rar'}
    if uploaded_file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return redirect(url_for('index'))

    # Check if the file is in the database already then don't upload it again
    file = db.session.query(File).filter_by(
        name=uploaded_file.filename).first()
    if file:
        return redirect(url_for('index'))
    else:
        # Store file in GridFS
        file_data = uploaded_file.read()
        file_id = fs.put(file_data)

        # Secure filename to prevent directory traversal attacks
        filename = secure_filename(uploaded_file.filename)

        # Create 'ESTIN' repository directory if it doesn't exist
        estin_repo_path = os.path.join('C:\\', 'ESTIN')
        if not os.path.exists(estin_repo_path):
            os.makedirs(estin_repo_path)

        # Determine repository (use existing or create new)
        repository = existing_repo if existing_repo else new_repo
        # style the repository name to remove special characters and capitalize the first letter of each word
        repository = repository.capitalize()
        repository = re.sub(r'\W+', '', repository)

        file_type = file_type if file_type else new_type
        file_type = file_type.capitalize()
        file_type = re.sub(r'\W+', '', file_type)

        # Create repository directory if it doesn't exist within 'ESTIN'
        repo_path = os.path.join(estin_repo_path, repository)
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)

        # Create folder for file type if it doesn't exist within repository
        file_type_path = os.path.join(repo_path, file_type)
        if not os.path.exists(file_type_path):
            os.makedirs(file_type_path)

        uploaded_file.save(os.path.join(file_type_path, filename))

        pathname = os.path.join(file_type_path, filename)

        new_file = File(name=filename, type=file_type,
                        repository=repository, pathname=pathname, created_at=datetime.utcnow(), mongo_file_id=file_id)
        db.session.add(new_file)
        db.session.commit()

        return redirect(url_for('index'))


mime_types = {
    '.txt': 'text/plain',
    '.pdf': 'application/pdf',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xlsm': 'application/vnd.ms-excel.sheet.macroEnabled.12',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.doc': 'application/msword',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.zip': 'application/zip',
    '.rar': 'application/x-rar-compressed'
}


@app.route('/download/<int:file>', methods=['GET'])
def download_file(file):
    file = db.session.query(File).filter_by(id=file).first()
    file_data = fs.get(ObjectId(file.mongo_file_id))
    file_extension = file.name.rsplit('.', 1)[1].lower()
    mime_type = mime_types.get(file_extension)
    if file_data:

        # Set appropriate MIME type
        if file_extension == 'jpeg' or file_extension == 'png' or file_extension == 'gif' or file_extension == 'txt':

            response = Response(file_data.read(), mimetype=file.type)
            # response.headers['Content-Type'] = mime_type
            response.headers['Content-Disposition'] = response.headers['Content-Disposition'] = \
                'inline; filename=' + file.name
        elif file_extension == 'pdf':
            response = make_response(file_data.read())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = \
                'inline; filename=' + file.name

        else:
            response = Response(file_data.read(), mimetype=mime_type)
            response.headers['Content-Type'] = mime_type
            response.headers['Content-Disposition'] = response.headers['Content-Disposition'] = \
                'attachment; filename=' + file.name
        return response
    else:
        return "File not found!", 404


@app.route('/delete/<int:file>', methods=['GET'])
def delete_file(file):
    print(f"Deleting file with id: {file}")
    file = db.session.query(File).filter_by(id=file).first()
    # delete file from GridFS
    fs.delete(ObjectId(file.mongo_file_id))
    print(f"Deleting file with id: {file}")
    db.session.delete(file)
    # after deleting the file from the database, reorganise database to avoid gaps in the ids
    db.session.execute(text('SET @count = 0'))
    db.session.execute(text('UPDATE file SET file.id = @count:= @count + 1'))

    db.session.commit()

    os.remove(file.pathname)

    return redirect(url_for('index'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", debug=True)

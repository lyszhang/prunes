# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask import jsonify
from sqlite import db, IPFS_hash

from werkzeug import secure_filename
import os
import ipfsapi

app = Flask(__name__)
api = ipfsapi.connect('127.0.0.1', 5001)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['IPFS_LIST'] = "ipfs.list"
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'avi', 'mp4', 'flv', 'mp3', 'wav', 'm4a', 'flac', 'ogg'])
app.config['VIDEO_TYPE'] = set(['avi', 'mp4', 'flv'])
app.config['MUSIC_TYPE'] = set(['mp3', 'wav', 'm4a', 'flac', 'ogg'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def publish_ipfs(file_category, filename, filehash):
    with open(app.config['IPFS_LIST'], 'a+') as f:
        f.write(filename.encode('utf-8') + '\t' + filehash.encode('utf-8') + '\t' + file_category.encode('utf-8') + '\n')

@app.before_first_request
def create_db():
  # Recreate database each time for demo
  #db.drop_all()
  db.create_all()

@app.route('/', methods=['GET', 'POST'])
@app.route('/<int:page>', methods=['GET', 'POST'])
def index(page = 1):
    if request.method == 'POST':
        try:
            filename = request.form.get('exampleInputName', '')
            filehash = request.form.get('exampleInputHash', '')
            file_category = request.form.get('inlineRadioOptions', '')
        except:
            flash("The parameters error")
        '''
        newfile = IPFS_hash(file_category, filename, filehash)
        db.session.add(newfile)
        db.session.commit()
        '''
        publish_ipfs(file_category, filename, filehash)

    files = IPFS_hash.query.paginate(page=page, per_page=10)

    for file in files.items:
        print(file.name)
    return render_template('index.html', files=files)


@app.route('/video/<string:video_hash>')
def video_player(video_hash):
    return render_template('video-player.html', video_hash=video_hash)


@app.route('/upload', methods=['GET', 'POST'])
def video_upload():
    if request.method == 'POST':
        uploaded_file = request.files['file']

        if uploaded_file and allowed_file(uploaded_file.filename):
            file_name = secure_filename(uploaded_file.filename)
            updir = os.path.join(basedir, 'upload/')
            file_fullpath = os.path.join(updir, file_name)
            uploaded_file.save(file_fullpath)
            '''
            file_size = os.path.getsize(os.path.join(updir, filename))
            '''
            file_hash = api.add(file_fullpath)

            if file_name.rsplit('.', 1)[1] in app.config['VIDEO_TYPE']:
                file_category = 'video'
            else:
                if file_name.rsplit('.', 1)[1] in app.config['VIDEO_MUSIC']:
                    file_category = 'music'
                else:
                    file_category = 'txt'

            newfile = IPFS_hash(file_category, file_name, file_hash['Hash'])
            db.session.add(newfile)
            db.session.commit()

            publish_ipfs(file_category, file_name, file_hash)

            return render_template('result.html', file_hash=file_hash)

        else:
            app.logger.info('ext name error')
            return jsonify(error='ext name error')
    return render_template('real-upload.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

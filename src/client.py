import os
import sys
from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from utils import get_song_metadata, get_spotify_node_instance
from spotify import SpotifyNode
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/static'
ALLOWED_EXTENSIONS = {'mp3'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'
Bootstrap(app)


@app.route("/", methods=['GET'])
def home():
    return render_template('home.html')


@app.route("/all-songs", methods=['GET', 'POST'])
def all_songs():
    if request.method == 'POST':
        song = request.form['song']
        title, author, _ = get_song_metadata(song)
        song_key = title + ' ' + author
        song = spotify_node.get_song(song_key)
        print(type(song[4]))

        with open('/static/track1.mp3', 'wb') as file:
            file.write(song[4].content)

        return render_template('music_player.html', content=[song])
    else:
        flag = 'songs'
        metadata = 'todas las canciones'
        data = spotify_node.get_all_songs()
        return render_template('result.html', content=[flag, metadata, data])


@app.route("/upload-song", methods=['GET', 'POST'])
def upload_song():
    if request.method == 'POST':
        title = request.form['title']
        gender = request.form['gender']
        author = request.form['author']
        song_file = request.files['songfile']

        if song_file and allowed_file(song_file.filename):
            print("ENTRO")
            filename = secure_filename(song_file.filename)
            song_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            

        song_key = title + ' ' + author
        # spotify_node.save_song(song_key, (title, author, gender, filename))

        return render_template('home.html')
    else:
        return render_template('upload_song.html')


@app.route("/search-by-title", methods=['GET', 'POST'])
def search_by_title():
    if request.method == 'POST':
        title = request.form['title']
        flag = 'title'
        metadata = title
        data = spotify_node.get_songs_by_title(title)
        return render_template('result.html', content=[flag, metadata, data])
    else:
        return render_template('search_by_title.html')


@app.route("/search-by-gender", methods=['GET', 'POST'])
def search_by_gender():
    if request.method == 'POST':
        gender = request.form['gender']
        flag = 'gender'
        metadata = gender
        data = spotify_node.get_songs_by_gender(gender)
        return render_template('result.html', content=[flag, metadata, data])
    else:
        return render_template('search_by_gender.html')


@app.route("/search-by-author", methods=['GET', 'POST'])
def search_by_author():
    if request.method == 'POST':
        author = request.form['author']
        flag = 'author'
        metadata = author
        data = spotify_node.get_songs_by_author(author)
        return render_template('result.html', content=[flag, metadata, data])
    else:
        return render_template('search_by_author.html')


def connect(spotify_address):
    spotify_node: SpotifyNode = get_spotify_node_instance(spotify_address)
    if not spotify_node:
        print(
            f'Error: Could not connect to spotify node with address: {spotify_address}')
        return None
    return spotify_node


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    if len(sys.argv) == 2:
        pass
        # spotify_node = connect(sys.argv[1])
    elif len(sys.argv) < 2:
        print('Error: Missing arguments, you must enter the spotify node address')
    else:
        print('Error: Too many arguments, you must enter only the spotify node address')

    app.run(debug=True)

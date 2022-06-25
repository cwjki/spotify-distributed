import os
import time
import sys
from random import randint
from serpent import tobytes
from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from utils import get_song_metadata, get_spotify_node_instance
from spotify import SpotifyNode


UPLOAD_FOLDER = os.getcwd() + '/static/upload'
ALLOWED_EXTENSIONS = {'mp3'}


class MyServer(Flask):
    def __init__(self, *args, **kwargs):
        super(MyServer, self).__init__(*args, **kwargs)
        self.spotify_node = None
        self.spotify_nodes_list = []


app = MyServer(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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

        song_file = make_request(1, song_key)

        encode_song = tobytes(song_file[4])
        with open('static/download/track.mp3', 'wb') as file:
            file.write(encode_song)

        return render_template('music_player.html', content=[song])
    else:
        flag = 'songs'
        metadata = 'todas las canciones'

        data = make_request(0)
        data = data if data else []
        song_count = len(data) if data else 0

        return render_template('result.html', content=[flag, metadata, data, song_count])


@app.route('/music-player', methods=['GET', 'POST'])
def music_player():
    song = request.form['song']
    title, author, _ = get_song_metadata(song)
    song_key = title + ' ' + author
    song_file = make_request(1, song_key)

    encode_song = tobytes(song_file[4])
    with open('static/download/track.mp3', 'wb') as file:
        file.write(encode_song)

    return render_template('music_player.html', content=[song])


@app.route("/upload-song", methods=['GET', 'POST'])
def upload_song():
    if request.method == 'POST':
        title = request.form['title']
        gender = request.form['gender']
        author = request.form['author']
        song_file = request.files['songfile']

        song_key = title + ' ' + author

        make_request(
            5, song_key, (title, author, gender, song_file.read()))

        return render_template('home.html')
    else:
        return render_template('upload_song.html')


@app.route("/search-by-title", methods=['GET', 'POST'])
def search_by_title():
    if request.method == 'POST':
        title = request.form['title']
        flag = 'title'
        metadata = title

        data = make_request(4, title)
        data = data if data else []
        song_count = len(data) if data else 0

        return render_template('result.html', content=[flag, metadata, data, song_count])
    else:
        return render_template('search_by_title.html')


@app.route("/search-by-gender", methods=['GET', 'POST'])
def search_by_gender():
    if request.method == 'POST':
        gender = request.form['gender']
        flag = 'gender'
        metadata = gender

        data = make_request(3, gender)
        data = data if data else []
        song_count = len(data) if data else 0

        return render_template('result.html', content=[flag, metadata, data, song_count])
    else:
        return render_template('search_by_gender.html')


@app.route("/search-by-author", methods=['GET', 'POST'])
def search_by_author():
    if request.method == 'POST':
        author = request.form['author']
        flag = 'author'
        metadata = author

        data = make_request(2, author)
        data = data if data else []
        song_count = len(data) if data else 0

        return render_template('result.html', content=[flag, metadata, data, song_count])
    else:
        return render_template('search_by_author.html')


def connect(spotify_address):
    spotify_node: SpotifyNode = get_spotify_node_instance(spotify_address)
    if not spotify_node:
        print(
            f'Error: Could not connect to spotify node with address: {spotify_address}')
        return None
    return spotify_node


def make_request(request_type, param1=None, param2=None):
    rindex = randint(0, len(app.spotify_nodes_list) - 1)
    spotify_node: SpotifyNode = None
    seconds = time.time()
    while True:
        for spotify_address in app.spotify_nodes_list[rindex:]:
            spotify_node = get_spotify_node_instance(spotify_address)
            if spotify_node:
                response = get_response(
                    spotify_node, request_type, param1, param2)
                if response:
                    app.spotify_nodes_list = spotify_node.spotify_nodes_list
                    return response

        for spotify_address in app.spotify_nodes_list[:rindex]:
            spotify_node = get_spotify_node_instance(spotify_address)
            if spotify_node:
                response = get_response(
                    spotify_node, request_type, param1, param2)
                if response:
                    app.spotify_nodes_list = spotify_node.spotify_nodes_list
                    return response

        if seconds > 20:
            print(f'Error: Could not connect to any spotify node')
            return None


def get_response(spotify_node, request_type, param1, param2):
    if request_type == 0:
        result = spotify_node.get_all_songs()
    elif request_type == 1:
        result = spotify_node.get_song(param1)
    elif request_type == 2:
        result = spotify_node.get_songs_by_author(param1)
    elif request_type == 3:
        result = spotify_node.get_songs_by_gender(param1)
    elif request_type == 4:
        result = spotify_node.get_songs_by_title(param1)
    else:
        result = spotify_node.save_song(param1, param2)
    return result


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    if len(sys.argv) == 2:
        app.spotify_node = connect(sys.argv[1])
        app.spotify_nodes_list = app.spotify_node.spotify_nodes_list
    elif len(sys.argv) < 2:
        print('Error: Missing arguments, you must enter the spotify node address')
    else:
        print('Error: Too many arguments, you must enter only the spotify node address')

    app.run(debug=True)

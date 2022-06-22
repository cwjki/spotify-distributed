import sys
from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from utils import get_spotify_node_instance, hashing
from spotify import SpotifyNode

app = Flask(__name__)
Bootstrap(app)

toy_data = [
    (
        'Under Pressure',
        'Shawn Mendes',
        'Pop'
    ),
    (
        'Cita con ángeles',
        'Silvio Rodríguez',
        'Trova'
    ),

]


@app.route("/", methods=['GET'])
def home():
    return render_template('home.html')


@app.route("/all-songs", methods=['GET', 'POST'])
def all_songs():
    if request.method == 'POST':

        song = None
        return render_template('music_player.html', content=[song])
    else:
        flag = 'songs'
        metadata = 'todas las canciones'
        # data = spotify_node.get_all_songs()
        data = toy_data
        return render_template('result.html', content=[flag, metadata, data])


@app.route("/upload-song", methods=['GET', 'POST'])
def upload_song():
    if request.method == 'POST':
        print(spotify_node)

        title = request.form['title']
        gender = request.form['gender']
        author = request.form['author']
        song = request.form['song']

        spotify_node.save_song(title, (title, author, gender, song))

        return render_template('home.html')
    else:
        print(spotify_node)
        return render_template('upload_song.html')


@app.route("/search-by-title", methods=['GET', 'POST'])
def search_by_title():
    if request.method == 'POST':
        title = request.form['title']
        flag = 'title'
        metadata = title
        data = []
        return render_template('result.html', content=[flag, metadata, data])
    else:
        return render_template('search_by_title.html')


@app.route("/search-by-gender", methods=['GET', 'POST'])
def search_by_gender():
    if request.method == 'POST':
        gender = request.form['gender']
        flag = 'gender'
        metadata = gender
        data = []
        return render_template('result.html', content=[flag, metadata, data])
    else:
        return render_template('search_by_gender.html')


@app.route("/search-by-author", methods=['GET', 'POST'])
def search_by_author():
    if request.method == 'POST':
        author = request.form['author']
        flag = 'author'
        metadata = author
        data = []
        return render_template('result.html', content=[flag, metadata, data])
    else:
        return render_template('search_by_author.html')


def connect(spotify_address):
    spotify_node = get_spotify_node_instance(spotify_address)
    if not spotify_node:
        print(
            f'Error: Could not connect to spotify node with address: {spotify_address}')
        return None
    return spotify_node


if __name__ == "__main__":
    if len(sys.argv) == 2:
        spotify_node = connect(sys.argv[1])
    elif len(sys.argv) < 2:
        print('Error: Missing arguments, you must enter the spotify node address')
    else:
        print('Error: Too many arguments, you must enter only the spotify node address')

    app.run(debug=True)

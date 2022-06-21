from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)


@app.route("/", methods=['GET'])
def home():
    return render_template('home.html')


@app.route("/all-songs", methods=['GET'])
def all_songs():
    flag = 'songs'
    metadata = 'todas las canciones'
    data = []
    return render_template('result.html', content=[flag, metadata, data])


@app.route("/upload-song", methods=['GET', 'POST'])
def upload_song():
    if request.method == 'POST':
        title = request.form['title']
        gender = request.form['gender']
        author = request.form['author']
        song = request.form['song']
        return render_template('home.html')
    else:
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


if __name__ == "__main__":
    app.run(debug=True)

from sys import flags
from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)


@app.route("/", methods=['GET'])
def home():
    return render_template('home.html')


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

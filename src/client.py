from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


if __name__ == "__client__":
    app.run(debug=True)

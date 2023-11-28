from flask import Flask, render_template, request
from firebaseAPI import *

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user', methods=['POST', 'GET'])
def user():
    result = request.form
    addUserURL('odu3971', result['URL'], result['Name'])

    docs_url = getUserURL('odu3971')
    docs_craw = getCrawling(docs_url[0]['url'])
    docs = [docs_url, docs_craw ]
    return render_template("user.html", docs=docs)

if __name__ == '__main__':
    app.run()

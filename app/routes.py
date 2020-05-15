from flask import render_template
from flask import request

from app import app

from QUERY import search

@app.route('/')
@app.route('/index')
def index():

    title = 'Boogle'
    text = request.args['query'].split()

    result = search(text)
    return render_template('index.html', title=title, text=text, result=result)

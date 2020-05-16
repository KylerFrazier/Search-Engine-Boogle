from flask import render_template
from flask import request
from flask import url_for

from app import app

from QUERY import search

@app.route('/')
@app.route('/index')
def index():

    title = "Boogle"

    try:
        query = request.args['query']
    except:
        query = ''

    obj = search(query)

    return render_template('index.html', title=title, query=query, obj=obj)


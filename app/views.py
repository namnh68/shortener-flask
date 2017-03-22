import utils
from app import app
from flask import request, url_for, render_template, send_file, redirect
from models import Url
from db_create import engine
from sqlalchemy.orm import sessionmaker
from rpc_client import TaskClient

task_rpc = TaskClient()


Session = sessionmaker(bind=engine)
session = Session()


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/<name>', methods=['GET'])
def image(name):
    if name == 'logo.png':
        return send_file('logo.png')
    elif name == 'time':
        time = utils.time()
        return render_template('time.html', time=time)
    else:
        try:
            origin_link = task_rpc.query_database(session, name)
        except Exception:
            raise Exception
        if origin_link is None:
            return render_template('not_link.html')
        return redirect(origin_link)


@app.route('/', methods=['POST'])
def accept():
    data_request = request.form['org_link']
    rand_link = utils.rand()
    record = Url(org_link=data_request, short_link=rand_link)
    task_rpc.insert_database(session, record)
    url = url_for('home', _external=True)
    final_url = url + rand_link
    return render_template('output.html', url=final_url)

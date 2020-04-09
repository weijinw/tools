import json
from flask import Flask, abort, make_response, request

app = Flask(__name__)

db = {}


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return "This is the Homepage!"


@app.route('/hello', methods=['GET'])
def hello():
    return "Hello world!"


@app.route('/add', methods=['PUT'])
def add():
    key, value = request.args.get('key'), request.args.get('value')
    db[key] = value
    return '', 204


@app.route('/get', methods=['GET'])
def get():
    key = request.args.get('key')
    if key not in db:
        return abort(404, 'key {} is not found'.format(key))
    return make_response(db[key], 200)


@app.route('/api1', methods=['GET'])
def api1():
    data = {
        'key': 'This is a demo value',
        'another-key': 'another demo value',
        'array-key': ['1', 2]
    }
    rsp = make_response(
        json.dumps(data),
        200,
    )
    rsp.headers = {
        'Content-Type': 'application/json',
        'head-key': 'head-value'
    }
    return rsp

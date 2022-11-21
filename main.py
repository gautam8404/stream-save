from flask import Flask, Response, jsonify, url_for, abort
from config import mclient
from functions.mongo.seriesdb import seriesStreams, seriesCatalog
from functions.mongo.moviedb import movieStreams, movieCatalog

MANIFEST = {
    "id": "org.stremio.streamsave",
    "version": "0.0.1",
    "name": "Stream Save",
    "description": "save custom stream links and play in different devices",

    'resources': [
        'catalog',
        {'name': 'stream', 'types': [
            'movie', 'series'], 'idPrefixes': ['tt']}
    ],

    "types": ["movie", "series"],

    'catalogs': [
        {'type': 'movie', 'id': 'stream_save_movies'},
        {'type': 'series', 'id': 'stream_save_series'},
    ],

    "idPrefixes": ["tt"]
}

app = Flask(__name__)


def respond_with(data):
    resp = jsonify(data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = '*'
    return resp


@app.route('/manifest.json')
def manifest():
    return respond_with(MANIFEST)


@app.route('/stream/<type>/<id>.json')
def stream(type, id):
    client = mclient
    if type not in MANIFEST['types']:
        abort(404)
    streams = {'streams': []}
    if type == 'movie':
        s = movieStreams(client)
    elif type == 'series':
        s = seriesStreams(client)
    else:
        abort(404)

    a = s.find(id)

    if a is not None:
        streams['streams'].append(a['data'])
        print(streams)
    return respond_with(streams)


@app.route('/catalog/<type>/<id>.json')
def addon_catalog(type, id):
    client = mclient
    if type not in MANIFEST['types']:
        abort(404)

    if type == 'movie':
        catalog = movieCatalog(client)
    elif type == 'series':
        catalog = seriesCatalog(client)
    else:
        abort(404)

    metaPreviews = {

    }

    c = catalog.full()

    if c is not None:
        metaPreviews['metas'] = c
    else:
        print("s")
        abort(404)

    return respond_with(metaPreviews)


if __name__ == '__main__':
    app.run()

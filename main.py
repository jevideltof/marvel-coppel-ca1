# https://stackoverflow.com/questions/56991649/virtualenv-not-activating-the-virtual-enviroment
# windows: $env:FLASK_APP = 'main', $env:FLASK_ENV = 1
# linux: export FLASK_APP=main, export FLASK_ENV=1

from datetime import datetime
import json
import math
import sys
import os
from flask import Flask, Response, render_template, request, redirect, url_for, flash, jsonify

sys.path.append('./comics')
from marvel import Marvel

public_key = os.environ.get("MARVEL_PUBLIC_KEY")
private_key = os.environ.get("MARVEL_PRIVATE_KEY")

app = Flask(__name__)

@app.route('/')
def index():
    mrlv = Marvel(private_key, public_key)
    comics = mrlv.get_results("Avengers")
    return json.dumps(comics.get('data'))

@app.route('/searchComics', methods=['GET'])
@app.route('/searchComics/', methods=['GET'])
# @app.route('/searchComics/<page>', methods=['GET'])
def searchComics():
    status = 404 # "Mientras no se demuestre que algo esta bien, está mal (política pesimista pero efectiva)"
    # Con json.loads() y json.dumps() juntos convertimos los argumentos a JSON y le quitanmos lo inmutable
    args = json.loads(json.dumps(request.args)) 

    resp = {}
    mrlv = Marvel(private_key, public_key)

    # Revisamos si hay un tipo de búsqueda / Check if there is a search type
    if 'type' not in args:
        args['type'] = 'characters'
    # Parámetros esperados / Expected parameters
    expected_params = ['s', 'type', 'offset', 'limit']
    # "Limpieza" de los parámetros / "Clean" of the parameters
    params = dict(
        filter(
            lambda x: 
                x[0] in expected_params, 
            args.items()
        )
    )
        
    # Obtenemos los comics / personajes // Get the comics / characters
    mrlv_response = mrlv.get_results(params)
    try:
        data = mrlv_response.get('data')
        results = data.get('results')
    except:
        results = []
    # Si hay o no resultados / If there are results or not
    if len(results) > 0:
        if params['type'] == 'characters':
            results = map(
                lambda x: {
                    "id": x['id'],
                    "name": x['name'],
                    "thumbnail": x['thumbnail']['path'] + '.' + x['thumbnail']['extension'],
                    "comics": x['comics']['items'],
                }, results)
        else:
            results = map(
                lambda x: { 
                    'id': x['id'],
                    'title': x['title'], # La forma correcta del título
                    'tittle': x['title'], # ¯\_(ツ)_/¯ La forma como indica el documento del examen
                    'image': x['thumbnail']['path'] + '.' + x['thumbnail']['extension'],
                    'onSaleDate': x['dates'][0]['date'], 
                }, results)
        # Definimos en la respuesta si los resultados son personajes o comics / Define in the response if the results are characters or comics
        # --> Recordar que args['type'] es 'characters' o 'comics'
        resp[args['type']] = list(results)
        # resp['page'] = int(data.get('offset') / data.get('limit')) + 1
        resp['total'] = data.get('total')
        resp['max_pages'] = int(data.get('total') / data.get('limit')) + 1
        status = 200 # En este punto claramente todo está bien
    else:
        resp['message'] = 'No results found'
    resp['status'] = status
    return json.dumps(resp), status, {'ContentType': 'application/json'}

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


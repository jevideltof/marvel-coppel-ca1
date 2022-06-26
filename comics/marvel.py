from datetime import datetime
import os
import requests
import hashlib
import urllib
from datetime import datetime

class Marvel:
    base_url = os.environ.get("MARVEL_BASE_URL")
    
    def __init__(self, private, public):
        self.private_key = private
        self.public_key = public
    
    def get_results(self, request_params=None):
        url = self.base_url + request_params['type'] + "?"
        # Creamos una key para el campo title o name según el tipo de búsqueda / Create a key for the title or name field according to the search type
        if request_params['type'] == 'characters':
            skey = 'nameStartsWith'
        else:
            skey = 'titleStartsWith' #Comics
        # Obtenemos el timestamp / Get the timestamp
        now = datetime.now()
        ts = int(datetime.timestamp(now))
        # Generamos el hash / Generate the hash
        hash = hashlib.md5((str(ts) + self.private_key + self.public_key).encode('utf-8')).hexdigest()
        # Creamos un diccionario con los datos / Create a dictionary with the data
        params = {
            "ts": ts,
            "apikey": self.public_key,
            "hash": hash,
        }
        # Si hay parámetros / If there are parameters
        fields_for_request = ['offset', 'limit']
        for field in fields_for_request:
            if field in request_params:
                params[field] = request_params[field]
        # Si hay un limit y es mayor que 100, lo cambiamos a 100 / If there is a limit and it's greater than 100, change it to 100
        if 'limit' in params and params['limit'] not in range(0, 100):
            params['limit'] = 100
        # Si hay un término de búsqueda 's', lo agregamos al diccionario / If there is a search term 's', add it to the dictionary
        if 's' in request_params:
            params[skey] = request_params['s']
        # print('____________________________')
        # print( url + urllib.parse.urlencode(params) )
        # print('____________________________')
        # Realizamos la petición / Make the request
        response = requests.get(url, params=params)
        # Convertimos la respuesta a JSON / Convert the response to JSON
        data = response.json()
        # Obtenemos los datos / Get the data
        return data
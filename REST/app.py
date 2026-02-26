from flask import Flask, request, jsonify, url_for, make_response
from flask_cors import CORS
import hashlib
import json
import subprocess
import os
import sys

app = Flask(__name__)
CORS(app)

# Base de données en mémoire
destinations = [
    {
        "id": 1,
        "name": "Paris",
        "country": "France",
        "price_per_day": 150,
        "activities": ["Tour Eiffel", "Louvre", "Champs-Élysées"]
    },
    {
        "id": 2,
        "name": "Tokyo",
        "country": "Japan",
        "price_per_day": 180,
        "activities": ["Mont Fuji", "Shibuya", "Temple Senso-ji"]
    },
    {
        "id": 3,
        "name": "New York",
        "country": "USA",
        "price_per_day": 200,
        "activities": ["Statue de la Liberté", "Central Park", "Times Square"]
    }
]

next_id = 4

# HATEOAS - Niveau 3 de Richardson

def generate_etag(data):
    """Génère un ETag pour le cache HTTP (RFC 7232)"""
    content = json.dumps(data, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()

def add_hateoas_links(destination, include_collection=True):
    """
    Ajoute les liens HATEOAS (Hypermedia As The Engine Of Application State)
    Niveau 3 du modèle de maturité de Richardson
    """
    links = {
        "self": {
            "href": url_for('get_destination', id=destination['id'], _external=True),
            "method": "GET"
        },
        "update": {
            "href": url_for('update_destination', id=destination['id'], _external=True),
            "method": "PUT"
        },
        "partial_update": {
            "href": url_for('patch_destination', id=destination['id'], _external=True),
            "method": "PATCH"
        },
        "delete": {
            "href": url_for('delete_destination', id=destination['id'], _external=True),
            "method": "DELETE"
        }
    }
    
    if include_collection:
        links["collection"] = {
            "href": url_for('get_destinations', _external=True),
            "method": "GET"
        }
    
    return {**destination, "_links": links}

@app.route('/')
def home():
    """
    Point d'entrée de l'API
    """
    return jsonify({
        "message": "Travel Planner REST API",
        "description": "API RESTful démontrant les principes REST",
        "_links": {
            "self": {
                "href": url_for('home', _external=True)
            },
            "destinations": {
                "href": url_for('get_destinations', _external=True),
                "method": "GET",
                "description": "Liste toutes les destinations"
            },
            "create_destination": {
                "href": url_for('create_destination', _external=True),
                "method": "POST",
                "description": "Crée une nouvelle destination"
            }
        },
        "maturity_level": "Richardson Level 3 (HATEOAS)"
    })

# GET - Récupérer toutes les destinations
@app.route('/destinations', methods=['GET'])
def get_destinations():
    """
    Récupère la liste des destinations avec liens HATEOAS
    Méthode sûre et idempotente
    """
    country = request.args.get('country')
    max_price = request.args.get('max_price', type=int)
    
    results = destinations
    
    if country:
        results = [d for d in results if d['country'].lower() == country.lower()]
    
    if max_price:
        results = [d for d in results if d['price_per_day'] <= max_price]
    
    # Ajouter les liens HATEOAS à chaque ressource
    results_with_links = [add_hateoas_links(d, include_collection=False) for d in results]
    
    # ETag pour le cache
    etag = generate_etag(results)
    
    # Vérifier si le client a déjà la version en cache (If-None-Match)
    if request.headers.get('If-None-Match') == etag:
        return '', 304  # Not Modified - le client peut utiliser son cache
    
    response = make_response(jsonify({
        "success": True,
        "count": len(results),
        "data": results_with_links,
        "_links": {
            "self": {
                "href": url_for('get_destinations', country=country, max_price=max_price, _external=True)
            },
            "create": {
                "href": url_for('create_destination', _external=True),
                "method": "POST"
            }
        }
    }), 200)
    
    # Headers HTTP avancés
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'max-age=300'  # Cache 5 minutes
    
    return response

# GET - Récupérer une destination par ID 
@app.route('/destinations/<int:id>', methods=['GET'])
def get_destination(id):
    """
    Récupère une destination spécifique avec liens HATEOAS
    Méthode sûre et idempotente
    Support du cache avec ETag
    """
    destination = next((d for d in destinations if d['id'] == id), None)
    
    if not destination:
        return jsonify({
            "success": False,
            "error": "Destination not found",
            "code": 404,
            "_links": {
                "collection": {
                    "href": url_for('get_destinations', _external=True)
                }
            }
        }), 404
    
    # ETag pour le cache (concurrence optimiste)
    etag = generate_etag(destination)
    
    # Support du cache HTTP 304
    if request.headers.get('If-None-Match') == etag:
        return '', 304
    
    # Ajouter les liens HATEOAS
    destination_with_links = add_hateoas_links(destination)
    
    response = make_response(jsonify({
        "success": True,
        "data": destination_with_links
    }), 200)
    
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'max-age=300'
    
    return response

# POST - Créer une nouvelle destination (avec Location header)
@app.route('/destinations', methods=['POST'])
def create_destination():
    """
    Crée une nouvelle destination
    Retourne 201 Created avec header Location
    Non-idempotente
    """
    global next_id
    
    data = request.get_json()
    
    # Validation
    required = ['name', 'country', 'price_per_day']
    for field in required:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing field: {field}",
                "code": 400
            }), 400
    
    # Vérifier si la destination existe déjà (éviter les doublons)
    existing = next((d for d in destinations if d['name'].lower() == data['name'].lower() 
                     and d['country'].lower() == data['country'].lower()), None)
    if existing:
        return jsonify({
            "success": False,
            "error": "Destination already exists",
            "code": 409,  # Conflict
            "_links": {
                "existing_resource": {
                    "href": url_for('get_destination', id=existing['id'], _external=True)
                }
            }
        }), 409
    
    new_destination = {
        "id": next_id,
        "name": data['name'],
        "country": data['country'],
        "price_per_day": data['price_per_day'],
        "activities": data.get('activities', [])
    }
    
    destinations.append(new_destination)
    next_id += 1
    
    # Ajouter les liens HATEOAS
    destination_with_links = add_hateoas_links(new_destination)
    
    response = make_response(jsonify({
        "success": True,
        "message": "Destination created",
        "data": destination_with_links
    }), 201)
    
    # Header Location - indique où trouver la ressource créée
    response.headers['Location'] = url_for('get_destination', id=new_destination['id'], _external=True)
    
    return response

# PUT - Mettre à jour une destination
@app.route('/destinations/<int:id>', methods=['PUT'])
def update_destination(id):
    """
    Met à jour complètement une destination
    Méthode IDEMPOTENTE : plusieurs appels identiques = même résultat
    Support de la concurrence optimiste avec If-Match (ETag)
    """
    destination = next((d for d in destinations if d['id'] == id), None)
    
    if not destination:
        return jsonify({
            "success": False,
            "error": "Destination not found",
            "code": 404
        }), 404
    
    # Concurrence optimiste : vérifier l'ETag (If-Match)
    current_etag = generate_etag(destination)
    if_match = request.headers.get('If-Match')
    
    if if_match and if_match != current_etag:
        return jsonify({
            "success": False,
            "error": "Precondition Failed - Resource was modified",
            "code": 412,
            "message": "La ressource a été modifiée. Veuillez récupérer la dernière version.",
            "_links": {
                "latest": {
                    "href": url_for('get_destination', id=id, _external=True)
                }
            }
        }), 412  # Precondition Failed
    
    data = request.get_json()
    
    # Mise à jour complète (PUT remplace toute la ressource)
    destination['name'] = data.get('name', destination['name'])
    destination['country'] = data.get('country', destination['country'])
    destination['price_per_day'] = data.get('price_per_day', destination['price_per_day'])
    destination['activities'] = data.get('activities', destination['activities'])
    
    # Nouvel ETag après modification
    new_etag = generate_etag(destination)
    
    destination_with_links = add_hateoas_links(destination)
    
    response = make_response(jsonify({
        "success": True,
        "message": "Destination updated (idempotent operation)",
        "data": destination_with_links
    }), 200)
    
    response.headers['ETag'] = new_etag
    
    return response

# PATCH - Mise à jour partielle d'une destination
@app.route('/destinations/<int:id>', methods=['PATCH'])
def patch_destination(id):
    """
    Mise à jour partielle d'une destination
    Seuls les champs fournis sont modifiés
    Support de la concurrence optimiste avec If-Match
    """
    destination = next((d for d in destinations if d['id'] == id), None)
    
    if not destination:
        return jsonify({
            "success": False,
            "error": "Destination not found",
            "code": 404
        }), 404
    
    # Concurrence optimiste
    current_etag = generate_etag(destination)
    if_match = request.headers.get('If-Match')
    
    if if_match and if_match != current_etag:
        return jsonify({
            "success": False,
            "error": "Precondition Failed",
            "code": 412
        }), 412
    
    data = request.get_json()
    
    # Mise à jour uniquement des champs fournis
    if 'name' in data:
        destination['name'] = data['name']
    if 'country' in data:
        destination['country'] = data['country']
    if 'price_per_day' in data:
        destination['price_per_day'] = data['price_per_day']
    if 'activities' in data:
        destination['activities'] = data['activities']
    
    new_etag = generate_etag(destination)
    destination_with_links = add_hateoas_links(destination)
    
    response = make_response(jsonify({
        "success": True,
        "message": "Destination partially updated",
        "data": destination_with_links
    }), 200)
    
    response.headers['ETag'] = new_etag
    
    return response

# DELETE - Supprimer une destination
@app.route('/destinations/<int:id>', methods=['DELETE'])
def delete_destination(id):
    """
    Supprime une destination
    Méthode IDEMPOTENTE : plusieurs DELETE sur la même ressource = même résultat
    Retourne 204 No Content si succès
    """
    global destinations
    
    destination = next((d for d in destinations if d['id'] == id), None)
    
    if not destination:
        # IDEMPOTENCE : DELETE sur ressource inexistante retourne 404
        # mais pourrait aussi retourner 204 (déjà supprimée)
        return jsonify({
            "success": False,
            "error": "Destination not found (already deleted or never existed)",
            "code": 404,
            "_links": {
                "collection": {
                    "href": url_for('get_destinations', _external=True)
                }
            }
        }), 404
    
    destinations = [d for d in destinations if d['id'] != id]
    
    # 204 No Content - pas de corps de réponse
    response = make_response('', 204)
    
    # Lien vers la collection dans les headers (optionnel)
    response.headers['Link'] = f'<{url_for("get_destinations", _external=True)}>; rel="collection"'
    
    return response

# ═══════════════════════════════════════════════════════ gRPC ═══

@app.route('/run-grpc-server', methods=['POST'])
def run_grpc_server():
    """
    Lance le serveur gRPC (grpc/server.py)
    """
    try:
        # Déterminer le répertoire du projet
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        grpc_server_path = os.path.join(base_dir, 'grpc', 'server.py')
        
        # Lancer le serveur en arrière-plan avec un timeout court pour capturer la sortie initiale
        result = subprocess.run(
            [sys.executable, grpc_server_path],
            cwd=os.path.join(base_dir, 'grpc'),
            capture_output=True,
            text=True,
            timeout=2
        )
        
        output = result.stdout + result.stderr
        
        return jsonify({
            "success": True,
            "output": output if output else "Serveur gRPC en cours de démarrage sur le port 50051..."
        }), 200
    except subprocess.TimeoutExpired:
        # Le timeout est attendu car le serveur reste actif
        return jsonify({
            "success": True,
            "output": "Serveur gRPC lancé avec succès sur le port 50051"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/run-grpc-client', methods=['POST'])
def run_grpc_client():
    """
    Lance le client gRPC (grpc/client.py) avec un sensor_id optionnel
    """
    try:
        data = request.get_json() or {}
        sensor_id = data.get('sensor_id', 'SN-001')
        
        # Déterminer le répertoire du projet
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        grpc_client_path = os.path.join(base_dir, 'grpc', 'client.py')
        
        # Créer un script temporaire qui appelle le client avec le sensor_id
        client_code = f"""
import grpc
import sensor_pb2
import sensor_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = sensor_pb2_grpc.SensorStub(channel)   
        response = stub.GetTemperature(sensor_pb2.SensorRequest(sensor_id="{sensor_id}"))
        
    print(f"Capteur: {sensor_id}")
    print(f"Température: {{response.temperature}}°{{response.unit}}")
    print(f"\\nRéponse gRPC reçue avec succès!")

if __name__ == '__main__':
    run()
"""
        
        # Lancer le client
        result = subprocess.run(
            [sys.executable, '-c', client_code],
            cwd=os.path.join(base_dir, 'grpc'),
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            output = result.stdout
            return jsonify({
                "success": True,
                "output": output
            }), 200
        else:
            error = result.stderr
            return jsonify({
                "success": False,
                "error": error if error else "Erreur lors de l'exécution du client gRPC"
            }), 500
    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "error": "Timeout: le serveur gRPC n'a pas répondu. Assurez-vous qu'il est lancé."
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("REST API started on http://localhost:5000")
    app.run(debug=True, port=5000)

from flask import Flask, request, jsonify

app = Flask(__name__)

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

@app.route('/')
def home():
    return jsonify({
        "message": "Travel Planner REST API",
        "endpoints": {
            "GET /destinations": "Liste toutes les destinations",
            "GET /destinations/<id>": "Récupère une destination",
            "POST /destinations": "Crée une destination",
            "PUT /destinations/<id>": "Met à jour une destination",
            "PATCH /destinations/<id>": "Mise à jour partielle d'une destination",
            "DELETE /destinations/<id>": "Supprime une destination"
        }
    })

# GET - Récupérer toutes les destinations
@app.route('/destinations', methods=['GET'])
def get_destinations():
    country = request.args.get('country')
    max_price = request.args.get('max_price', type=int)
    
    results = destinations
    
    if country:
        results = [d for d in results if d['country'].lower() == country.lower()]
    
    if max_price:
        results = [d for d in results if d['price_per_day'] <= max_price]
    
    return jsonify({
        "success": True,
        "count": len(results),
        "data": results
    }), 200

# GET - Récupérer une destination par ID
@app.route('/destinations/<int:id>', methods=['GET'])
def get_destination(id):
    destination = next((d for d in destinations if d['id'] == id), None)
    
    if not destination:
        return jsonify({
            "success": False,
            "error": "Destination not found"
        }), 404
    
    return jsonify({
        "success": True,
        "data": destination
    }), 200

# POST - Créer une nouvelle destination
@app.route('/destinations', methods=['POST'])
def create_destination():
    global next_id
    
    data = request.get_json()
    
    # Validation
    required = ['name', 'country', 'price_per_day']
    for field in required:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing field: {field}"
            }), 400
    
    new_destination = {
        "id": next_id,
        "name": data['name'],
        "country": data['country'],
        "price_per_day": data['price_per_day'],
        "activities": data.get('activities', [])
    }
    
    destinations.append(new_destination)
    next_id += 1
    
    return jsonify({
        "success": True,
        "message": "Destination created",
        "data": new_destination
    }), 201

# PUT - Mettre à jour une destination
@app.route('/destinations/<int:id>', methods=['PUT'])
def update_destination(id):
    destination = next((d for d in destinations if d['id'] == id), None)
    
    if not destination:
        return jsonify({
            "success": False,
            "error": "Destination not found"
        }), 404
    
    data = request.get_json()
    
    destination['name'] = data.get('name', destination['name'])
    destination['country'] = data.get('country', destination['country'])
    destination['price_per_day'] = data.get('price_per_day', destination['price_per_day'])
    destination['activities'] = data.get('activities', destination['activities'])
    
    return jsonify({
        "success": True,
        "message": "Destination updated",
        "data": destination
    }), 200

# PATCH - Mise à jour partielle d'une destination
@app.route('/destinations/<int:id>', methods=['PATCH'])
def patch_destination(id):
    destination = next((d for d in destinations if d['id'] == id), None)
    
    if not destination:
        return jsonify({
            "success": False,
            "error": "Destination not found"
        }), 404
    
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
    
    return jsonify({
        "success": True,
        "message": "Destination partially updated",
        "data": destination
    }), 200

# DELETE - Supprimer une destination
@app.route('/destinations/<int:id>', methods=['DELETE'])
def delete_destination(id):
    global destinations
    
    destination = next((d for d in destinations if d['id'] == id), None)
    
    if not destination:
        return jsonify({
            "success": False,
            "error": "Destination not found"
        }), 404
    
    destinations = [d for d in destinations if d['id'] != id]
    
    return jsonify({
        "success": True,
        "message": "Destination deleted"
    }), 200

if __name__ == '__main__':
    print("🚀 REST API started on http://localhost:5000")
    app.run(debug=True, port=5000)

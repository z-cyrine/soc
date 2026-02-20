import requests
import json

BASE_URL = "http://localhost:5000"

def print_response(title, response):
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")

print("Test de l'API REST Travel Planner\n")

# 1. GET - Toutes les destinations
print("\n1️⃣ GET - Récupérer toutes les destinations")
response = requests.get(f"{BASE_URL}/destinations")
print_response("GET /destinations", response)

# 2. GET - Filtrer par pays
print("\n2️⃣ GET - Filtrer par pays (France)")
response = requests.get(f"{BASE_URL}/destinations?country=France")
print_response("GET /destinations?country=France", response)

# 3. GET - Filtrer par prix
print("\n3️⃣ GET - Filtrer par prix (max 160€)")
response = requests.get(f"{BASE_URL}/destinations?max_price=160")
print_response("GET /destinations?max_price=160", response)

# 4. GET - Une destination spécifique
print("\n4️⃣ GET - Récupérer destination ID=1")
response = requests.get(f"{BASE_URL}/destinations/1")
print_response("GET /destinations/1", response)

# 5. POST - Créer une nouvelle destination
print("\n5️⃣ POST - Créer une nouvelle destination")
new_dest = {
    "name": "Barcelona",
    "country": "Spain",
    "price_per_day": 130,
    "activities": ["Sagrada Familia", "Park Güell", "La Rambla"]
}
response = requests.post(f"{BASE_URL}/destinations", json=new_dest)
print_response("POST /destinations", response)
new_id = response.json()['data']['id']

# 6. PUT - Mettre à jour
print(f"\n6️⃣ PUT - Mettre à jour destination ID={new_id}")
update_data = {
    "name": "Barcelona",
    "country": "Spain",
    "price_per_day": 140,
    "activities": ["Sagrada Familia", "Park Güell", "La Rambla", "Camp Nou"]
}
response = requests.put(f"{BASE_URL}/destinations/{new_id}", json=update_data)
print_response(f"PUT /destinations/{new_id}", response)

# 7. PATCH - Mise à jour partielle (seulement le prix)
print(f"\n7️⃣ PATCH - Mise à jour partielle destination ID={new_id}")
patch_data = {
    "price_per_day": 125
}
response = requests.patch(f"{BASE_URL}/destinations/{new_id}", json=patch_data)
print_response(f"PATCH /destinations/{new_id} (prix uniquement)", response)

# 8. DELETE - Supprimer
print(f"\n8️⃣ DELETE - Supprimer destination ID={new_id}")
response = requests.delete(f"{BASE_URL}/destinations/{new_id}")
print_response(f"DELETE /destinations/{new_id}", response)

# 9. Vérifier après suppression
print("\n9️⃣ GET - Vérifier après suppression")
response = requests.get(f"{BASE_URL}/destinations")
print_response("GET /destinations (après suppression)", response)

print("\n✅ Tests terminés!")

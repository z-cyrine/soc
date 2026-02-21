import requests
import json

BASE_URL = "http://localhost:5000"

def print_response(title, response):
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    print(f"Status: {response.status_code} {response.reason}")
    
    # Afficher les headers importants
    important_headers = ['ETag', 'Location', 'Cache-Control', 'Link']
    headers_found = {h: response.headers.get(h) for h in important_headers if h in response.headers}
    if headers_found:
        print(f"Headers: {json.dumps(headers_found, indent=2)}")
    
    # Afficher le corps de la réponse si présent
    if response.text:
        try:
            print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"Response: {response.text}")
    else:
        print("Response: <No Content>")

print("\n" + "="*80)
print("TEST DE L'API REST")
print("="*80)

# ==============================================================================
# PARTIE 1: HATEOAS - Découvrabilité de l'API
# ==============================================================================
print("\n\n" + "="*80)
print("PARTIE 1: HATEOAS - DÉCOUVRABILITÉ")
print("="*80)

print("\n1️⃣  GET / - Point d'entrée")
response = requests.get(f"{BASE_URL}/")
print_response("GET / (Entry Point)", response)
entry_point = response.json()

# ==============================================================================
# PARTIE 2: GET avec HATEOAS et Cache HTTP
# ==============================================================================
print("\n\n" + "="*80)
print("PARTIE 2: GET AVEC HATEOAS ET CACHE HTTP")
print("="*80)

print("\n2️⃣  GET /destinations - Récupérer toutes les destinations")
response = requests.get(f"{BASE_URL}/destinations")
print_response("GET /destinations", response)
etag_collection = response.headers.get('ETag')

print("\n3️⃣  Démonstration du cache HTTP - 304 Not Modified")
print("   → Envoi de If-None-Match avec l'ETag reçu")
headers = {'If-None-Match': etag_collection}
response = requests.get(f"{BASE_URL}/destinations", headers=headers)
print_response("GET /destinations (avec If-None-Match)", response)

print("\n4️⃣  GET /destinations/1 - Récupérer une destination")
response = requests.get(f"{BASE_URL}/destinations/1")
print_response("GET /destinations/1", response)
destination_data = response.json()
etag_dest_1 = response.headers.get('ETag')

# Vérifier les liens HATEOAS
print("\n   📋 Liens HATEOAS disponibles:")
if '_links' in destination_data['data']:
    for rel, link in destination_data['data']['_links'].items():
        print(f"      • {rel}: {link.get('href')} [{link.get('method', 'N/A')}]")

# ==============================================================================
# PARTIE 3: POST avec Header Location
# ==============================================================================
print("\n\n" + "="*80)
print("PARTIE 3: POST - CRÉATION AVEC HEADER LOCATION (201 Created)")
print("="*80)

print("\n5️⃣  POST /destinations - Créer une nouvelle destination")
new_dest = {
    "name": "Barcelona",
    "country": "Spain",
    "price_per_day": 130,
    "activities": ["Sagrada Familia", "Park Güell", "La Rambla"]
}
response = requests.post(f"{BASE_URL}/destinations", json=new_dest)
print_response("POST /destinations", response)
created_location = response.headers.get('Location')
new_id = response.json()['data']['id']

print(f"\n   📋 Header Location: {created_location}")
print("      → Indique l'URI de la ressource créée")

print("\n6️⃣  Test du code 409 Conflict - Tentative de créer un doublon")
response = requests.post(f"{BASE_URL}/destinations", json=new_dest)
print_response("POST /destinations (doublon)", response)

# ==============================================================================
# PARTIE 4: PUT - Mise à jour complète
# ==============================================================================
print("\n\n" + "="*80)
print("PARTIE 4: PUT - MISE À JOUR COMPLÈTE")
print("="*80)

print(f"\n7️⃣  PUT /destinations/{new_id} - Mise à jour complète de la destination")
update_data = {
    "name": "Barcelona",
    "country": "Spain",
    "price_per_day": 140,
    "activities": ["Sagrada Familia", "Park Güell", "La Rambla", "Camp Nou"]
}
response = requests.put(f"{BASE_URL}/destinations/{new_id}", json=update_data)
print_response(f"PUT /destinations/{new_id}", response)

print(f"\n8️⃣  Vérification de la mise à jour - GET /destinations/{new_id}")
response = requests.get(f"{BASE_URL}/destinations/{new_id}")
print_response(f"GET /destinations/{new_id} (après PUT)", response)

# ==============================================================================
# PARTIE 5: PATCH - Mise à jour partielle
# ==============================================================================
print("\n\n" + "="*80)
print("PARTIE 5: PATCH - MISE À JOUR PARTIELLE")
print("="*80)

print(f"\n🔟 PATCH /destinations/{new_id} - Modifier uniquement le prix")
patch_data = {"price_per_day": 125}
response = requests.patch(f"{BASE_URL}/destinations/{new_id}", json=patch_data)
print_response(f"PATCH /destinations/{new_id}", response)

# ==============================================================================
# PARTIE 6: DELETE avec Idempotence (204 No Content)
# ==============================================================================
print("\n\n" + "="*80)
print("PARTIE 6: DELETE - IDEMPOTENCE ET CODE 204 NO CONTENT")
print("="*80)

print(f"\n1️⃣1️⃣  DELETE /destinations/{new_id} - Première suppression (204 No Content)")
response = requests.delete(f"{BASE_URL}/destinations/{new_id}")
print_response(f"DELETE /destinations/{new_id}", response)

print(f"\n1️⃣2️⃣  DELETE /destinations/{new_id} - Deuxième suppression (IDEMPOTENCE)")
print("   → DELETE est idempotent : plusieurs appels = même résultat")
response = requests.delete(f"{BASE_URL}/destinations/{new_id}")
print_response(f"DELETE /destinations/{new_id} (2ème appel)", response)

# ==============================================================================
# PARTIE 7: Vérification finale
# ==============================================================================
print("\n\n" + "="*80)
print("PARTIE 7: VÉRIFICATION FINALE")
print("="*80)

print("\n1️⃣3️⃣  GET /destinations - État final")
response = requests.get(f"{BASE_URL}/destinations")
print_response("GET /destinations (final)", response)

# ==============================================================================
# RÉSUMÉ
# ==============================================================================
print("\n\n" + "="*80)
print("✅ RÉSUMÉ DES TESTS")
print("="*80)
print("\n📊 Concepts REST testés:")
print("   ✅ HATEOAS : Liens hypermédia dans toutes les réponses")
print("   ✅ Cache HTTP : ETag + If-None-Match → 304 Not Modified")
print("   ✅ Header Location : 201 Created avec URI de la ressource")
print("   ✅ Idempotence : PUT et DELETE testés plusieurs fois")
print("   ✅ Code 204 : No Content pour DELETE réussi")
print("   ✅ Code 409 : Conflict pour détection de doublon")
print("   ✅ Méthodes HTTP : GET, POST, PUT, PATCH, DELETE")
print("\n🎓 Modèle de maturité de Richardson:")
print("   • Niveau 0 ❌ : RPC sur HTTP (tunneling)")
print("   • Niveau 1 ❌ : Ressources différenciées")
print("   • Niveau 2 ✅ : Verbes et codes HTTP")
print("   • Niveau 3 ✅ : HATEOAS (implémenté)")
print("="*80 + "\n")


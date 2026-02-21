# Travel Planner REST API 

**API RESTful démontrant les principes REST**

## Objectif

Tester une API REST complète avec:
- Opérations CRUD (Create, Read, Update, Delete)
- Gestion du cache HTTP
- HATEOAS pour la découvrabilité
- Codes de statut HTTP appropriés

## Concepts REST démontrés

| Concept | Description |
|---------|-------------|
| **HATEOAS** | Liens hypermédia (`_links`) pour naviguer dans l'API |
| **Cache HTTP** | ETag + If-None-Match → code 304 |
| **Header Location** | 201 Created avec URI de la nouvelle ressource |
| **Idempotence** | PUT et DELETE donnent le même résultat si répétés |
| **Méthodes HTTP** | GET, POST, PUT, PATCH, DELETE |
| **Codes HTTP** | 200, 201, 204, 304, 400, 404, 409 |

## Installation

```bash
# Installer les dépendances
pip install -r requirements.txt
```

##  Démarrage

```bash
# Démarrer le serveur
python app.py
```

L'API sera disponible sur: `http://localhost:5000`

## Tester l'API

```bash
# Lancer les tests automatisés
python test_api.py
```

**Ce qui est testé** :
- ✅ Découvrabilité de l'API (HATEOAS)
- ✅ Opérations CRUD complètes
- ✅ Cache HTTP avec ETag
- ✅ Idempotence (PUT, DELETE)
- ✅ Tous les codes de statut HTTP

---

## Vue d'ensemble des opérations

| Méthode | Endpoint | Action | Codes |
|---------|----------|--------|-------|
| GET | `/destinations` | Liste toutes les destinations | 200, 304 |
| GET | `/destinations/<id>` | Récupère une destination | 200, 304, 404 |
| POST | `/destinations` | Crée une destination | 201, 409 |
| PUT | `/destinations/<id>` | Mise à jour complète | 200, 404 |
| PATCH | `/destinations/<id>` | Mise à jour partielle | 200, 404 |
| DELETE | `/destinations/<id>` | Supprime une destination | 204, 404 |

### Exemple de réponse avec HATEOAS
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Paris",
    "country": "France",
    "price_per_day": 150,
    "activities": ["Tour Eiffel", "Louvre"],
    "_links": {
      "self": {
        "href": "http://localhost:5000/destinations/1",
        "method": "GET"
      },
      "update": {
        "href": "http://localhost:5000/destinations/1",
        "method": "PUT"
      },
      "delete": {
        "href": "http://localhost:5000/destinations/1",
        "method": "DELETE"
      },
      "collection": {
        "href": "http://localhost:5000/destinations",
        "method": "GET"
      }
    }
  }
}
```

---

## Endpoints détaillés

### 1. Point d'entrée (HATEOAS)

```http
GET / HTTP/1.1
```

**Réponse** : Liens vers toutes les opérations disponibles (découvrabilité).

---

### 2. Lister les destinations

```http
GET /destinations HTTP/1.1
If-None-Match: "abc123"  #  Pour cache
```

**Paramètres de requête** :
- `country` : Filtrer par pays (ex: `?country=France`)
- `max_price` : Prix maximum par jour (ex: `?max_price=150`)

**Headers de réponse** :
- `ETag` : "abc123" - Identifiant de version pour le cache
- `Cache-Control` : max-age=300 - Mise en cache 5 minutes

**Codes de retour** :
- `200 OK` : Succès avec données
- `304 Not Modified` : Données en cache toujours valides

---

### 3. Récupérer une destination

```http
GET /destinations/1 HTTP/1.1
If-None-Match: "xyz789"  # Optionnel
```

**Codes de retour** :
- `200 OK` : Destination trouvée
- `304 Not Modified` : Cache valide
- `404 Not Found` : Destination inexistante

---

### 4. Créer une destination

```http
POST /destinations HTTP/1.1
Content-Type: application/json

{
  "name": "Barcelona",
  "country": "Spain",
  "price_per_day": 130,
  "activities": ["Sagrada Familia", "Park Güell"]
}
```

**Headers de réponse** :
- `Location` : URL de la ressource créée

**Codes de retour** :
- `201 Created` : Création réussie
- `400 Bad Request` : Données invalides
- `409 Conflict` : Destination déjà existante

---

### 5. Mettre à jour une destination (PUT)

```http
PUT /destinations/1 HTTP/1.1
Content-Type: application/json

{
  "name": "Paris",
  "country": "France",
  "price_per_day": 160,
  "activities": ["Tour Eiffel"]
}
```

**Comportement** : Remplace entièrement la ressource (idempotent).

**Codes de retour** :
- `200 OK` : Mise à jour réussie
- `404 Not Found` : Destination inexistante

---

### 6. Mise à jour partielle (PATCH)

```http
PATCH /destinations/1 HTTP/1.1
Content-Type: application/json

{
  "price_per_day": 145
}
```

**Différence avec PUT** : Seuls les champs fournis sont modifiés.

---

### 7. Supprimer une destination (DELETE - IDEMPOTENT)

```http
DELETE /destinations/1 HTTP/1.1
```

**Idempotence** : Supprimer plusieurs fois la même ressource = même résultat final.

**Codes de retour** :
- `204 No Content` : Suppression réussie (pas de corps)
- `404 Not Found` : Destination déjà supprimée/inexistante

---

## Codes de statut HTTP utilisés

| Code | Signification | Utilisation |
|------|---------------|-------------|
| **200** | OK | GET, PUT, PATCH réussis |
| **201** | Created | POST réussi - nouvelle ressource créée |
| **204** | No Content | DELETE réussi - pas de contenu |
| **304** | Not Modified | Ressource non modifiée (cache valide) |
| **400** | Bad Request | Données de requête invalides |
| **404** | Not Found | Ressource inexistante |
| **409** | Conflict | Conflit (ex: doublon) |

---

## Test en ligne de commande

### Utiliser curl

```bash
# Lister les destinations
curl http://localhost:5000/destinations

# Créer une destination
curl -X POST http://localhost:5000/destinations \
  -H "Content-Type: application/json" \
  -d '{"name":"Tokyo","country":"Japan","price_per_day":180,"activities":["Shibuya","Temple"]}'

# Récupérer une destination
curl http://localhost:5000/destinations/1

# Mettre à jour
curl -X PUT http://localhost:5000/destinations/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Paris","country":"France","price_per_day":160,"activities":["Eiffel"]}'

# Supprimer
curl -X DELETE http://localhost:5000/destinations/1
```
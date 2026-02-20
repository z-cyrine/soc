# Travel Planner REST API

API REST simple pour la gestion de destinations de voyage.

## Objectif

Démonstration des concepts REST avec:
- ✅ Opérations CRUD (GET, POST, PUT, PATCH, DELETE)
- ✅ Format JSON
- ✅ Codes HTTP appropriés
- ✅ Architecture stateless

## Installation

```bash
# Installer les dépendances
pip install -r requirements.txt
```

## Démarrage

```bash
# Démarrer le serveur
python app.py
```

L'API sera disponible sur: `http://localhost:5000`

## Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/destinations` | Liste toutes les destinations |
| GET | `/destinations?country=France` | Filtre par pays |
| GET | `/destinations?max_price=150` | Filtre par prix |
| GET | `/destinations/<id>` | Récupère une destination |
| POST | `/destinations` | Crée une destination |
| PUT | `/destinations/<id>` | Met à jour une destination (complète) |
| PATCH | `/destinations/<id>` | Mise à jour partielle d'une destination |
| DELETE | `/destinations/<id>` | Supprime une destination |

## Tester

```bash
# Dans un nouveau terminal
python test_api.py
```

## Exemples avec curl

```bash
# GET - Toutes les destinations
curl http://localhost:5000/destinations

# GET - Filtrer par pays
curl http://localhost:5000/destinations?country=France

# POST - Créer une destination
curl -X POST http://localhost:5000/destinations \
  -H "Content-Type: application/json" \
  -d '{"name":"Rome","country":"Italy","price_per_day":140,"activities":["Colisée"]}'

# PUT - Mettre à jour
curl -X PUT http://localhost:5000/destinations/1 \
  -H "Content-Type: application/json" \
  -d '{"price_per_day":160}'

# PATCH - Mise à jour partielle (seulement le prix)
curl -X PATCH http://localhost:5000/destinations/1 \
  -H "Content-Type: application/json" \
  -d '{"price_per_day":145}'

# DELETE - Supprimer
curl -X DELETE http://localhost:5000/destinations/3
```

## Caractéristiques REST

1. **Stateless**: Chaque requête est indépendante
2. **Ressources**: `/destinations`, `/destinations/{id}`
3. **Méthodes HTTP**: GET, POST, PUT, PATCH, DELETE
4. **JSON**: Format de données
5. **HTTP Status**: 200, 201, 404, 400

## Structure des données

```json
{
  "id": 1,
  "name": "Paris",
  "country": "France",
  "price_per_day": 150,
  "activities": ["Tour Eiffel", "Louvre"]
}
```

---
**Technologie**: Python + Flask + REST

# Travel Planner GraphQL API

**API GraphQL démontrant la sélection flexible de champs**

## Objectif

Tester une API GraphQL complète avec:
- Sélection flexible de champs (obtenez UNIQUEMENT ce dont vous avez besoin)
- Requêtes avec filtres (country, max_price)
- Mutations (Create, Update, Delete)
- Introspection et documentation automatique

## Concepts GraphQL démontrés

| Concept | Description |
|---------|-------------|
| **Field Selection** | Sélection flexible de champs (vs REST qui retourne tout) |
| **Filtering** | Filtres côté serveur (country, max_price) |
| **Mutations** | Opérations d'écriture (CREATE, UPDATE, DELETE) |
| **Strong Typing** | Schéma fortement typé avec validation |
| **Introspection** | Découvrir le schéma automatiquement |
| **Single Endpoint** | Un seul endpoint POST (vs REST multi-endpoint) |

## Installation

```bash
# Installer les dépendances
pip install -r requirements.txt
```

## Démarrage

```bash
# Démarrer le serveur
python server.py
```

L'API sera disponible sur: `http://localhost:5001`

## Tester l'API

### Option 1: Utiliser le client Python

```bash
# Lancer le client avec exemples
python client.py
```

**Ce qui est testé** :
- ✅ Requêtes simples (query destinations)
- ✅ Filtres (country, max_price)
- ✅ Sélection flexible de champs
- ✅ Mutations (create, update, delete)
- ✅ Gestion d'erreurs

### Option 2: Utiliser GraphQL Playground (navigateur)

1. Démarrer le serveur: `python server.py`
2. Ouvrir dans le navigateur: `http://localhost:5001/playground`
3. Écrire et exécuter des requêtes GraphQL

---

## Vue d'ensemble des opérations

### Requêtes (Lectures)

| Requête | Description | Paramètres |
|---------|-------------|-----------|
| `destination(id)` | Récupère une destination par ID | `id: Int` |
| `destinations(country, max_price)` | Liste les destinations | `country: String`, `max_price: Float` |

### Mutations (Écritures)

| Mutation | Description | Paramètres |
|----------|-------------|-----------|
| `createDestination(input)` | Crée une destination | `name`, `country`, `price_per_day`, `activities` |
| `updateDestination(id, ...)` | Met à jour une destination | `id`, champs à modifier |
| `deleteDestination(id)` | Supprime une destination | `id: Int` |

---

## Exemples de Requêtes GraphQL

### 1. Récupérer TOUTES les destinations (complètes)

```graphql
query {
  destinations {
    id
    name
    country
    price_per_day
    activities
  }
}
```

**Réponse**:
```json
{
  "data": {
    "destinations": [
      {
        "id": 1,
        "name": "Paris",
        "country": "France",
        "price_per_day": 150.0,
        "activities": ["Tour Eiffel", "Louvre", "Champs-Élysées"]
      },
      ...
    ]
  }
}
```

---

### 2. Sélection MINIMALE de champs (avantage GraphQL!)

```graphql
query {
  destination(id: 1) {
    name
    activities
  }
}
```

**Réponse** (plus légère, seulement 2 champs):
```json
{
  "data": {
    "destination": {
      "name": "Paris",
      "activities": ["Tour Eiffel", "Louvre", "Champs-Élysées"]
    }
  }
}
```

💡 **Avantage GraphQL**: Avec REST, vous recevriez TOUS les champs même si vous n'en aviez besoin que de 2!

---

### 3. Filtrer par pays

```graphql
query {
  destinations(country: "France") {
    id
    name
    price_per_day
  }
}
```

**Réponse**:
```json
{
  "data": {
    "destinations": [
      {
        "id": 1,
        "name": "Paris",
        "price_per_day": 150.0
      }
    ]
  }
}
```

---

### 4. Filtrer par budget

```graphql
query {
  destinations(max_price: 150) {
    name
    country
    price_per_day
  }
}
```

---

### 5. Créer une destination (Mutation)

```graphql
mutation {
  createDestination(input: {
    name: "Rome"
    country: "Italy"
    price_per_day: 140
    activities: ["Colosseum", "Vatican", "Trevi Fountain"]
  }) {
    success
    message
    destination {
      id
      name
    }
  }
}
```

**Réponse**:
```json
{
  "data": {
    "createDestination": {
      "success": true,
      "message": "Destination 'Rome' créée avec succès",
      "destination": {
        "id": 5,
        "name": "Rome"
      }
    }
  }
}
```

---

### 6. Mettre à jour une destination (Mutation)

```graphql
mutation {
  updateDestination(id: 1, price_per_day: 160) {
    success
    message
    destination {
      name
      price_per_day
    }
  }
}
```

---

### 7. Supprimer une destination (Mutation)

```graphql
mutation {
  deleteDestination(id: 4) {
    success
    message
  }
}
```

---

## Comparaison GraphQL vs REST

### Exemple: Récupérer une destination avec ses détails

#### 📌 Approche REST (1 ou plusieurs requêtes)

```bash
# Requête 1: Récupérer la destination
GET /destinations/1

# Réponse: TOUS les champs (waste!)
{
  "id": 1,
  "name": "Paris",
  "country": "France",
  "price_per_day": 150,
  "activities": [...]
}
```

**Problème REST**: Vous recevez des champs inutiles.

#### 📌 Approche GraphQL (1 requête, sélection flexible)

```graphql
query {
  destination(id: 1) {
    name
    price_per_day
  }
}

# Réponse: UNIQUEMENT les 2 champs demandés
{
  "data": {
    "destination": {
      "name": "Paris",
      "price_per_day": 150
    }
  }
}
```

**Avantage GraphQL**: Bandwidth optimisé, réponse plus légère!

---

## Architecture GraphQL

```
┌─────────────────────────────────────────┐
│         CLIENT (Python/Browser)         │
│   • Envoie requête GraphQL JSON         │
│   • Sélectionne champs souhaités        │
└──────────────┬──────────────────────────┘
               │ POST /graphql
               │ {"query": "..."}
               ▼
┌─────────────────────────────────────────┐
│        SERVEUR GRAPHQL (Flask)          │
│   • Parser la requête GraphQL           │
│   • Valider contre le schéma            │
│   • Résoudre les champs demandés        │
│   • Retourner JSON avec données         │
└──────────────┬──────────────────────────┘
               │ {"data": {...}}
               ▼
┌─────────────────────────────────────────┐
│      CLIENT reçoit réponse JSON         │
│   • Seulement les champs demandés       │
│   • Format prévisible                   │
└─────────────────────────────────────────┘
```

---

## Points clés de GraphQL

✅ **Avantages**:
- Sélection flexible de champs (bandwidth optimisé)
- Un seul endpoint pour toutes les requêtes
- Schéma fortement typé et documenté
- Filtres côté serveur (pas de filtrage client)
- Réductions de requêtes (vs REST qui en demande plusieurs)

❌ **Inconvénients**:
- Courbe d'apprentissage plus abrupte que REST
- Caching HTTP moins intuitif (single endpoint)
- Peut être "overkill" pour APIs simples
- Requêtes complexes peuvent être coûteuses en serveur

---

## Fichiers du projet

- **server.py** — Serveur GraphQL (Graphene + Flask)
- **client.py** — Client Python avec 7 scénarios de test
- **requirements.txt** — Dépendances (graphene, flask, requests)
- **README.md** — Cette documentation

---

## Cas d'usage réels de GraphQL

- 🌍 **Facebook** (créateur de GraphQL)
- 🔍 **GitHub** (GitHub API v4)
- 🎬 **Shopify** (plateforme e-commerce)
- 📱 **Twitter**, **Slack**, **Stripe**

Ces entreprises utilisent GraphQL car:
- Clients mobiles ont besoin de réduire la bande passante
- APIs flexibles pour différents use cases
- Schéma auto-documenté pour les développeurs


"""
GraphQL Server Example - Travel Planner Service
Ce serveur expose un service de voyage via GraphQL avec sélection de champs
Cas d'usage réel: Les APIs modernes utilisent GraphQL pour la flexibilité des clients
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import graphene
from graphene import Schema, ObjectType, String, Int, Float, List, Field
from graphql import graphql_sync

app = Flask(__name__)
CORS(app)


#Classe Destination
class Destination(ObjectType):
    """Type GraphQL représentant une destination de voyage"""
    id = Int()
    name = String()
    country = String()
    price_per_day = Float()
    activities = List(String)
    
    class Meta:
        description = "Une destination touristique"

# BD SIMULÉE (En mémoire)

DESTINATIONS_DB = [
    {
        "id": 1,
        "name": "Paris",
        "country": "France",
        "price_per_day": 150.0,
        "activities": ["Tour Eiffel", "Louvre", "Champs-Élysées"]
    },
    {
        "id": 2,
        "name": "Tokyo",
        "country": "Japan",
        "price_per_day": 180.0,
        "activities": ["Mont Fuji", "Shibuya", "Temple Senso-ji"]
    },
    {
        "id": 3,
        "name": "New York",
        "country": "USA",
        "price_per_day": 200.0,
        "activities": ["Statue de la Liberté", "Central Park", "Times Square"]
    },
    {
        "id": 4,
        "name": "Barcelona",
        "country": "Spain",
        "price_per_day": 130.0,
        "activities": ["Sagrada Familia", "Park Güell", "Las Ramblas"]
    }
]

next_id = 5

# Requetes GraphQL (Lectures)

class Query(ObjectType):
    
    destination = Field(
        Destination,
        id=Int(required=True)
    )
    
    destinations = List(
        Destination,
        country=String(),
        max_price=Float()
    )
    
    def resolve_destination(self, info, id):
        """Résout une requête pour une destination spécifique"""
        print(f"GraphQL Query: destination(id: {id})")
        destination = next((d for d in DESTINATIONS_DB if d['id'] == id), None)
        if not destination:
            raise Exception(f"Destination avec ID {id} non trouvée")
        return destination
    
    def resolve_destinations(self, info, country=None, max_price=None):
        """Résout une requête pour toutes les destinations avec filtres"""
        print(f"GraphQL Query: destinations(country: {country}, max_price: {max_price})")
        
        results = DESTINATIONS_DB
        
        # Filtrer par pays si spécifié
        if country:
            results = [d for d in results if d['country'].lower() == country.lower()]
        
        # Filtrer par prix maximum si spécifié
        if max_price:
            results = [d for d in results if d['price_per_day'] <= max_price]
        
        return results

# Requetes GraphQL (Écritures)

#Créer une destination
class CreateDestinationInput(graphene.InputObjectType):
    """Input pour créer une destination"""
    name = String(required=True)
    country = String(required=True)
    price_per_day = Float(required=True)
    activities = List(String)


class CreateDestination(graphene.Mutation):
    """créer une nouvelle destination"""
    
    destination = Field(Destination)
    success = graphene.Boolean()
    message = String()
    
    class Arguments:
        input = CreateDestinationInput(required=True)
    
    def mutate(self, info, input):
        global next_id
        
        print(f"GraphQL Mutation: createDestination({input})")
        
        # Vérifier si la destination existe déjà
        existing = next((d for d in DESTINATIONS_DB 
                        if d['name'].lower() == input.name.lower() 
                        and d['country'].lower() == input.country.lower()), None)
        
        if existing:
            return CreateDestination(
                destination=None,
                success=False,
                message=f"Destination '{input.name}' existe déjà en {input.country}"
            )
        
        # Créer la nouvelle destination
        new_destination = {
            "id": next_id,
            "name": input.name,
            "country": input.country,
            "price_per_day": input.price_per_day,
            "activities": input.activities or []
        }
        
        DESTINATIONS_DB.append(new_destination)
        next_id += 1
        
        return CreateDestination(
            destination=new_destination,
            success=True,
            message=f"Destination '{input.name}' créée avec succès"
        )


#mettre à jour une destination
class UpdateDestination(graphene.Mutation):
    
    destination = Field(Destination)
    success = graphene.Boolean()
    message = String()
    
    class Arguments:
        id = Int(required=True)
        name = String()
        country = String()
        price_per_day = Float()
        activities = List(String)
    
    def mutate(self, info, id, name=None, country=None, price_per_day=None, activities=None):
        print(f"GraphQL Mutation: updateDestination(id: {id})")
        
        destination = next((d for d in DESTINATIONS_DB if d['id'] == id), None)
        
        if not destination:
            return UpdateDestination(
                destination=None,
                success=False,
                message=f"Destination avec ID {id} non trouvée"
            )
        
        # Mettre à jour les champs fournis
        if name is not None:
            destination['name'] = name
        if country is not None:
            destination['country'] = country
        if price_per_day is not None:
            destination['price_per_day'] = price_per_day
        if activities is not None:
            destination['activities'] = activities
        
        return UpdateDestination(
            destination=destination,
            success=True,
            message=f"Destination '{destination['name']}' mise à jour"
        )

#Suppression
class DeleteDestination(graphene.Mutation):
    
    success = graphene.Boolean()
    message = String()
    
    class Arguments:
        id = Int(required=True)
    
    def mutate(self, info, id):
        global DESTINATIONS_DB
        
        print(f"GraphQL Mutation: deleteDestination(id: {id})")
        
        destination = next((d for d in DESTINATIONS_DB if d['id'] == id), None)
        
        if not destination:
            return DeleteDestination(
                success=False,
                message=f"Destination avec ID {id} non trouvée"
            )
        
        DESTINATIONS_DB = [d for d in DESTINATIONS_DB if d['id'] != id]
        
        return DeleteDestination(
            success=True,
            message=f"Destination supprimée avec succès"
        )


class Mutation(ObjectType):
    """Mutations disponibles dans le service GraphQL"""
    create_destination = CreateDestination.Field()
    update_destination = UpdateDestination.Field()
    delete_destination = DeleteDestination.Field()


# SCHÉMA GraphQL - Créer correctement le schéma Graphene

schema = Schema(query=Query, mutation=Mutation)

# Obtenir le schéma GraphQL interne (pas Graphene)
graphql_schema = schema.graphql_schema


# ROUTES FLASK

@app.route('/')
def home():
    """Point d'entrée du service GraphQL"""
    return jsonify({
        "message": "Travel Planner GraphQL API",
        "endpoint": "/graphql"
    })


@app.route('/graphql', methods=['POST'])
def graphql_endpoint():
    """
    Endpoint GraphQL principal
    Accepte des requêtes GraphQL en JSON
    """
    try:
        data = request.get_json()
        query = data.get('query')
        variables = data.get('variables', {})
        
        if not query:
            return jsonify({
                "errors": [{"message": "Requête GraphQL manquante"}]
            }), 400
        
        print(f"\n{'='*70}")
        print(f"GraphQL Request:")
        print(f"{query}")
        if variables:
            print(f"Variables: {variables}")
        print(f"{'='*70}")
        
        result = graphql_sync(
            graphql_schema,
            query,
            variable_values=variables
        )
        
        response_data = {
            "data": result.data
        }
        
        if result.errors:
            response_data["errors"] = [
                {"message": str(error)} for error in result.errors
            ]
        
        print(f"\nGraphQL Response:")
        print(f"{response_data}")
        print(f"{'='*70}\n")
        
        status_code = 200 if not result.errors else 400
        return jsonify(response_data), status_code
    
    except Exception as e:
        print(f"Erreur GraphQL: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "errors": [{"message": str(e)}]
        }), 500


def main():
    """Démarre le serveur GraphQL"""
    print("\n" + "="*70)
    print("SERVEUR GRAPHQL - DÉMARRÉ")
    print("="*70)
    print("URL du service: http://localhost:5001")
    print("Endpoint GraphQL: POST http://localhost:5001/graphql")
    print("="*70)
    
    try:
        app.run(debug=True, port=5001)
    except KeyboardInterrupt:
        print("\n\nServeur GraphQL arrêté avec succès\n")


if __name__ == '__main__':
    main()

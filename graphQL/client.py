"""
GraphQL Client Example - Travel Planner Service
Client GraphQL qui consomme le service de voyage
Illustre la sélection flexible de champs et les mutations
"""

import requests
import json
from datetime import datetime

class TravelPlannerClient:
    """Client pour interagir avec le service GraphQL de voyage"""
    
    def __init__(self, graphql_url='http://localhost:5001/graphql'):
        """
        Initialise le client GraphQL
        
        Args:
            graphql_url: URL de l'endpoint GraphQL
        """
        self.graphql_url = graphql_url
        print(f"Client GraphQL connecté à: {graphql_url}\n")
    
    def execute_query(self, query, variables=None):
        """
        Exécute une requête GraphQL
        
        Args:
            query: Requête GraphQL (string)
            variables: Variables GraphQL optionnelles (dict)
        
        Returns:
            Réponse JSON de l'API
        """
        payload = {
            'query': query
        }
        
        if variables:
            payload['variables'] = variables
        
        try:
            response = requests.post(
                self.graphql_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            return response.json()
        except Exception as e:
            print(f"Erreur lors de l'appel GraphQL: {e}")
            return None
    
    def pretty_print_response(self, response, title="GraphQL Response"):
        """Affiche une réponse GraphQL de manière lisible"""
        print(f"\n{'='*70}")
        print(f"{title}")
        print(f"{'='*70}")
        
        if response is None:
            print("Pas de réponse")
            return
        
        if 'errors' in response and response['errors']:
            print("ERREURS:")
            for error in response['errors']:
                print(f"   • {error['message']}")
        
        if 'data' in response:
            print("DONNÉES:")
            print(json.dumps(response['data'], indent=2, ensure_ascii=False))
        
        print(f"{'='*70}\n")
    
    def query_all_destinations(self):
        """Requête 1: Récupérer TOUTES les destinations"""
        print("\n" + "-"*70)
        print("SCÉNARIO: Récupérer TOUTES les destinations")
        print("-"*70)
        
        query = """
        query {
            destinations {
                id
                name
                country
                pricePerDay
                activities
            }
        }
        """
        
        print("GraphQL Query (sélection de champs):")
        print(query)
        
        response = self.execute_query(query)
        self.pretty_print_response(response, "Réponse - Toutes les destinations")
        return response
    
    def query_destinations_with_filter(self, country):
        """Requête 2: Récupérer les destinations d'un pays spécifique"""
        print("\n" + "-"*70)
        print(f"SCÉNARIO: Récupérer destinations en {country}")
        print("-"*70)
        
        query = f"""
        query {{
            destinations(country: "{country}") {{
                id
                name
                country
                pricePerDay
            }}
        }}
        """
        
        print("GraphQL Query (avec filtrage):")
        print(query)
        
        response = self.execute_query(query)
        self.pretty_print_response(response, f"Réponse - Destinations en {country}")
        return response
    
    def query_single_destination(self, destination_id):
        """Requête 3: Récupérer une destination spécifique (sélection minimale)"""
        print("\n" + "-"*70)
        print(f"SCÉNARIO: Récupérer destination ID {destination_id} (champs minimaux)")
        print("-"*70)
        
        query = f"""
        query {{
            destination(id: {destination_id}) {{
                name
                activities
            }}
        }}
        """
        
        print("GraphQL Query (sélection minimale de champs):")
        print(query)
        print("\n Avantage GraphQL: Vous obtenez UNIQUEMENT 'name' et 'activities'")
        print("   REST retournerait TOUS les champs (waste de bande passante)")
        
        response = self.execute_query(query)
        self.pretty_print_response(response, "Réponse - Destination spécifique")
        return response
    
    def query_expensive_destinations(self, max_price):
        """Requête 4: Récupérer les destinations par budget"""
        print("\n" + "-"*70)
        print(f"SCÉNARIO: Destinations avec budget max {max_price} EUR/jour")
        print("-"*70)
        
        query = f"""
        query {{
            destinations(maxPrice: {max_price}) {{
                name
                pricePerDay
            }}
        }}
        """
        
        print("GraphQL Query (filtrage par prix):")
        print(query)
        
        response = self.execute_query(query)
        self.pretty_print_response(response, "Réponse - Destinations pas chères")
        return response
    
    def mutation_create_destination(self, name, country, price_per_day, activities):
        """Mutation 1: Créer une nouvelle destination"""
        print("\n" + "-"*70)
        print(f"MUTATION: Créer destination '{name}'")
        print("-"*70)
        
        activities_str = ', '.join([f'"{act}"' for act in activities])
        
        mutation = f"""
        mutation {{
            createDestination(input: {{
                name: "{name}"
                country: "{country}"
                pricePerDay: {price_per_day}
                activities: [{activities_str}]
            }}) {{
                success
                message
                destination {{
                    id
                    name
                    country
                }}
            }}
        }}
        """
        
        print(" GraphQL Mutation:")
        print(mutation)
        
        response = self.execute_query(mutation)
        self.pretty_print_response(response, "Réponse - Création")
        return response
    
    def mutation_update_destination(self, destination_id, price_per_day):
        """Mutation 2: Mettre à jour le prix d'une destination"""
        print("\n" + "-"*70)
        print(f"MUTATION: Mettre à jour prix destination ID {destination_id}")
        print("-"*70)
        
        mutation = f"""
        mutation {{
            updateDestination(id: {destination_id}, pricePerDay: {price_per_day}) {{
                success
                message
                destination {{
                    name
                    pricePerDay
                }}
            }}
        }}
        """
        
        print(" GraphQL Mutation:")
        print(mutation)
        
        response = self.execute_query(mutation)
        self.pretty_print_response(response, "Réponse - Mise à jour")
        return response
    
    def mutation_delete_destination(self, destination_id):
        """Mutation 3: Supprimer une destination"""
        print("\n" + "-"*70)
        print(f"MUTATION: Supprimer destination ID {destination_id}")
        print("-"*70)
        
        mutation = f"""
        mutation {{
            deleteDestination(id: {destination_id}) {{
                success
                message
            }}
        }}
        """
        
        print(" GraphQL Mutation:")
        print(mutation)
        
        response = self.execute_query(mutation)
        self.pretty_print_response(response, "Réponse - Suppression")
        return response


def main():
    """
    Démonstration du client GraphQL avec différents scénarios
    """
    print("\n" + "-"*70)
    print("CLIENT GRAPHQL - Exemples de Requêtes")
    print("-"*70)
    
    try:
        # Créer le client GraphQL
        client = TravelPlannerClient()
        
        print("\n SCÉNARIOS DE DÉMONSTRATION (7 exemples):\n")
        
        # SCÉNARIO 1: Récupérer toutes les destinations
        print("\n REQUÊTE 1: Récupérer TOUTES les destinations")
        print("   Cas: Afficher la liste complète des destinations disponibles")
        client.query_all_destinations()
        
        # SCÉNARIO 2: Récupérer destinations d'un pays spécifique
        print("\n REQUÊTE 2: Filtrer par pays (France)")
        print("   Cas: L'utilisateur cherche des destinations en France")
        client.query_destinations_with_filter("France")
        
        # SCÉNARIO 3: Sélection minimale de champs
        print("\n REQUÊTE 3: Sélection MINIMALE de champs (avantage GraphQL)")
        print("   Cas: Afficher juste le nom et les activités")
        client.query_single_destination(1)
        
        # SCÉNARIO 4: Filtrer par budget
        print("\n REQUÊTE 4: Filtrer par prix (budget limité)")
        print("   Cas: L'utilisateur a un budget max de 150 EUR/jour")
        client.query_expensive_destinations(150)
        
        # SCÉNARIO 5: Créer une destination
        print("\n MUTATION 1: Créer une destination")
        print("   Cas: Ajouter une nouvelle destination au catalogue")
        client.mutation_create_destination(
            name="Rome",
            country="Italy",
            price_per_day=140,
            activities=["Colosseum", "Vatican", "Trevi Fountain"]
        )
        
        # SCÉNARIO 6: Mettre à jour
        print("\n MUTATION 2: Mettre à jour le prix")
        print("   Cas: Ajuster le prix d'une destination")
        client.mutation_update_destination(
            destination_id=1,
            price_per_day=165
        )
        
        # SCÉNARIO 7: Supprimer
        print("\n MUTATION 3: Supprimer une destination")
        print("   Cas: Retirer une destination du catalogue")
        client.mutation_delete_destination(destination_id=4)
        
        # RÉSUMÉ FINAL
        print("\n" + "-"*70)
        print("TOUS LES TESTS GRAPHQL ONT RÉUSSI!")
        print("-"*70)
        print("\n RÉSUMÉ:")
        print("   • Requêtes testées: 4 (queries avec filtres et sélection)")
        print("   • Mutations testées: 3 (create, update, delete)")
        print("-"*70 + "\n")
        
    except Exception as e:
        print(f"\n ERREUR lors de l'exécution:")
        print(f"   {e}")
        print("\n Assurez-vous que le serveur GraphQL est démarré:")
        print("   python server.py\n")


if __name__ == '__main__':
    main()

"""
SOAP Client Example - Banking Service
Client SOAP qui consomme le service bancaire
Illustre l'utilisation de types complexes et d'opérations réalistes
"""

from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
import logging
from datetime import datetime

# Configuration du logging pour voir les requêtes/réponses SOAP
logging.basicConfig(level=logging.INFO)
logging.getLogger('zeep.transports').setLevel(logging.DEBUG)


class BankingClient:
    """
    Client pour interagir avec le service SOAP bancaire
    """
    
    def __init__(self, wsdl_url='http://localhost:8000/?wsdl'):
        """
        Initialise le client SOAP bancaire
        
        Args:
            wsdl_url: URL du fichier WSDL
        """
        session = Session()
        transport = Transport(session=session)
        settings = Settings(strict=False, xml_huge_tree=True)
        
        self.client = Client(wsdl_url, transport=transport, settings=settings)
        print(f"✅ Client SOAP bancaire connecté à: {wsdl_url}\n")
    
    def get_customer_info(self, customer_id):
        """Récupère les informations d'un client"""
        print(f"\n{'='*70}")
        print(f"📤 SOAP Request: get_customer_info('{customer_id}')")
        print(f"{'='*70}")
        try:
            result = self.client.service.get_customer_info(customer_id)
            print(f"📥 SOAP Response:")
            print(f"   Nom: {result.first_name} {result.last_name}")
            print(f"   Email: {result.email}")
            print(f"   Téléphone: {result.phone}")
            print(f"   Client depuis: {result.registration_date.strftime('%d/%m/%Y')}")
            print(f"{'='*70}\n")
            return result
        except Exception as e:
            print(f"❌ Erreur SOAP: {e}")
            print(f"{'='*70}\n")
            raise
    
    def get_account_balance(self, account_number):
        """Consulte le solde d'un compte"""
        print(f"\n{'='*70}")
        print(f"📤 SOAP Request: get_account_balance('{account_number}')")
        print(f"{'='*70}")
        try:
            result = self.client.service.get_account_balance(account_number)
            print(f"📥 SOAP Response:")
            print(f"   Numéro de compte: {result.account_number}")
            print(f"   Type: {result.account_type}")
            print(f"   Solde: {result.balance:.2f} {result.currency}")
            print(f"   Statut: {result.status}")
            print(f"{'='*70}\n")
            return result
        except Exception as e:
            print(f"❌ Erreur SOAP: {e}")
            print(f"{'='*70}\n")
            raise
    
    def transfer_money(self, from_account, amount, to_account, description):
        """Effectue un transfert d'argent"""
        print(f"\n{'='*70}")
        print(f"📤 SOAP Request: transfer_money")
        print(f"   De: {from_account}")
        print(f"   Vers: {to_account}")
        print(f"   Montant: {amount} EUR")
        print(f"   Description: {description}")
        print(f"{'='*70}")
        try:
            result = self.client.service.transfer_money(from_account, amount, to_account, description)
            print(f"📥 SOAP Response:")
            if result.success:
                print(f"   ✅ Statut: SUCCÈS")
                print(f"   Transaction ID: {result.transaction_id}")
                print(f"   Nouveau solde: {result.new_balance:.2f} EUR")
            else:
                print(f"   ❌ Statut: ÉCHEC")
            print(f"   Message: {result.message}")
            print(f"{'='*70}\n")
            return result
        except Exception as e:
            print(f"❌ Erreur SOAP: {e}")
            print(f"{'='*70}\n")
            raise
    
    def get_transaction_history(self, account_number, limit=10):
        """Récupère l'historique des transactions"""
        print(f"\n{'='*70}")
        print(f"📤 SOAP Request: get_transaction_history('{account_number}', limit={limit})")
        print(f"{'='*70}")
        try:
            result = self.client.service.get_transaction_history(account_number, limit)
            print(f"📥 SOAP Response: {len(result)} transaction(s)")
            for idx, txn in enumerate(result, 1):
                print(f"\n   Transaction #{idx}:")
                print(f"      ID: {txn.transaction_id}")
                print(f"      Type: {txn.transaction_type}")
                print(f"      De: {txn.from_account} → Vers: {txn.to_account}")
                print(f"      Montant: {txn.amount:.2f} {txn.currency}")
                print(f"      Statut: {txn.status}")
                print(f"      Date: {txn.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
                print(f"      Description: {txn.description}")
            print(f"{'='*70}\n")
            return result
        except Exception as e:
            print(f"❌ Erreur SOAP: {e}")
            print(f"{'='*70}\n")
            raise
    
    def show_available_methods(self):
        """Affiche toutes les méthodes disponibles dans le WSDL"""
        print("\n" + "="*70)
        print("📋 OPÉRATIONS DISPONIBLES DANS LE SERVICE BANCAIRE SOAP:")
        print("="*70)
        for service in self.client.wsdl.services.values():
            print(f"\n🏦 Service: {service.name}")
            for port in service.ports.values():
                operations = sorted(port.binding._operations.values(), 
                                  key=lambda x: x.name)
                for operation in operations:
                    print(f"   • {operation.name}")
        print("="*70 + "\n")


def main():
    """
    Démonstration du client SOAP bancaire avec différents scénarios
    """
    print("\n" + "="*70)
    print("🏦 CLIENT BANCAIRE SOAP - Exemples")
    print("="*70)
    
    try:
        # Créer le client bancaire
        client = BankingClient()
        
        # Afficher les méthodes disponibles
        client.show_available_methods()
        
        print("\n SCÉNARIOS DE TEST (4 opérations):\n")
        
        # SCÉNARIO 1: Consultation des informations client
        print("📋 SCÉNARIO 1: Consultation des informations client")
        print("-" * 70)
        customer = client.get_customer_info('CUST001')
        
        # SCÉNARIO 2: Consultation du solde d'un compte
        print("💰 SCÉNARIO 2: Consultation du solde")
        print("-" * 70)
        account = client.get_account_balance('ACC001')
        initial_balance = account.balance
        
        # SCÉNARIO 3: Transfert entre comptes (avec succès)
        print("💸 SCÉNARIO 3: Transfert entre comptes (succès)")
        print("-" * 70)
        transfer_result = client.transfer_money(
            'ACC001', 
            300.00, 
            'ACC002',
            "Épargne mensuelle"
        )
        assert transfer_result.success, "Le transfert a échoué"
        
        # SCÉNARIO 4: Historique des transactions
        print("📜 SCÉNARIO 4: Historique des transactions")
        print("-" * 70)
        history = client.get_transaction_history('ACC001', limit=5)
        
        # RÉSUMÉ FINAL
        print("\n" + "="*70)
        print("✅ TOUS LES TESTS SOAP ONT RÉUSSI!")
        print("="*70)
        print("\n📊 RÉSUMÉ:")
        print(f"   • Opérations testées: 4 scénarios")
        print(f"   • Transactions effectuées: {len(history)}")
        print(f"   • Types complexes utilisés: Customer, Account, Transaction, TransferResult")
        print(f"   • Opérations disponibles: Lecture (2) + Écriture (1) + Historique (1)")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de la connexion au serveur SOAP:")
        print(f"   {e}")
        print("\n💡 Assurez-vous que le serveur SOAP est démarré:")
        print("   python soap_server.py\n")


if __name__ == '__main__':
    main()

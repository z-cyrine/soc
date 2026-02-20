"""
🎬 DÉMONSTRATION COMPLÈTE DU SERVICE BANCAIRE SOAP
===================================================
Ce script teste toutes les opérations du service bancaire SOAP/WSDL

PRÉREQUIS:
1. Le serveur SOAP doit être démarré: python soap_server.py
2. Attendre que le message "SERVEUR BANCAIRE SOAP - DÉMARRÉ" apparaisse

UTILISATION:
python test_demo.py
"""

from zeep import Client
from zeep.exceptions import Fault
import time


# Configuration
WSDL_URL = 'http://localhost:8000/?wsdl'


def print_section(title):
    """Affiche un séparateur de section"""
    print("\n" + "=" * 70)
    print(f"🔹 {title}")
    print("=" * 70)


def print_success(message):
    """Affiche un message de succès"""
    print(f"✅ {message}")


def print_error(message):
    """Affiche un message d'erreur"""
    print(f"❌ {message}")


def print_info(label, value):
    """Affiche une information"""
    print(f"   • {label}: {value}")


def demo_1_get_customer_info(client):
    """Test 1: Récupération des informations client"""
    print_section("TEST 1: CONSULTATION DES INFORMATIONS CLIENT")
    
    try:
        # Client existant
        customer = client.service.get_customer_info('CUST001')
        print_success("Client CUST001 trouvé")
        print_info("Nom complet", f"{customer.first_name} {customer.last_name}")
        print_info("Email", customer.email)
        print_info("Téléphone", customer.phone)
        print_info("Date d'inscription", customer.registration_date.strftime("%d/%m/%Y"))
        
    except Fault as e:
        print_error(f"Erreur SOAP: {e.message}")
    except Exception as e:
        print_error(f"Erreur: {e}")


def demo_2_get_account_balance(client):
    """Test 2: Consultation du solde"""
    print_section("TEST 2: CONSULTATION DU SOLDE D'UN COMPTE")
    
    try:
        # Compte existant
        account = client.service.get_account_balance('ACC001')
        print_success("Compte ACC001 trouvé")
        print_info("Numéro de compte", account.account_number)
        print_info("Type de compte", account.account_type)
        print_info("Solde disponible", f"{account.balance:.2f} {account.currency}")
        print_info("Statut", account.status)
        print_info("Date de création", account.created_date.strftime("%d/%m/%Y"))
        
    except Fault as e:
        print_error(f"Erreur SOAP: {e.message}")
    except Exception as e:
        print_error(f"Erreur: {e}")


def demo_3_transfer_success(client):
    """Test 3: Transfert réussi"""
    print_section("TEST 3: TRANSFERT D'ARGENT (SUCCÈS)")
    
    try:
        # Vérifier le solde avant
        account_before = client.service.get_account_balance('ACC001')
        print_info("Solde avant transfert", f"{account_before.balance:.2f} EUR")
        
        # Effectuer le transfert
        result = client.service.transfer_money(
            from_account='ACC001',
            amount=300.0,
            to_account='ACC002',
            description='Test de transfert - Démo'
        )
        
        if result.success:
            print_success("Transfert réussi")
            print_info("ID Transaction", result.transaction_id)
            print_info("Montant transféré", "300.00 EUR")
            print_info("De", "ACC001 → ACC002")
            print_info("Nouveau solde", f"{result.new_balance:.2f} EUR")
            print_info("Message", result.message)
        else:
            print_error(f"Transfert échoué: {result.message}")
            
    except Fault as e:
        print_error(f"Erreur SOAP: {e.message}")
    except Exception as e:
        print_error(f"Erreur: {e}")


def demo_4_transfer_insufficient_funds(client):
    """Test 4: Transfert avec solde insuffisant"""
    print_section("TEST 4: TRANSFERT AVEC SOLDE INSUFFISANT (ERREUR MÉTIER)")
    
    try:
        # Tenter un transfert impossible
        result = client.service.transfer_money(
            from_account='ACC001',
            amount=999999.0,
            to_account='ACC002',
            description='Transfert impossible'
        )
        
        if not result.success:
            print_error("Transfert refusé (comportement attendu)")
            print_info("Raison", result.message)
            print_info("Solde actuel", f"{result.new_balance:.2f} EUR")
        else:
            print_success("⚠️  Transfert accepté (ne devrait pas arriver)")
            
    except Fault as e:
        print_error(f"Erreur SOAP: {e.message}")
    except Exception as e:
        print_error(f"Erreur: {e}")


def demo_5_account_not_found(client):
    """Test 5: Compte inexistant"""
    print_section("TEST 5: CONSULTATION D'UN COMPTE INEXISTANT (SOAP FAULT)")
    
    try:
        # Tenter d'accéder à un compte inexistant
        account = client.service.get_account_balance('ACC999')
        print_error("⚠️  Le compte inexistant a été trouvé (ne devrait pas arriver)")
        
    except Fault as e:
        print_error("SOAP Fault déclenché (comportement attendu)")
        print_info("Code d'erreur", e.code)
        print_info("Message", e.message)
    except Exception as e:
        print_error(f"Erreur: {e}")


def demo_6_transaction_history(client):
    """Test 6: Historique des transactions"""
    print_section("TEST 6: HISTORIQUE DES TRANSACTIONS")
    
    try:
        # Récupérer les 5 dernières transactions
        transactions = client.service.get_transaction_history('ACC001', limit=5)
        
        if transactions:
            print_success(f"{len(transactions)} transaction(s) trouvée(s)")
            for i, txn in enumerate(transactions, 1):
                print(f"\n   📝 Transaction #{i}")
                print_info("ID", txn.transaction_id)
                print_info("Type", txn.transaction_type)
                print_info("De → Vers", f"{txn.from_account} → {txn.to_account}")
                print_info("Montant", f"{txn.amount:.2f} {txn.currency}")
                print_info("Statut", txn.status)
                print_info("Date", txn.timestamp.strftime("%d/%m/%Y %H:%M:%S"))
                print_info("Description", txn.description)
        else:
            print_info("Résultat", "Aucune transaction trouvée")
            
    except Fault as e:
        print_error(f"Erreur SOAP: {e.message}")
    except Exception as e:
        print_error(f"Erreur: {e}")


def main():
    """Fonction principale de démonstration"""
    print("\n" + "=" * 70)
    print("🎬 DÉMONSTRATION DU SERVICE BANCAIRE SOAP/WSDL")
    print("=" * 70)
    print("📡 Connexion au serveur SOAP...")
    
    try:
        # Créer le client SOAP
        client = Client(WSDL_URL)
        print_success(f"Connecté au service: {WSDL_URL}")
        print_info("Service", "BankingService")
        print_info("Namespace", "http://banking.soap.example.com")
        
        # Pause pour la lisibilité
        time.sleep(1)
        
        # Exécuter tous les tests
        demo_1_get_customer_info(client)
        time.sleep(0.5)
        
        demo_2_get_account_balance(client)
        time.sleep(0.5)
        
        demo_3_transfer_success(client)
        time.sleep(0.5)
        
        demo_4_transfer_insufficient_funds(client)
        time.sleep(0.5)
        
        demo_5_account_not_found(client)
        time.sleep(0.5)
        
        demo_6_transaction_history(client)
        
        # Résumé final
        print_section("RÉSUMÉ DE LA DÉMONSTRATION")
        print_success("Tous les tests ont été exécutés")
        print_info("Opérations testées", "6/6")
        print_info("Cas de succès", "✓ Consultation client, compte, transfert, historique")
        print_info("Gestion d'erreurs", "✓ Solde insuffisant, compte inexistant")
        
        print("\n" + "=" * 70)
        print("🎉 DÉMONSTRATION TERMINÉE AVEC SUCCÈS")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print_error(f"\n⚠️  Impossible de se connecter au serveur SOAP")
        print_info("Erreur", str(e))
        print("\n💡 VÉRIFICATIONS:")
        print("   1. Le serveur est-il démarré? → python soap_server.py")
        print("   2. Le serveur écoute-t-il sur le port 8000?")
        print("   3. L'URL WSDL est-elle accessible? → http://localhost:8000/?wsdl")
        print()


if __name__ == '__main__':
    main()

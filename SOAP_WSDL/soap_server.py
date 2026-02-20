"""
SOAP/WSDL Server Example - Banking Service
Ce serveur expose un service bancaire complet via SOAP avec un contrat WSDL
Cas d'usage réel: Les services bancaires utilisent massivement SOAP/WSDL
"""

from spyne import Application, rpc, ServiceBase, Integer, Unicode, Float, DateTime, ComplexModel, Array, Boolean
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
from datetime import datetime, timedelta
import uuid


# ===================================================================
# MODÈLES DE DONNÉES
# ===================================================================

class Customer(ComplexModel):
    """Représente un client de la banque"""
    __namespace__ = 'http://banking.soap.example.com'
    
    customer_id = Unicode
    first_name = Unicode
    last_name = Unicode
    email = Unicode
    phone = Unicode
    registration_date = DateTime


class Account(ComplexModel):
    """Représente un compte bancaire"""
    __namespace__ = 'http://banking.soap.example.com'
    
    account_number = Unicode
    customer_id = Unicode
    account_type = Unicode  # CHECKING, SAVINGS, BUSINESS
    balance = Float
    currency = Unicode
    status = Unicode  # ACTIVE, SUSPENDED, CLOSED
    created_date = DateTime


class Transaction(ComplexModel):
    """Représente une transaction bancaire"""
    __namespace__ = 'http://banking.soap.example.com'
    
    transaction_id = Unicode
    from_account = Unicode
    to_account = Unicode
    amount = Float
    currency = Unicode
    transaction_type = Unicode  # TRANSFER, DEPOSIT, WITHDRAWAL
    status = Unicode  # COMPLETED, PENDING, FAILED
    timestamp = DateTime
    description = Unicode


class TransferResult(ComplexModel):
    """Résultat d'un transfert"""
    __namespace__ = 'http://banking.soap.example.com'
    
    success = Boolean
    transaction_id = Unicode
    message = Unicode
    new_balance = Float


# ===================================================================
# BASE DE DONNÉES SIMULÉE (En mémoire)
# ===================================================================

# Clients
CUSTOMERS_DB = {
    'CUST001': Customer(
        customer_id='CUST001',
        first_name='Cyrine',
        last_name='Bennour',
        email='cyrine.bennour@example.com',
        phone='+216 20 123 456',
        registration_date=datetime(2024, 1, 15)
    ),
    'CUST002': Customer(
        customer_id='CUST002',
        first_name='Ahmed',
        last_name='Ben Ali',
        email='ahmed.benali@example.com',
        phone='+216 22 987 654',
        registration_date=datetime(2024, 3, 10)
    )
}

# Comptes bancaires
ACCOUNTS_DB = {
    'ACC001': Account(
        account_number='ACC001',
        customer_id='CUST001',
        account_type='CHECKING',
        balance=5000.00,
        currency='EUR',
        status='ACTIVE',
        created_date=datetime(2024, 1, 15)
    ),
    'ACC002': Account(
        account_number='ACC002',
        customer_id='CUST001',
        account_type='SAVINGS',
        balance=15000.00,
        currency='EUR',
        status='ACTIVE',
        created_date=datetime(2024, 1, 15)
    ),
    'ACC003': Account(
        account_number='ACC003',
        customer_id='CUST002',
        account_type='CHECKING',
        balance=3500.00,
        currency='EUR',
        status='ACTIVE',
        created_date=datetime(2024, 3, 10)
    )
}

# Historique des transactions
TRANSACTIONS_DB = []


# ===================================================================
# SERVICE BANCAIRE SOAP
# ===================================================================

class BankingService(ServiceBase):
    """
    Service SOAP pour les opérations bancaires
    Illustre un cas d'usage réel de SOAP/WSDL dans le secteur financier
    """
    
    @rpc(Unicode, _returns=Customer)
    def get_customer_info(ctx, customer_id):
        """
        Récupère les informations d'un client
        
        Args:
            customer_id: Identifiant unique du client
            
        Returns:
            Informations complètes du client
        """
        if customer_id not in CUSTOMERS_DB:
            raise ValueError(f"Client {customer_id} introuvable")
        
        return CUSTOMERS_DB[customer_id]
    
    @rpc(Unicode, _returns=Account)
    def get_account_balance(ctx, account_number):
        """
        Consulte le solde d'un compte
        
        Args:
            account_number: Numéro de compte
            
        Returns:
            Informations complètes du compte incluant le solde
        """
        if account_number not in ACCOUNTS_DB:
            raise ValueError(f"Compte {account_number} introuvable")
        
        return ACCOUNTS_DB[account_number]
    
    @rpc(Unicode, Float, Unicode, Unicode, _returns=TransferResult)
    def transfer_money(ctx, from_account, amount, to_account, description):
        """
        Effectue un transfert d'argent entre deux comptes
        
        Args:
            from_account: Compte source
            amount: Montant à transférer
            to_account: Compte destinataire
            description: Description du transfert
            
        Returns:
            Résultat du transfert avec le nouveau solde
        """
        # Validation des comptes
        if from_account not in ACCOUNTS_DB:
            return TransferResult(
                success=False,
                transaction_id='',
                message=f"Compte source {from_account} introuvable",
                new_balance=0.0
            )
        
        if to_account not in ACCOUNTS_DB:
            return TransferResult(
                success=False,
                transaction_id='',
                message=f"Compte destinataire {to_account} introuvable",
                new_balance=0.0
            )
        
        # Validation du montant
        if amount <= 0:
            return TransferResult(
                success=False,
                transaction_id='',
                message="Le montant doit être supérieur à zéro",
                new_balance=ACCOUNTS_DB[from_account].balance
            )
        
        # Vérification du solde suffisant
        source_account = ACCOUNTS_DB[from_account]
        if source_account.balance < amount:
            return TransferResult(
                success=False,
                transaction_id='',
                message=f"Solde insuffisant. Solde actuel: {source_account.balance} EUR",
                new_balance=source_account.balance
            )
        
        # Effectuer le transfert
        dest_account = ACCOUNTS_DB[to_account]
        source_account.balance -= amount
        dest_account.balance += amount
        
        # Créer la transaction
        transaction_id = f"TXN{str(uuid.uuid4())[:8].upper()}"
        transaction = Transaction(
            transaction_id=transaction_id,
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            currency='EUR',
            transaction_type='TRANSFER',
            status='COMPLETED',
            timestamp=datetime.now(),
            description=description
        )
        TRANSACTIONS_DB.append(transaction)
        
        return TransferResult(
            success=True,
            transaction_id=transaction_id,
            message=f"Transfert réussi de {amount} EUR",
            new_balance=source_account.balance
        )
    
    @rpc(Unicode, Integer, _returns=Array(Transaction))
    def get_transaction_history(ctx, account_number, limit=10):
        """
        Récupère l'historique des transactions d'un compte
        
        Args:
            account_number: Numéro de compte
            limit: Nombre maximum de transactions à retourner
            
        Returns:
            Liste des dernières transactions
        """
        if account_number not in ACCOUNTS_DB:
            raise ValueError(f"Compte {account_number} introuvable")
        
        # Filtrer les transactions liées au compte
        account_transactions = [
            txn for txn in TRANSACTIONS_DB
            if txn.from_account == account_number or txn.to_account == account_number
        ]
        
        # Trier par date décroissante et limiter
        account_transactions.sort(key=lambda x: x.timestamp, reverse=True)
        return account_transactions[:limit]


def create_application():
    """
    Crée et configure l'application SOAP
    """
    application = Application(
        [BankingService],
        tns='http://banking.soap.example.com',  # Target Namespace
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11()
    )
    
    return application


def main():
    """
    Démarre le serveur SOAP bancaire
    """
    application = create_application()
    wsgi_application = WsgiApplication(application)
    
    # Créer le serveur sur le port 8000
    server = make_server('localhost', 8000, wsgi_application)
    
    print("\n" + "=" * 70)
    print("🏦 SERVEUR BANCAIRE SOAP - DÉMARRÉ")
    print("=" * 70)
    print("🚀 URL du service: http://localhost:8000")
    print("📄 WSDL disponible à: http://localhost:8000/?wsdl")
    print("=" * 70)
    print("\n📊 DONNÉES DISPONIBLES:")
    print("   • 2 Clients (CUST001, CUST002)")
    print("   • 3 Comptes bancaires (ACC001, ACC002, ACC003)")
    print("=" * 70)
    print("\n🔧 OPÉRATIONS SOAP DISPONIBLES (4 opérations essentielles):")
    print("   • get_customer_info(customer_id)")
    print("   • get_account_balance(account_number)")
    print("   • transfer_money(from, amount, to, description)")
    print("   • get_transaction_history(account, limit)")
    print("=" * 70)
    print("\n⚡ Appuyez sur Ctrl+C pour arrêter le serveur\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ Serveur bancaire SOAP arrêté avec succès")
        print(f"📊 Total de transactions effectuées: {len(TRANSACTIONS_DB)}\n")


if __name__ == '__main__':
    main()

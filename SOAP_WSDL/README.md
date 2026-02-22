# 🏦 Service Bancaire SOAP/WSDL

Service bancaire utilisant SOAP avec génération automatique du contrat WSDL.

## Structure du Projet

```
SOAP_WSDL/
├── soap_server.py      # Serveur SOAP (génère le WSDL automatiquement)
├── soap_client.py      # Client SOAP (exemples d'utilisation)
├── test_demo.py        # Tests complets pour la démo 
├── requirements.txt    # Dépendances Python
└── README.md          
```

## Installation

```powershell
# Installer les dépendances
pip install -r requirements.txt
```

## Démonstration

### Étape 1 : Démarrer le serveur

```powershell
python soap_server.py
```

### Étape 2 : Lancer la démo complète

**Dans un nouveau terminal :**

```powershell
python test_demo.py
```

Cette démo exécute automatiquement :
- ✅ Consultation des informations client
- ✅ Consultation du solde d'un compte
- ✅ Transfert d'argent (succès)
- ✅ Gestion d'erreur : solde insuffisant
- ✅ Gestion d'erreur : compte inexistant
- ✅ Historique des transactions

### Utiliser le client interactif

```powershell
python soap_client.py
```

## Données de Test

**Clients disponibles :**
- `CUST001` : Cyrine Zribi
- `CUST002` : Ilef Rjiba
- `CUST003` : Sarra Ragguem

**Comptes disponibles :**
- `ACC001` : Compte courant (5000 EUR)
- `ACC002` : Compte épargne (15000 EUR)
- `ACC003` : Compte courant (3500 EUR)

## Opérations SOAP Disponibles

1. **get_customer_info**(customer_id) → Customer
2. **get_account_balance**(account_number) → Account
3. **transfer_money**(from, amount, to, description) → TransferResult
4. **get_transaction_history**(account, limit) → Transaction[]

## Accéder au WSDL

Une fois le serveur démarré, le WSDL est généré automatiquement :

```
http://localhost:8000/?wsdl
```

## Technologies Utilisées

- **Spyne** : Framework SOAP pour Python (génération WSDL)
- **Zeep** : Client SOAP moderne pour Python
- **WSGI** : Interface serveur web Python

## Configuration

- **Port** : 8000
- **URL** : http://localhost:8000
- **Namespace** : http://banking.soap.example.com

---
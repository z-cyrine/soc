#!/bin/bash
set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Déterminer le répertoire de base
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "======================================================================"
echo "🌐 LANCEMENT DE L'INTERFACE SOC"
echo "======================================================================"
echo "REST · SOAP/WSDL · GraphQL · gRPC"
echo "======================================================================"
echo ""

# Vérifier que les fichiers existent
echo "📋 Vérification des fichiers..."
echo ""

MISSING=0

if [ ! -f "$BASE_DIR/REST/app.py" ]; then
    echo -e "  ${RED}❌${NC} REST: app.py non trouvé"
    MISSING=1
else
    echo -e "  ${GREEN}✅${NC} REST: app.py"
fi

if [ ! -f "$BASE_DIR/graphQL/server.py" ]; then
    echo -e "  ${RED}❌${NC} GraphQL: server.py non trouvé"
    MISSING=1
else
    echo -e "  ${GREEN}✅${NC} GraphQL: server.py"
fi

if [ ! -f "$BASE_DIR/SOAP_WSDL/soap_server.py" ]; then
    echo -e "  ${RED}❌${NC} SOAP: soap_server.py non trouvé"
    MISSING=1
else
    echo -e "  ${GREEN}✅${NC} SOAP: soap_server.py"
fi

if [ ! -f "$BASE_DIR/grpc/server.py" ]; then
    echo -e "  ${RED}❌${NC} gRPC: server.py non trouvé"
    MISSING=1
else
    echo -e "  ${GREEN}✅${NC} gRPC: server.py"
fi

if [ ! -f "$BASE_DIR/demo.html" ]; then
    echo -e "  ${RED}❌${NC} Interface HTML: demo.html non trouvé"
    MISSING=1
else
    echo -e "  ${GREEN}✅${NC} Interface HTML: demo.html"
fi

if [ $MISSING -eq 1 ]; then
    echo ""
    echo "======================================================================"
    echo -e "${RED}❌ ERREURS - Fichiers manquants${NC}"
    echo "======================================================================"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Tous les fichiers sont présents!${NC}"
echo ""

# Installer les dépendances
echo "📦 Installation des dépendances..."
echo ""

for req_dir in "REST" "graphQL" "SOAP_WSDL" "grpc"; do
    if [ -f "$BASE_DIR/$req_dir/requirements.txt" ]; then
        echo -e "  📥 Installation de ${req_dir}/requirements.txt..."
        python3 -m pip install -q -r "$BASE_DIR/$req_dir/requirements.txt" 2>/dev/null || true
        echo -e "     ${GREEN}✅${NC} ${req_dir} - OK"
    fi
done

echo ""
echo -e "${GREEN}✅ Installation terminée!${NC}"
echo ""

# Fonction de nettoyage
cleanup() {
    echo ""
    echo ""
    echo "======================================================================"
    echo "🛑 ARRÊT DES SERVEURS"
    echo "======================================================================"
    echo ""
    
    # Arrêter tous les processus en arrière-plan
    jobs -p | xargs -r kill 2>/dev/null || true
    
    sleep 1
    
    echo -e "${GREEN}✅ Tous les serveurs ont été arrêtés${NC}"
    echo "======================================================================"
    echo ""
    exit 0
}

# Configurer le signal Ctrl+C
trap cleanup INT TERM

# Démarrer les serveurs
echo "🚀 Démarrage des serveurs..."
echo ""

(cd "$BASE_DIR/REST" && python3 app.py > /tmp/rest.log 2>&1) &
echo -e "  ${GREEN}✅${NC} REST API (port 5000) - PID $!"

(cd "$BASE_DIR/graphQL" && python3 server.py > /tmp/graphql.log 2>&1) &
echo -e "  ${GREEN}✅${NC} GraphQL Server (port 5001) - PID $!"

(cd "$BASE_DIR/SOAP_WSDL" && python3 soap_server.py > /tmp/soap.log 2>&1) &
echo -e "  ${GREEN}✅${NC} SOAP Server (port 8000) - PID $!"

(cd "$BASE_DIR/grpc" && python3 server.py > /tmp/grpc.log 2>&1) &
echo -e "  ${GREEN}✅${NC} gRPC Server (port 50051) - PID $!"

echo ""
echo "⏳ Attente du démarrage des serveurs (5 secondes)..."
sleep 5

# Ouvrir l'interface HTML
echo ""
echo "🌐 Ouverture de l'interface..."
echo ""

if command -v xdg-open &> /dev/null; then
    xdg-open "file://$BASE_DIR/demo.html" 2>/dev/null &
elif command -v open &> /dev/null; then
    open "file://$BASE_DIR/demo.html" 2>/dev/null &
elif command -v firefox &> /dev/null; then
    firefox "file://$BASE_DIR/demo.html" 2>/dev/null &
elif command -v google-chrome &> /dev/null; then
    google-chrome "file://$BASE_DIR/demo.html" 2>/dev/null &
else
    echo -e "  ${YELLOW}⚠️ Impossible d'ouvrir le navigateur${NC}"
    echo "  Ouvrez manuellement: file://$BASE_DIR/demo.html"
fi

echo -e "  ${GREEN}✅${NC} Interface ouverte"
echo ""

# Afficher les instructions
echo "======================================================================"
echo "✅ TOUS LES SERVEURS SONT LANCÉS"
echo "======================================================================"
echo ""
echo "Serveurs en cours d'exécution:"
echo "  • REST API           → http://localhost:5000"
echo "  • GraphQL Server     → http://localhost:5001/graphql"
echo "  • SOAP Server        → http://localhost:8000"
echo "  • gRPC Server        → localhost:50051"
echo ""
echo "Interface web:"
echo "  • file://$BASE_DIR/demo.html"
echo ""
echo "======================================================================"
echo "📝 COMMANDES DISPONIBLES:"
echo "======================================================================"
echo "  • Appuyez sur Ctrl+C pour arrêter tous les serveurs"
echo "  • Fermez le navigateur quand vous avez terminé"
echo "======================================================================"
echo ""

# Garder le script actif
wait

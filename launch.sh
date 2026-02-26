#!/bin/bash
set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Déterminer le répertoire de base (chemin relatif à partir du dossier du script)
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

echo ""
echo "======================================================================"
echo "🌐 LANCEMENT DE L'INTERFACE SOC"
echo "======================================================================"
echo "REST · SOAP/WSDL · GraphQL · gRPC"
echo "======================================================================"
echo ""
echo "📍 Répertoire de base: $SCRIPT_DIR"
echo ""

# Vérifier que les fichiers existent
echo "📋 Vérification des fichiers..."
echo ""

MISSING=0

check_file() {
    local file_path="$1"
    local file_name="$2"
    if [ ! -f "$file_path" ]; then
        echo -e "  ${RED}❌${NC} $file_name non trouvé"
        MISSING=1
    else
        echo -e "  ${GREEN}✅${NC} $file_name"
    fi
}

check_file "$SCRIPT_DIR/REST/app.py" "REST: app.py"
check_file "$SCRIPT_DIR/graphQL/server.py" "GraphQL: server.py"
check_file "$SCRIPT_DIR/SOAP_WSDL/soap_server.py" "SOAP: soap_server.py"
check_file "$SCRIPT_DIR/grpc/server.py" "gRPC: server.py"
check_file "$SCRIPT_DIR/demo.html" "Interface HTML: demo.html"

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

install_requirements() {
    local req_dir="$1"
    local req_path="$SCRIPT_DIR/$req_dir/requirements.txt"
    
    if [ -f "$req_path" ]; then
        echo -e "  📥 Installation de $req_dir/requirements.txt..."
        python3 -m pip install -q -r "$req_path" 2>/dev/null || true
        echo -e "     ${GREEN}✅${NC} $req_dir - OK"
    fi
}

install_requirements "REST"
install_requirements "graphQL"
install_requirements "SOAP_WSDL"
install_requirements "grpc"

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

(cd "$SCRIPT_DIR/REST" && python3 app.py > /tmp/rest.log 2>&1) &
echo -e "  ${GREEN}✅${NC} REST API (port 5000) - PID $!"

(cd "$SCRIPT_DIR/graphQL" && python3 server.py > /tmp/graphql.log 2>&1) &
echo -e "  ${GREEN}✅${NC} GraphQL Server (port 5001) - PID $!"

(cd "$SCRIPT_DIR/SOAP_WSDL" && python3 soap_server.py > /tmp/soap.log 2>&1) &
echo -e "  ${GREEN}✅${NC} SOAP Server (port 8000) - PID $!"

(cd "$SCRIPT_DIR/grpc" && python3 server.py > /tmp/grpc.log 2>&1) &
echo -e "  ${GREEN}✅${NC} gRPC Server (port 50051) - PID $!"

echo ""
echo "⏳ Attente du démarrage des serveurs (5 secondes)..."
sleep 5

# Ouvrir l'interface HTML
echo ""
echo "🌐 Ouverture de l'interface..."
echo ""

# Déterminer le navigateur disponible et ouvrir le fichier HTML
open_browser() {
    local html_file="file://$SCRIPT_DIR/demo.html"
    
    if command -v xdg-open &> /dev/null; then
        xdg-open "$html_file" 2>/dev/null &
    elif command -v open &> /dev/null; then
        open "$html_file" 2>/dev/null &
    elif command -v firefox &> /dev/null; then
        firefox "$html_file" 2>/dev/null &
    elif command -v google-chrome &> /dev/null; then
        google-chrome "$html_file" 2>/dev/null &
    elif command -v chromium &> /dev/null; then
        chromium "$html_file" 2>/dev/null &
    else
        echo -e "  ${YELLOW}⚠️ Impossible d'ouvrir le navigateur automatiquement${NC}"
        echo "  Ouvrez manuellement le fichier: $html_file"
        return 1
    fi
    return 0
}

if open_browser; then
    echo -e "  ${GREEN}✅${NC} Interface ouverte"
fi

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
echo "  • file://$SCRIPT_DIR/demo.html"
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

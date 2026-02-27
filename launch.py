#!/usr/bin/env python3
"""
Lanceur universel pour l'interface SOC
Compatible avec Windows, macOS et Linux
"""

import os
import sys
import subprocess
import signal
import time
import webbrowser
import shutil
from pathlib import Path

# Couleurs ANSI
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

# Déterminer le répertoire de base (où se trouve ce script)
SCRIPT_DIR = Path(__file__).resolve().parent
PROCESSES = []

def print_header(text):
    """Afficher un titre"""
    print(f"\n{'='*70}")
    print(text)
    print('='*70)
    print()

def print_success(text):
    """Afficher un message de succès"""
    print(f"{Colors.GREEN}[OK]{Colors.NC} {text}")

def print_error(text):
    """Afficher un message d'erreur"""
    print(f"{Colors.RED}[ERREUR]{Colors.NC} {text}")

def print_info(text):
    """Afficher un message d'information"""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {text}")

def print_warning(text):
    """Afficher un avertissement"""
    print(f"{Colors.YELLOW}[ATTENTION]{Colors.NC} {text}")

def check_files():
    """Vérifier que tous les fichiers nécessaires existent"""
    print_header("LANCEMENT DE L'INTERFACE SOC")
    print("REST · SOAP/WSDL · GraphQL · gRPC")
    print()
    print_info(f"Répertoire de base: {SCRIPT_DIR}")
    print()
    
    print("Vérification des fichiers...")
    print()
    
    files_to_check = [
        ("REST/app.py", "REST: app.py"),
        ("graphQL/server.py", "GraphQL: server.py"),
        ("SOAP_WSDL/soap_server.py", "SOAP: soap_server.py"),
        ("grpc/server.py", "gRPC: server.py"),
        ("demo.html", "Interface HTML: demo.html"),
    ]
    
    missing = False
    for file_path, file_name in files_to_check:
        full_path = SCRIPT_DIR / file_path
        if not full_path.exists():
            print_error(f"{file_name} non trouvé")
            missing = True
        else:
            print_success(file_name)
    
    if missing:
        print()
        print_header(f"{Colors.RED}ERREURS - Fichiers manquants{Colors.NC}")
        sys.exit(1)
    
    print()
    print_success("Tous les fichiers sont présents!")
    print()

def install_requirements():
    """Installer les dépendances de tous les modules"""
    print("Installation des dépendances...")
    print()
    
    modules = ["REST", "graphQL", "SOAP_WSDL", "grpc"]
    
    for module in modules:
        req_path = SCRIPT_DIR / module / "requirements.txt"
        
        if req_path.exists():
            print(f"  Installation de {module}/requirements.txt...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-q", "-r", str(req_path)],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print_success(f"{module} - OK")
            except Exception as e:
                print_warning(f"{module} - Erreur: {e}")
    
    print()
    print_success("Installation terminée!")
    print()

def start_server(name, module, script, port):
    """Démarrer un serveur Python"""
    server_dir = SCRIPT_DIR / module
    log_file = f"/tmp/{name.lower()}.log"
    
    try:
        proc = subprocess.Popen(
            [sys.executable, script],
            cwd=str(server_dir),
            stdout=open(log_file, 'w'),
            stderr=subprocess.STDOUT
        )
        PROCESSES.append(proc)
        print_success(f"{name} (port {port}) - PID {proc.pid}")
        return proc
    except Exception as e:
        print_error(f"{name} - Erreur de démarrage: {e}")
        return None

def start_servers():
    """Démarrer tous les serveurs"""
    print_header("Démarrage des serveurs...")
    
    start_server("REST API", "REST", "app.py", "5000")
    start_server("GraphQL Server", "graphQL", "server.py", "5001")
    start_server("SOAP Server", "SOAP_WSDL", "soap_server.py", "8000")
    start_server("gRPC Server", "grpc", "server.py", "50051")
    
    print()
    print("Attente du démarrage des serveurs (5 secondes)...")
    time.sleep(5)
    print()

def open_browser():
    """Ouvrir le navigateur avec le fichier HTML"""
    print("Ouverture de l'interface...")
    print()
    
    html_file = SCRIPT_DIR / "demo.html"
    html_url = f"file://{html_file}"
    
    try:
        webbrowser.open(html_url)
        print_success("Interface ouverte")
    except Exception as e:
        print_warning(f"Impossible d'ouvrir le navigateur automatiquement")
        print(f"  Ouvrez manuellement le fichier: {html_url}")
    
    print()

def show_instructions():
    """Afficher les instructions finales"""
    print_header("TOUS LES SERVEURS SONT LANCES")
    
    print("Serveurs en cours d'exécution:")
    print("  • REST API           → http://localhost:5000")
    print("  • GraphQL Server     → http://localhost:5001/graphql")
    print("  • SOAP Server        → http://localhost:8000")
    print("  • gRPC Server        → localhost:50051")
    print()
    print("Interface web:")
    print(f"  • file://{SCRIPT_DIR / 'demo.html'}")
    print()
    
    print_header("COMMANDES DISPONIBLES")
    print("  • Appuyez sur Ctrl+C pour arrêter tous les serveurs")
    print("  • Fermez le navigateur quand vous avez terminé")
    print()

def cleanup(signum=None, frame=None):
    """Arrêter tous les serveurs"""
    print()
    print()
    print_header("ARRET DES SERVEURS")
    
    for proc in PROCESSES:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except:
            try:
                proc.kill()
            except:
                pass
    
    time.sleep(1)
    print_success("Tous les serveurs ont été arrêtés")
    print("="*70)
    print()
    sys.exit(0)

def main():
    """Fonction principale"""
    # Configurer les signaux pour le nettoyage
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    try:
        # Vérifier les fichiers
        check_files()
        
        # Installer les dépendances
        install_requirements()
        
        # Démarrer les serveurs
        start_servers()
        
        # Ouvrir le navigateur
        open_browser()
        
        # Afficher les instructions
        show_instructions()
        
        # Garder le script actif
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        print_error(f"Erreur: {e}")
        cleanup()

if __name__ == "__main__":
    main()

# Étude Pratique gRPC : Système de Télémétrie par Capteur

 1. Installation des dépendances (le framework gRPC et les outils de compilation pour Python )

```bash
pip install grpcio grpcio-tools
```
2. Compilation du contrat (.proto)
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. sensor.proto
```
Note : Cette commande crée les fichiers sensor_pb2.py et sensor_pb2_grpc.py.

3. Exécution de la démonstration
Ouvrez deux terminaux :

Démarrer le Serveur :

```bash
python server.py
```
Exécuter le Client :

```bash
python client.py
```
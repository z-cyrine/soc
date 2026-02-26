"""
Pont HTTP → gRPC
Expose le service gRPC via HTTP pour permettre l'appel depuis le navigateur.
Port : 8083
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request
from flask_cors import CORS
import grpc
import sensor_pb2
import sensor_pb2_grpc
from datetime import datetime

app = Flask(__name__)
CORS(app)

GRPC_HOST = 'localhost:50051'

@app.route('/grpc/temperature', methods=['GET'])
def get_temperature():
    sensor_id = request.args.get('sensor_id', 'SN-001')
    try:
        with grpc.insecure_channel(GRPC_HOST) as channel:
            stub = sensor_pb2_grpc.SensorStub(channel)
            response = stub.GetTemperature(
                sensor_pb2.SensorRequest(sensor_id=sensor_id)
            )
        return jsonify({
            "success": True,
            "request": {
                "sensor_id": sensor_id,
                "method": "GetTemperature",
                "channel": GRPC_HOST,
                "protocol": "gRPC / HTTP2 + Protobuf"
            },
            "response": {
                "temperature": response.temperature,
                "unit": response.unit
            },
            "message": f"Réponse du serveur : {response.temperature} {response.unit}",
            "timestamp": datetime.now().isoformat()
        })
    except grpc.RpcError as e:
        return jsonify({
            "success": False,
            "error": str(e.code()),
            "details": e.details(),
            "hint": "Assurez-vous que le serveur gRPC tourne : python grpc/server.py"
        }), 503
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/grpc/status', methods=['GET'])
def status():
    try:
        with grpc.insecure_channel(GRPC_HOST) as channel:
            grpc.channel_ready_future(channel).result(timeout=2)
        return jsonify({"online": True, "host": GRPC_HOST})
    except:
        return jsonify({"online": False, "host": GRPC_HOST}), 503

if __name__ == '__main__':
    print("=" * 55)
    print("  Pont HTTP → gRPC — port 8083")
    print(f"  Connecté au serveur gRPC : {GRPC_HOST}")
    print("  GET /grpc/temperature?sensor_id=SN-001")
    print("=" * 55)
    app.run(port=8083, debug=False)

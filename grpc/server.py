import grpc
from concurrent import futures
import sensor_pb2
import sensor_pb2_grpc

class SensorServicer(sensor_pb2_grpc.SensorServicer):
    def GetTemperature(self, request, context):
        print(f"Requête reçue pour le capteur : {request.sensor_id}")
        # Simulation d'une lecture de capteur
        return sensor_pb2.SensorResponse(temperature=22.5, unit="Celsius")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sensor_pb2_grpc.add_SensorServicer_to_server(SensorServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Serveur gRPC lancé sur le port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
import grpc
import sensor_pb2
import sensor_pb2_grpc

def run():

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = sensor_pb2_grpc.SensorStub(channel)   
        response = stub.GetTemperature(sensor_pb2.SensorRequest(sensor_id="SN-001"))
        
    print(f"Réponse du serveur : {response.temperature} {response.unit}")

if __name__ == '__main__':
    run()
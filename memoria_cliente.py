import logging
import sys
import grpc
import memoria_pb2
import memoria_pb2_grpc
from concurrent import futures
from google.protobuf.wrappers_pb2 import BoolValue
from threading import Thread

class MemoriaCliente(memoria_pb2_grpc.MemoriaClienteServicer):
    def iniciar(self, request, context):
        logging.debug(f"Jogo iniciado com {request.numCartas} cartas.")
        print(request.numCartas)
        # Adicione a lógica necessária aqui para lidar com o início do jogo
        return BoolValue(value=True)

def serve_cliente():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    memoria_pb2_grpc.add_MemoriaClienteServicer_to_server(MemoriaCliente(), server)
    server.add_insecure_port('localhost:8080')
    server.start()
    logging.debug("Cliente aguardando requisições do servidor...")
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s -> %(message)s', stream=sys.stdout, level=logging.DEBUG)

    # Iniciar o servidor do cliente em um thread separado
    cliente_thread = Thread(target=serve_cliente)
    cliente_thread.start()

    # Conectar ao servidor
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = memoria_pb2_grpc.MemoriaServidorStub(channel)
        
        jogador = memoria_pb2.Jogador(
            id=1,
            nome='Jogador 1',
            pontuacao=0,
            endereco='localhost:8080'
        )
        
        resposta = stub.conectar(jogador)
        if resposta:
            print("resposta")
        logging.debug(f'Resposta: {resposta.value}')

    # Esperar o cliente terminar
    cliente_thread.join()

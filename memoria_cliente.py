import logging
import sys
import grpc
import memoria_pb2
import memoria_pb2_grpc
from concurrent import futures
from threading import Thread
from  MemoriaCliente import MemoriaCliente

id = 1
nome = 'Jogador 1'
endereco = 'localhost:8080'
enderecoServidor = 'localhost:50051'

def serve_cliente(memoriaCliente):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    memoria_pb2_grpc.add_MemoriaClienteServicer_to_server(memoriaCliente, server)
    server.add_insecure_port(endereco)
    server.start()
    logging.debug("Cliente aguardando requisições do servidor...")
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s -> %(message)s', stream=sys.stdout, level=logging.DEBUG)
    memoriaCliente = MemoriaCliente(id, nome, endereco)
    # Iniciar o servidor do cliente em um thread separado
    cliente_thread = Thread(target=serve_cliente, args=(memoriaCliente,))
    cliente_thread.start()

    # Conectar ao servidor
    channel =  grpc.insecure_channel(enderecoServidor)
    stub = memoria_pb2_grpc.MemoriaServidorStub(channel)
    jogador = memoria_pb2.Jogador(
        id=id,
        nome=nome,
        pontuacao=0,
        endereco=endereco
    )
    
    memoriaCliente.setStub(stub)
    resposta = stub.conectar(jogador)
    if resposta:
        logging.debug(f'Resposta: {resposta.value}')

    # Esperar o cliente terminar
    cliente_thread.join()

    channel.close()
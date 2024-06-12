import logging
import sys
from threading import Thread
import grpc
from concurrent import futures
from MemoriaServidor import MemoriaServidor
import memoria_pb2_grpc
# Supondo que as classes MemoriaServidor e memoria_pb2_grpc foram definidas corretamente em outro lugar.

# valoresCartas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M' ,'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M' ,'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y'] 

valoresCartas = ['A', 'B', 'C', 'A', 'B', 'C']   
numCartas = 3
numJogadores = 3

def verificarNumeroJogadores(memoriaServidor):
    while True:

        if int(memoriaServidor.getNumJogadoresAtual()) == numJogadores and int(memoriaServidor.getStatusJogo()) == 1:
            memoriaServidor.iniciarJogo()

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s -> %(message)s', stream=sys.stdout, level=logging.DEBUG)
    
    memoriaServidor = MemoriaServidor(valoresCartas, numCartas, numJogadores)
    
    # Iniciar a thread para verificar o número de jogadores
    server_thread = Thread(target=verificarNumeroJogadores, args=(memoriaServidor,))
    server_thread.start()
    
    # Configurar o servidor gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    memoria_pb2_grpc.add_MemoriaServidorServicer_to_server(memoriaServidor, server)
    print('Servidor de Memória iniciado na porta 50051...')
    server.add_insecure_port('[::]:50051')
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Servidor encerrado pelo usuário.")
    
    server_thread.join()

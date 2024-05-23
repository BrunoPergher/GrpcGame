import logging
import sys
from concurrent import futures
import grpc
import memoria_pb2_grpc
from MemoriaServidor import MemoriaServidor

numCartas = 25
valoresCartas = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y"]
cartas = []
numJogadores = 1
        
if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s -> %(message)s', stream=sys.stdout, level=logging.DEBUG)
    
    memoriaServidor = MemoriaServidor(valoresCartas, numCartas, numJogadores)
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    memoria_pb2_grpc.add_MemoriaServidorServicer_to_server(memoriaServidor, server)
    
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
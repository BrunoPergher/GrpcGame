import logging
import sys
from concurrent import futures
import grpc
import memoria_pb2
import memoria_pb2_grpc
import random
from google.protobuf.wrappers_pb2 import BoolValue

numCartas = 25
valoresCartas = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y"]

class Memoria(memoria_pb2_grpc.MemoriaServidorServicer):
    
    def __init__(self):
  #     self.jogadores = []
        self.jogo = memoria_pb2.Jogo(
            numCartas=numCartas,
            numCartasRestantes=numCartas*2,
            cartas=[],
            tamanhoLinhas=10,
            jogadorAtual=0,
            jogadores=[]
        )
    
    def conectar(self, request, context):
        jogador_existente = next((j for j in self.jogo.jogadores if j.id == request.id), None)
        
        if jogador_existente:
            logging.debug(f"Jogador {request.nome} (ID: {request.id}) já está conectado.")
            return BoolValue(value=False)
        
      #  self.jogadores.append(request)
        self.jogo.jogadores.append(request)
        
        logging.debug(f"Jogador {request.nome} (ID: {request.id}) conectado com sucesso.")
        
        if len(self.jogo.jogadores) == 1:
            self.criarJogo()
            
        return BoolValue(value=True)
    
    def criarJogo(self):
        i=0
        random.shuffle(valoresCartas)
        while i < 2:
            self.jogo.cartas.append(memoria_pb2.Carta(
                id=i+1,
                valor = valoresCartas[i],
                ativo = False))
            i+=1
                    
        # Converte de volta para a lista de Protobuf
        self.informarInicioJogo()

    def informarInicioJogo(self):
        for jogador in self.jogo.jogadores:
            with grpc.insecure_channel(jogador.endereco) as channel:
                cliente_stub = memoria_pb2_grpc.MemoriaClienteStub(channel)
                response = cliente_stub.iniciar(self.jogo)
                logging.debug(f"Resposta do cliente ao iniciar o jogo: {response.value}")

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s -> %(message)s', stream=sys.stdout, level=logging.DEBUG)
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    memoria_pb2_grpc.add_MemoriaServidorServicer_to_server(Memoria(), server)
    
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
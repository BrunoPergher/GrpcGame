import logging
import grpc
import memoria_pb2
import memoria_pb2_grpc
import random
from google.protobuf.wrappers_pb2 import BoolValue

class MemoriaServidor(memoria_pb2_grpc.MemoriaServidorServicer):
    
    def __init__(self, valoresCartas, numCartas, numJogadores):
        self.numCartas = numCartas
        self.valoresCartas = valoresCartas
        self.jogo = memoria_pb2.Jogo(
            numCartas=numCartas,
            numCartasRestantes=numCartas*2,
            cartas=[],
            tamanhoLinhas=10,
            jogadorAtual=0,
            jogadores=[]
        )
        self.numJogadores = numJogadores
    
    #cliente se conecta ao servidor passando o objeto com os dados do jogador
    def conectar(self, request, context):
        jogadorExistente = next((j for j in self.jogo.jogadores if j.id == request.id), None)
        
        if jogadorExistente:
            logging.debug(f"Jogador {request.nome} (ID: {request.id}) já está conectado.")
            return BoolValue(value=False)
        
      #  self.jogadores.append(request)
        self.jogo.jogadores.append(request)
        
        logging.debug(f"Jogador {request.nome} (ID: {request.id}) conectado com sucesso.")
        
        if len(self.jogo.jogadores) == self.numJogadores:
            self.criarJogo()
            
        return BoolValue(value=True)
    
    #cria o jogo com as cartas embaralhadas
    def criarJogo(self):
        i=0
        random.shuffle(self.valoresCartas) #embaralha
        while i < self.numCartas*2:
            self.jogo.cartas.append(memoria_pb2.Carta( #cria as cartas
                id=i+1,
                valor = self.valoresCartas[i],
                ativo = False,
                selecionada = False))
            i+=1
        self.jogo.jogadorAtual = self.jogo.jogadores[0].id         #define o primeiro jogador
        # Converte de volta para a lista de Protobuf
        self.informarInicioJogoJogadores()

    # passa as informações do jogo para o cliente
    def informarInicioJogoJogadores(self):
        for jogador in self.jogo.jogadores:
            self.informarInicioJogo(jogador)
            
    def informarInicioJogo(self, jogador):
        with grpc.insecure_channel(jogador.endereco) as channel: #cria o stub dos clientes
            cliente_stub = memoria_pb2_grpc.MemoriaClienteStub(channel)
            response = cliente_stub.iniciar(self.jogo)  #inicia o joga e informa os clientes
            logging.debug(f"Resposta do cliente ao iniciar o jogo: {response.value}")
                
    #o cliente informa a jogada que deseja fazer para o servidor, que informa os clientes o resultado da jogada       
    def jogada(self, jogada, context):
        carta1 = self.jogo.cartas[jogada.carta1] # obtém as cartas
        carta2 = self.jogo.cartas[jogada.carta2]
        
        if (carta1.valor == carta2.valor) and (carta1.ativo is False) and (carta2.ativo is False):
            for jogador in self.jogo.jogadores: #aumenta a pontuação do jogador que acertou
                jogador.pontuacao += 1
            self.jogo.cartas[jogada.carta1].ativo = True #marca as cartas como ativas
            self.jogo.cartas[jogada.carta2].ativo = True
            self.jogo.numCartasRestantes -= 2
        
        self.jogo.cartas[jogada.carta1].selecionada = True #marca as cartas como selecionadas
        self.jogo.cartas[jogada.carta2].selecionada = True
        
        #define o próximo jogador
        if(self.jogo.jogadorAtual == self.jogo.jogadores[-1].id):
            self.jogo.jogadorAtual = self.jogo.jogadores[0].id
        else:
            self.jogo.jogadorAtual = self.jogo.jogadores[self.jogo.jogadores.index(jogador)+1].id
        print(self.jogo.jogadorAtual)   
        
        self.jogo.cartas[jogada.carta1].selecionada = False
        self.jogo.cartas[jogada.carta2].selecionada = False #desmarca as cartas selecionadas
         
        return BoolValue(value=True)

    def informarJogada(self, request, context):
        for jogador in self.jogo.jogadores:
            with grpc.insecure_channel(jogador.endereco) as channel:
                cliente_stub = memoria_pb2_grpc.MemoriaClienteStub(channel)
                response = cliente_stub.informarJogada(self.jogo)
                logging.debug(f"Resposta do cliente ao receber a jogada: {response.value}")
        return BoolValue(value=True)
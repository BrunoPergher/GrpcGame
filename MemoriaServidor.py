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
            jogadores=[],
            idJogadorAtual=0,
            idUltimoJogador=0
        )
        
        self.numJogadores = numJogadores
        self.jogadoresChannel = []
        self.jogadoresStub = []
        self.statusJogo = 0 # 0 aguardando jogadores, 1 em andamento, 2 finalizado
        
    def getNumJogadoresAtual(self):
        return len(self.jogo.jogadores)
    
    def getStatusJogo(self):
        return self.statusJogo
    
    #cliente se conecta ao servidor passando o objeto com os dados do jogador
    def conectar(self, request, context):
        jogadorExistente = next((j for j in self.jogo.jogadores if j.id == request.id), None)
        
        if jogadorExistente:
            logging.debug(f"Jogador {request.nome} (ID: {request.id}) já está conectado.")
            return BoolValue(value=False)
        
        if len(self.jogo.jogadores) == 0:
            self.criarJogo()
            
      #  self.jogadores.append(request)
        self.jogo.jogadores.append(request)
        
        #salva o stub e o channel do cliente
        stub, channel = self.criarStub(request.endereco)
        self.jogadoresChannel.append(channel)
        self.jogadoresStub.append(stub)
        
        logging.debug(f"Jogador {request.nome} (ID: {request.id}) conectado com sucesso.")
        
        if len(self.jogo.jogadores) == self.numJogadores:
            self.jogo.idJogadorAtual = self.jogo.jogadores[0].id         #define o primeiro jogador
            self.statusJogo = 1
        
        return BoolValue(value=True)
    
    def iniciarJogo(self):
        while (len(self.jogo.jogadores) >= 1 and self.jogo.numCartasRestantes > 0):
            self.informarVezJogador()    
        
    def informarVezJogador(self): #chamar no cliente
        for jogador, stub in zip(self.jogo.jogadores, self.jogadoresStub):
            if jogador.id == self.jogo.idJogadorAtual:
                jogada = stub.informarJogador(self.jogo)
                resultado = self.verificarJogada(jogada)
                if resultado == 0:
                    print("Jogada válida")
                    #informarJogadaCliente()
                                                
        #else: encerrarJogo
        
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
                    
    #o cliente informa a jogada que deseja fazer para o servidor, que informa os clientes o resultado da jogada       
    def verificarJogada(self, jogada):
        if self.jogo.idJogadorAtual == jogada.idJogador:
            
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
            
            self.definirProximoJogador()
            
            self.jogo.cartas[jogada.carta1].selecionada = False
            self.jogo.cartas[jogada.carta2].selecionada = False #desmarca as cartas selecionadas
            
            return 0
        
        return -1
    
    def definirProximoJogador(self):
        if(self.jogo.idJogadorAtual == self.jogo.jogadores[-1].id):
            self.jogo.idUltimoJogador = self.jogo.idJogadorAtual
            self.jogo.idJogadorAtual = self.jogo.jogadores[0].id
        else:
            self.jogo.idUltimoJogador = self.jogo.idJogadorAtual
            self.jogo.idJogadorAtual = self.jogo.jogadores[self.jogo.jogadores.index(jogador)+1].id
            
    def criarStub(self, endereco):
        channel = grpc.insecure_channel(endereco)
        stub = memoria_pb2_grpc.MemoriaClienteStub(channel)
        return stub, channel
    
    def encerrar(self):
        for channel in self.jogadoresChannel:
            self.encerrarChannel(channel)

    def encerrarChannel(channel):
        channel.close()
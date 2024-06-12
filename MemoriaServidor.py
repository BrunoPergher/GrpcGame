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
            jogadores=[],
            idJogadorAtual=0,
            idUltimoJogador=0
        )
        self.numCartasTotal = numCartas
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
        self.criarJogo()
        while (len(self.jogo.jogadores) > 1 and self.jogo.numCartasRestantes > 0):
            self.informarVezJogador()
        self.encerrarJogo()
        self.resetarJogo()
        
    def informarVezJogador(self): #chamar no cliente
        for jogador, stub in zip(self.jogo.jogadores, self.jogadoresStub):
            if jogador.id == self.jogo.idJogadorAtual:
                jogada = stub.informarJogador(self.jogo)
                carta1, carta2 = self.verificarJogada(jogada, jogador)
                
                if (carta1 is not None) and (carta2 is not None):
                    self.informarJogadaCliente()
                    self.jogo.cartas[jogada.carta1].selecionada = False
                    self.jogo.cartas[jogada.carta2].selecionada = False #desmarca as cartas selecionadas    
                if self.jogo.numCartasRestantes == 0:
                    break
                
    def informarJogadaCliente(self):
        for stub, jogador in zip(self.jogadoresStub, self.jogo.jogadores):
            response = stub.receberJogada(self.jogo)
            if response.value is False:
                logging.error(f"Erro ao informar jogada para o jogador {jogador.nome} (ID: {jogador.id})")
            else:
                logging.debug(f"Jogada informada para o jogador {jogador.nome} (ID: {jogador.id})")

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
    def verificarJogada(self, jogada, jogador):
        jogadores = list(self.jogo.jogadores)
        if self.jogo.idJogadorAtual == jogada.idJogador:
            if (jogada.carta1 >=0) and (jogada.carta1 <= (self.jogo.numCartas*2)-1) and (jogada.carta2 >=0) and (jogada.carta2 <= 49) and (jogada.carta1 != jogada.carta2):
                carta1 = self.jogo.cartas[jogada.carta1] # obtém as cartas
                carta2 = self.jogo.cartas[jogada.carta2]
                
                if (carta1.valor == carta2.valor) and (carta1.ativo is False) and (carta2.ativo is False):
                    self.jogo.jogadores[jogadores.index(jogador)].pontuacao += 1
                        
                    self.jogo.cartas[jogada.carta1].ativo = True #marca as cartas como ativas
                    self.jogo.cartas[jogada.carta2].ativo = True
                    
                    self.jogo.cartas[jogada.carta1].valor = self.sublinhar(self.jogo.cartas[jogada.carta1].valor)
                    self.jogo.cartas[jogada.carta2].valor = self.sublinhar(self.jogo.cartas[jogada.carta2].valor)
                    self.jogo.numCartasRestantes -= 2
                
                self.jogo.cartas[jogada.carta1].selecionada = True #marca as cartas como selecionadas
                self.jogo.cartas[jogada.carta2].selecionada = True
                
                self.definirProximoJogador(jogador)
                return carta1, carta2
            
        self.definirProximoJogador(jogador)
        return None, None
           
    def sublinhar(self,letra):
        return f'\033[4m{letra}\033[0m'
 
    def definirProximoJogador(self, jogador):
        jogadores = list(self.jogo.jogadores)
        if(jogador.id == self.jogo.jogadores[-1].id):
            self.jogo.idUltimoJogador = self.jogo.idJogadorAtual
            self.jogo.idJogadorAtual = self.jogo.jogadores[0].id
        else:
            self.jogo.idUltimoJogador = self.jogo.idJogadorAtual
            self.jogo.idJogadorAtual = jogadores[jogadores.index(jogador)+1].id
            
    def criarStub(self, endereco):
        channel = grpc.insecure_channel(endereco)
        stub = memoria_pb2_grpc.MemoriaClienteStub(channel)
        return stub, channel
    
    def encerrarJogo(self):
        self.statusJogo = 2
        for stub in self.jogadoresStub:
            stub.informarFimJogo(self.jogo)
        self.encerrar()
    
    def resetarJogo(self):
        self.jogo.numCartasRestantes = self.numCartasTotal*2
        self.jogo.idUltimoJogador = 0
        self.jogo.idJogadorAtual = 0
        self.jogadoresChannel.clear()
        self.jogadoresStub.clear()
        self.statusJogo = 0
        
        while len(self.jogo.cartas) > 0:
            self.jogo.cartas.pop()
        
        while len(self.jogo.jogadores) > 0:
            self.jogo.jogadores.pop()
        
    def encerrar(self):
        for channel in self.jogadoresChannel:
            self.encerrarChannel(channel)

    def encerrarChannel(self, channel):
        channel.close()
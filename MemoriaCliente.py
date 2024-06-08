import logging
import memoria_pb2
import memoria_pb2_grpc
from google.protobuf.wrappers_pb2 import BoolValue

class MemoriaCliente(memoria_pb2_grpc.MemoriaClienteServicer):
    
    def __init__(self, id, nome, enderecoCliente):
         self.stub = None
         self.nome = nome
         self.id = id
         self.enderecoCliente = enderecoCliente
         
    def setStub(self, stub):
        self.stub = stub
        
    ## imprime os dados do jogo e pergunta as cartas que o jogador quer escolher, se for sua vez
    def imprimirJogo(self, jogo):
        cartas = list(jogo.cartas)
        print("\n - Indices das Cartas: ")
        for carta in cartas:
            print(f" {cartas.index(carta)}", end=" ")
        print("\n")
        
        print(" - Cartas Escolhidas: ")
        
        for carta in cartas:
            if carta.ativo and carta.selecionada is False:
                print(" " + carta.valor + " ", end=" ")
            elif carta.selecionada:
                print(" " + carta.valor + " ", end=" ")
                jogo.cartas[cartas.index(carta)].selecionada = False
            else :
                print(f" {cartas.index(carta)}", end=" ")
        print("\n")

    ## pergunta quais as cartas escolhidas pelo jogador
    def perguntarCartas(self):
        print("\nSua vez de jogar. Escolha duas cartas para virar: ")
        try:
            carta1 = int(input(" - Primeira carta: "))
            carta2 = int(input(" - Segunda carta: "))
        except:
            return self.perguntarCartas()
            
        jogada = memoria_pb2.Jogada(
            carta1=carta1,
            carta2=carta2,
            idJogador=self.id
        )
        
        return jogada
    
    def imprimirPlacar(self, jogo):
        print("Placar:")
        for jogador in jogo.jogadores:
            print(f"{jogador.id} - {jogador.nome}: {jogador.pontuacao}") 
    
    def receberJogada(self, jogo, context):
        try:
            if jogo.idUltimoJogador == self.id:
                print("\nSua jogada: ")
                
            else:
                print(f"\nJogada do jogador {jogo.idUltimoJogador}:")
                
            self.imprimirJogo(jogo)
            self.imprimirPlacar(jogo)            
            return BoolValue(value=True)
        
        except Exception as e:
            logging.error(f"Erro ao receber jogada: {e}")
            return BoolValue(value=False)
        
    def informarJogador(self, jogo, context):
        self.imprimirJogo(jogo)
        self.imprimirPlacar(jogo)
        return self.perguntarCartas()
    
    def informarFimJogo(self, jogo, context):
        print("\nFim de jogo! \nPlacar final:")
        self.imprimirPlacar(jogo)
        return BoolValue(value=True)     
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

    ##funcao chamada pelo servidor que inicia o jogo, passando todas as informacoes do jogo
    ## self - stub
    ## jogo - objeto do tipo Jogo
    def iniciar(self, jogo, context):
        logging.debug(f"Jogo iniciado com {jogo.numCartas} cartas.")
        print(jogo.numCartas)
        self.imprimirJogo(jogo)
        return BoolValue(value=True)
    
    ## imprime os dados do jogo e pergunta as cartas que o jogador quer escolher, se for sua vez
    def imprimirJogo(self, jogo):
        cartas = list(jogo.cartas)
        i = 0

        for carta in cartas:
            if i > 0 and i % 5 == 0:
                print("\n")
            if carta.ativo:
                print(" " + carta.valor + " ", end=" ")
            elif carta.selecionada:
                print(" " + carta.valor + " ", end=" ")
                carta.selecionada = False
            else:
                print(i, end=" ")

            i += 1
            
        print("\n")

        if jogo.jogadorAtual == self.id:
            self.perguntarCartas()
    
    ## pergunta quais as cartas escolhidas pelo jogador
    def perguntarCartas(self):
        print("Escolha duas cartas para virar: ")
        carta1 = int(input("Primeira carta: "))
        carta2 = int(input("Segunda carta: "))

        jogada = memoria_pb2.Jogada(
            carta1=carta1,
            carta2=carta2,
            idJogador=self.id
        )
        
        response = self.stub.jogada(jogada)
        print(f"Informativo da jogada: {response.value}")
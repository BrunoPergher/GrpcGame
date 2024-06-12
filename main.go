package main

import (
	"bufio"
	"context"
	"fmt"
	"log"
	"net"
	"os"
	"strconv"
	"strings"
	"time"

	pb "grpcgame/pb"

	"google.golang.org/grpc"
	"google.golang.org/protobuf/types/known/wrapperspb"
)

const (
	serverAddr      = "localhost:50051"
	localClientAddr = "localhost:8083"
)

type memoriaCliente struct {
	pb.UnimplementedMemoriaClienteServer
	id             int32
	nome           string
	endereco       string
	client         pb.MemoriaServidorClient
	lastGame       *pb.Jogo
	cartasVisiveis map[int]string // Mapa para manter o estado visível das cartas
}

func newMemoriaCliente(id int32, nome, endereco string, client pb.MemoriaServidorClient) *memoriaCliente {
	return &memoriaCliente{
		id:             id,
		nome:           nome,
		endereco:       endereco,
		client:         client,
		cartasVisiveis: make(map[int]string),
	}
}

func (c *memoriaCliente) Conectar() error {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second*10)
	defer cancel()

	jogador := &pb.Jogador{
		Id:       c.id,
		Nome:     c.nome,
		Endereco: c.endereco,
	}

	_, err := c.client.Conectar(ctx, jogador)
	if err != nil {
		return fmt.Errorf("falha ao conectar: %v", err)
	}
	fmt.Printf("Conexão bem-sucedida: Jogador %s\n", c.nome)
	return nil
}

func (c *memoriaCliente) ReceberJogada(ctx context.Context, jogo *pb.Jogo) (*wrapperspb.BoolValue, error) {
	fmt.Printf("\nÚltima jogada do jogador %d\n", jogo.IdUltimoJogador)
	c.updateGameBoard(jogo)
	c.imprimirEstadoDoJogo(jogo)
	return &wrapperspb.BoolValue{Value: true}, nil
}

func (c *memoriaCliente) InformarJogador(ctx context.Context, jogo *pb.Jogo) (*pb.Jogada, error) {
	fmt.Println("Sua vez de jogar!")
	c.updateGameBoard(jogo)
	c.imprimirEstadoDoJogo(jogo)
	return c.perguntarCartas(), nil
}

func (c *memoriaCliente) InformarFimJogo(ctx context.Context, jogo *pb.Jogo) (*wrapperspb.BoolValue, error) {
	fmt.Println("Fim do jogo! Placar final:")
	c.imprimirPlacar(jogo)
	return &wrapperspb.BoolValue{Value: true}, nil
}

func (c *memoriaCliente) updateGameBoard(jogo *pb.Jogo) {
	for idx, carta := range jogo.Cartas {
		if carta.Selecionada {
			c.cartasVisiveis[idx] = carta.Valor // Marca as cartas selecionadas como visíveis
		} else if !carta.Ativo {
			c.cartasVisiveis[idx] = "x" // Marca as cartas não ativas
		}
	}
}

func (c *memoriaCliente) imprimirEstadoDoJogo(jogo *pb.Jogo) {
	fmt.Println("\n - Indices das Cartas: ")
	for idx := range jogo.Cartas {
		fmt.Printf("%d ", idx)
	}
	fmt.Println("\n\n - Cartas Escolhidas: ")
	for idx := range jogo.Cartas {
		if val, ok := c.cartasVisiveis[idx]; ok {
			fmt.Printf("%s ", val) // Exibe o valor da carta se ela foi revelada
		} else {
			fmt.Printf("_ ") // Caso contrário, mostra como oculta
		}
	}
	fmt.Println("\n")
	c.imprimirPlacar(jogo)
}

func (c *memoriaCliente) imprimirPlacar(jogo *pb.Jogo) {
	fmt.Println("Placar:")
	for _, jogador := range jogo.Jogadores {
		fmt.Printf("%d - %s: %d\n", jogador.Id, jogador.Nome, jogador.Pontuacao)
	}
}

func (c *memoriaCliente) perguntarCartas() *pb.Jogada {
	reader := bufio.NewReader(os.Stdin)
	fmt.Println("Escolha duas cartas para virar: ")
	fmt.Print(" - Primeira carta (índice): ")
	carta1Str, _ := reader.ReadString('\n')
	carta1, _ := strconv.Atoi(strings.TrimSpace(carta1Str))

	fmt.Print(" - Segunda carta (índice): ")
	carta2Str, _ := reader.ReadString('\n')
	carta2, _ := strconv.Atoi(strings.TrimSpace(carta2Str))

	jogada := &pb.Jogada{
		Carta1:    int32(carta1),
		Carta2:    int32(carta2),
		IdJogador: c.id,
	}
	c.cartasVisiveis[int(carta1)] = "?" // Marca a carta selecionada como "em jogo" até ser atualizada
	c.cartasVisiveis[int(carta2)] = "?"
	return jogada
}

func main() {
	conn, err := grpc.Dial(serverAddr, grpc.WithInsecure(), grpc.WithBlock())
	if err != nil {
		log.Fatalf("Não foi possível conectar ao servidor: %v", err)
	}
	defer conn.Close()

	client := pb.NewMemoriaServidorClient(conn)
	mc := newMemoriaCliente(50, "Pergher", localClientAddr, client)
	if err := mc.Conectar(); err != nil {
		log.Fatalf("Erro na conexão: %v", err)
	}

	lis, err := net.Listen("tcp", localClientAddr)
	if err != nil {
		log.Fatalf("Falha ao abrir o porto local: %v", err)
	}
	s := grpc.NewServer()
	pb.RegisterMemoriaClienteServer(s, mc)

	go func() {
		if err := s.Serve(lis); err != nil {
			log.Fatalf("Falhou ao servir: %v", err)
		}
	}()

	fmt.Println("Cliente aguardando requisições do servidor...")
	select {} // Bloqueia o main indefinidamente para o servidor continuar rodando
}

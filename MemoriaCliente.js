const readline = require('readline-sync');

class MemoriaCliente {
  constructor(id, nome, enderecoCliente) {
    this.nome = nome;
    this.id = id;
    this.enderecoCliente = enderecoCliente;
  }

  receberJogada(call, callback) {
    try {
      if (call.request.idUltimoJogador === this.id) {
        console.log("\nSua jogada: ");
      } else {
        console.log(`\nJogada do jogador ${call.request.idUltimoJogador}:`);
      }
      this.imprimirJogo(call.request);
      this.imprimirPlacar(call.request);
      callback(null, { value: true });
    } catch (error) {
      console.error(`Erro ao receber jogada: ${error.message}`);
      callback(null, { value: false });
    }
  }

  informarJogador(call, callback) {
    this.imprimirJogo(call.request);
    const jogada = this.perguntarCartas();
    callback(null, jogada);
  }

  informarFimJogo(call, callback) {
    console.log("\nFim de jogo! \nPlacar final:");
    this.imprimirPlacar(call.request);
    callback(null, { value: true });
  }

  imprimirJogo(jogo) {
    console.log("\n - Indices das Cartas: ");
    jogo.cartas.forEach((carta, index) => {
      process.stdout.write(`${index} `);
    });
    console.log("\n");

    console.log(" - Cartas Escolhidas: ");
    jogo.cartas.forEach((carta, index) => {
      if (carta.ativo && !carta.selecionada) {
        process.stdout.write(`${carta.valor} `);
      } else if (carta.selecionada) {
        process.stdout.write(`${carta.valor} `);
      } else {
        process.stdout.write(`${index} `);
      }
    });
    console.log("\n");
  }

  perguntarCartas() {
    console.log("\nSua vez de jogar. Escolha duas cartas para virar: ");
    const carta1 = readline.questionInt(" - Primeira carta: ");
    const carta2 = readline.questionInt(" - Segunda carta: ");

    return {
      carta1: carta1,
      carta2: carta2,
      idJogador: this.id
    };
  }

  imprimirPlacar(jogo) {
    console.log("Placar:");
    jogo.jogadores.forEach(jogador => {
      console.log(`${jogador.id} - ${jogador.nome}: ${jogador.pontuacao}`);
    });
  }
}

module.exports = MemoriaCliente;

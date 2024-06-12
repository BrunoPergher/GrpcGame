const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const MemoriaCliente = require('./MemoriaCliente');

const packageDefinition = protoLoader.loadSync('memoria.proto', {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});

const memoriaProto = grpc.loadPackageDefinition(packageDefinition).agenda;

const enderecoServidor = 'localhost:50051';
const endereco = 'localhost:8082';
const id = 2;
const nome = 'Jogador 2';

const server = new grpc.Server();

const memoriaCliente = new MemoriaCliente(id, nome, endereco);

server.addService(memoriaProto.MemoriaCliente.service, memoriaCliente);
server.bindAsync(endereco, grpc.ServerCredentials.createInsecure(), (err, port) => {
  if (err) {
    console.error(err);
    return;
  }
  console.log('Cliente aguardando requisições do servidor...');

  const client = new memoriaProto.MemoriaServidor(enderecoServidor, grpc.credentials.createInsecure());

  const jogador = {
    id: id,
    nome: nome,
    pontuacao: 0,
    endereco: endereco
  };

  client.conectar(jogador, (error, response) => {
    if (error) {
      console.error(`Erro ao conectar: ${error.message}`);
      return;
    }
    if (response.value) {
      console.log(`Jogador ${nome} conectado com sucesso.`);
    }
  });
});

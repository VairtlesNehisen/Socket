# Socket Cliente-Servidor com Protobuf

Este projeto implementa um sistema de comunicação cliente-servidor utilizando sockets e Protocol Buffers (Protobuf) para serialização de mensagens. O servidor gerencia conexões de múltiplos clientes, permitindo o envio de mensagens entre eles, listagem de usuários conectados, e outras funcionalidades.

## Funcionalidades

- **CMD_ID**: Identificação do cliente no servidor.
- **CMD_LIST**: Lista de usuários conectados.
- **CMD_SENDALL**: Envia uma mensagem para todos os usuários conectados.
- **CMD_SENDONE**: Envia uma mensagem para um único usuário.
- **CMD_SENDLIST**: Envia uma mensagem para uma lista específica de usuários.

## Estrutura do Projeto

- **servidor.py**: Código do servidor que gerencia as conexões dos clientes e processa as mensagens.
- **cliente.py**: Código do cliente que se conecta ao servidor e envia/recebe mensagens.
- **protocol_to_server_pb2.py**: Arquivo gerado pelo Protobuf que define as mensagens e comandos.

## Pré-requisitos

- Python 3.x
- Biblioteca `protobuf` instalada (`pip install protobuf`)

## Configuração

1. **Instalação do Protobuf**:
   - Certifique-se de ter o compilador `protoc` instalado.
   - Gere o arquivo `protocol_to_server_pb2.py` a partir do arquivo `.proto`:
     ```bash
     protoc --python_out=. protocol_to_server.proto
     ```

2. **Configuração do Servidor**:
   - O servidor está configurado para rodar em `localhost` (`::1`) na porta `1234`.
   - Para alterar o host ou porta, modifique as variáveis `HOST` e `PORT` no arquivo `servidor.py`.

3. **Configuração do Cliente**:
   - O cliente se conecta ao servidor no mesmo host e porta.
   - Para alterar o host ou porta, modifique as variáveis `HOST` e `PORT` no arquivo `cliente.py`.

## Execução

1. **Iniciar o Servidor**:
   ```bash
   python servidor.py

import socket
import protocol_to_server_pb2 as proto
import sys
import threading
import time

HOST = '127.0.0.1'
PORT = 1234



client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Defina o tempo limite para aguardar mensagens (por exemplo, 10 segundos)
client_socket.settimeout(10)

u = input("Digite seu nome de usuário: ")

print("\n LISTA DE COMANDO: \n 0 - CMD_ID \n 1 - CMD_LIST \n 2 - CMD_SENDALL \n 3 - CMD_SENDONE \n 4 - CMD_SENDLIST \n 5 - Receber Mensagem")

server_res = proto.BCC_Dist_toClient()

while True:
    cmd = int(input("\nDigite um comando: "))

    if cmd == 0:
        message = proto.BCC_Dist_toServer()
        message.command = proto.BCC_Dist_toServer.CMD_ID
        message.myname = u
        client_socket.send(message.SerializeToString())

        #recebendo a confirmação do servidor
        server_res = proto.BCC_Dist_toClient()

        response_data = client_socket.recv(1024)
        server_res.ParseFromString(response_data)

        if server_res.command == proto.BCC_Dist_toClient.CMD_MSG:
            print(f"{server_res.message.source}: {server_res.message.message}")




client_socket.close()

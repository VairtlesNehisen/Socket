import socket
import protocol_to_server_pb2 as proto
import sys
import threading
import time


HOST = '::1'  
PORT = 1234   

client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) 
client_socket.connect((HOST, PORT))


# Defina o tempo limite para aguardar mensagens (por exemplo, 10 segundos)
client_socket.settimeout(10)

u = input("Digite seu nome de usuário: ")

print("\n LISTA DE COMANDO: \n 0 - CMD_ID \n 1 - CMD_LIST \n 2 - CMD_SENDALL \n 3 - CMD_SENDONE \n 4 - CMD_SENDLIST")

server_res = proto.BCC_Dist_toClient()

# Função para receber mensagens do servidor em segundo plano
def receive_messages():
    while True:
        try:
            response_data = client_socket.recv(1024)
            server_res.ParseFromString(response_data)

            if server_res.command == proto.BCC_Dist_toClient.CMD_MSG:

                print("{:>50}: {}".format(server_res.message.source, server_res.message.message))

              

            elif server_res.command == proto.BCC_Dist_toClient.CMD_LIST:
                
                user_on = []

                for user in server_res.users:
                    user_on.append(user.name)
                    
                
                user_list = ', '.join(user_on)
                print("{:>50}: {}".format(server_res.message.message,  user_list))




               
        except socket.timeout:
            pass

# Inicie a thread para receber mensagens
message_thread = threading.Thread(target=receive_messages)
message_thread.daemon = True
message_thread.start()

while True:
    cmd = int(input("\nDigite um comando: "))

    if cmd == 0:
        message = proto.BCC_Dist_toServer()
        message.command = proto.BCC_Dist_toServer.CMD_ID
        message.myname = u
        client_socket.send(message.SerializeToString())



    elif cmd == 1:
        message = proto.BCC_Dist_toServer()
        message.command = proto.BCC_Dist_toServer.CMD_LIST
        message.myname = u
        client_socket.send(message.SerializeToString())
        
       
    
    elif cmd == 2:

        msg = input("Digite sua mensagem: ")
        message = proto.BCC_Dist_toServer()
        message.command = proto.BCC_Dist_toServer.CMD_SENDALL
        message.myname = u
        message.message = msg
        client_socket.send(message.SerializeToString())





    elif cmd == 3:
        
        msg = input("\n Digite sua mensagem: ")
        dest = input("pra quem deseja enviar :: ")
        message = proto.BCC_Dist_toServer()
        user = proto.BCC_users()
        user = message.receivers.add()
        user.name = dest
        message.command = proto.BCC_Dist_toServer.CMD_SENDONE
        message.myname = u
        message.message = msg
        client_socket.send(message.SerializeToString())
    

    elif cmd == 4:

        msg = input("\n Digite sua mensagem: ")
        dest_list = input("Escreve o nomes de destinatarios :: ")
        dest_users = dest_list.split(',')
        message = proto.BCC_Dist_toServer()

        message.command = proto.BCC_Dist_toServer.CMD_SENDLIST
        message.myname = u
        message.message = msg

        for dest in dest_users:
            user = proto.BCC_users()
            user.name = dest
            message.receivers.extend([user])
        client_socket.send(message.SerializeToString())

    else:
        print("Comando inválido. Escolha um comando válido.")



client_socket.close()

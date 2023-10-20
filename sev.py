import socket
import protocol_to_server_pb2 as proto
import threading
import time

# Configurações do servidor
HOST = '::1' 
PORT = 1234  

BUFFER_SIZE = 1024


usuarios_conectados= []

# Dicionário para mapear nomes de usuário para sockets de cliente
clientes = {}
# Dicionário para mapear IDs de thread para sockets de cliente
clientes_por_thread = {}

# Semáforo para controlar o envio de mensagens
envio_mensagem = threading.Semaphore()



# Função para transformar a lista de clientes em uma string
def connected_users_to_string():
    user_list = "\n".join([user.myname for user in usuarios_conectados])
    return user_list

def handle_client(client_socket):

    try:
         # Obtém o ID da thread atual
        thread_id = threading.get_ident()

        # Armazena o socket do cliente no dicionário usando o ID da thread como chave
        clientes_por_thread[thread_id] = client_socket

        #print(f"thread atual --> {thread_id} \n")

        while True:
            dados = client_socket.recv(BUFFER_SIZE)
            if not dados:
                break

            # Deserializar a mensagem recebida
            received_message = proto.BCC_Dist_toServer()
            received_message.ParseFromString(dados)
            client_res = proto.BCC_Dist_toClient()

       
            # Processar a mensagem com base no comando recebido
            if received_message.command == proto.BCC_Dist_toServer.CMD_ID:
               # print(f"\n Recebido CMD_ID de {received_message.myname}\n")

                username = received_message.myname
                
                clientes[received_message.myname] = client_socket  # Associa o nome de usuário ao socket do cliente

                # Adicione o nome de usuário à lista de usuários conectados
                usuarios_conectados.append(username)
                
                print(f"{username} conectado.")

                # Abre o arquivo para leitura
                with open("Mensagem_pendente.txt", "r") as arquivo:
                    conteudo = arquivo.read()

                # Verifica se o conteúdo do arquivo não está vazio
                if conteudo:
                    print("Enviando mensagens pendente!.")
                    send_message(username,"conexao bem sucedida")
                    time.sleep(1)
                    send_pending_message(client_socket,username)
                    
                else:
                    print("O arquivo está vazio.")
                    send_message(username,"conexao bem sucedida")


                

                

            elif received_message.command == proto.BCC_Dist_toServer.CMD_LIST:
               # print(f"\n Recebido CMD_LIST de {received_message.myname}")

                sender = received_message.myname

                send_list(client_socket, sender)


            elif received_message.command == proto.BCC_Dist_toServer.CMD_SENDONE:

                # Adquira o semáforo para enviar mensagem
                envio_mensagem.acquire()

                try:

                    mensagem = received_message.message
                    receiver = received_message.receivers[0].name
                    sender = received_message.myname
                    print(f"\n Recebido CMD_SENDONE de {received_message.myname}")
                    print(f"\n Mensagem recebida de {received_message.myname}: {mensagem} - Destinatario -> {receiver}")
                    # Verifiaque se a chave 'idade' está no dicionário
                    if receiver in clientes:

                        print(f"*cliente {receiver} esta na lista*")

                        send_one(sender,receiver,mensagem)
                        #enviando um confirmation pro remetente
                        send_message(sender,"mensegem enviada!")
                    
                    if receiver not in clientes:

                        print(f"*cliente {receiver} nao esta na lista*")

                        with open("Mensagem_pendente.txt", "w") as arquivo:
                            sender = sender
                            mensagem = mensagem
                            receiver = receiver
                            # Escreva as informações no arquivo
                            arquivo.write(f"{sender} ,{mensagem} ,{receiver}")


                        
                        send_message(sender,"mensegem nao enviada!")
                        

                

                finally:
                    # Libere o semáforo após enviar a mensagem
                    envio_mensagem.release()




            elif received_message.command == proto.BCC_Dist_toServer.CMD_SENDALL:

                mensagem = received_message.message
                sender = received_message.myname

                send_all(sender,mensagem)
            
            elif received_message.command == proto.BCC_Dist_toServer.CMD_SENDLIST:

               # print(f"\nRecebido CMD_SENDLIST do {received_message.myname}\n")

                list_cliente = received_message.receivers
                message = received_message.message
                sender = received_message.myname
                 
                user_list = []

                for user in list_cliente:
                  
                  user_name = user.name

                  print(f"\n usuario ->>: {user_name}")

                  if user_name in clientes:
                         
                         send_one(sender, user_name, message)
                  else:
                         # Salve a mensagem para usuários offline no arquivo "Mensagem_pendente.txt"
                         with open("Mensagem_pendente.txt", "a") as arquivo:
                             arquivo.write(f"{sender},{message},{user_name}\n")

               
       
       
       





    finally:

        # Remove o cliente do dicionário quando a thread é encerrada
        del clientes_por_thread[thread_id]

        # Remove o nome do cliente do dicionário quando a conexão é encerrada
        for username, socket in list(clientes.items()):
            if socket == client_socket:
                del clientes[username]
            break

        # Remove o nome do cliente da lista de usuários conectados quando a conexão é encerrada
        if received_message.myname in usuarios_conectados:
            usuarios_conectados.remove(received_message.myname)


        print(f"Conexão encerrada com {received_message.myname}")
        client_socket.close()




def send_pending_message(client_socket,cliente):

    mensagem_pendente = []

    # Abra o arquivo para leitura
    with open("Mensagem_pendente.txt", "r") as arquivo:
        linhas = arquivo.readlines()

    # Processa as linhas do arquivo
    for linha in linhas:
        partes = linha.strip().split(',')
        if len(partes) == 3:
            sender, message, receiver = partes
            if receiver == cliente:
                mensagem_pendente.append((sender, message))

    # Envie as mensagens pendentes para o cliente
    for sender, message in mensagem_pendente:
        send_one(sender, cliente, message)

    # Limpe as mensagens pendentes do arquivo
    with open("Mensagem_pendente.txt", "w") as arquivo:
        arquivo.write("")

    # Outra opção seria manter um arquivo de log das mensagens pendentes para evitar a repetição.


def send_message(receiver, message):
    # Função para enviar mensagens para um único destinatário
    if receiver in clientes:
        user_socket = clientes[receiver]
        client_res = proto.BCC_Dist_toClient()
        client_res.command = proto.BCC_Dist_toClient.CMD_MSG
        client_res.message.receiver = receiver
        client_res.message.message = message
        client_res.message.source = "SERVIDOR"
        user_socket.send(client_res.SerializeToString())
    


def send_one(sender, receiver, message):
    # Função para enviar mensagens para um único destinatário
    if receiver in clientes:
        user_socket = clientes[receiver]
        client_res = proto.BCC_Dist_toClient()
        client_res.command = proto.BCC_Dist_toClient.CMD_MSG
        client_res.message.receiver = receiver
        client_res.message.message = message
        client_res.message.source = sender
        user_socket.send(client_res.SerializeToString())
        send_message(sender,"mensegem enviada!")
    

def send_all(sender, message):

    client_res = proto.BCC_Dist_toClient()
    client_res.command = proto.BCC_Dist_toClient.CMD_MSG
    client_res.message.message = message
    client_res.message.source = sender
    
    for receiver in usuarios_conectados:

        if receiver != sender:
            if receiver in clientes:
                user_socket = clientes[receiver]
                client_res.message.receiver = receiver
                user_socket.send(client_res.SerializeToString())
                send_message(sender,"mensegem enviada a *todos*")

            else:

                with open("Mensagem_pendente.txt", "w") as arquivo:
                    sender = sender
                    mensagem = message
    
                    # Escreva as informações no arquivo
                    arquivo.write(f"Remetente: {sender}\n mensagem: {mensagem}\n")

                

def send_list(client_socket, sender):

    client_res = proto.BCC_Dist_toClient()
    client_res.command = proto.BCC_Dist_toClient.CMD_LIST
    client_res.message.message = "Lista de usuario online -- "
    client_res.message.source = "SERVIDOR"
    client_res.message.receiver = sender
    
    # Itera pela lista de usuários conectados e adiciona cada usuário como um destinatário
    for dest in usuarios_conectados:
        user = proto.BCC_users()
        user.name = dest
        client_res.users.extend([user])

    client_socket.send(client_res.SerializeToString())




# Inicializar o socket do servidor
server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Servidor ouvindo em {HOST} -- {PORT}")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Conexão estabelecida com {client_address}")

    # Criar uma nova thread para lidar com cada cliente
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()

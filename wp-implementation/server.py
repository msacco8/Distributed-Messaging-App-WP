import socket
import threading


MSG_SIZE = 1024
HOST = '65.112.8.52'
PORT = 6000

class Server():

    def __init__(self):
        self.accounts = {}
        self.connections = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def DeleteAccount(self, clientSocket, username):
        deleteAccountResponse = ''

        if username in self.accounts:
            del self.accounts[username]
            deleteAccountResponse = "1|" + username
            print("User " + username + " deleted.")
        else:
            deleteAccountResponse = "0|" + username
            print("Error deleting user " + username + ".")

        clientSocket.send(deleteAccountResponse.encode())
        return

    def ListAccounts(self, clientSocket, wildcard):
        listAccountsResponse = '1|'

        #implement wildcard search

        for account in self.accounts.keys():
            if wildcard in account:
                listAccountsResponse += account + "|"
        
        clientSocket.send(listAccountsResponse.encode())
        return

    def LogIn(self, clientSocket, clientAddress, username):
        logInResponse = ''

        if username in self.accounts and username not in self.connections:
            self.connections[username] = clientAddress
            logInResponse = "1|" + username
        else:
            logInResponse = "0|" + username
        
        clientSocket.send(logInResponse.encode())
        return

    def CreateAccount(self, clientSocket, clientAddress, username):
        createAccountResponse = ''

        if username not in self.accounts:
            self.connections[username] = clientAddress
            self.accounts[username] = []
            createAccountResponse = "1|" + username
        
        else:
            createAccountResponse = "0|" + username
        
        print(createAccountResponse)
        clientSocket.send(createAccountResponse.encode())
        return

    def GetMessages(self, clientSocket, username):
        # need to handle for when size of list is greater than msg size
        getMessagesResponse = ''

        if username in self.accounts and self.accounts[username]:
            getMessagesResponse = "1"
            for sender, message in self.accounts[username]:
                getMessagesResponse += "|" + sender + "|" + message
            self.accounts[username] = []
        else:
            getMessagesResponse = "0|"
        clientSocket.send(getMessagesResponse.encode())
        return 

    def SendMessage(self, clientSocket, sender, recipient, message):
        sendMessageResponse = ''

        if recipient in self.accounts:
            self.accounts[recipient].append([sender, message])
            sendMessageResponse = "1|" + recipient
        else:
            sendMessageResponse = "0|" + recipient
        # print(self.accounts[recipient])
        clientSocket.send(sendMessageResponse.encode())
        return

    def Listen(self):

        # self.sock.bind((socket.gethostname(), PORT))
        # self.sock.bind((HOST, PORT))
        self.sock.bind(('0.0.0.0', PORT))
        # print(self.sock.gethostbyname(self.sock.gethostname()))

        # become a server socket
        self.sock.listen(5)
        print("Listening on " + HOST + ":" + str(PORT))

        while True:
            # accept connections from outside
            (clientSocket, clientAddress) = self.sock.accept()
            print(clientAddress[0] + ":" + str(clientAddress[1]) + ' connected!')

            clientThread= threading.Thread(target=self.ClientThread, args=(clientSocket, clientAddress))
            clientThread.start()

        self.sock.close()

    def ClientThread(self, clientSocket, clientAddress):
        print("Hello")

        while True:
            clientRequest = clientSocket.recv(MSG_SIZE).decode()
            if not clientRequest:
                break
            if clientRequest:
                clientRequest = clientRequest.strip().split("|")
                opCode = clientRequest[0]

                if opCode == "0":
                    self.LogIn(clientSocket, clientAddress, clientRequest[1])

                elif opCode == "1":
                    self.CreateAccount(clientSocket, clientAddress, clientRequest[1])
                
                elif opCode == "2":
                    self.SendMessage(clientSocket, clientRequest[1], clientRequest[2], clientRequest[3])

                elif opCode == "3":
                    self.GetMessages(clientSocket, clientRequest[1])

                elif opCode == "4":
                    self.ListAccounts(clientSocket, clientRequest[1])

                elif opCode == "5":
                    self.DeleteAccount(clientSocket, clientRequest[1])
                    
        for user, (addr, port) in self.connections.items():
            if addr == clientAddress[0] and port == clientAddress[1]:
                print("User " + user + " at " + addr + ":" + str(port) + " disconnected")
                del self.connections[user]
                break
        clientSocket.close()   

if __name__ == '__main__':
    server = Server()
    server.Listen()


# # list to store created accounts
# created_accounts = {}

# # list to store current client connections
# clients = {}

# # def send_message(message, receiver_socket):
# #     receiver_socket.send(message)

# def client_thread(client_socket, client_address):

#     client_socket.send("Welcome to the messaging center. Please enter your username: ".encode())
#     username = client_socket.recv(1024).decode().strip()

#     # check if username already exists - HANDLE LOGIC LATER
#     # prompt user 'do you have an account yet? if not then check if input exists and add, if yes then check f input exists and sign in

#     # add username to list of accounts
#     created_accounts[username] = client_socket
#     # clients.append(client_socket)
#     print(f"{username} has created an account.")
#     client_socket.send((f"Welcome {username}!").encode())
#     while True:
#         message = client_socket.recv(1024).decode().strip()
#         if message:
#             created_accounts[message[:3]].send(message[3:])

#     client_socket.close()


# serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# # serversocket.bind((socket.gethostname(), 3020))
# serversocket.bind(('0.0.0.0', 6000))
# print(socket.gethostbyname(socket.gethostname()))

# # become a server socket
# serversocket.listen(5)

# while True:
#     # accept connections from outside
#     (client_socket, client_address) = serversocket.accept()
#     print(client_address[0] + ' connected!')

#     cl_thread= threading.Thread(target=client_thread, args=(client_socket, client_address))
#     cl_thread.start()


# serversocket.close()
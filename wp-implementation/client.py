import socket
import select
import sys

MSG_SIZE = 1024

class Client():

    def __init__(self):
        self.username = ''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def Connect(self):
        self.sock.connect((socket.gethostname(), 6000))
    
    def LogIn(self):
        username = input("Please enter your username: ")

        # check username constraints

        # build request string
        opCode = "1"
        logInRequest = (opCode + "|" + username).encode()
        
        self.sock.send(logInRequest)

        logInResponse = self.sock.recv(MSG_SIZE).decode().strip()
        return logInResponse.split("|")

    def CreateAccount(self):
        username = input("Enter your desired username to create an account: ")

        # check username constraints

        # build request string
        opCode = "1"
        createAccountRequest = (opCode + "|" + username).encode()

        # send request string to server and get response
        self.sock.send(createAccountRequest)
        createAccountResponse = self.sock.recv(MSG_SIZE).decode().strip()
        # print(createAccountResponse)
        return createAccountResponse.split("|")

    def SendMessage(self):
        opCode = "2"
        recipient = input("To: ")
        message = input("Message: ")

        # check recipient constraints
        # check message constraints

        sendMessageRequest = (opCode + "|" + self.username + "|" + recipient + "|" + message).encode()
        self.sock.send(sendMessageRequest)
        sendMessageResponse = self.sock.recv(MSG_SIZE).decode().strip().split("|")

        if sendMessageResponse[0] == "1":
            print("Message sent to " + recipient + ".")
        else:
            print("Error sending message.")

        return
    
    def GetMessages(self):
        # need to handle for when size of list is greater than msg size
        opCode = "3"
        getMessagesRequest = (opCode + "|" + self.username).encode()
        self.sock.send(getMessagesRequest)
        getMessagesResponse = self.sock.recv(MSG_SIZE).decode().strip().split("|")

        if getMessagesResponse[0] == "1":
            msgPtr = 1
            print("Messages:")
            while msgPtr < len(getMessagesResponse) - 1:
                sender = getMessagesResponse[msgPtr]
                message = getMessagesResponse[msgPtr + 1]
                print("<" + sender + "> " + message)
                msgPtr += 2
        else:
            print("There are no unread messages.")
        input("Press enter to continue.")
        return

    def ListAccounts(self):
        opCode = "4"
        wildcard = input("Search for subset (blank input will show all accounts): ")
        listAccountsRequest = (opCode + "|" + wildcard).encode()
        self.sock.send(listAccountsRequest)
        listAccountsResponse = self.sock.recv(MSG_SIZE).decode().strip().split("|")
        if listAccountsResponse[0] == "1" and len(listAccountsResponse[1]) > 0:
            for account in listAccountsResponse[1:]:
                print(account)
        else:
            print("No accounts found starting with \"" + wildcard + "\".")
        input("Press enter to continue.")
        return
    
    def DeleteAccount(self):
        opCode = "5"
        deleteAccountRequest = (opCode + "|" + self.username).encode()
        self.sock.send(deleteAccountRequest)
        deleteAccountResponse = self.sock.recv(MSG_SIZE).decode().strip().split("|")
        if deleteAccountResponse[0] == "1":
            print("User " + self.username + " successfully deleted. Bye.")
        else:
            print("There was an error deleting your account.")
        return
    
    def Run(self):

        print("Welcome to the messaging center.\n")

        while True:
            has_account = input("Do you have an account already? (y/n): ")

            if has_account.lower() == 'y':
                loginStatus, username  = self.LogIn()
                if loginStatus == "1":
                    self.username = username
                    print("User " + username + " logged in.")
                    break
                else:
                    print("Username " + username + " does not exist or is logged in, please try again.")
            
            if has_account.lower() == 'n':
                loginStatus, username = self.CreateAccount()
                if loginStatus == "1":
                    self.username = username
                    print("User " + username + " created.")
                    break
                else:
                    print("Username " + username + " is taken, please try again.")
        
        self.username = username

        while True:

            print("l = List accounts")
            print("s = Send message")
            print("g = Get messages")
            print("d = Delete account")
            print("e = Exit")
            action = input("Action: ")
            
            if action.lower() == 'l':
                self.ListAccounts()
            
            elif action.lower() == 's':
                self.SendMessage()

            elif action.lower() == 'g':
                self.GetMessages()

            elif action.lower() == 'd':
                self.DeleteAccount()
                break

            elif action.lower() == 'e':
                break
        
            else:
                print("Please enter a valid action.")
        
        self.sock.close()

if __name__ == '__main__':
    client = Client()
    client.Connect()
    client.Run()

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# # server.connect((socket.gethostname(), 3020))
# server.connect((socket.gethostname(), 6000))
# print(socket.gethostname())

# while True:

#     print("l = List accounts")
#     print("s = Send message")
#     print("g = Get messages")
#     print("d = Delete account")
#     print("e = Exit")
#     action = input("Action: ")

#     sockets_list = [sys.stdin, server]

#     read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])

#     for socks in read_sockets:
#         if socks == server:
#             message = socks.recv(2048)
#             # print (message)
#         else:
#             message = sys.stdin.readline()
#             server.send(message.encode())
#             sys.stdout.write("<You>")
#             sys.stdout.write(message)
#             sys.stdout.flush()


# server.close()
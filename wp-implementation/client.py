import socket
import select
import sys

MSG_SIZE = 1024
HEADER_LENGTH = 2

class Client():

    def __init__(self):
        self.username = ''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def Connect(self):
        self.sock.connect((socket.gethostname(), 6000))
        # self.sock.connect(('172.30.18.52', 6000))
        # self.sock.connect(('172.30.18.52', 6000))
    
    def LogIn(self):

        # check username constraints
        while True:
            username = input("Please enter your username: ")
            if len(username) > 16:
                print("Usernames cannot contain more than 16 characters. Please try again.")
            else:
                break

        # build request string
        opCode = "0"
        logInRequest = (opCode + "|" + username).encode()
        
        try:
            self.sock.send(logInRequest)
        except:
            print("Error sending login request")

        try:
            logInResponse = self.sock.recv(MSG_SIZE).decode().strip()
        except:
            print("Error receiving login response")

        print(logInResponse)

        return logInResponse.split("|")

    def CreateAccount(self):

        # check username constraints
        while True:
            username = input("Enter your desired username to create an account: ")
            if len(username) > 16:
                print("Username must be 16 characters or less")
            else:
                break

        # build request string
        opCode = "1"
        createAccountRequest = (opCode + "|" + username).encode()

        # send request string to server and get response
        try:
            self.sock.send(createAccountRequest)
        except:
            print("Error sending create account request")

        try:
            createAccountResponse = self.sock.recv(MSG_SIZE).decode().strip()
        except:
            print("Error receiving create account response")

        return createAccountResponse.split("|")

    def SendMessage(self):
        opCode = "2"

        # check recipient constraints
        while True:
            recipient = input("To: ")
            if len(recipient) > 16:
                print("Usernames cannot contain more than 16 characters. Please try again.")
            else:
                break

        # check message constraints
        while True:
            message = input("Message: ")
            if len(message) > 256:
                print("Messages cannot contain more than 256 characters. Please try again.")
            else:
                break

        sendMessageRequest = (opCode + "|" + self.username + "|" + recipient + "|" + message).encode()

        try:
            self.sock.send(sendMessageRequest)
        except:
            print("Error sending message request")

        try:
            sendMessageResponse = self.sock.recv(MSG_SIZE).decode().strip().split("|")
        except:
            print("Error receiving send message response")

        if sendMessageResponse[0] == "1":
            print("Message sent to " + recipient + ".")
        else:
            print("User " + recipient + "does not exist.")

        return
    
    def GetMessages(self):
        # need to handle for when size of list is greater than msg size
        opCode = "3"
        getMessagesRequest = (opCode + "|" + self.username).encode()
        self.sock.send(getMessagesRequest)
        getMessagesResponse = self.sock.recv(MSG_SIZE).decode()
        getMessageLength = int(getMessagesResponse.split("|")[0])
        totalRecvd = MSG_SIZE

        if getMessageLength != 0:
            if getMessageLength > 1:
                while totalRecvd < (getMessageLength * MSG_SIZE):
                    getMessagesResponse += self.sock.recv(MSG_SIZE).decode()
                    totalRecvd += MSG_SIZE
            getMessagesResponse = getMessagesResponse.strip().split("|")
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
        self.GetMessages()
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
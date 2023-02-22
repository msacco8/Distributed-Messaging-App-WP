import socket
import sys

MSG_SIZE = 1024

class Client():

    def __init__(self):

        # store username of current client session
        self.username = ''

        # initialize client socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def Connect(self, serverAddress):

        # connect to server from system arguments
        self.sock.connect((serverAddress, 6000))
    
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
        
        # send log in request to server and get response
        try:
            self.sock.send(logInRequest)
        except:
            print("Error sending login request")

        try:
            logInResponse = self.sock.recv(MSG_SIZE).decode().strip()
        except:
            print("Error receiving login response")

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

        # send create account request to server and get response
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

        # build pipe delimited request string
        sendMessageRequest = (opCode + "|" + self.username + "|" + recipient + "|" + message).encode()

        # send message request to server and get response
        try:
            self.sock.send(sendMessageRequest)
        except:
            print("Error sending message request")

        try:
            sendMessageResponse = self.sock.recv(MSG_SIZE).decode().strip().split("|")
        except:
            print("Error receiving send message response")

        # reflect success status to client
        if sendMessageResponse[0] == "1":
            print("Message sent to " + recipient + ".")
        else:
            print("User " + recipient + "does not exist.")

        return
    
    def GetMessages(self):
        opCode = "3"

        # send username to server to await return of messages
        getMessagesRequest = (opCode + "|" + self.username).encode()
        self.sock.send(getMessagesRequest)

        # get first chunk of size MSG_SIZE to receive number of required messages
        getMessagesResponse = self.sock.recv(MSG_SIZE).decode()
        getMessageLength = int(getMessagesResponse.split("|")[0])
        totalRecvd = MSG_SIZE

        # receive chunks of MSG_SIZE until entire message is received
        if getMessageLength != 0:
            if getMessageLength > 1:
                while totalRecvd < (getMessageLength * MSG_SIZE):
                    getMessagesResponse += self.sock.recv(MSG_SIZE).decode()
                    totalRecvd += MSG_SIZE
            getMessagesResponse = getMessagesResponse.strip().split("|")
            msgPtr = 1
            print("Messages:")
            # output sender + message for each message in response
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

        # take user input to search for any substring that matches a subset of user strings
        wildcard = input("Search for subset (blank input will show all accounts): ")

        # build request and send to server
        listAccountsRequest = (opCode + "|" + wildcard).encode()
        self.sock.send(listAccountsRequest)

        # receive list of accounts from server based on wildcard
        listAccountsResponse = self.sock.recv(MSG_SIZE).decode().strip().split("|")

        # output accounts to client interface if there is a successful response
        if listAccountsResponse[0] == "1" and len(listAccountsResponse[1]) > 0:
            for account in listAccountsResponse[1:]:
                print(account)
        else:
            print("No accounts found starting with \"" + wildcard + "\".")
        input("Press enter to continue.")
        return
    
    def DeleteAccount(self):
        opCode = "5"

        # list all messages to client prior to account deletion
        self.GetMessages()

        # send deletion request to server
        deleteAccountRequest = (opCode + "|" + self.username).encode()
        self.sock.send(deleteAccountRequest)

        # receive deletion response and display to client
        deleteAccountResponse = self.sock.recv(MSG_SIZE).decode().strip().split("|")
        if deleteAccountResponse[0] == "1":
            print("User " + self.username + " successfully deleted. Bye.")
        else:
            print("There was an error deleting your account.")
        return
    
    def Run(self):

        print("Welcome to the messaging center.\n")

        # login control loop
        while True:
            has_account = input("Do you have an account already? (y/n): ")

            # handle existing user
            if has_account.lower() == 'y':
                loginStatus, username  = self.LogIn()
                if loginStatus == "1":
                    self.username = username
                    print("User " + username + " logged in.")
                    break
                else:
                    print("Username " + username + " does not exist or is logged in, please try again.")
            
            # handle new user
            if has_account.lower() == 'n':
                loginStatus, username = self.CreateAccount()
                if loginStatus == "1":
                    self.username = username
                    print("User " + username + " created.")
                    break
                else:
                    print("Username " + username + " is taken, please try again.")
        
        # set user once client has logged in or created account
        self.username = username

        # enter main control loop for dispatching to server
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
    serverAddress = sys.argv[1]
    if not serverAddress:
        print("Please try again and enter the server IP address as an argument.")
    else:
        client = Client()
        client.Connect(serverAddress)
        client.Run()
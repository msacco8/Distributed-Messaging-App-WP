# SERVER SIDE OF GRPC APPLICATION
import logging
from concurrent import futures
import socket

import grpc
import app_pb2
import app_pb2_grpc

class AppServicer(app_pb2_grpc.AppServicer):

    def __init__(self):
        # will hold usernames and two entreis: first is an indicator for if the user
        # is logged in, and second entry contains all unsent messages that should be 
        # passed to each user when that user logs in
        self.accounts = {}


    # creates an account if it does not already exist. Since client side will automatically
    # log in after account creation, set the log-in indicator to true
    def CreateAccount(self, request, context):
        if request.username not in self.accounts:
            self.accounts[request.username] = [[True],[]]
            return app_pb2.SuccessResponse(
                success=True,
                message="Account successfully created!"
            )
        else:
            return app_pb2.SuccessResponse(
                success=False,
                message="Sorry, that username is taken already."
            )
        

    # will log in successfully if the account exists and if no other client is currently logged
    # into the account, done by checking the account dict for username key and log-in indicator
    def LogIn(self, request, context):
        if request.username in self.accounts and not self.accounts[request.username][0]:
            self.accounts[request.username][0] = True
            return app_pb2.SuccessResponse(
                success=True,
                message="You are logged in!"
            )
        elif request.username in self.accounts:
            return app_pb2.SuccessResponse(
                success=False,
                message="There was an issue logging in -- please make sure this account is logged out of other clients."
            )
        else:
            return app_pb2.SuccessResponse(
                success=False,
                message="There was an issue logging in -- please make sure this account exists."
            )
            

    # returns list of accounts which contain the wildcard text supplied by the client
    def ListAccounts(self, request, context):
        for account in self.accounts:
            if request.text in account:
                yield app_pb2.Account(username=account)


    # "sends" message to another user by adding it to their message queue. Also verifies
    # that the recipient exists before doing so
    def SendMessage(self, request, context):
        if request.recipient in self.accounts:
            self.accounts[request.recipient][1].append([request.sender, request.text])
            return app_pb2.SuccessResponse(
                success=True,
                message="Message sent!"
            )
        else:
            return app_pb2.SuccessResponse(
                success=False,
                message="There was an issue sending the message -- please make sure this account exists."
            )


    # empties all messages in a specified account's queue to the client side along with
    # relevant metadata
    def GetMessage(self, request, context):
        messages = self.accounts[request.username][1]
        self.accounts[request.username][1] = []
        for message in messages:
            yield app_pb2.Message(
                sender=message[0],
                recipient=request.username,
                text=message[1]
            )


    # logs out user by setting the account's indicator variable to false
    def LogOut(self, request, context):
        self.accounts[request.username][0] = False
        return app_pb2.SuccessResponse(
            success=True,
            message="You have been logged out."
        )


    # deletes account by simply deleting account's key in dictionary
    def DeleteAccount(self, request, context):
        try:
            del self.accounts[request.username]
            return app_pb2.SuccessResponse(
                success=True,
                message="Account deleted. Goodbye!"
            )
        except KeyError:
            return app_pb2.SuccessResponse(
                success=False,
                message="Unkown error occured."
            )


# run server with 10 threads to handle multiple clients
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    app_pb2_grpc.add_AppServicer_to_server(AppServicer(), server)

    # get ip address of current server and make sure server listens on port 6000
    ip_address = socket.gethostbyname(socket.gethostname())
    print("When running your client, specify " + ip_address + " as an argument to the terminal.")
    server.add_insecure_port(ip_address + ':6000')

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
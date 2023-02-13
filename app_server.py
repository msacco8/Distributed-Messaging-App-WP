import logging
from concurrent import futures

import grpc
import app_pb2
import app_pb2_grpc

class AppServicer(app_pb2_grpc.AppServicer):

    def __init__(self):
        # will hold usernames and all unsent messages that should be passed to
        # each user when that user logs in
        self.accounts = {}


    def CreateAccount(self, request, context):
        if request.username not in self.accounts:
            self.accounts[request.username] = []
            return app_pb2.SuccessResponse(
                success=True,
                message="Account successfully created!"
            )
        else:
            return app_pb2.SuccessResponse(
                success=False,
                message="Sorry, that username is taken already."
            )
        

    def LogIn(self, request, context):
        if request.username in self.accounts:
            return app_pb2.SuccessResponse(
                success=True,
                message="You are logged in!"
            )
        else:
            return app_pb2.SuccessResponse(
                success=False,
                message="There was an issue logging in -- please make sure this account exists."
            )
            

    def ListAccounts(self, request, context):
        for account in self.accounts:
            if request.text in account:
                yield app_pb2.Account(username=account)


    def SendMessage(self, request, context):
        if request.recipient in self.accounts:
            self.accounts[request.recipient].append([request.sender, request.text])
            return app_pb2.SuccessResponse(
                success=True,
                message="Message sent!"
            )
        
        else:
            return app_pb2.SuccessResponse(
                success=False,
                message="There was an issue sending the message -- please make sure this account exists."
            )


    def GetMessage(self, request, context):
        messages = self.accounts[request.username]
        self.accounts[request.username] = []
        for message in messages:
            yield app_pb2.Message(
                sender=message[0],
                recipient=request.username,
                text=message[1]
            )


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


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    app_pb2_grpc.add_AppServicer_to_server(AppServicer(), server)
    server.add_insecure_port('[::]:6000')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
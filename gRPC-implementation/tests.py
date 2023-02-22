# TESTS FOR APP
import os
import socket
import time
import unittest

import grpc
import app_pb2
import app_pb2_grpc


class Tests(unittest.TestCase):

    # upon setup, tests run a temporary server and connect to it with a client stub.
    # Essentially runs two terminals in one file for client and server
    @classmethod
    def setUpClass(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        os.system('python3 app_server.py &')
        time.sleep(2)
        server_addr = socket.gethostbyname(socket.gethostname())
        channel = grpc.insecure_channel(server_addr + ":6000")
        self.stub = app_pb2_grpc.AppStub(channel)
        # adding some test accounts for following tests
        self.stub.CreateAccount(app_pb2.Account(username="FOO"))
        self.stub.CreateAccount(app_pb2.Account(username="BAR"))

    # succeed in creating a new account
    def test_a_create_account_succeeds(self):
        create_account_request = app_pb2.Account(username="BAZ")
        create_account_response = self.stub.CreateAccount(create_account_request)
        self.assertTrue(create_account_response.success)
    
    # fail upon trying to create the same account again
    def test_b_create_account_failure(self):
        create_account_request = app_pb2.Account(username="BAZ")
        create_account_response = self.stub.CreateAccount(create_account_request)
        self.assertFalse(create_account_response.success)

    # make sure list accounts returns the right amount of accounts matching a wildcard
    def test_c_list_accounts(self):
        text = "BA"
        list_accounts_request = app_pb2.UserSearch(text=text)
        list_accounts_response = self.stub.ListAccounts(list_accounts_request)
        counter = 0 
        for _ in list_accounts_response:
            counter += 1
        self.assertTrue(counter==2)

    # sending a message from existing sender and recipient suceeds
    def test_d_send_message_succeeds(self):
        for _ in range(3):
            text = "Hello"
            sender = "FOO"
            recipient = "BAR"
            send_messages_request = app_pb2.Message(
                sender=sender,
                recipient=recipient,
                text=text
            )
            send_messages_response = self.stub.SendMessage(send_messages_request)
            self.assertTrue(send_messages_response.success)

    # sending a message to a non existent user fails
    def test_e_send_message_fails(self):
        text = "Hello"
        sender = "FOO"
        recipient = "NON_EXISTENT_USER"
        send_messages_request = app_pb2.Message(
            sender=sender,
            recipient=recipient,
            text=text
        )
        send_messages_response = self.stub.SendMessage(send_messages_request)
        self.assertFalse(send_messages_response.success)

    # test that the messages sent earlier are received correctly by recipient
    def test_f_get_messages(self):
        get_messages_request = app_pb2.Account(username="BAR")
        get_messages_response = self.stub.GetMessage(get_messages_request)
        counter = 0
        for message in get_messages_response:
            counter += 1
            self.assertTrue(message.sender=="FOO")
            self.assertTrue(message.text=="Hello")
        self.assertTrue(counter==3)

    # succeed in deleting an account
    def test_g_delete_account_succeeds(self):
        delete_account_request = app_pb2.Account(username="FOO")
        delete_account_response = self.stub.DeleteAccount(delete_account_request)
        self.assertTrue(delete_account_response.success)
    
    # fail when trying to delete the same account again
    def test_h_delete_account_fails(self):
        delete_account_request = app_pb2.Account(username="FOO")
        delete_account_response = self.stub.DeleteAccount(delete_account_request)
        self.assertFalse(delete_account_response.success)

    # succeed in logging out existing account
    def test_i_log_out(self):
        log_out_request = app_pb2.Account(username="BAR")
        log_out_response = self.stub.LogOut(log_out_request)
        self.assertTrue(log_out_response.success)

    # clean up server when done
    @classmethod
    def tearDownClass(self):
        os.system('pkill -f server.py')


if __name__ == '__main__':
    unittest.main()

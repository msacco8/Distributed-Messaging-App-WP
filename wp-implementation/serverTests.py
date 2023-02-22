import unittest
from unittest.mock import Mock
from server import Server

class TestServer(unittest.TestCase):

    def setUp(self):
        self.server = Server()

    def test_log_in(self):
        clientSocket = Mock()
        self.server.accounts = {'user1': []}
        self.server.LogIn(clientSocket, ('0.0.0.0', 10000), 'user1')
        self.assertIn('user1', self.server.connections)
        clientSocket.send.assert_called_with('1|user1'.encode())
        self.server.sock.close()

    def test_log_in_already_logged_in(self):
        clientSocket = Mock()
        self.server.accounts = {'user1': []}
        self.server.connections = {'user1': ('0.0.0.0', 1234)}
        self.server.LogIn(clientSocket, ('0.0.0.0', 5678), 'user1')
        self.assertIn('user1', self.server.connections)
        clientSocket.send.assert_called_with('0|user1'.encode())
        self.server.sock.close()

    def test_log_in_invalid_user(self):
        clientSocket = Mock()
        self.server.LogIn(clientSocket, ('0.0.0.0', 5678), 'user2')
        self.assertNotIn('user2', self.server.connections)
        clientSocket.send.assert_called_with('0|user2'.encode())
        self.server.sock.close()
    
    def test_create_account(self):
        clientSocket = Mock()
        self.server.CreateAccount(clientSocket, ('0.0.0.0', 10000), 'user1')
        self.assertEqual(self.server.connections['user1'], ('0.0.0.0', 10000))
        self.assertIn('user1', self.server.accounts)
        clientSocket.send.assert_called_with('1|user1'.encode())
        self.server.sock.close()

    def test_delete_account(self):
        clientSocket = Mock()
        self.server.accounts = {'user1': [], 'user2': []}
        self.server.DeleteAccount(clientSocket, 'user1')
        self.assertNotIn('user1', self.server.accounts)
        clientSocket.send.assert_called_with('1|user1'.encode())
        self.server.sock.close()

    def test_list_accounts(self):
        clientSocket = Mock()
        self.server.accounts = {'user1': [], 'user2': [], 'user3': []}
        self.server.ListAccounts(clientSocket, '')
        clientSocket.send.assert_called_with('1|user1|user2|user3'.encode())
        self.server.sock.close()

    def test_list_accounts(self):
        clientSocket = Mock()
        self.server.accounts = {'user1': [], 'user12': [], 'user3': []}
        self.server.ListAccounts(clientSocket, 'user1', )
        clientSocket.send.assert_called_with('1|user1|user12'.encode())
        self.server.sock.close()

    def test_get_messages(self):
        clientSocket = Mock()
        self.server.accounts = {'user1': [['user2', 'hello'], ['user3', 'world']]}
        self.server.GetMessages(clientSocket, 'user1')
        clientSocket.send.assert_called_with('1|user2|hello|user3|world'.encode())
        self.server.sock.close()

    def test_send_message(self):
        clientSocket = Mock()
        self.server.accounts = {'user1': [], 'user2': []}
        self.server.SendMessage(clientSocket, 'user1', 'user2', 'hello')
        self.assertEqual(self.server.accounts['user2'], [['user1', 'hello']])
        clientSocket.send.assert_called_with('1|user2'.encode())
        self.server.sock.close()
    
if __name__ == '__main__':
    unittest.main()

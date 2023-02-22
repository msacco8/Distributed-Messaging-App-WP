
import unittest
from io import StringIO
from unittest.mock import MagicMock

from client import Client

class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.client.sock = MagicMock()

    def tearDown(self):
        self.client.sock.close()

    def test_LogIn(self):
        self.client.sock.recv.return_value = b"1|Welcome, testuser"
        expected = ["1", "Welcome, testuser"]
        with unittest.mock.patch('builtins.input', return_value="testuser"):
            self.assertEqual(self.client.LogIn(), expected)
        self.client.sock.send.assert_called_once_with(b"0|testuser")
        self.client.sock.close()

    def test_CreateAccount(self):
        self.client.sock.recv.return_value = b"1|User testuser created"
        expected = ["1", "User testuser created"]
        with unittest.mock.patch('builtins.input', return_value="testuser"):
            self.assertEqual(self.client.CreateAccount(), expected)
        self.client.sock.send.assert_called_once_with(b"1|testuser")
        self.client.sock.close()

    def test_SendMessage(self):
        self.client.username = "testuser"
        self.client.sock.recv.return_value = b"1|Message sent"
        with unittest.mock.patch('builtins.input', side_effect=["recipient", "test message"]):
            self.client.SendMessage()
        self.client.sock.send.assert_called_once_with(b"2|testuser|recipient|test message")
        self.client.sock.close()

    def test_ListAccounts(self):
        self.client.sock.recv.return_value = b"1|user1|user2|user3"
        with unittest.mock.patch('builtins.input', return_value=""):
            with unittest.mock.patch('sys.stdout', new=StringIO()) as fakeOutput:
                self.client.ListAccounts()
                self.assertIn("user1\nuser2\nuser3", fakeOutput.getvalue())
        self.client.sock.send.assert_called_once_with(b"4|")
        self.client.sock.close()

    def test_DeleteAccount(self):
        self.client.username = "testuser"
        self.client.sock.recv.return_value = b"1|User testuser deleted"
        self.client.DeleteAccount()
        self.client.sock.send.assert_called_with(b"5|testuser")
        self.client.sock.close()

if __name__ == '__main__':
    unittest.main()

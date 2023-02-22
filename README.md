# Design Documentation

Words.

## Wire Protocal Configuration

Words.

## Wire Protocal Engineering Notebook

Words.

## gRPC Configuration 

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install grpc.

```bash
pip install grpcio
```

To run the client and server, make sure that the two terminals are on the same network. Then, run:

```bash
python3 app_server.py
```

This will display some IP address to the terminal which is the IP that the client will connect to.
Therefore, run the client and add this IP address as an argument on the command line:

```bash
python3 app_client.py <server IP address>
```

Once connected, the client will display instructions for using the messaging system.

## gRPC Engineering Notebook

The process for creating the gRPC messaging app started with creating the .proto file. In this file, I specified the rpc methods of the server (the argument types and return types of all the predicted functions). An example of this is here, specifying that to log in, the server needs an account object. It will then return either that the operation succeeded or failed:

```
rpc LogIn(Account) returns (SuccessResponse) {}
```
Where the account is made up of a username string, and the response is a boolean success indicator along with some message describing the operation's success or failure:

```
message Account {
    string username = 1;
}

message SuccessResponse {
    bool success = 1;
    string message = 2;
}
```

Once I defined all the server methods, I let gRPC create the auto-generated files needed to build the client and server by running in the terminal:

```bash
python3 -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. ./app.proto
```

Next, I moved onto implementing the functions on the server side. The first real design choice I had to make was how to hold messages for each account on the server. I knew that it should be possible for an account to send a message to an account that is not online (therefore it has to be stored somewhere on the server for some time), so my first idea was to have the server contain a dictionary of users where each key is a username and each value is a list of undelivered messages to that user. I then started to fill in server-side functions. Creating an account simply adds a key to the accounts dictionary with the new username (which will be given from the client), and fails if that username is in the dictionary already. Logging in makes sure the user exists in the dictionary and fails otherwise. Listing accounts matches a client-provided text wildcard to all usernames and yields each successful match. Sending a message adds the client-provided text message to the specified recipient's value in the dictionary if the recipient exists. Getting messages empties the queue of messages for a specific account one-by-one by essentially popping them from the dictionary. Deleting an account deletes the account's key in the username (which should never fail because the client will only be able to supply a username which the user is logged into). After implementing all this, I finally used the gRPC documentation to learn how to run the server with multiple threads to handle up to 10 clients at a time. The server also prints the IP address its running on to the terminal such that whoever is running the client knows which address to specify:

```
ip_address = socket.gethostbyname(socket.gethostname())
print("When running your client, specify " + ip_address + " as an argument to the terminal.")
server.add_insecure_port(ip_address + ':6000')
```

The client side was mostly implementing control flow such that the operations are easy enough for the user -- implementing a messaging app solely in a terminal proved to be hard when it comes to UX (if we had more time, I would've tried to make a basic GUI for this app). The client connects to the server using the generated AppStub. It then either creates an account or logs in a user (decided by user input) and holds the resulting username in a variable. It then displays the actions which the server can handle -- listing accounts, sending messages, getting messages, deleting the current account, and exiting (not server related, just breaks out of the loop which keeps the client running and ends the program). Each client action essentially just calls the equivalent server function. Most will just return some success or failure message, but for actions like getting messages or listing accounts, the client prints the list of results to the terminal. The prompt for actions will continue until the user deletes the account or exits. Most of the design issues came from building a correct control flow for the user, but solving these issues was not too hard -- mostly just a matter of thinking harder.

One design detail which caused some overhaul of both the client and server code came when we realized that allowing two clients to be logged into the same account at the same time would cause some issues (e.g. one client deletes the account at the same time a message is being sent from the other client). We decided to implement a guard for this by adding an indicator boolean within the account dictionary (on the server side) that is "True" when logging into an account and "False" when logged out. Then, when logging in from another client, the process will fail if the indicator boolean is already set to "True". This also means that I had to implement a log out function (which turns off indicator) which runs in 3 scenarios: when exiting the client appropriately, deleting the account, or exiting the client abruptly with cmd+C. This solved the potential issues relating to multiple login capability.

Another design decision was how the client should receive messages. Since it is a terminal based application, it would be awkward to display them instantly as it might interfere strangely with the program's control flow, so I decided to have the user have to enter a separate message-receiving area within the application to see all the unread ones. This means that message receiving is not nescessarily "instant" on the client-side -- instead, they are given only when the user wants to see them. 

Lastly, we decided that when an account is deleted, it should empty all unread messages onto the terminal before deleting such that no message goes unseen and the server is not left having to clean up unused message queues.

## Notable Differences between Wire Protocal and gRPC

Words.
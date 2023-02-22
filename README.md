# Design Documentation

Project done by John Minicus and Michael Sacco

## Wire Protocol Configuration

wp-implementation uses only the Python standard library

To run the client and server. make sure that the two terminals are on the same network and that you have navigated to the 'wp-implementation' directory. Then, run:

```bash
python3 server.py
```

This will display the IP address and port that the server is listening on in the terminal. Use the IP address as a command line argument when running the client to connect to the server.

```bash
python3 client.py <server IP address>
```

Once connected, the client will display instructions for using the messaging system.

To run the Client and Server tests enter the following commands in the 'wp-implementation' directory.

Client:
```bash
python3 clientTests.py
```

Server:
```bash
python3 serverTests.py
```

## Wire Protocol Engineering Notebook

In order to create the wire protocol, we first tried to understand the restrictions that we would set on the actions of a client user. Considerations such as message size limits, simultaneous logins, and user character limits were brought up. These allowed us to think about the edge cases of the protocol and how we would deal with them.

By beginning with the gRPC implementation, we were able to use the request and response model that gRPC uses for each of the calls on the wire protocol. This would ensure that we would have sufficient knowledge at each point above the transfer layer to understand where things were going wrong.

Each method on the client side began with the building of a request string, and the specific method was chosen by the control flow loop in the terminal interface. Each method's request was built from an operation code, and the arguments to the function, delimited by pipes, so that the server could scan the request and quickly gather information about what needed to be done. The opcodes correspond to the following functions:

```
"0" - LogIn
"1" - CreateAccount
"2" - SendMessage
"3" - GetMessages
"4" - ListAccounts
"5" - DeleteAccount
```

The client request would then dispatch to the server where the server would alter the data structures necessary for the function, then return a pipe delimited response, where the first character indicated whether the call failed. In special cases, like in GetMessages, the first character indicated the sum of the length of all unread messages. If the character was 0 however, it always represented that an error had occurred or a restriction had been broken. Since every action that needed to be implemented could easily be done using strings, I believe the pipe delimited messages separating strings was a solid design choice for this particular assignment.

The client would then await the response from the server to visually relay the status of the client's request to the user. This end to end request/response model was chosen to clearly display on both ends what was occurring, and was heavily influenced by gRPC's implementation of client/server communication.

Much of the input handling was done on the client side, to minimize the calls to the server. A call was made to the server only when checking the server's data storage was necessary. This was an easy way to create a more efficient system. Examples of this usually involved limiting input sizes based on the purpose of the data that was being sent to the server.

On the server side, a mapping from users to messages seemed to be a sufficient way to keep track of the state of each user, and was also a rapid way to check if specific users existed for use in other functions. To handle the issue of multiple users logging in simultaneously, a mapping from usernames to a tuple of address and port was utilized and entries were deleted upon client sockets disconnecting.

Initially, every message was set to a fixed length and trailing space was stripped to keep the implementation simple, although not very space effective. We decided to keep the message length at 1024 and focus on reducing edge cases. By limiting the message size to 1024, we soon realized that a user who had multiple long messages, with a total length exceeding 1024, would not be able to receive everything. Given this, we decided to modify the GetMessages function to first gather the total length of all messages into a prelimanary response string on the server side. This length was divided by the MSG_SIZE in order to specify how many chunks of 1024 we would need to send to the client. The response string's status code, which lead the string, represented this number so that the client knew when to stop receiving. This method efficiently solved the issue in which a user had many long messages, and was an interesting way to let the message receiver know the length of the message before it's received in its entirety.

Many of the other design decisions which overlap with the wire protocol implementation are described in the gRPC section.

## gRPC Configuration 

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install grpc.

```bash
pip install grpcio
```

To run the client and server, make sure that the two terminals are on the same network. Then, in the 
gRPC-implementation directory, run:

```bash
python3 app_server.py
```

This will display some IP address to the terminal which is the IP that the client will connect to.
Therefore, run the client and add this IP address as an argument on the command line:

```bash
python3 app_client.py <server IP address>
```

Once connected, the client will display instructions for using the messaging system.

To test the code, make sure the Python unittest package is installed and run:

```bash
python3 tests.py
```

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

## Notable Differences between Wire Protocol and gRPC

gRPC was great given the understandability of the clearly defined protocol for sending and receiving mesages. It is also clear that the marshalling implementations by gRPC are extremely optimized and robust, making it a much more suitable candidate for message transger across systems. That being said, it was great to implement the messaging center in gRPC first, as this provided a mental framework for the call and response model that we implemented in the wire protocol. The implementation details of the data preparation in gRPC are obviously not clearly recognized, but the assignment of specific data types to messages allowed for us to imagine how we could implement similar procedures in the wire protocol.

Our WP was definitely quite rudimentary compared to gRPC but we can see the changes that could be made to the protocol to get closer to their specifications. Examples of this include using a header with each message to give the types and sizes of the different pieces of data in a message, and to know how many bytes should be received.

Overall, we feel that working in each environment helped us understand the other to a much greater degree, and we look forward to potentially being able to use gRPC in future projects.

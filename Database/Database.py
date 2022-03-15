import socket
from sqlite3 import Timestamp
from threading import Thread
import db_handler
import re

# server's IP address
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 80 # port we want to use
separator_token = "<SEP>" # we will use this to separate the client name & message


# initialize list/set of all connected client's sockets
client_sockets = set()
# create a TCP socket
s = socket.socket()
# make the port as reusable port
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind the socket to the address we specified
s.bind((SERVER_HOST, SERVER_PORT))
# listen for upcoming connections
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

sql_create_chat_logs_table = """CREATE TABLE IF NOT EXISTS chat_logs (
                                            id integer PRIMARY KEY AUTOINCREMENT,
                                            message text NOT NULL,
                                            post_date timestamp NOT NULL
                                            );"""

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])') #used to strip out the ANSI escape characters from user msg

def listen_for_client(cs):
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to all other connected clients
    """
    while True:
        try:
            # keep listening for a message from `cs` socket
            msg = cs.recv(1024).decode()
        except Exception as e:
            # client no longer connected
            # remove it from the set
            print(f"[!] Error: {e}")
            client_sockets.remove(cs)
        else:
            # if we received a message, replace the <SEP> 
            # token with ": " for nice printing
            msg = msg.replace(separator_token, ": ")

            database = db_handler.db_handler_class("actual_database.db")
            database.create_table(sql_create_chat_logs_table)
            print("Adding message")
            split_msg = msg.split("]", 1)
            #split_msg[0] contains the timestamp from the msg with the square brackets stripped off.
            #split_msg[1] has the user
            msg_time = split_msg[0].lstrip(split_msg[0][0]) #not used but might be useful at some point
            msg_payload = split_msg[1].strip()
            msg_string = ansi_escape.sub('', msg_payload)
            print(msg_string)
            database.add_message(msg_string)
            for message in database.retrieve_messages():
                print(message)
        # iterate over all connected sockets
        for client_socket in client_sockets:
            # and send the message
            client_socket.send(msg.encode())


connected = False
while not connected:
    # we keep listening for new connections all the time
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")
    # add the new connected client to connected sockets
    client_sockets.add(client_socket)
    if len(client_sockets) != 0:
        connected = True
    # start a new thread that listens for each client's messages
    t = Thread(target=listen_for_client, args=(client_socket,))
    # make the thread daemon so it ends whenever the main thread ends
    t.daemon = True
    # start the thread
    t.start()
    while connected:
        pass

# close client sockets
for cs in client_sockets:
    cs.close()
# close server socket
s.close()
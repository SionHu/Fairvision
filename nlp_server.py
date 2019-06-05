import comm as comm
import socket
import RedundancyV1
import importlib
import spacy
# import threading  # Possible need to allow multiple connections if Django does not handle them

def process_connection(sock):
    print("processing transmission from client...")
    print("Running Module Reload...")
    importlib.reload(RedundancyV1)
    # receive data from the client
    data = comm.receive_data(sock)
    # do something with the data # TODO: Add link to main redundancy code.
    reducer = RedundancyV1.RedundancyRemover()
    data = reducer.get_reduced_records(*data)  # See CSV file for the format of the data
    print(data)
    # send the result back to the client
    comm.send_data(data, sock)
    # close the socket with this particular client
    sock.close()
    print("finished processing transmission from client...")


server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# open socket even if it was used recently (e.g., server restart)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.bind((comm.server_host, comm.server_port))
# queue up to 5 connections
server_sock.listen(5)

# Start loading neural net down here to minimize the risk of dropped requests
from csgame.nlp_loader import nlp

print("listening on port {}...".format(comm.server_port))
try:
    while True:
        # accept connections from clients
        (client_sock, address) = server_sock.accept()
        # process this connection
        # (this could be launched in a separate thread or process)
        process_connection(client_sock)

except KeyboardInterrupt:
    print("Server process terminated.")
finally:
    server_sock.close()

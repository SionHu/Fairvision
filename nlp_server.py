import comm as comm
import socket
import RedundancyV1
import importlib
# import threading  # Possible need to allow multiple connections if Django does not handle them

def process_connection(sock):
    print("processing transmission from client...")
    print("Running Module Reload...")
    importlib.reload(RedundancyV1)
    # receive data from the client
    data = comm.receive_data(sock)
    # do something with the data # TODO: Add link to main redundancy code.
    reducer = RedundancyV1.RedundancyRemover(nlp)
    data, merges = reducer.get_reduced_records(*data)  # See CSV file for the format of the data
    result = {"data received": data, "merged entries": merges}
    print(result)
    # send the result back to the client
    comm.send_data(result, sock)
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
import spacy
nlp = spacy.load('en_core_web_md')  # Single load in memory till killed

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

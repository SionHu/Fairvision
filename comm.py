import sys
import socket
import struct
import _pickle as pickle  # Depreciated code. # TODO: Try to update to pickle 3.6+
import os


# pick a port that is not used by any other process
server_host = '127.0.0.1'  # localhost

def getPort():
    herokuPort = int(os.getenv('PORT', '17001'))
    choices = range(6379, 6381)#range(3002, 5001)
    forcedPort = 0

    assert herokuPort not in choices
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    main_name = os.path.splitext(os.path.basename(sys.modules['__main__'].__file__))[0]
    # I don't know if binding will always work. The client and server may fight over the space to the port.
    # If so, uncomment the rest of the line.
    force = sock.bind# if main_name == 'nlp_server' else sock.connect
    for forcedPort in choices:
        try:
            force((server_host,forcedPort))
            break
        except IOError:
            pass
    else:
        raise IOError("No port could be forced open.")
    sock.close()

    print("Hosting on port %d." % (forcedPort,))
    return forcedPort

server_port = os.getenv('NLP_PORT') or getPort()
message_size = 8192
# code to use with struct.pack to convert transmission size (int)
# to a byte string
header_pack_code = '>I'
# number of bytes used to represent size of each transmission
# (corresponds to header_pack_code)
header_size = 4


def send_data(data_object, sock):
    # serialize the data so it can be sent through a socket
    data_string = pickle.dumps(data_object, -1)
    data_len = len(data_string)
    # send a header showing the length, packed into 4 bytes
    sock.sendall(struct.pack(header_pack_code, data_len))
    # send the data
    sock.sendall(data_string)


def receive_data(sock):
    """ Receive a transmission via a socket, and convert it back into a binary object. """
    # This runs as a loop because the message may be broken into arbitrary-size chunks.
    # This assumes each transmission starts with a 4-byte binary header showing the size of the transmission.
    # See https://docs.python.org/3/howto/sockets.html
    # and http://code.activestate.com/recipes/408859-socketrecv-three-ways-to-turn-it-into-recvall/

    header_data = b''
    header_done = False
    # set dummy values to start the loop
    received_len = 0
    transmission_size = sys.maxsize  # Updated to python 3 + value. May cause an error ?

    while received_len < transmission_size:
        sock_data = sock.recv(message_size)  # Modified load data

        if not header_done:
            # still receiving header info
            header_data += sock_data
            if len(header_data) >= header_size:
                header_done = True
                # split the already-received data between header and body
                messages = [header_data[header_size:]]
                received_len = len(messages[0])
                header_data = header_data[:header_size]
                # find actual size of transmission
                transmission_size = struct.unpack(header_pack_code, header_data)[0]
        else:
            # already receiving data
            received_len += len(sock_data)
            messages.append(sock_data)

    # combine messages into a single string
    data_string = b''.join(messages)
    # convert to an object
    data_object = pickle.loads(data_string)
    return data_object

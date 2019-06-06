"""
Client code for server setup for nlp.
Script will connect to the server that we setup to reduce the nlp time stuff.
"""

import socket
import comm as comm
import csv


def send__receive_data(new_Qs, old_Qs):
    """
    Method to send the data to the server and get the result from it.
    :param new_Qs: The new questions with IDs that need to be compared.
    :param old_Qs: The old questions with IDs already in the database. Should be all dissimilar.
    :return: new data returned by the server, which is in return data given by algorithm
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
    sock.connect((comm.server_host, comm.server_port))
    comm.send_data((new_Qs, old_Qs), sock)
    print("Sent Data Successfully.")
    result = comm.receive_data(sock)
    print("Received Data Successfully")
    sock.close()

    # do something with the result...
    #print("result from server:")
    #for row_rec in result[0]:
    #    print(row_rec)
    return result

if __name__ == "__main__":
    old = []
    new = []
    with open('Q & A - Haobo.csv') as test_att_csv:
        csv_reader = csv.reader(test_att_csv, delimiter=',')
        for row in csv_reader:
            old.append(row)
    with open('test_att.csv') as turdy:
        csv_reader = csv.reader(turdy, delimiter=',')
        for row in csv_reader:
            new.append(row)
    try:
        print(send__receive_data(new, old))


    except ConnectionRefusedError:
        print("CHECK IF SERVER IS RUNNING !!")

    print("Run complete")


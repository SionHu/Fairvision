<<<<<<< HEAD
"""
Client code for server setup for nlp.
Script will connect to the server that we setup to reduce the nlp time stuff.
"""

import socket
import comm as comm
import csv
import requests


def send__receive_data_old(new_Qs, old_Qs):
    """
    Method to send the data to the server and get the result from it.
    :param new_Qs: The new questions with IDs that need to be compared.
    :param old_Qs: The old questions with IDs already in the database. Should be all dissimilar.
    :return: new data returned by the server, which is in return data given by algorithm
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
    sock.connect((comm.server_host, comm.server_port))
    print("create a socket Successfully")

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

def send__receive_data(new_Qs, old_Qs):
    stuff_to_give = {"new_ques": new_Qs, "old_ques": old_Qs}

    res = requests.post('https://nlp-hosty.appspot.com/receive', json=stuff_to_give, verify=False)
    if res.ok:
       return res.json()
    else:
       print(res.reason)

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
=======
"""
Client code for server setup for nlp.
Script will connect to the server that we setup to reduce the nlp time stuff.
"""

import socket
import comm as comm
import csv
import requests


def send__receive_data(new_Qs, old_Qs):
    stuff_to_give = {"new_ques": new_Qs, "old_ques": old_Qs}

    print("before the server host")
    res = requests.post('https://nlp-hosted.herokuapp.com/receive', json=stuff_to_give, verify=False)
    print("AFTER the server host")

    if res.ok:
       return res.json()
    else:
       print(res.reason)

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
>>>>>>> 2faf8d79d31808870b78a172b993d5b418471289

#!/usr/bin/env python
"""
Client code for server setup for nlp.
Script will connect to the server that we setup to reduce the nlp time stuff.
"""

import csv
import requests

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

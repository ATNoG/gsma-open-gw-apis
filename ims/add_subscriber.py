#!/usr/bin/env python3

import sys
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument("imsi")
parser.add_argument("msisdn")

parser.add_argument("-u", "--url", default="http://localhost:8080")
parser.add_argument("-d", "--domain", default="ims.mnc003.mcc999.3gppnetwork.org")

args = parser.parse_args()

ki = input("ki: ")
opc = input("opc: ")

res = requests.get(f"{args.url}/apn/1")

if res.status_code == 200:
    if res.json() != None:
        print("APN already exists")
    else:
        print("APN doesn't exist, creating")

        res = requests.put(
            f"{args.url}/apn",
            json={"apn": "ims", "apn_ambr_dl": 0, "apn_ambr_ul": 0},
        )

        if res.status_code != 200:
            print(res.text)
            print("Failed to create APN")
            sys.exit(1)
else:
    print(res.text)
    print("Failed to fetch APN")
    sys.exit(1)

res = requests.put(
    f"{args.url}/auc",
    json={"ki": ki, "opc": opc, "amf": "9001", "sqn": 0, "imsi": args.imsi},
)

if res.status_code != 200:
    print(res.text)
    print("Failed to create AuC")
    sys.exit(1)

print("AuC created succefully")

auc_id = res.json()["auc_id"]

res = requests.put(
    f"{args.url}/subscriber",
    json={
        "imsi": args.imsi,
        "enabled": True,
        "auc_id": auc_id,
        "msisdn": args.msisdn,
        "ue_ambr_dl": 0,
        "ue_ambr_ul": 0,
        "default_apn": 1,
        "apn_list": "1",
    },
)

if res.status_code != 200:
    print(res.text)
    print("Failed to create subscriber")
    sys.exit(1)

print("Subscriber created succefully")

res = requests.put(
    f"{args.url}/ims_subscriber",
    json={
        "imsi": args.imsi,
        "msisdn": args.msisdn,
        "sh_profile": "string",
        "scscf_peer": f"scscf.{args.domain}",
        "msisdn_list": f"[{args.msisdn}]",
        "ifc_path": "default_ifc.xml",
        "scscf": f"sip:scscf.{args.domain}:6060",
        "scscf_realm": args.domain,
    },
)

if res.status_code != 200:
    print(res.text)
    print("Failed to create IMS subscriber")
    sys.exit(1)

print("IMS subscriber created succefully")

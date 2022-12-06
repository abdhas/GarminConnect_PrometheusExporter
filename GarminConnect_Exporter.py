#!/usr/bin/env python3
import datetime
import time
import json
from prometheus_client import start_http_server, Summary
import random
from prometheus_client import Gauge, CollectorRegistry
import datetime
import json
import logging
import os
import sys
import requests
import pwinput
import readchar

g = Gauge('Heart_Rate', 'heart_rate', ['timestamp'])
today = datetime.date.today()

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)


def return_json(api_call, output):
    """Format API output for better readability."""

    dashed = "-"*20
    header = f"{dashed} {api_call} {dashed}"
    footer = "-"*len(header)

    #print(header)
    return ("["+json.dumps(output, indent=4)+"]")
    #print(footer)

def init_api(email, password):
    """Initialize Garmin API with your credentials."""

    try:
        ## Try to load the previous session
        with open("session.json") as f:
            saved_session = json.load(f)

            print(
                "Login to Garmin Connect using session loaded from 'session.json'...\n"
            )

            # Use the loaded session for initializing the API (without need for credentials)
            api = Garmin(session_data=saved_session)

            # Login using the
            api.login()

    except (FileNotFoundError, GarminConnectAuthenticationError):
        # Login to Garmin Connect portal with credentials since session is invalid or not present.
        print(
            "Session file not present or turned invalid, login with your Garmin Connect credentials.\n"
            "NOTE: Credentials will not be stored, the session cookies will be stored in 'session.json' for future use.\n"
        )
        try:
            api = Garmin(email, password)
            api.login()

            # Save session dictionary to json file for future use
            with open("session.json", "w", encoding="utf-8") as f:
                json.dump(api.session_data, f, ensure_ascii=False, indent=4)
        except (
                GarminConnectConnectionError,
                GarminConnectAuthenticationError,
                GarminConnectTooManyRequestsError,
                requests.exceptions.HTTPError,
        ) as err:
            print("Error occurred during Garmin Connect communication: %s", err)
            return None
    return api

# Main program loop
if __name__ == '__main__':
    # Display header and login
    start_http_server(9100)
    api = init_api("USERNAME", "PASSWORD")
    while True:
        garmin_json = str(return_json(f"api.get_heart_rates('{today.isoformat()}')", api.get_heart_rates(today.isoformat())))
        y = json.loads(garmin_json.replace("None", "" ))
        #print(y)
        #print (len(y[0]['heartRateValues']))

        for x in range(len(y[0]['heartRateValues'])):
            timestamp = str(y[0]['heartRateValues'][x][0])
            dt = str(datetime.datetime.fromtimestamp(int(timestamp) / 1000.0, tz=datetime.timezone.utc))
            heart_rate = str(y[0]['heartRateValues'][x][1])
            #print (timestamp + " " + heart_rate )
            if heart_rate != "None":
                print (dt + " " + heart_rate )
                g.labels(dt).set(float(heart_rate))

        print ("Job complete.")
        print ("Sleeping for 12 hours.")
        time.sleep(43200)



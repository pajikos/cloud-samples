import json
import datetime
import logging
from urllib.request import urlopen
import azure.functions as func
import os

def read_api():
    base_url = os.environ["BASE_URL"]
    system_a_url = f"{base_url}/api/system-a"
    logging.info(f"Trying to open url {system_a_url}")
    response = urlopen(system_a_url, timeout=5)
    # storing the JSON response 
    # from url in data
    data_json = json.loads(response.read())
    return data_json

def main(mytimer: func.TimerRequest, msgOut: func.Out[str]):
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info('The timer is past due!')
        return
    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    try:
        outdata = read_api()
        data = json.dumps(outdata)
        logging.info(f'Processed Service Bus Queue message: {data}')
        msgOut.set(data)
    except Exception as e:
        logging.error('Error:')
        logging.error(e)
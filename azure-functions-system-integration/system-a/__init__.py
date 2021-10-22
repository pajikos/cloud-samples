import logging

import azure.functions as func
import json
import random
import names

def gen_phone():
    first = str(random.randint(100,999))
    second = str(random.randint(100,999))

    last = str(random.randint(100,999))

    return '{} {} {}'.format(first, second, last)

CITIES = ["Praha", "Brno", "Olomouc"]
STREETS = ["Horni", "Dolni", "Zadni", "Predni"]
STATES = ["NEW", "UPDATED", "DELETED"]



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    response = {
        "rollno" : 56,
        "cgpa" : 8.6,
        "phonenumber" : gen_phone(),
        "address_line1": f"{random.choice(STREETS)} {str(random.randint(1,999))}",
        "address_line2": f"{random.choice(CITIES)}/{str(random.randint(100,999))} {str(random.randint(10,99))}"
    }
    response["state"] = random.choice(STATES)
    response["first_name"] = names.get_first_name()
    response["last_name"] = names.get_last_name()
    
    return func.HttpResponse(json.dumps(response, indent = 4) )



    

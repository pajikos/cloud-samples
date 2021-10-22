import logging

import azure.functions as func
import requests
import json
import os

def map(data, mappings):
    new_dict = data.copy()
    if mappings:
        mapping = json.loads(mappings[0].to_json())
        if "new_fields" in mapping:
            for new_field_def in mapping["new_fields"]:
                if new_field_def["operation"] == "CONCAT":
                    new_field_content = new_field_def["separator"].join([new_dict[new_field_def["input_fields"][0]], new_dict[new_field_def["input_fields"][1]]])
                    new_dict[new_field_def["output_fields"][0]] = new_field_content
                if new_field_def["operation"] == "SPLIT":
                    new_field_content = new_dict[new_field_def["input_fields"][0]].split(new_field_def["separator"])
                    new_dict[new_field_def["output_fields"][0]] = new_field_content[0]
                    new_dict[new_field_def["output_fields"][1]] = new_field_content[1]
            for delete_field in mapping["delete_fields"]:
                new_dict.pop(delete_field, None)
    else:
        logging.error(f"Missing mapping for message {data}")

    return new_dict

def main(message: func.ServiceBusMessage, mappings: func.DocumentList):
    logging.info("Python ServiceBus topic trigger processed message.")
    message_body = message.get_body().decode("utf-8")
    base_url = os.environ["BASE_URL"]
    logging.debug(f"Message Content Type: {message.content_type}")
    logging.info(f"Message received from bus: {message_body}")
    data = json.loads(message_body)
    system_b_url = f"{base_url}/api/system-b"
    if "state" in data and data["state"] == "NEW":
        data = map(data, mappings=mappings)
        response = requests.post(system_b_url, json=data, timeout=5)
        logging.info(f"Send message to {system_b_url} with response {response.content}")
    else:
        logging.info(f"Skipping message {data} due to state is not NEW")
    
        
    
    


    
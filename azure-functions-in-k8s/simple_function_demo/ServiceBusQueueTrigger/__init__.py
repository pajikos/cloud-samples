import logging

import azure.functions as func


def main(msg: func.ServiceBusMessage):
    logging.warn('Python ServiceBus queue trigger processed message: %s',
                 msg.get_body().decode('utf-8'))

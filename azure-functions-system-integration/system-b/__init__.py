import logging

import azure.functions as func


def main(req: func.HttpRequest, doc: func.Out[func.Document]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        doc.set(func.Document.from_json(req.get_body()))
        logging.info(f"System B: Document saved {req.get_json()}")
        return func.HttpResponse(
            "OK",
            status_code=200
        )
    except Exception as e:
        logging.error('Error:')
        logging.error(e)
        return func.HttpResponse(
            "Error in data",
            status_code=500
        )

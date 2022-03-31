import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage

# CONNECTION_STR = "Endpoint=sb://xxx.servicebus.windows.net/;SharedAccessKeyName=func-demo;SharedAccessKey=xxxxx;"
CONNECTION_STR = os.getenv('ServiceBusConnectionString')
QUEUE_NAME = "queue-input"

def send_single_message(sender):
    message = ServiceBusMessage("Single Message")
    sender.send_messages(message)
    print("Sent a single message")

def send_a_list_of_messages(sender):
    messages = [ServiceBusMessage("Message in list") for _ in range(100)]
    sender.send_messages(messages)
    print("Sent a list of 100 messages")

def send_batch_message(sender):
    batch_message = sender.create_message_batch()
    for _ in range(100):
        try:
            batch_message.add_message(ServiceBusMessage("Message inside a ServiceBusMessageBatch"))
        except ValueError:
            # ServiceBusMessageBatch object reaches max_size.
            # New ServiceBusMessageBatch object can be created here to send more data.
            break
    sender.send_messages(batch_message)
    print("Sent a batch of 100 messages")

servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)

with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    with sender:
        # send_single_message(sender)
        send_a_list_of_messages(sender)
        send_batch_message(sender)

print("Done sending messages")
print("-----------------------")

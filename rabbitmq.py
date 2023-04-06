import json
import logging
import os
from enum import Enum

import pika

from utils import db_models


class Queues(Enum):
    AdminMessages = "admin_messages"
    ErrorMessages = "error_messages"
    EmailNotifications = "email_notifications"


class MQMessage:
    def __init__(self, message: str):
        self.message = message
        self.queue = Queues.ErrorMessages

    def send(self):
        with RabbitMQConn() as connection:
            channel = connection.channel()
            channel.basic_publish(exchange='',
                                  routing_key=self.queue.value,
                                  body=self.message.encode("utf-8"))
            logging.info(f"Sent message: {self.message} to {self.queue.value}")


class AdminMessage(MQMessage):
    def __init__(self, message: str):
        super().__init__(message)
        self.queue = Queues.AdminMessages


class EmailNotification(MQMessage):
    def __init__(self, subject: str, message: str, team: db_models.Team):
        msg = f"""Sehr geehrtes Team "{team.name}",
        
{message}
        
Mit freundlichen Grüßen,
das airLAN Team
        """

        msg_struct: dict = {
            "email": team.account.username,
            "subject": subject,
            "message": msg
        }

        super().__init__(json.dumps(msg_struct))
        self.queue = Queues.EmailNotifications


class ErrorMessage(MQMessage):
    def __init__(self, message: str):
        super().__init__(message)
        self.queue = Queues.ErrorMessages


class RabbitMQConn:
    def __init__(self):
        credentials = pika.PlainCredentials(os.getenv("RABBITMQ_USER", "guest"),
                                            os.getenv("RABBITMQ_PASSWORD", "guest"))
        self.rabbit_mq_connection_params = pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
                                                                     port=int(os.getenv("RABBITMQ_PORT", "5672")),
                                                                     credentials=credentials)
        self.connection = pika.BlockingConnection(self.rabbit_mq_connection_params)

    def __enter__(self):
        return self.connection

    def __exit__(self, exception_type, exception_value, traceback):
        self.connection.close()


def declare_queues() -> dict:
    res = {}
    with RabbitMQConn() as connection:
        channel = connection.channel()
        for queue in Queues:
            res[queue.value] = channel.queue_declare(queue=queue.value, durable=True)

    logging.info("Done declaring queues")
    return res

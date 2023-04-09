import base64
import datetime
import json
import logging
import os
from enum import Enum
from typing import Union

import pika

from utils import db_models


class Queues(Enum):
    AdminMessages = os.getenv("RABBITMQ_Q_ADMIN_MESSAGES", "admin_messages")
    ErrorMessages = os.getenv("RABBITMQ_Q_ERROR_MESSAGES", "error_messages")
    EmailNotifications = os.getenv("RABBITMQ_Q_EMAIL_NOTIFICATIONS", "email_notifications")


class MQMessage:
    def __init__(self, message: str):
        self.message = message
        self.queue = Queues.ErrorMessages

    def send(self):
        if self.message == "":
            logging.error("Tried to send empty message")
            return

        declare_queues()
        with RabbitMQConn() as connection:
            channel = connection.channel()
            channel.basic_publish(exchange='',
                                  routing_key=self.queue.value,
                                  body=self.message.encode("utf-8"))
            logging.info(f"Sent message: {self.message} to {self.queue.value}")


class EmailNotification(MQMessage):
    def __init__(self):
        super().__init__("")
        self.queue = Queues.EmailNotifications

    def team_message(self, subject: str, message: str, team: db_models.Team):
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
        return self

    def manual_message(self, subject: str, message: str, email: str):
        msg_struct: dict = {
            "email": email,
            "subject": subject,
            "message": message
        }

        super().__init__(json.dumps(msg_struct))
        self.queue = Queues.EmailNotifications
        return self


class AdminMessage(MQMessage):
    def __init__(self, message: str):
        logging.info(f"Admin Message: {message}")

        msg: dict = {
            "message": message,
            "timestamp": str(datetime.datetime.now())
        }

        super().__init__(json.dumps(msg))
        self.queue = Queues.AdminMessages


class ErrorMessage(MQMessage):
    def __init__(self, message: str, json_data: Union[None, dict] = None):
        logging.error(f"Error: {message} - {json_data}")

        msg: dict = {
            "message": message,
            "timestamp": str(datetime.datetime.now())
        }

        if json_data is not None:
            msg["json"] = base64.b64encode(json.dumps(json_data, indent=4, ensure_ascii=False).encode()).decode()

        super().__init__(json.dumps(msg))
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
            res[queue.value] = channel.queue_declare(queue=queue.value, durable=True,
                                                     arguments={"x-queue-type": "quorum"})

    return res

"""
Script to create the pewee models from the database.

Run like: python3 create_models.py
Prompt for password and enter it.
Output: db_models.py
"""
import os

peewee_injection = """
from contextvars import ContextVar
from peewee import *

import os
import peewee

db_state_default = {"closed": None, "conn": None, "ctx": None, "transactions": None}
db_state = ContextVar("db_state", default=db_state_default.copy())


class PeeweeConnectionState(peewee._ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__("_state", db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]


database = PostgresqlDatabase(os.getenv('POSTGRES_DB', 'postgres'),
                              **{'host': os.getenv('POSTGRES_DB_HOST', 'db'),
                                 'port': int(os.getenv('POSTGRES_DB_PORT', '5432')),
                                 'user': os.getenv('POSTGRES_USER', 'postgres'),
                                 'password': os.getenv('POSTGRES_PASSWORD', 'pass')})
database._state = PeeweeConnectionState()
"""

if __name__ == '__main__':
    os.system("python3 -m pwiz -e postgresql -u postgres -p 5432 -H 127.0.0.1 -P postgres > db_models.py")

    lines = peewee_injection.split("\n")
    with open("db_models.py", "r") as f:
        lines.extend(f.readlines())

    for i in range(0, len(lines)):
        if "database = PostgresqlDatabase('p" in lines[i]:
            lines[i] = ""
        if "from peewee import *" in lines[i] and "from peewee import *" in lines[0:i]:
            lines[i] = ""

    with open("db_models.py", "w") as f:
        f.write("\n".join(lines))

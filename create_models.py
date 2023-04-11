#!/usr/bin/env python3
"""
Script to create the pewee models from the database.

Run like: python3 create_models.py
Prompt for password and enter it.
Output: db_models.py
"""
import os

if __name__ == '__main__':
    os.system("python3 -m pwiz -e postgresql -u postgres -p 5432 -H 127.0.0.1 -P postgres > db_models.py")

    lines = ["import os", "from playhouse.pool import PooledPostgresqlExtDatabase"]
    with open("db_models.py", "r") as f:
        lines.extend(f.readlines())

    for i in range(0, len(lines)):
        if "database = PostgresqlDatabase('p" in lines[i]:
            lines[
                i] = "database = PooledPostgresqlExtDatabase(os.getenv('POSTGRES_DB', 'postgres'), max_connections=int(os.getenv('POSTGRES_DB_POOL_CONNS', '2')), stale_timeout=300, **{'host': os.getenv('POSTGRES_DB_HOST', 'db'), 'port': int(os.getenv('POSTGRES_DB_PORT', '5432')), 'user': os.getenv('POSTGRES_USER', 'postgres'), 'password': os.getenv('POSTGRES_PASSWORD', 'pass')})"

    with open("db_models.py", "w") as f:
        f.write("\n".join(lines))

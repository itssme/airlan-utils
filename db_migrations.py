import os

from yoyo import read_migrations
from yoyo import get_backend


def apply_migrations():
    backend = get_backend(
        f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'pass')}@{os.getenv('POSTGRES_DB_HOST', 'db')}:{int(os.getenv('POSTGRES_DB_PORT', '5432'))}/{os.getenv('POSTGRES_DB', 'postgres')}")
    migrations = read_migrations("/app/utils/postgres/migrations")

    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))

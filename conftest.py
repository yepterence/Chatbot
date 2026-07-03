import os

# Provide dummy DB env vars before any api.* module is imported.
# database.py instantiates Settings() at module level to build the engine URL;
# without these vars, pydantic-settings raises a ValidationError during collection
# even for tests that never touch the database.
os.environ.setdefault("db_user", "test")
os.environ.setdefault("db_pass", "test")
os.environ.setdefault("db_name", "test")
os.environ.setdefault("db_host", "localhost")
os.environ.setdefault("db_port", "5432")

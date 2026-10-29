import os

# Every path is relative to this folder, not to the working directory, so the app can be started from anywhere
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))

# Environment variable with the path of the database, to use another one than the default
DB_PATH_ENV = 'ACCOUNTANCY_DB'

def config_path(*parts):
    return os.path.join(CONFIG_DIR, *parts)

def db_path():
    return os.path.abspath(os.path.expanduser(os.environ.get(DB_PATH_ENV) or config_path('db', 'accountancy.db')))

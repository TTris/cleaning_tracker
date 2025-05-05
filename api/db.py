import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_conn():
    return psycopg2.connect(os.getenv("SUPABASE_DB_URL"))

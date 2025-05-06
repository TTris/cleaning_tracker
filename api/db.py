import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_conn():
    return psycopg2.connect(os.getenv("SUPABASE_DB_URL"))


# # try to Connect to the database
# try:
#     connection = get_db_conn()
#     print("Connection successful!")
    
#     # Create a cursor to execute SQL queries
#     cursor = connection.cursor()
    
#     # Example query
#     cursor.execute("SELECT NOW();")
#     result = cursor.fetchone()
#     print("Current Time:", result)

#     # Close the cursor and connection
#     cursor.close()
#     connection.close()
#     print("Connection closed.")

# except Exception as e:
#     print(f"Failed to connect: {e}")


# # create tables 
# create_locations_table = """
# CREATE TABLE IF NOT EXISTS locations(
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
#     name TEXT NOT NULL,
#     created_at TIMESTAMPTZ DEFAULT timezone('utc', now())
# );
# """

# create_records_table = """
# CREATE TABLE IF NOT EXISTS records(
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
#     location_id UUID NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
#     date DATE NOT NULL,
#     cleaned BOOLEAN DEFAULT false,
#     created_at TIMESTAMPTZ DEFAULT timezone('utc', now())
# );
# """

# try:
#     conn = get_db_conn()
#     cur = conn.cursor()

#     cur.execute(create_locations_table)
#     cur.execute(create_records_table)

#     conn.commit()
#     cur.close()
#     conn.close()
#     print("資料表建立成功！")

# except Exception as e:
#     print("建立資料表失敗：", e)
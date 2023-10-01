from utils.data import get_trajectories_df, get_user_ids

from DbConnector import DbConnector
from tabulate import tabulate

connection = DbConnector()
cursor = connection.cursor
db_connection = connection.db_connection

# Using "UserTable" as the table name
table_name = "UserTable"

query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
        id VARCHAR(3),
        has_label TINYINT(1)
    )
"""

cursor.execute(query)
db_connection.commit()

print(f"{table_name} Contents")
cursor.execute(f"SELECT * FROM {table_name}")
rows = cursor.fetchall()
print(tabulate(rows, headers=cursor.column_names))

print("getuserfunction")
for user in get_user_ids():
    print(user)

connection.close_connection()

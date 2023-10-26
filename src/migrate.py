from bson import ObjectId
from pymongo import MongoClient
from tqdm import tqdm
from utils.data import (
    get_trajectories_df,
    get_user_ids,
    get_labeled_ids,
    get_activities_df,
)
from utils.connection import DbConnector
from datetime import datetime


def create_user_collection(client: MongoClient, db):
    """
    Creates 'UserCollection' with two attributes:
    - 'id' (string)
    - 'has_label' (boolean)

    """

    # Create table
    collection_name = "UserCollection"

    collection = db.create_collection(collection_name)

    # Insert data
    docs = []

    for user in get_user_ids():
        entry = {
            "_id": user,
            "activities": get_activities_df(user)["id"].to_list(),
        }
        if user in get_labeled_ids():
            entry["has_label"] = 1
        else:
            entry["has_label"] = 0

        docs.append(entry)

    collection.insert_many(docs)

    print("Created collection: \n", collection)


def create_activity_collection(client: MongoClient, db):
    """
    Creates 'ActivityTable' SQL table with the following columns:
    - 'id' (INT AUTO_INCREMENT NOT NULL PRIMARY KEY)
    - 'user_id' (VARCHAR(255) NOT NULL FOREIGN KEY)
    - 'start_date_time' (DATETIME)
    - 'end_date_time' (DATETIME)
    - 'transportation_mode' (VARCHAR(20))
    """

    # Create table
    collection_name = "ActivityCollection"

    collection = db.create_collection(collection_name)

    # query = f"""
    # CREATE TABLE IF NOT EXISTS {table_name} (
    #         id INT AUTO_INCREMENT NOT NULL,
    #         user_id VARCHAR(255) NOT NULL,
    #         start_date_time DATETIME,
    #         end_date_time DATETIME,
    #         transportation_mode VARCHAR(20),
    #         FOREIGN KEY (user_id) REFERENCES UserTable(id),
    #         PRIMARY KEY (id)
    #     )
    # """

    # cursor.execute(query)
    # db_connection.commit()

    # Insert data
    user_ids = get_user_ids()

    pbar = tqdm(user_ids)

    for user in pbar:
        docs = []

        activities_df = get_activities_df(user)

        pbar.set_description("Processing TrackPoints of user %s" % user)
        print()
        trajectories_df = get_trajectories_df(user)

        for _, row in activities_df.iterrows():
            entry = {
                "_id": row["id"],
                "user": row["user_id"],
                "start_date_time": row["start_date_time"],
                "end_date_time": row["end_date_time"],
                "transportation_mode": row["transportation_mode"],
                "track_points": trajectories_df[
                    trajectories_df["activity_id"] == row["id"]
                ][["latitude", "longitude", "altitude", "date_time"]].to_dict(
                    "records"
                ),
            }
            docs.append(entry)

        if len(docs) == 0:
            continue

        pbar.set_description("Migrating TrackPoints of user %s" % user)
        collection.insert_many(docs)

    print("Created collection: \n", collection)


# def create_track_point_table(client: MongoClient, db: Database):
#     """
#     Creates 'TrackPointTable' SQL table with the following columns:
#     - 'id' (INT AUTO_INCREMENT NOT NULL PRIMARY KEY)
#     - 'activity_id' (INT NOT NULL FOREIGN KEY)
#     - 'lat' (FLOAT)
#     - 'lon' (FLOAT)
#     - 'altitude' (FLOAT)
#     - 'date_time' (DATETIME)
#     """

#     # Create table
#     table_name = "TrackPointTable"

#     query = f"""
#     CREATE TABLE IF NOT EXISTS {table_name} (
#             id INT AUTO_INCREMENT NOT NULL,
#             activity_id INT NOT NULL,
#             lat FLOAT,
#             lon FLOAT,
#             altitude FLOAT,
#             date_time DATETIME,
#             FOREIGN KEY (activity_id) REFERENCES ActivityTable(id),
#             PRIMARY KEY (id)
#         )
#     """

#     cursor.execute(query)
#     db_connection.commit()

#     # Insert data
#     user_ids = get_user_ids()

#     pbar = tqdm(user_ids)
#     for user in pbar:
#         pbar.set_description("Processing TrackPoints of user %s" % user)
#         trajectories_df = get_trajectories_df(user)
#         data_to_insert = []

#         pbar.set_description("Appending TrackPoints of user %s" % user)
#         for _, row in trajectories_df.iterrows():
#             data_to_insert.append(
#                 (
#                     row["activity_id"],
#                     row["latitude"],
#                     row["longitude"],
#                     row["altitude"],
#                     row["date_time"].strftime("%Y-%m-%d %H:%M:%S"),
#                 )
#             )

#         pbar.set_description("Migrating TrackPoints of user %s" % user)

#         insert_query = f"""
#             INSERT INTO {table_name} (activity_id, lat, lon, altitude, date_time)
#             VALUES (%s, %s, %s, %s, %s)
#         """
#         cursor.executemany(insert_query, data_to_insert)
#         db_connection.commit()


# def create_track_point_table_spatial(client: MongoClient, db: Database):
#     """
#     Creates 'TrackPointTable' SQL table with the following columns:
#     - 'id' (INT AUTO_INCREMENT NOT NULL PRIMARY KEY)
#     - 'activity_id' (INT NOT NULL FOREIGN KEY)
#     - 'lat' (FLOAT)
#     - 'lon' (FLOAT)
#     - 'altitude' (FLOAT)
#     - 'date_time' (DATETIME)
#     - 'geom_point' (POINT, a spatial column to store the lon, lat values)
#     """

#     # Create table
#     table_name = "TrackPointTable"

#     query = f"""
#     CREATE TABLE IF NOT EXISTS {table_name} (
#             id INT AUTO_INCREMENT NOT NULL,
#             activity_id INT NOT NULL,
#             lat FLOAT,
#             lon FLOAT,
#             altitude FLOAT,
#             date_time DATETIME,
#             geom_point POINT NOT NULL,
#             FOREIGN KEY (activity_id) REFERENCES ActivityTable(id),
#             PRIMARY KEY (id)
#         )
#     """

#     cursor.execute(query)

#     # Add spatial index
#     index_query = f"ALTER TABLE {table_name} ADD SPATIAL INDEX(geom_point)"
#     cursor.execute(index_query)

#     db_connection.commit()

#     # Insert data
#     user_ids = get_user_ids()

#     pbar = tqdm(user_ids)
#     for user in pbar:
#         pbar.set_description("Processing TrackPoints of user %s" % user)
#         trajectories_df = get_trajectories_df(user)
#         data_to_insert = []

#         pbar.set_description("Appending TrackPoints of user %s" % user)
#         for _, row in trajectories_df.iterrows():
#             data_to_insert.append(
#                 (
#                     row["activity_id"],
#                     row["latitude"],
#                     row["longitude"],
#                     row["altitude"],
#                     row["date_time"],
#                     row["longitude"],
#                     row["latitude"],
#                 )
#             )

#         pbar.set_description("Migrating TrackPoints of user %s" % user)

#         insert_query = f"""
#             INSERT INTO {table_name} (activity_id, lat, lon, altitude, date_time, geom_point)
#             VALUES (%s, %s, %s, %s, %s, POINT(%s, %s))
#         """
#         cursor.executemany(insert_query, data_to_insert)
#         db_connection.commit()


def drop_tables(client: MongoClient, db):
    """
    Drops the specified tables from the database.
    """

    db["UserCollection"].drop()
    db["ActivityCollection"].drop()

    print("Tables dropped successfully.")


def migrate():
    print("Migrating...")

    connection = DbConnector()
    client = connection.client
    db = connection.db

    drop_tables(client, db)

    create_user_collection(client, db)
    create_activity_collection(client, db)
    # create_track_point_table(cursor, db_connection)

    # Close connection
    connection.close_connection()


if __name__ == "__main__":
    migrate()

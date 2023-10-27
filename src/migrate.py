from bson import ObjectId
from pymongo import MongoClient
from pymongo.database import Database
from tqdm import tqdm
from utils.data import (
    get_trajectories_df,
    get_user_ids,
    get_labeled_ids,
    get_activities_df,
)
from utils.connection import DbConnector
from datetime import datetime


def create_user_collection(client: MongoClient, db: Database):
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
            "activities": [
                ObjectId(f"{id:024x}") for id in get_activities_df(user)["id"].to_list()
            ],
        }
        if user in get_labeled_ids():
            entry["has_label"] = 1
        else:
            entry["has_label"] = 0

        docs.append(entry)

    collection.insert_many(docs)

    print("Created collection: \n", collection)


def create_activity_collection(client: MongoClient, db: Database):
    """
    Creates 'ActivityCollection' with five attributes:
    - 'id' (string)
    - 'user' (string)
    - 'start_date_time' (datetime)
    - 'end_date_time' (datetime)
    - 'transportation_mode' (string)
    - 'track_points' (list of dicts)

    """

    # Create table
    collection_name = "ActivityCollection"

    collection = db.create_collection(collection_name)

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
            if trajectories_df[trajectories_df["activity_id"] == row["id"]].empty:
                continue

            entry = {
                "_id": ObjectId(f'{row["id"]:024x}'),
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


def drop_tables(client: MongoClient, db: Database):
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

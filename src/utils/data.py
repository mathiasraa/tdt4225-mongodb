import pandas as pd
import numpy as np
from numpy import loadtxt
import warnings
import os

warnings.simplefilter(action="ignore", category=FutureWarning)

dir_path = os.path.dirname(os.path.realpath(__file__))
data_path = dir_path + "/../../data/Data"
data = []


def get_user_ids():
    """Returns a list of the user ids

    Returns:
        list[str]
    """

    return [f.name for f in os.scandir(data_path) if f.is_dir()]


def get_labeled_ids():
    """Returns a list of the user ids that have labeled activities

    Returns:
        list[str]
    """

    lines = loadtxt(f"{dir_path}/../../data/labeled_ids.txt", dtype=str)

    return list(lines)


def get_activities_df(user_id: str):
    """Returns a DataFrame of the activities of a user_id

    Arguments:
        user_id {string} -- The id of the user

    Returns:
        DataFrame
    """

    # Create an empty DataFrame to store the activities
    activities = pd.DataFrame(
        columns=[
            "start_date_time",
            "end_date_time",
            "transportation_mode",
            "user_id",
            "id",
        ]
    )

    # Check if the user has labeled activities
    if user_id in get_labeled_ids():
        # Read the labels.txt file into a DataFrame
        activities[
            ["start_date_time", "end_date_time", "transportation_mode"]
        ] = loadtxt(
            f"{data_path}/{user_id}/labels.txt",
            skiprows=1,
            delimiter="\t",
            dtype=str,
        )

        # Clean columns
        activities["user_id"] = user_id
        activities["start_date_time"] = pd.to_datetime(
            activities["start_date_time"], format="%Y/%m/%d %H:%M:%S"
        )
        activities["end_date_time"] = pd.to_datetime(
            activities["end_date_time"], format="%Y/%m/%d %H:%M:%S"
        )
        activities.reset_index(drop=True, inplace=True)
        activities["id"] = ("1" + activities.index.astype(str) + user_id + "1").astype(
            int
        )
        return activities
    else:  # If the user has no labeled activities, use trajectory file as activity
        rows_list = []

        for _, _, files in os.walk(f"{data_path}/{user_id}/Trajectory"):
            # Loop through the files in the Trajectory folder
            for index, name in enumerate(files):
                trajectory = pd.read_csv(
                    f"{data_path}/{user_id}/Trajectory/{name}",
                    names=[
                        "latitude",
                        "longitude",
                        "_",
                        "altitude",
                        "days",
                        "date",
                        "time",
                    ],
                    sep=",",
                    encoding="ISO-8859-1",
                    skiprows=6,
                )
                if trajectory.shape[0] > 2500:
                    continue

                trajectory["date_time"] = pd.to_datetime(
                    trajectory["date"] + " " + trajectory["time"],
                    format="%Y-%m-%d %H:%M:%S",
                )

                start_time = trajectory["date_time"].min()
                end_time = trajectory["date_time"].max()
                id = int("1" + str(index) + user_id + "1")

                rows_list.append([start_time, end_time, None, user_id, id])

        return pd.DataFrame(
            rows_list,
            columns=[
                "start_date_time",
                "end_date_time",
                "transportation_mode",
                "user_id",
                "id",
            ],
        )


def get_trajectories_df(user_id: str):
    """Returns a DataFrame of the trajectories of a user_id

    Arguments:
        user_id {string} -- The id of the user

    Returns:
        DataFrame
    """

    for _, _, files in os.walk(f"{data_path}/{user_id}/Trajectory"):
        # Create an empty DataFrame to store the trajectories
        trajectories = pd.DataFrame(
            columns=["latitude", "longitude", "altitude", "date_time", "activity_id"]
        )
        activities = get_activities_df(user_id)

        # Check if the user has labeled activities
        if activities.empty:
            return trajectories

        # Get the start dates of the activities as strings
        start_dates = [
            start_date
            for start_date in activities["start_date_time"]
            .dt.date.astype(str)
            .values.tolist()
        ]

        # Create an empty list to store selected trajectories
        selected_trajectories = []

        # Loop through the files in the Trajectory folder
        for name in files:
            # Check if the trajectory file is in the date of an activity
            if f"{name[:4]}-{name[4:6]}-{name[6:8]}" not in start_dates:
                continue

            trajectory = pd.read_csv(
                f"{data_path}/{user_id}/Trajectory/{name}",
                names=[
                    "latitude",
                    "longitude",
                    "_",
                    "altitude",
                    "days",
                    "date",
                    "time",
                ],
                sep=",",
                encoding="ISO-8859-1",
                skiprows=6,
            )
            trajectory["date_time"] = pd.to_datetime(
                trajectory["date"] + " " + trajectory["time"],
                format="%Y-%m-%d %H:%M:%S",
            )
            trajectory = trajectory.drop(columns=["_", "date", "time", "days"])

            # Add trajectory to trajectories dataframe
            trajectories = pd.concat([trajectories, trajectory])

        print(f"Relating {trajectories.shape[0]} track points to activities...")

        # Create an empty list to store selected trajectories
        selected_trajectories = []

        # Loop through activities and filter trajectories
        for _, activity in activities.iterrows():
            mask = (trajectories["date_time"] >= activity["start_date_time"]) & (
                trajectories["date_time"] <= activity["end_date_time"]
            )
            trajectory = trajectories.copy()[mask]

            if not trajectory.empty and trajectory.shape[0] <= 2500:
                trajectory["activity_id"] = activity["id"]
                selected_trajectories.append(trajectory)

        # Concatenate the selected trajectories into a single DataFrame
        if len(selected_trajectories) > 0:
            trajectories = pd.concat(selected_trajectories)
            trajectories = trajectories.reset_index(drop=True)

            return trajectories
        else:
            return pd.DataFrame(
                columns=[
                    "latitude",
                    "longitude",
                    "altitude",
                    "date_time",
                    "activity_id",
                ]
            )

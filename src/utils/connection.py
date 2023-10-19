from pymongo import MongoClient, version


class DbConnector:
    """
    Connects to the MongoDB server on the Ubuntu virtual machine.
    Connector needs HOST, USER and PASSWORD to connect.
    """

    def __init__(
        self,
        DATABASE="mongodb",
    ):
        # Connect to the databases
        try:
            self.client = MongoClient()
            self.db = self.client[DATABASE]
        except Exception as e:
            print("ERROR: Failed to connect to db:", e)

        # get database information
        print("You are connected to the database:", self.db.name)
        print("-----------------------------------------------\n")

    def close_connection(self):
        # close the cursor
        # close the DB connection
        self.client.close()
        print("\n-----------------------------------------------")
        print("Connection to %s-db is closed" % self.db.name)

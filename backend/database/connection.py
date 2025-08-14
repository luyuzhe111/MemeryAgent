from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseConnection:
    _instance: DatabaseConnection | None = None
    _client: MongoClient | None = None
    _db: Database | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self.connect()

    def connect(self):
        """Establish connection to MongoDB"""
        try:
            mongodb_uri = os.getenv("MONGODB_URI")
            if not mongodb_uri:
                raise ValueError("MONGODB_URI not found in environment variables")

            self._client = MongoClient(mongodb_uri)
            # Test the connection
            self._client.admin.command("ping")

            # Use a database name (you can change this)
            self._db = self._client.twitter_bot

            print("Successfully connected to MongoDB")

        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise

    def get_database(self) -> Database:
        """Get the database instance"""
        if self._db is None:
            self.connect()
        return self._db

    def close(self):
        """Close the database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            print("MongoDB connection closed")


# Global database instance
db_connection = DatabaseConnection()


def get_db() -> Database:
    """Get database instance - convenience function"""
    return db_connection.get_database()

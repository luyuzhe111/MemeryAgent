from datetime import UTC, datetime
from typing import Any

from pymongo.collection import Collection

from .connection import get_db


class ProcessedMention:
    """Model for tracking processed mentions"""

    def __init__(self):
        self.collection: Collection = get_db().processed_mentions

    def mark_as_processed(
        self,
        mention_id: str,
        username: str,
        tweet_text: str,
        image_path: str | None = None,
    ) -> bool:
        """Mark a mention as processed"""
        try:
            # Set status based on image_path
            if image_path == "processing":
                status = "processing"
            elif image_path is None:
                status = "failed"
            else:
                status = "completed"

            doc = {
                "mention_id": mention_id,
                "username": username,
                "tweet_text": tweet_text,
                "image_path": image_path,
                "processed_at": datetime.now(UTC),
                "status": status,
            }

            result = self.collection.insert_one(doc)
            print(f"Marked mention {mention_id} with status '{status}' in database")
            return result.acknowledged

        except Exception as e:
            print(f"Error marking mention as processed: {e}")
            return False

    def is_processed(self, mention_id: str) -> bool:
        """Check if a mention has already been processed"""
        try:
            return self.collection.find_one({"mention_id": mention_id}) is not None
        except Exception as e:
            print(f"Error checking if mention is processed: {e}")
            return False

    def get_processed_mentions(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent processed mentions"""
        try:
            cursor = self.collection.find().sort("processed_at", -1).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"Error getting processed mentions: {e}")
            return []


class BotState:
    """Model for tracking bot state and configuration"""

    def __init__(self):
        self.collection: Collection = get_db().bot_state
        self._state_doc_id = "twitter_bot_state"

    def get_last_mention_id(self) -> str | None:
        """Get the last processed mention ID"""
        try:
            doc = self.collection.find_one({"_id": self._state_doc_id})
            return doc.get("last_mention_id") if doc else None
        except Exception as e:
            print(f"Error getting last mention ID: {e}")
            return None

    def set_last_mention_id(self, mention_id: str) -> bool:
        """Set the last processed mention ID"""
        try:
            update_doc = {
                "$set": {"last_mention_id": mention_id, "updated_at": datetime.now(UTC)}
            }

            result = self.collection.update_one(
                {"_id": self._state_doc_id},
                update_doc,
                upsert=True,  # Create if doesn't exist
            )
            return result.acknowledged

        except Exception as e:
            print(f"Error setting last mention ID: {e}")
            return False

    def get_bot_stats(self) -> dict[str, Any]:
        """Get bot statistics"""
        try:
            doc = self.collection.find_one({"_id": self._state_doc_id})
            if not doc:
                return {
                    "total_mentions_processed": 0,
                    "last_active": None,
                    "uptime_start": datetime.now(UTC),
                }

            return {
                "total_mentions_processed": doc.get("total_mentions_processed", 0),
                "last_active": doc.get("updated_at"),
                "uptime_start": doc.get("uptime_start", datetime.now(UTC)),
            }
        except Exception as e:
            print(f"Error getting bot stats: {e}")
            return {}

    def increment_processed_count(self) -> bool:
        """Increment the count of processed mentions"""
        try:
            update_doc = {
                "$inc": {"total_mentions_processed": 1},
                "$set": {"updated_at": datetime.now(UTC)},
                "$setOnInsert": {"uptime_start": datetime.now(UTC)},
            }

            result = self.collection.update_one(
                {"_id": self._state_doc_id}, update_doc, upsert=True
            )
            return result.acknowledged

        except Exception as e:
            print(f"Error incrementing processed count: {e}")
            return False

from backend.database.models import BotState, ProcessedMention


def test_bot_state():
    """Test BotState database operations"""
    bot_state = BotState()

    # Test setting and getting last mention ID
    test_mention_id = "1234567890123456789"
    success = bot_state.set_last_mention_id(test_mention_id)
    assert success, "Failed to set last mention ID"

    retrieved_id = bot_state.get_last_mention_id()
    assert retrieved_id == test_mention_id, "Retrieved ID doesn't match set ID"

    # Test bot stats
    stats = bot_state.get_bot_stats()
    assert isinstance(stats, dict), "Bot stats should be a dictionary"
    assert "total_mentions_processed" in stats, "Stats should include processed count"


def test_processed_mentions():
    """Test ProcessedMention database operations"""
    processed_mentions = ProcessedMention()

    # Test marking mention as processed
    test_mention_data = {
        "mention_id": "9876543210987654321",
        "username": "test_user",
        "tweet_text": "Hello bot!",
        "image_path": "/path/to/test/image.png",
    }

    success = processed_mentions.mark_as_processed(**test_mention_data)
    assert success, "Failed to mark mention as processed"

    # Test checking if processed
    is_processed = processed_mentions.is_processed(test_mention_data["mention_id"])
    assert is_processed, "Mention should be marked as processed"

    # Test getting processed mentions
    recent_mentions = processed_mentions.get_processed_mentions(limit=5)
    assert isinstance(recent_mentions, list), "Should return list of mentions"

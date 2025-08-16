# MemeryAgent

A Twitter bot that automatically generates and replies with AI-created images based on mentions.

## Architecture Overview

### Twitter Bot Design

**Asynchronous Processing**
- **Fully async/await architecture**: Main polling loop, mention processing, and image generation all use async/await
- **Non-blocking concurrent processing**: Multiple image generations run simultaneously without blocking new mention checks
- **Event loop management**: Uses `asyncio.run()` to manage the main event loop
- 90-second polling interval for checking new mentions

**Image Generation**
- OpenAI Agents SDK integration for AI-powered image creation
- Agent initialized once as instance variable for efficiency
- Custom tools: `select_local_image`, `download_x_profile_picture`, `create_composite_image`

**Error Handling & Recovery**
- Graceful handling of failed image generations
- Mentions marked as "processing" immediately to avoid duplicates
- Failed generations logged and marked appropriately in database

### Database Design (MongoDB)

**ProcessedMention Collection**
- Tracks all processed mentions with metadata
- Fields: `mention_id`, `username`, `tweet_text`, `image_path`, `processed_at`, `status`
- Status progression: "processing" → "completed"/"failed"
- Prevents duplicate processing of mentions

**BotState Collection**
- Maintains bot persistence across restarts
- Tracks `last_mention_id` for incremental processing
- Bot statistics: `total_mentions_processed`, `uptime_start`, `last_active`
- Single document with `_id: "twitter_bot_state"`

### Key Design Decisions

**Why Async Without Acknowledgment**
- Cleaner user experience (no "processing..." messages)
- True concurrency for multiple simultaneous image generations
- Perfect for I/O-bound OpenAI API calls
- Maintains debugger compatibility (no ThreadPoolExecutor)

**Why MongoDB for Metadata + File Storage for Images**
- **MongoDB**: Efficient querying/filtering of mention metadata
- **File Storage**: Cost-effective for large image files
- **Hybrid approach**: Best of both worlds - queryable metadata + cheap storage

**Database Schema Choices**
- Immediate "processing" status prevents race conditions
- Separate collections for different concerns (mentions vs bot state)
- Atomic operations with upsert for bot state updates

**Image Storage Strategy**
- Railway persistent volumes: `/app/output_images/` (production)
- Local storage: `output_images/` (development)
- Filename format: `{mention_id}_{username}_{timestamp}.png`
- MongoDB stores file path for easy retrieval and analysis

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your Twitter API keys and MongoDB URI

# Run the bot
python main.py
```

## Deployment

Designed for Railway deployment with:
- Persistent volumes for image storage ($0.15/GB)
- MongoDB Atlas integration for database persistence

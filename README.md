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

### Prerequisites
- Python 3.12 or higher
- pip

### Installation

```bash
# Create conda environment
conda create -n memery python=3.12
conda activate memery

# Install dependencies using pyproject.toml
pip install -e .

# For development dependencies
pip install -e ".[dev]"
```

### Environment Variables

Create a `.env` file in the project root with the following variables:

#### For agent.py (AI image generation):
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

#### For main.py (Twitter bot):
```bash
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret
MONGODB_URI=your_mongodb_connection_string
```

### Pre-commit Setup (Optional)

Set up pre-commit hooks to automatically format and lint code before commits:

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files (optional, to test setup)
pre-commit run --all-files
```

The pre-commit hooks will automatically run:
- Black (code formatting)
- Ruff (linting)
- MyPy (type checking)

### Running the Application

```bash
# Run the AI agent (standalone image generation)
python agent.py

# Run the Twitter bot
python main.py
```

## Deployment

Designed for Railway deployment with:
- Persistent volumes for image storage ($0.15/GB)
- MongoDB Atlas integration for database persistence

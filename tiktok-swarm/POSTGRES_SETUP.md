# PostgreSQL Setup for TikTok Swarm

This guide explains how to set up PostgreSQL for both short-term (conversation) and long-term (cross-thread) memory.

## Quick Start with Docker

1. **Start PostgreSQL using Docker Compose:**
   ```bash
   docker-compose up -d
   ```
   This will start PostgreSQL with:
   - Database: `tiktok_swarm`
   - User: `postgres`
   - Password: `password`
   - Port: `5432`

2. **Update your .env file:**
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   DATABASE_URL=postgresql://postgres:password@localhost:5432/tiktok_swarm
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database setup:**
   ```bash
   python setup_database.py
   ```

5. **Start the application:**
   ```bash
   python run_local.py
   ```

## Manual PostgreSQL Setup

If you prefer to use an existing PostgreSQL installation:

1. **Create the database:**
   ```sql
   CREATE DATABASE tiktok_swarm;
   ```

2. **Update .env with your connection string:**
   ```
   DATABASE_URL=postgresql://your_user:your_password@your_host:5432/tiktok_swarm
   ```

3. **Run the setup script:**
   ```bash
   python setup_database.py
   ```

## Memory System Overview

### Short-term Memory (Checkpointer)
- Stores conversation history per thread
- Maintains agent state and messages
- Powered by `AsyncPostgresSaver`
- Data stored in LangGraph checkpointer tables

### Long-term Memory (Custom Store)
- User preferences persist across conversations
- Trending patterns are stored and analyzed
- Video templates can be reused
- Data stored in `langgraph_store` table

## Using Memory Management

### Store User Preferences
```python
from src.memory.manager import memory_manager

# Store a preference
memory_manager.store_user_preference(
    user_id="user123",
    key="preferred_content",
    value={"type": "cooking", "style": "quick_recipes"}
)

# Get all user preferences
prefs = memory_manager.get_user_preferences("user123")
```

### Store and Retrieve Trends
```python
# Store trend data
memory_manager.store_trend_data(
    trend_type="hashtags",
    data={"tag": "#cooking", "views": 1000000}
)

# Get recent trends
recent_trends = memory_manager.get_recent_trends("hashtags", limit=5)
```

### Video Templates
```python
# Store a successful template
memory_manager.store_video_template(
    template_id="cooking_quick_001",
    template_data={
        "category": "cooking",
        "duration": 30,
        "structure": ["hook", "main", "cta"]
    }
)

# Get templates by category
templates = memory_manager.get_video_templates(category="cooking")
```

## Database Schema

### Checkpointer Tables (Automatic)
- Created by AsyncPostgresSaver
- Stores conversation checkpoints
- Handles thread state management

### Store Table Structure
```sql
CREATE TABLE langgraph_store (
    namespace TEXT[],
    key TEXT,
    value JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (namespace, key)
);
```

## Troubleshooting

### Connection Issues
- Ensure PostgreSQL is running: `docker-compose ps`
- Check connection string in .env
- Verify firewall allows port 5432

### Permission Issues
- Ensure database user has CREATE TABLE permissions
- Check database ownership

### Performance
- The system includes indexes for optimal performance
- Consider periodic cleanup of old data:
  ```python
  memory_manager.clear_old_data(["trends"], days_to_keep=30)
  ```

## Backing Up Data

To backup your swarm data:
```bash
docker exec tiktok_swarm_postgres pg_dump -U postgres tiktok_swarm > backup.sql
```

To restore:
```bash
docker exec -i tiktok_swarm_postgres psql -U postgres tiktok_swarm < backup.sql
```
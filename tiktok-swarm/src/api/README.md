# TikTok API Endpoints

All TikTok analysis tools are now available as direct API endpoints for testing and debugging.

## Available Endpoints

### 1. Analyze Trending Videos
**POST** `/tiktok/analyze/trending`

```json
{
  "count": 10
}
```

### 2. Analyze Hashtag
**POST** `/tiktok/analyze/hashtag`

```json
{
  "hashtag": "cooking",
  "count": 20
}
```

### 3. Analyze Video
**POST** `/tiktok/analyze/video`

```json
{
  "video_url_or_id": "https://www.tiktok.com/@user/video/1234567890"
}
```

### 4. Get Video Details
**POST** `/tiktok/analyze/video/details`

```json
{
  "video_url_or_id": "1234567890"
}
```

### 5. Search Content
**POST** `/tiktok/search`

```json
{
  "query": "cooking",
  "count": 20
}
```

### 6. Analyze User Profile
**POST** `/tiktok/analyze/user`

```json
{
  "username": "therock",
  "video_count": 20
}
```

### 7. Get Session Stats
**GET** `/tiktok/session/stats`

Returns current TikTok session statistics and health information.

## Testing with Swagger UI

1. Navigate to http://localhost:8000/docs
2. Authenticate using the "Authorize" button with your Bearer token
3. Find the TikTok Analysis section
4. Try any endpoint directly

## Authentication

All endpoints require authentication. Include your JWT token in the Authorization header:

```
Authorization: Bearer your_jwt_token_here
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error Type",
  "message": "Detailed error message",
  "action_required": "What to do to fix this"
}
```

## Architecture

The endpoints follow this pattern:

1. **API Layer** (`tiktok_routes.py`) - Handles HTTP requests/responses
2. **Business Logic** (analyzer classes) - Core analysis logic
3. **Tools** (`src/tools/tiktok/`) - LangGraph tool wrappers that can call either:
   - The API endpoints (for production)
   - The analyzer classes directly (for development)

This allows for:
- Independent testing of each analysis function
- Performance monitoring per endpoint
- Rate limiting per function
- Easy debugging without involving agents
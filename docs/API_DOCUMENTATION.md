# NarrativeForge API Documentation

## Overview

The NarrativeForge API provides endpoints for creating and managing interactive AI-powered storytelling experiences. The API is built with FastAPI and supports real-time story generation using large language models.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication. In production, consider implementing JWT-based authentication.

## Endpoints

### Story Management

#### Create Story
**POST** `/stories`

Creates a new story session with the specified genre and difficulty.

**Request Body:**
```json
{
  "genre": "fantasy",
  "difficulty": "medium"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Story created successfully",
  "data": {
    "session_id": "uuid-12345"
  }
}
```

#### Get Story State
**GET** `/stories/{session_id}`

Retrieves the current state of a story session.

**Response:**
```json
{
  "success": true,
  "message": "Story state retrieved successfully",
  "data": {
    "story_id": "uuid-12345",
    "current_segment": {
      "id": "segment-1",
      "text": "You stand at the entrance...",
      "choices": [
        {
          "text": "Enter boldly",
          "action": "bold_entrance"
        }
      ]
    },
    "story_history": [],
    "genre": "fantasy",
    "difficulty": "medium"
  }
}
```

#### Make Choice
**POST** `/stories/{session_id}/choices`

Makes a choice in the story and generates the next segment.

**Request Body:**
```json
{
  "choice_index": 0
}
```

**Response:**
```json
{
  "segment": {
    "id": "segment-2",
    "text": "You stride confidently...",
    "choices": [
      {
        "text": "Continue forward",
        "action": "continue"
      }
    ]
  },
  "session_id": "uuid-12345"
}
```

#### Get Story History
**GET** `/stories/{session_id}/history`

Retrieves the complete story history for a session.

**Response:**
```json
{
  "success": true,
  "message": "Story history retrieved successfully",
  "data": {
    "history": [
      {
        "id": "segment-1",
        "text": "You stand at the entrance...",
        "choices": []
      }
    ],
    "total_segments": 1
  }
}
```

#### End Story
**DELETE** `/stories/{session_id}`

Ends a story session.

**Response:**
```json
{
  "success": true,
  "message": "Story session ended successfully"
}
```

#### List Active Stories
**GET** `/stories`

Lists all active story sessions.

**Response:**
```json
{
  "success": true,
  "message": "Active sessions retrieved successfully",
  "data": {
    "active_sessions": ["uuid-12345", "uuid-67890"],
    "count": 2
  }
}
```

### Configuration

#### Get Available Genres
**GET** `/genres`

Retrieves available story genres.

**Response:**
```json
{
  "success": true,
  "message": "Genres retrieved successfully",
  "data": {
    "genres": [
      {
        "id": "fantasy",
        "name": "Fantasy",
        "description": "Epic adventures in magical realms"
      },
      {
        "id": "scifi",
        "name": "Science Fiction",
        "description": "Space exploration and technology"
      }
    ]
  }
}
```

#### Get Available Difficulties
**GET** `/difficulties`

Retrieves available difficulty levels.

**Response:**
```json
{
  "success": true,
  "message": "Difficulties retrieved successfully",
  "data": {
    "difficulties": [
      {
        "id": "easy",
        "name": "Easy",
        "description": "Gentle storytelling"
      },
      {
        "id": "medium",
        "name": "Medium",
        "description": "Balanced challenge"
      }
    ]
  }
}
```

## Data Models

### StoryChoice
```json
{
  "text": "string",
  "action": "string",
  "description": "string (optional)"
}
```

### StorySegment
```json
{
  "id": "string",
  "text": "string",
  "choices": ["StoryChoice"],
  "background_context": "string (optional)",
  "mood": "string (optional)",
  "location": "string (optional)"
}
```

### StoryState
```json
{
  "story_id": "string",
  "current_segment": "StorySegment",
  "story_history": ["StorySegment"],
  "character_info": "object",
  "world_info": "object",
  "genre": "string",
  "difficulty": "string",
  "created_at": "datetime",
  "last_updated": "datetime (optional)"
}
```

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (session not found)
- `500` - Internal Server Error (server error)

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## CORS

The API supports CORS for cross-origin requests from web and mobile applications.

## WebSocket Support

Future versions may include WebSocket support for real-time story updates.

## Examples

### Complete Story Flow

1. **Create Story:**
```bash
curl -X POST "http://localhost:8000/api/v1/stories" \
  -H "Content-Type: application/json" \
  -d '{"genre": "fantasy", "difficulty": "medium"}'
```

2. **Get Story State:**
```bash
curl "http://localhost:8000/api/v1/stories/uuid-12345"
```

3. **Make Choice:**
```bash
curl -X POST "http://localhost:8000/api/v1/stories/uuid-12345/choices" \
  -H "Content-Type: application/json" \
  -d '{"choice_index": 0}'
```

4. **End Story:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/stories/uuid-12345"
```

# Python API Standards (The "How")
Implementation of: /api_standards.md

## Relationship to Standards
This file provides the Python-specific implementation ("How") for the API standards defined in `/api_standards.md` ("What").

## 1. Framework & Libraries

- **Primary Framework**: FastAPI (async, auto OpenAPI generation).
- **Alternatives**: Flask for simple APIs, Django REST Framework for complex apps.
- **Authentication**: FastAPI Users with OAuth2/JWT.
- **Validation**: Pydantic v2 for request/response models.
- **Documentation**: Auto-generated Swagger UI from FastAPI.

## 2. Project Structure

```text
myapi/
├── main.py              # FastAPI app instance
├── routers/             # API endpoints grouped by resource
├── models/              # Pydantic models
├── dependencies/        # Auth, DB connections
├── config.py            # Settings with Pydantic BaseSettings
└── tests/               # API tests
```

## 3. Example: Basic CRUD API

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="My API", version="1.0.0")

class Item(BaseModel):
    id: int
    name: str
    description: str | None = None

items = []

@app.get("/items", response_model=List[Item])
async def read_items():
    return items

@app.post("/items", response_model=Item)
async def create_item(item: Item):
    items.append(item)
    return item
```

## 4. Security Implementation

- **CORS**: Use `fastapi.middleware.cors` for cross-origin requests.
- **Rate Limiting**: Implement with `slowapi` or Redis.
- **Input Sanitization**: Rely on Pydantic validation; use `bleach` for HTML inputs.

## 5. Performance Tips

- **Async/Await**: Use async endpoints for I/O operations.
- **Caching**: Integrate Redis with `aioredis`.
- **Pagination**: Use `fastapi-pagination` for cursor-based pagination.

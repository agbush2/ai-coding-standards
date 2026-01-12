# Python Examples & Templates
Implementation of: /master_standards.md

## Relationship to Standards
This file provides the Python-specific implementation ("How") for the code templates and patterns requested in `/master_standards.md` ("What").

## Template 1: Pydantic Settings
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "My Service"
    db_url: str
    api_key: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

## Template 2: FastAPI Route (Async)
```python
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()

class ItemRequest(BaseModel):
    name: str
    quantity: int

@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemRequest):
    # BAD: print(f"Creating {item.name}")
    # GOOD: logger.info("creating_item", name=item.name)
    
    if item.quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    
    return {"id": 123, **item.model_dump()}
```

## Template 3: Pyproject.toml (Tooling)
```toml
[tool.ruff]
line-length = 88
target-version = "py312"
select = ["E", "F", "B", "I", "S"] # S = bandit

[tool.mypy]
python_version = "3.12"
strict = true
disallow_untyped_defs = true
```

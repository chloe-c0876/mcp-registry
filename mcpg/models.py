from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import jsonschema  # For MCP schema

# MCP v0 schema (simplified; fetch full from https://modelcontextprotocol.io/schema/v0/server.json)
MCP_SERVER_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "version": {"type": "string"},
        "endpoint": {"type": "string", "format": "uri"},
        "tools": {"type": "array", "items": {"type": "object"}},
        "auth_methods": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["name", "endpoint"]
}

class Tool(BaseModel):
    name: str
    description: str

class Server(BaseModel):
    id: str = Field(..., description="Unique namespace-prefixed ID, e.g., kp.internal.example/github")
    name: str
    description: str
    version: str
    endpoint: str
    tools: List[Tool]
    auth_methods: List[str]
    owner: str  # Azure AD email
    team: str
    tags: Optional[List[str]] = []
    metadata: Dict[str, Any]  # Full server.json
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_public: bool = False

    @field_validator('metadata')
    @classmethod
    def validate_mcp_schema(cls, v):
        jsonschema.validate(instance=v, schema=MCP_SERVER_SCHEMA)
        return v

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
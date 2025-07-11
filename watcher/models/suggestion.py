from pydantic import BaseModel, Field
from typing import Literal

class Suggestion(BaseModel):
    suggestion: str = Field(..., description="What to do next")
    severity: Literal["low", "medium", "high"] = Field(..., description="Urgency level")
    confidence: float = Field(..., ge=0, le=1, description="Model confidence score")
    remediation: str = Field(..., description="Exact command or snippet to run")

# app/models.py
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class AgentType(Enum):
    BLOCK = "BLOCK"
    COUNSELING = "COUNSELING"
    GOSPEL = "GOSPEL"

class HandoffUrgency(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

@dataclass
class Message:
    content: str
    agent_type: Optional[AgentType] = None
    timestamp: Optional[str] = None
    metadata: Optional[Dict] = None

@dataclass
class QnAData:
    question: str
    answer: str
    category: Optional[str] = None

@dataclass
class HandoffRequest:
    user_phone: str
    user_message: str
    urgency: HandoffUrgency
    reason: str
    counselor_type: str
    timestamp: str
    conversation_summary: str
    session_id: str

@dataclass
class Counselor:
    id: str
    name: str
    whatsapp: str
    expertise: List[str]
    availability: str
    priority: int
    is_available: bool = True
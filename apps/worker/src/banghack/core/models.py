"""Core data models for v0.4 Live Orchestrator."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class LiveMode(str, Enum):
    """Live session mode."""
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"


class CommentAction(str, Enum):
    """Action to take for a classified comment."""
    REPLY = "REPLY"
    SKIP = "SKIP"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"


class AudioJobKind(str, Enum):
    """Type of audio job."""
    CLIP = "CLIP"           # Pre-generated clip from library
    TTS = "TTS"             # Real-time TTS generation
    REPLY = "REPLY"         # Reply to comment
    ANNOUNCEMENT = "ANNOUNCEMENT"  # Host announcement


@dataclass
class LiveState:
    """Complete state of a live session."""
    session_id: str
    mode: LiveMode
    started_at: float
    max_duration_s: int
    
    # Feature flags
    reply_enabled: bool = False
    auto_voice_enabled: bool = True
    llm_enabled: bool = True
    tts_enabled: bool = True
    
    # Current state
    phase: str = ""
    phase_idx: int = 0
    phase_total: int = 0
    product: str = ""
    elapsed_s: int = 0
    remaining_s: int = 0
    
    # Metrics
    total_comments: int = 0
    total_replies: int = 0
    total_decisions: int = 0
    token_budget_remaining: float = 0.0
    
    # Metadata
    operator_id: str = ""
    metadata: dict = field(default_factory=dict)  # type: ignore[type-arg]


@dataclass
class CommentDecision:
    """Decision made by classifier/orchestrator for a comment."""
    comment_id: str
    user: str
    text: str
    
    # Classification
    intent: str
    confidence: float
    action: CommentAction
    priority: int  # 0-10, higher = more urgent
    
    # Reasoning
    reason: str
    needs_llm: bool
    safe_category: bool  # True if spam/forbidden (safe to skip)
    
    # Context
    product: str = ""
    timestamp: float = 0.0
    metadata: dict = field(default_factory=dict)  # type: ignore[type-arg]


@dataclass
class AudioJob:
    """Audio playback job for the queue."""
    job_id: str
    kind: AudioJobKind
    priority: int  # 0-10, higher = more urgent
    
    # Content
    text: str = ""           # For TTS jobs
    file_path: str = ""      # For CLIP jobs
    clip_id: str = ""        # For CLIP jobs
    
    # Context
    user: str = ""
    product: str = ""
    comment_id: str = ""
    
    # Metadata
    created_at: float = 0.0
    duration_ms: int = 0
    metadata: dict = field(default_factory=dict)  # type: ignore[type-arg]

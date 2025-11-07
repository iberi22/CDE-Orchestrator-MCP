"""
Pydantic models for Dynamic Skill Management System (DSMS).

Defines skill data structures, lifecycle types, and metadata for the skill
management system that powers AI agent knowledge generation and updates.
"""

from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SkillType(str, Enum):
    """Skill lifecycle types."""

    BASE = "base"  # Persistent, accumulative, grows over time
    EPHEMERAL = "ephemeral"  # Task-specific, temporary, auto-cleaned after 24h


class ComplexityLevel(str, Enum):
    """Task/skill complexity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EPIC = "epic"


class SkillDomain(str, Enum):
    """Knowledge domains for skill classification."""

    BACKEND = "backend"
    FRONTEND = "frontend"
    DEVOPS = "devops"
    DATABASE = "database"
    SECURITY = "security"
    DATA_SCIENCE = "data_science"
    INFRASTRUCTURE = "infrastructure"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    ARCHITECTURE = "architecture"


class SkillStatus(str, Enum):
    """Skill lifecycle status."""

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class SkillRequirement(BaseModel):
    """
    Result of task analysis by SkillRequirementDetector.

    Indicates whether a skill is needed and what gaps exist.
    """

    needs_skill: bool
    complexity: ComplexityLevel
    domain: SkillDomain
    knowledge_gaps: List[str]  # e.g., ["redis pub/sub", "fastapi websockets"]
    confidence: float = Field(ge=0, le=1.0)  # Confidence score 0-1
    reasoning: str  # Why this skill was recommended

    class Config:
        """Pydantic config."""

        use_enum_values = True


class UpdateNote(BaseModel):
    """
    Record of a skill update event.

    Tracks what was updated, when, and what changed.
    """

    date: datetime
    version: str  # e.g., "1.2.0"
    changes: str  # What changed (e.g., "Updated async examples")
    sources: List[str]  # URLs or references for the update
    archived: bool = False  # True if archived (>90 days old)

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class BaseSkill(BaseModel):
    """
    Persistent, accumulative skill stored in `.copilot/skills/base/`.

    Grows over time as learnings are distilled from task executions.
    """

    id: str  # Unique identifier (e.g., "redis-caching")
    title: str
    description: str
    domain: SkillDomain
    complexity: ComplexityLevel
    status: SkillStatus = SkillStatus.ACTIVE

    # Content
    content: str  # Full markdown content (SKILL.md)
    examples: Dict[str, str] = Field(default_factory=dict)  # Code examples
    best_practices: List[str] = Field(default_factory=list)
    known_issues: Dict[str, str] = Field(default_factory=dict)  # Issue -> Workaround

    # Metadata
    created_at: datetime
    updated_at: datetime
    version: str = "1.0.0"
    author: str
    tags: List[str] = Field(default_factory=list)
    external_sources: List[str] = Field(default_factory=list)  # External repos

    # Lifecycle
    update_notes: List[UpdateNote] = Field(default_factory=list)
    last_review: datetime = Field(default_factory=datetime.now)
    review_frequency_days: int = 30  # Review every N days
    confidence_score: float = Field(default=0.8, ge=0, le=1.0)

    # References
    related_skills: List[str] = Field(default_factory=list)  # Skill IDs
    dependencies: List[str] = Field(default_factory=list)  # Library/tool deps
    references: List[str] = Field(default_factory=list)  # Documentation links

    class Config:
        """Pydantic config."""

        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat()}

    @property
    def needs_review(self) -> bool:
        """Check if skill needs review based on last_review date."""
        days_since_review = (datetime.now(timezone.utc) - self.last_review).days
        return days_since_review >= self.review_frequency_days

    @property
    def size_tokens(self) -> int:
        """Estimate token count (rough approximation: 1 token ≈ 4 chars)."""
        return len(self.content) // 4

    def mark_reviewed(self) -> None:
        """Mark skill as reviewed now."""
        self.last_review = datetime.now(timezone.utc)

    def add_update_note(self, version: str, changes: str, sources: List[str]) -> None:
        """Record an update to this skill."""
        note = UpdateNote(
            date=datetime.now(timezone.utc),
            version=version,
            changes=changes,
            sources=sources,
        )
        self.update_notes.append(note)
        self.updated_at = datetime.now(timezone.utc)
        self.version = version


class EphemeralSkill(BaseModel):
    """
    Task-specific, temporary skill stored in `.copilot/skills/ephemeral/`.

    Auto-cleaned after 24 hours. Contains context-rich information tailored
    to a specific task, generated by SkillGenerator.
    """

    id: str  # Unique ID (e.g., "task-uuid-redis-caching")
    title: str
    description: str
    domain: SkillDomain
    complexity: ComplexityLevel

    # Content (task-specific)
    content: str  # Full markdown content
    context: Dict[str, Any]  # Task-specific context injected by generator
    examples: Dict[str, str] = Field(default_factory=dict)
    workarounds: Dict[str, str] = Field(default_factory=dict)

    # Lifecycle
    created_at: datetime
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24)
    )
    task_id: str  # Link to parent task
    generated_from_base_skill: Optional[str] = None  # Parent base skill ID

    # Generation metadata
    generation_time_seconds: float  # How long it took to generate
    research_sources: List[str] = Field(default_factory=list)  # Web research URLs
    generated_by: str = "SkillGenerator"  # Component that created this
    confidence_score: float = Field(default=0.7, ge=0, le=1.0)

    # Tags for filtering/cleanup
    tags: List[str] = Field(default_factory=list)
    archived: bool = False

    class Config:
        """Pydantic config."""

        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat()}

    @property
    def is_expired(self) -> bool:
        """Check if this skill has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def time_to_expiry_hours(self) -> float:
        """Hours until this skill expires."""
        delta = self.expires_at - datetime.now(timezone.utc)
        return delta.total_seconds() / 3600

    @property
    def size_tokens(self) -> int:
        """Estimate token count."""
        return len(self.content) // 4


class SkillSearchResult(BaseModel):
    """Result from searching for skills (base or external)."""

    skill_id: str
    title: str
    description: str
    domain: SkillDomain
    complexity: ComplexityLevel
    match_score: float = Field(ge=0, le=1.0)  # Relevance score
    source: str  # "base", "external", "ephemeral"
    url: Optional[str] = None  # For external skills


class SkillMetadata(BaseModel):
    """Minimal metadata for skill indexing/searching."""

    id: str
    title: str
    domain: SkillDomain
    complexity: ComplexityLevel
    tags: List[str]
    status: SkillStatus
    updated_at: datetime
    size_tokens: int
    confidence_score: float

    class Config:
        """Pydantic config."""

        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class SkillGenerationRequest(BaseModel):
    """Request to generate a new ephemeral skill."""

    task_description: str
    domain: SkillDomain
    complexity: ComplexityLevel
    knowledge_gaps: List[str]
    parent_base_skill_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    required_accuracy: float = Field(default=0.8, ge=0, le=1.0)


class SkillGenerationResponse(BaseModel):
    """Response from skill generation."""

    status: str  # "success", "partial", "failed"
    skill: Optional[EphemeralSkill] = None
    error: Optional[str] = None
    generation_time_seconds: float
    confidence_score: float
    research_urls: List[str] = Field(default_factory=list)


class SkillIndexEntry(BaseModel):
    """Entry in the skill index for fast lookup."""

    skill_id: str
    skill_type: SkillType
    domain: SkillDomain
    complexity: ComplexityLevel
    tags: List[str]
    file_path: Path
    last_indexed: datetime
    size_bytes: int
    status: SkillStatus

    class Config:
        """Pydantic config."""

        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Path: lambda v: str(v),
        }


class SkillUpdateRequest(BaseModel):
    """Request to update an existing base skill."""

    skill_id: str
    version: str
    changes: str  # What changed
    sources: List[str]  # Research URLs
    new_examples: Optional[Dict[str, str]] = None
    new_best_practices: Optional[List[str]] = None
    new_known_issues: Optional[Dict[str, str]] = None


class SkillStats(BaseModel):
    """Statistics about skills in the system."""

    total_base_skills: int
    total_ephemeral_skills: int
    total_tokens_base: int
    total_tokens_ephemeral: int
    by_domain: Dict[str, int]  # Domain -> count
    by_complexity: Dict[str, int]  # Complexity -> count
    average_confidence_base: float
    average_confidence_ephemeral: float
    skills_needing_review: int
    expired_ephemeral_skills: int

    class Config:
        """Pydantic config."""

        use_enum_values = True

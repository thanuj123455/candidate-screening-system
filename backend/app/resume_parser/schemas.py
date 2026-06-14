from pydantic import BaseModel, Field
from typing import Optional


class ParsedResume(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    skills: list[str] = Field(default_factory=list)
    programming_languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    education: str = ""
    certifications: list[str] = Field(default_factory=list)
    raw_text: str = ""

    def to_summary(self) -> str:
        """Human-readable summary used in LLM prompts."""
        parts = []
        if self.name:
            parts.append(f"Name: {self.name}")
        if self.education:
            parts.append(f"Education: {self.education}")
        if self.programming_languages:
            parts.append(f"Languages: {', '.join(self.programming_languages)}")
        if self.frameworks:
            parts.append(f"Frameworks: {', '.join(self.frameworks)}")
        if self.skills:
            parts.append(f"Skills: {', '.join(self.skills)}")
        if self.tools:
            parts.append(f"Tools: {', '.join(self.tools)}")
        if self.projects:
            parts.append(f"Projects: {', '.join(self.projects)}")
        if self.experience:
            parts.append(f"Experience: {'; '.join(self.experience)}")
        return "\n".join(parts)

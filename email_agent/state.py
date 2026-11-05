"""The data that flows through the graph.

In LangGraph, every node receives the current State and returns a dict
with the fields it wants to update. Think of State as the agent's memory
for one email.
"""
from typing import Literal, NotRequired, TypedDict

from pydantic import BaseModel, Field


class Email(TypedDict):
    id: str
    sender: str
    subject: str
    body: str
    # Only set for real Gmail messages (used to thread reply drafts):
    thread_id: NotRequired[str]
    message_id: NotRequired[str]
    reply_to: NotRequired[str]


Category = Literal[
    "Account & Security",
    "Career & Internships",
    "College The PSU",
    "Events",
    "Financial & Bread $",
    "Gotta respond ts",
    "Newsletters (boring)",
    "Personal",
    "W Deals %",
]


class Classification(BaseModel):
    """The LLM fills this in. Pydantic + with_structured_output() forces
    the model to return exactly these fields instead of free text."""

    is_spam: bool = Field(description="True for scams, phishing, or junk the user never signed up for")
    category: Category = Field(description="The best-fitting category for the email")
    priority: Literal["high", "medium", "low"] = Field(description="How urgently the user should look at it")
    reason: str = Field(description="One short sentence explaining the decision")


class EmailState(TypedDict, total=False):
    email: Email
    classification: Classification
    draft_reply: str
    action: str  # what the agent decided to do, for the final summary
    apply_to_gmail: bool  # True = actually label the email / save the draft in Gmail

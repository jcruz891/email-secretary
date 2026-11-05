"""The steps (nodes) of the agent. Each one is a plain Python function:
it takes the State and returns the fields it changed."""
import os
from functools import lru_cache

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from .state import Classification, EmailState

YOUR_NAME = os.getenv("YOUR_NAME", "Juan")


@lru_cache
def get_llm():
    # init_chat_model lets you swap providers by changing one string, e.g.
    # "anthropic:claude-haiku-5-5" or "openai:gpt-4o-mini". Set MODEL in .env.
    return init_chat_model(os.getenv("MODEL", "anthropic:claude-haiku-5-5"))


def format_email(state: EmailState) -> str:
    e = state["email"]
    return f"From: {e['sender']}\nSubject: {e['subject']}\n\n{e['body']}"


# ---------- Node 1: classify ----------
CLASSIFY_PROMPT = f"""You sort email for {YOUR_NAME}, a college student at Penn State.
First decide is_spam: scams, phishing, fake "you won" messages, suspicious links,
or junk they never signed up for. Be skeptical: urgent requests for passwords or
payment are phishing, even if they claim to be from Penn State.

Then pick exactly one category:
- Gotta respond ts: a real person is waiting on a reply from them (a question, a
  meeting request, an RSVP, a headcount). This beats every other category.
- Account & Security: real login alerts, password resets, 2-step verification,
  verification codes, new-device or new-app notices from services they use
- Career & Internships: jobs, internships, recruiters, Handshake, career fairs
- College The PSU: classes, professors, TAs, Canvas, LionPATH, university offices
- Events: club meetings, games, campus events, parties, things to attend
- Financial & Bread $: bills, banks, Venmo, financial aid, tuition, paychecks
- Newsletters (boring): mailing lists and digests that are just info
- Personal: friends and family (when no reply is needed)
- W Deals %: sales, discounts, coupons, promo codes from stores they use"""


def classify(state: EmailState) -> dict:
    classifier = get_llm().with_structured_output(Classification)
    result = classifier.invoke([
        SystemMessage(CLASSIFY_PROMPT),
        HumanMessage(format_email(state)),
    ])
    return {"classification": result}


# ---------- Router: decides which node runs next ----------
def route(state: EmailState) -> str:
    c = state["classification"]
    if c.is_spam:
        return "spam"
    if c.category == "Gotta respond ts":
        return "reply"
    return "file"


# ---------- Node 2a: spam ----------
def handle_spam(state: EmailState) -> dict:
    return {"action": "flagged as spam"}


# ---------- Node 2b: draft a reply ----------
REPLY_PROMPT = f"""You write email replies on behalf of {YOUR_NAME}, a Penn State student.
Match the tone of the sender (formal for professors, casual for friends).
Keep it short. Never invent facts, dates, or commitments; use [brackets]
for anything {YOUR_NAME} needs to fill in. Return only the reply body."""


def draft_reply(state: EmailState) -> dict:
    reply = get_llm().invoke([
        SystemMessage(REPLY_PROMPT),
        HumanMessage(format_email(state)),
    ])
    return {"draft_reply": reply.content, "action": "drafted a reply"}


# ---------- Node 2c: just file it ----------
def file_email(state: EmailState) -> dict:
    return {"action": f"filed under {state['classification'].category}"}


# ---------- Node 3: write the result back to Gmail ----------
def sync_gmail(state: EmailState) -> dict:
    """Runs after every branch. Does nothing for sample emails or --dry-run."""
    if not state.get("apply_to_gmail"):
        return {}
    from .gmail_client import LABEL_PREFIX, apply_label, save_draft

    c = state["classification"]
    label = f"{LABEL_PREFIX}/{'Spam' if c.is_spam else c.category}"
    apply_label(state["email"]["id"], label)
    action = f"{state['action']} → labeled {label}"
    if state.get("draft_reply"):
        save_draft(state["email"], state["draft_reply"])
        action += " + saved to Drafts"
    return {"action": action}

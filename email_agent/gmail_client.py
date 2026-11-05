"""Read Gmail, add labels, and save reply drafts.

Setup (one time):
  1. Go to https://console.cloud.google.com, create a project, enable the Gmail API.
  2. Google Auth Platform -> External, add yourself as a test user.
  3. Clients -> Create client -> Desktop app -> download as credentials.json
     into this project folder.
The first run opens a browser to sign in; a token.json is saved afterwards.
Never commit credentials.json or token.json to GitHub.

Permissions: "modify" lets the agent read mail, add labels, and create drafts.
This code never sends or deletes anything.
"""
import base64
import os
from email.message import EmailMessage
from functools import lru_cache

from .state import Email

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
LABEL_PREFIX = "Secretary"  # every label the agent makes lives under "Secretary/" in the Gmail sidebar


@lru_cache
def get_service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


# ---------- Labels ----------
_labels: dict[str, str] | None = None  # label name -> label id


def _all_labels() -> dict[str, str]:
    global _labels
    if _labels is None:
        resp = get_service().users().labels().list(userId="me").execute()
        _labels = {l["name"]: l["id"] for l in resp.get("labels", [])}
    return _labels


def get_or_create_label(name: str) -> str:
    labels = _all_labels()
    if name not in labels:
        # Gmail only shows "AI/Events" nested under "AI" if the parent exists.
        parent = name.split("/")[0]
        if "/" in name and parent not in labels:
            get_or_create_label(parent)
        created = get_service().users().labels().create(
            userId="me",
            body={"name": name, "labelListVisibility": "labelShow", "messageListVisibility": "show"},
        ).execute()
        labels[name] = created["id"]
    return labels[name]


def apply_label(message_id: str, name: str) -> None:
    get_service().users().messages().modify(
        userId="me", id=message_id, body={"addLabelIds": [get_or_create_label(name)]}
    ).execute()


# ---------- Drafts ----------
def save_draft(email: Email, body: str) -> None:
    """Saves a reply in Gmail's Drafts folder, threaded under the original email."""
    msg = EmailMessage()
    msg["To"] = email.get("reply_to") or email["sender"]
    subject = email["subject"]
    msg["Subject"] = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    if email.get("message_id"):
        msg["In-Reply-To"] = email["message_id"]
        msg["References"] = email["message_id"]
    msg.set_content(body)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    get_service().users().drafts().create(
        userId="me", body={"message": {"raw": raw, "threadId": email.get("thread_id")}}
    ).execute()


# ---------- Reading ----------
def _body_text(payload) -> str:
    """Emails are nested MIME parts; dig out the first plain-text part."""
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", "ignore")
    for part in payload.get("parts", []):
        text = _body_text(part)
        if text:
            return text
    return ""


def fetch_emails(limit: int = 10, query: str = "in:inbox newer_than:7d") -> list[Email]:
    """Returns up to `limit` emails, skipping ones the agent already labeled
    (so re-running doesn't create duplicate drafts)."""
    service = get_service()
    ours = {lid for name, lid in _all_labels().items() if name.startswith(LABEL_PREFIX + "/")}
    resp = service.users().messages().list(userId="me", q=query, maxResults=limit).execute()
    emails: list[Email] = []
    for m in resp.get("messages", []):
        msg = service.users().messages().get(userId="me", id=m["id"], format="full").execute()
        if ours & set(msg.get("labelIds", [])):
            continue
        headers = {h["name"].lower(): h["value"] for h in msg["payload"]["headers"]}
        emails.append({
            "id": m["id"],
            "thread_id": msg["threadId"],
            "message_id": headers.get("message-id", ""),
            "reply_to": headers.get("reply-to", ""),
            "sender": headers.get("from", ""),
            "subject": headers.get("subject", "(no subject)"),
            "body": _body_text(msg["payload"])[:4000],  # trim long emails to save tokens
        })
    return emails

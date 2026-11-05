"""Run the email agent.

  python main.py                  # use the fake sample emails
  python main.py --gmail -n 5     # organize your 5 newest Gmail messages (labels + drafts)
  python main.py --gmail --dry-run  # same, but only print; don't change Gmail
"""
import argparse

from dotenv import load_dotenv

load_dotenv()  # reads ANTHROPIC_API_KEY etc. from .env

from email_agent.graph import build_graph  # noqa: E402
from email_agent.sample_emails import SAMPLE_EMAILS  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gmail", action="store_true", help="read from Gmail instead of samples")
    parser.add_argument("-n", type=int, default=10, help="how many emails")
    parser.add_argument("--dry-run", action="store_true", help="with --gmail: print only, don't change Gmail")
    args = parser.parse_args()

    if args.gmail:
        from email_agent.gmail_client import fetch_emails
        emails = fetch_emails(limit=args.n)
    else:
        emails = SAMPLE_EMAILS[: args.n]

    agent = build_graph()
    apply = args.gmail and not args.dry_run
    if not emails:
        print("No new emails to organize (already-labeled ones are skipped).")

    for email in emails:
        result = agent.invoke({"email": email, "apply_to_gmail": apply})
        c = result["classification"]
        print("=" * 70)
        print(f"{email['subject']}  —  {email['sender']}")
        label = "🚫 SPAM" if c.is_spam else c.category
        print(f"  category: {label} | priority: {c.priority} | {result['action']}")
        print(f"  why: {c.reason}")
        if "draft_reply" in result:
            print("  --- draft reply (not sent" + (", saved in Gmail Drafts" if apply else "") + ") ---")
            for line in result["draft_reply"].splitlines():
                print(f"  {line}")


if __name__ == "__main__":
    main()

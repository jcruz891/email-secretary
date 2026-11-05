"""Fake emails so you can test the agent without touching your real inbox."""
from .state import Email

SAMPLE_EMAILS: list[Email] = [
    {
        "id": "1",
        "sender": "Prof. Rivera <arivera@psu.edu>",
        "subject": "CMPSC 442 project meeting",
        "body": "Hi, I saw your proposal on LangGraph agents. Can you meet Thursday at 2pm "
                "in Westgate to discuss scope? Let me know if that works.",
    },
    {
        "id": "2",
        "sender": "PSU IT Support <helpdesk@psu-verify-account.com>",
        "subject": "URGENT: Your Penn State account will be suspended",
        "body": "Your access ID will be deactivated in 24 hours. Click here and enter your "
                "password to keep your account: http://psu-verify-account.com/login",
    },
    {
        "id": "3",
        "sender": "LangChain Newsletter <news@langchain.dev>",
        "subject": "This week in LangGraph",
        "body": "New tutorials on human-in-the-loop agents, memory, and multi-agent systems.",
    },
    {
        "id": "4",
        "sender": "Maya <maya.chen@gmail.com>",
        "subject": "tailgate saturday?",
        "body": "yo are you coming to the tailgate before the game? we need a headcount for food",
    },
    {
        "id": "5",
        "sender": "Office of Student Aid <studentaid@psu.edu>",
        "subject": "Your Spring aid package is ready",
        "body": "Your financial aid offer for Spring is available in LionPATH. No action is "
                "required unless you want to make changes.",
    },
    {
        "id": "6",
        "sender": "Chipotle <rewards@chipotle.com>",
        "subject": "BOGO burritos for students this week 🌯",
        "body": "Show your student ID for buy-one-get-one entrees through Sunday. Use code PSU2026 online.",
    },
    {
        "id": "7",
        "sender": "Nittany AI Club <nittanyai@psu.edu>",
        "subject": "Workshop: build your first LangGraph agent",
        "body": "Join us Wednesday 7pm in IST 110 for a hands-on agents workshop. Pizza provided!",
    },
    {
        "id": "8",
        "sender": "Handshake <noreply@joinhandshake.com>",
        "subject": "3 new internships match your profile",
        "body": "Software Engineering Intern (Summer 2027) at Vanguard, ML Intern at Comcast, "
                "and Data Analyst Intern at Lockheed Martin. Apply on Handshake.",
    },
]

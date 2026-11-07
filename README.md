# Email Agent (LangChain + LangGraph)

An AI agent that reads email, sorts it into categories, flags spam, and drafts replies.
It **never sends anything**: drafts are printed for you to review.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then paste your API key into .env
python main.py              # runs on 5 fake sample emails
```

Get an Anthropic API key at https://console.anthropic.com. To use a different provider,
change `MODEL` in `.env` (e.g. `openai:gpt-4o-mini`) and `pip install langchain-openai`.

## How it works

```
START → classify ─┬─ spam  ─┐
                  ├─ reply ─┼→ END
                  └─ file  ─┘
```

| File | What it teaches |
|---|---|
| `email_agent/state.py` | **State**: the shared data every node reads and updates. **Structured output**: a Pydantic model the LLM must fill in. |
| `email_agent/nodes.py` | **Nodes**: plain functions that call the LLM. `init_chat_model` makes the provider swappable. |
| `email_agent/graph.py` | **Graph**: wiring nodes with edges, and a **conditional edge** (`route`) that picks the next step. |
| `email_agent/gmail_client.py` | Reading real mail with the Gmail API (read-only scope). |

### LangChain vs LangGraph
- **LangChain** gives you building blocks: chat models, prompts, structured output, tools.
- **LangGraph** arranges those blocks into a flow with state, branches, loops, and pauses.
  That's what turns "an LLM call" into "an agent".

## Using your real email

- **Gmail**: follow the steps at the top of `gmail_client.py`, then run `python main.py --gmail -n 5`.
  Each email gets a label under **Secretary Maurice/** in Gmail's sidebar (e.g. `Secretary Maurice/W Deals %`, `Secretary Maurice/Spam`), and
  replies are saved to **Drafts**. Nothing is sent, moved or deleted. Already-labeled emails are
  skipped on the next run. Add `--dry-run` to just print results.
- **Penn State (Outlook / Microsoft 365)**: needs the Microsoft Graph API and an Azure app
  registration, which university accounts often block. Easiest path: forward a few emails to
  a personal Gmail, or paste them into `sample_emails.py`.

Privacy note: running on real mail sends each email's text to the LLM provider.

## Ideas to try next (in rough order of difficulty)

1. Add a category (e.g. `clubs`) or tweak the prompts in `nodes.py` and see how results change.
2. Run emails in parallel with `agent.batch([...])` instead of a loop.
3. **Human-in-the-loop**: use LangGraph's `interrupt()` + a checkpointer so the agent pauses
   and asks you to approve/edit each draft.
4. Archive newsletters and deals automatically (remove the `INBOX` label).
5. Give the reply node **tools** (e.g. check your calendar before agreeing to a meeting).
6. Trace runs in LangSmith (set `LANGSMITH_TRACING=true`) to see every LLM call.

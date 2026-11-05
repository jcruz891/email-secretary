"""Wires the nodes together into a graph.

        START
          |
       classify
      /   |    \\
   spam reply  file
      \\   |    /
     sync_gmail      (adds the label / saves the draft in Gmail)
          |
         END
"""
from langgraph.graph import END, START, StateGraph

from .nodes import classify, draft_reply, file_email, handle_spam, route, sync_gmail
from .state import EmailState


def build_graph():
    g = StateGraph(EmailState)

    g.add_node("classify", classify)
    g.add_node("spam", handle_spam)
    g.add_node("reply", draft_reply)
    g.add_node("file", file_email)
    g.add_node("sync_gmail", sync_gmail)

    g.add_edge(START, "classify")
    # A conditional edge: route() returns "spam", "reply" or "file",
    # and LangGraph jumps to the node with that name.
    g.add_conditional_edges("classify", route, ["spam", "reply", "file"])
    # All three branches join back together at sync_gmail.
    for node in ["spam", "reply", "file"]:
        g.add_edge(node, "sync_gmail")
    g.add_edge("sync_gmail", END)

    return g.compile()

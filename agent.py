"""The agent loop. The model picks its own tools and retries its own searches,
which is why there's no rewrite or grading node here."""

import os
from datetime import date, datetime, timedelta

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

import prompts

COMPANY = os.getenv("COMPANY_NAME", "the company")
ANSWER_MODEL = "llama-3.3-70b-versatile"
JUDGE_MODEL = "llama-3.1-8b-instant"
TOP_K = 4
MAX_TOOL_TURNS = 5

UNVERIFIED = ("\n\n---\n*I couldn't match all of this back to the handbook. "
              "Check with HR before you rely on it.*")


class Grounded(BaseModel):
    grounded: bool = Field(description="every claim appears in the search results")


def build_agent(vectorstore):

    @tool
    def search_policy(query: str) -> str:
        """Search the company policy documents. Use the formal wording a
        handbook would use, not casual phrasing."""
        hits = vectorstore.similarity_search(query, k=TOP_K)
        if not hits:
            return "Nothing matched."
        blocks = []
        for i, doc in enumerate(hits, 1):
            source = os.path.basename(doc.metadata.get("source", "policy"))
            page = doc.metadata.get("page", "?")
            blocks.append(f"[p{page}]\n{doc.page_content}")
        return "\n\n".join(blocks)

    @tool
    def calculate_date(start_date: str, days: int, working_days_only: bool) -> str:
        """Add days to a date. start_date is YYYY-MM-DD. Pass
        working_days_only as true for notice periods counted in working days,
        false otherwise."""
        try:
            current = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            return "Date must be YYYY-MM-DD."
        if working_days_only:
            counted = 0
            while counted < days:
                current += timedelta(days=1)
                if current.weekday() < 5:
                    counted += 1
        else:
            current += timedelta(days=days)
        unit = "working days" if working_days_only else "calendar days"
        return f"{days} {unit} from {start_date} is {current:%A, %d %B %Y}."

    @tool
    def escalate_to_hr(question: str, reason: str) -> str:
        """Draft an email to HR when the handbook can't answer the question.
        Returns a draft for the employee to send themselves."""
        return (f"To: hr@company.com\n"
                f"Subject: Handbook doesn't cover this\n\n"
                f"Hi,\n\nI couldn't find this in the employee handbook:\n\n"
                f"{question}\n\n{reason}\n\nCould you advise?\n\nThanks")

    toolbelt = [search_policy, calculate_date, escalate_to_hr]
    llm = ChatGroq(model=ANSWER_MODEL, temperature=0)
    llm_tools = llm.bind_tools(toolbelt, parallel_tool_calls=False)
    must_search = llm.bind_tools(toolbelt, tool_choice="search_policy")
    judge = ChatGroq(model=JUDGE_MODEL, temperature=0).with_structured_output(Grounded)
    def searches(messages):
        return "\n\n".join(m.content for m in messages
                           if isinstance(m, ToolMessage) and m.name == "search_policy")

    def used_up_budget(messages):
        return sum(1 for m in messages
                   if isinstance(m, AIMessage) and m.tool_calls) >= MAX_TOOL_TURNS
    def is_text_tool_call(message):
        text = (message.content or "")
        return any(name in text for name in
                   ("search_policy", "calculate_date", "escalate_to_hr", "<function"))
        
    def think(state):
        system = SystemMessage(prompts.SYSTEM.format(
            company=COMPANY, today=date.today().isoformat()))
        history = [system] + state["messages"]

        if used_up_budget(state["messages"]):
            model = llm
        elif not searches(state["messages"]):
            model = must_search      # first pass always hits the handbook
        else:
            model = llm_tools

        try:
            reply = model.invoke(history)
        except Exception:
            reply = None

        if reply is None or (not reply.tool_calls and is_text_tool_call(reply)):
            nudge = SystemMessage(
                "Use the tool calling interface. Do not write function calls "
                "in your reply text.")
            try:
                reply = model.invoke(history + [nudge])
            except Exception:
                reply = llm.invoke(history)

        return {"messages": [reply]}

    def verify(state):
        answer = state["messages"][-1].content
        try:
            ok = judge.invoke(prompts.GROUNDING.format(
                context=searches(state["messages"]), answer=answer)).grounded
        except Exception:
            ok = True  # a parse failure shouldn't swallow a good answer
        if ok:
            return {}
        return {"messages": [AIMessage(answer + UNVERIFIED)]}

    def next_step(state):
        last = state["messages"][-1]
        if getattr(last, "tool_calls", None):
            return "tools"
        return "verify" if searches(state["messages"]) else END

    graph = StateGraph(MessagesState)
    graph.add_node("think", think)
    graph.add_node("tools", ToolNode(toolbelt))
    graph.add_node("verify", verify)

    graph.add_edge(START, "think")
    graph.add_conditional_edges("think", next_step,
                                {"tools": "tools", "verify": "verify", END: END})
    graph.add_edge("tools", "think")
    graph.add_edge("verify", END)

    return graph.compile(checkpointer=MemorySaver())


if __name__ == "__main__":
    from dotenv import load_dotenv
    from langchain_core.messages import HumanMessage

    import ingest

    load_dotenv()
    bot = build_agent(ingest.load())
    thread = {"configurable": {"thread_id": "cli"}}
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if question.lower() in {"exit", "quit", ""}:
            break
        result = bot.invoke({"messages": [HumanMessage(question)]}, thread)
        print("\n" + result["messages"][-1].content)
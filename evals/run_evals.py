"""Runs the question set and reports three numbers: did retrieval surface the
right section, did the answer contain the right facts, and did it stay inside
the sources."""

import json
import sys
import uuid
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage

import ingest
from agent import build_agent

load_dotenv()

QUESTIONS = Path(__file__).parent / "questions.jsonl"


def contains_any(text, terms):
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def main():
    bot = build_agent(ingest.load())
    cases = [json.loads(line) for line in QUESTIONS.read_text().splitlines() if line.strip()]

    retrieval_hits = 0
    answer_hits = 0
    wrongly_answered = 0
    failures = []

    for case in cases:
        state = bot.invoke(
            {"messages": [HumanMessage(case["question"])]},
            {"configurable": {"thread_id": str(uuid.uuid4())}},
        )
        answer = state["messages"][-1].content
        context = " ".join(m.content for m in state["messages"]
                           if isinstance(m, ToolMessage) and m.name == "search_policy")

        if case["answerable"]:
            got_context = contains_any(context, case["expect"])
            got_answer = contains_any(answer, case["expect"])
            retrieval_hits += got_context
            answer_hits += got_answer
            if not got_answer:
                failures.append((case["question"], "missed", answer[:120]))
        else:
            # Should have admitted it doesn't know rather than inventing something
            refused = contains_any(answer, [
                "couldn't find", "could not find", "not covered", "doesn't cover",
                "does not cover", "doesn't specify", "does not specify",
                "doesn't provide", "does not provide", "not in the handbook",
                "unable to find", "check with hr", "hr@",
            ])
            if not refused:
                wrongly_answered += 1
                failures.append((case["question"], "made something up", answer[:120]))
        time.sleep(2)

    answerable = sum(1 for c in cases if c["answerable"])
    unanswerable = len(cases) - answerable

    print(f"\n{len(cases)} questions ({answerable} answerable, {unanswerable} not)")
    print(f"retrieval found the right section : {retrieval_hits}/{answerable}")
    print(f"answer contained the right facts  : {answer_hits}/{answerable}")
    print(f"invented an answer when it shouldn't: {wrongly_answered}/{unanswerable}")

    if failures:
        print("\nfailures:")
        for question, kind, snippet in failures:
            print(f"  [{kind}] {question}\n      {snippet}")


if __name__ == "__main__":
    main()
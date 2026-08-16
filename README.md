# PDFQuery

Answers new starters' questions about company policy from the employee
handbook. More usefully, it tells you when the handbook doesn't say.


## The problem with the first version

I built this originally as a normal RAG chatbot. Embed the question, pull four
chunks, stuff them in a prompt, answer. It demoed fine and broke on real
questions.

"What about time off?" retrieved nothing useful, because handbooks say "annual
leave" and nobody asks it that way. "How much notice do I give, and does that
change during probation?" needed two lookups and got one. And when retrieval
came back with nothing, the model answered anyway using what it knows about
employment law in general, which is the last thing you want from an HR tool.

So I rebuilt it as an agent.

## What the agent actually does

The model gets three tools and decides for itself what to do with them. There's
no fixed path anymore. One question might take a single step, another takes
five.

In practice that means:

It rewrites my question before searching. People ask casually, handbooks are
written formally, so "can I quit" becomes a search for termination and notice
periods.

It searches again when a search fails. I asked about notice periods during
probation and watched it run three searches with three different phrasings
before deciding the handbook doesn't specify one. Nobody wrote that logic. It
just reacts to what comes back.

It splits compound questions into separate searches rather than one query that
half-matches both halves.

It routes to the right tool. Dates go to a date calculator, because language
models are bad at counting days and I'd rather not find out the hard way.
Questions the handbook can't answer go to an email drafter for HR.

Then before you see anything, a smaller model checks whether every claim in the
answer actually appears in the text that was retrieved. If it doesn't, the
answer gets flagged.

Five tool calls is the hard limit. After that the tools get taken away and it
has to answer with what it has.

**What it isn't:** there's no goal beyond the question in front of it, no plan
across turns, and no side effects. The escalation tool writes an email, it
doesn't send one. Three tools is a small action space. The honest name for this
is corrective RAG, not an autonomous agent.

## How it's put together

```
      ┌──────────────────────────────┐
      │                              │
 ──> think ──> tools ────────────────┘
       │
       ├── searched ──> verify ──> answer
       │
       └── didn't need to search ──> answer
```

Three nodes on LangGraph. `think` calls the model, `tools` runs whatever it
asked for, `verify` does the grounding check.

Worth noting: the loop between `think` and `tools` replaced four nodes I'd
hand-written for query rewriting and relevance grading. The model does both
itself, so the agent version is shorter than the pipeline version. That
surprised me.

Tools are `search_policy` (six passages with page numbers), `calculate_date`,
and `escalate_to_hr`.

## Running it

```bash
git clone https://github.com/swethamkulkarni/PDFQuery-RAG-Chatbot.git
cd PDFQuery-RAG-Chatbot
pip install -r requirements.txt
cp .env.example .env      # add your Groq key
```

Handbook PDFs go in `data/`. Then:

```bash
python ingest.py
streamlit run app.py
```

`python agent.py` for a terminal version.

## Testing

35 questions in `evals/questions.jsonl`. 22 answerable from the handbook, 13
not. The 13 are the interesting ones, and 9 of those are near-misses where the
handbook discusses the topic without answering the question. Parental leave,
pensions, overtime, probation notice periods. Harder than obviously
out-of-scope questions because retrieval brings back something that looks
right.

```bash
python evals/run_evals.py
```

### What I found

**It invented a leave entitlement.** I asked how many days of annual leave I
get and it told me a specific number, with a page citation. There is no leave
figure anywhere in the 47 page handbook. The number came from what the model
knows about typical employment terms, the citation pointed at a real page, and
my grounding check waved it through. Nothing about the output looked wrong. I
only caught it because I went and read the source document.

**Retrieval depends on which words you use.** "Annual leave" found the right
section. "Holiday entitlement" landed in the benefits pages, among stock
options and social events. Same handbook, same question, different words.

**Refusals can be wrong too.** When it couldn't find something it told me the
handbook has no policy on it. It sees six chunks out of 254 per search, so it
has no way of knowing that. Correct answer, indefensible reasoning.

**It sometimes skips retrieval without failing.** Groq's LLaMA occasionally
writes the tool call out as plain text instead of calling it. Nothing runs, no
error appears, and it answers from general knowledge. I found this in the
LangSmith traces, not from anything visible in the app.

### What I changed

The prompt now says it can't state a figure or date that didn't come out of a
lookup, and that it can only say it didn't find something, never that the
handbook has no policy on it.

Both are patches. Prompting makes fabrication less likely, it doesn't stop it.
The two things that would actually move the numbers are hybrid retrieval,
adding keyword search alongside the vector search to fix the vocabulary
problem, and a better grounding check, either a bigger model or verifying
claims one sentence at a time instead of judging the answer as a whole.

### Cost

About 12,000 tokens per question, against roughly 2,000 for the old fixed
chain. Nearly all of it is input, not output, because the whole conversation
plus every retrieved chunk gets resent on each pass through the loop. So the
better answers cost about 6x, and if I needed to bring that down I'd start with
what goes back into the loop rather than what comes out.

## Stack

Python, LangGraph, ChromaDB, Streamlit, LangSmith. Embeddings are fastembed
with BAAI/bge-small-en-v1.5, running locally, so no API cost per query.
Inference is Groq: LLaMA-3.3-70B writes the answers, LLaMA-3.1-8B does the
grounding check because it's a yes/no judgement and the big model is wasted on
it.

I started with OpenAI embeddings and moved off them after a quota error. Tried
sentence-transformers next and it broke, because the version of transformers it
pulls in wants a newer PyTorch than I had. fastembed runs on ONNX instead, 50MB
rather than 2GB, which is also what makes free tier deployment possible.

The ingestion and retrieval baseline came from Alejandro AO's LangChain RAG
tutorial. The agent loop, tools, grounding check, eval set and the failure
analysis above are mine.

## Limits

One vector store, no metadata filtering, so it can't tell you which version of
a policy was in force last March. Semantic search only, which is the direct
cause of the vocabulary problem. Conversation memory dies with the Streamlit
session. The HR escalation drafts an email but doesn't send it. And the
grounding judge is the same family of model that wrote the answer, so it
probably shares some blind spots.

It's a prototype. Running it for real would need persistent storage, access
control so people only see policies that apply to them, audit logs, and an
escalation path that reaches an actual human.
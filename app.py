import uuid

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

import ingest
from agent import build_agent

load_dotenv()

st.set_page_config(page_title="Policy Assistant", page_icon="📘")
st.title("📘 Policy Assistant")

STATUS = {
    "search_policy": "Looking up: {query}",
    "calculate_date": "Counting the days",
    "escalate_to_hr": "Drafting an email to HR",
}


@st.cache_resource
def get_agent():
    return build_agent(ingest.load())


bot = get_agent()

if "thread" not in st.session_state:
    st.session_state.thread = str(uuid.uuid4())
    st.session_state.log = []

with st.sidebar:
    st.caption("Answers come from the handbook only. Nothing else.")
    if st.button("Start over"):
        st.session_state.clear()
        st.rerun()

for who, text in st.session_state.log:
    with st.chat_message(who):
        st.markdown(text)

question = st.chat_input("Annual leave, notice periods, expenses...")

if question:
    st.session_state.log.append(("user", question))
    with st.chat_message("user"):
        st.markdown(question)

    answer = "Something broke. Check the terminal."
    retrieved = []

    with st.chat_message("assistant"):
        with st.status("Working on it", expanded=True) as status:
            stream = bot.stream(
                {"messages": [HumanMessage(question)]},
                {"configurable": {"thread_id": st.session_state.thread}},
                stream_mode="updates",
            )
            for step in stream:
                for node, update in step.items():
                    if not isinstance(update, dict):
                        continue
                    for msg in update.get("messages", []):
                        if isinstance(msg, AIMessage) and msg.tool_calls:
                            for call in msg.tool_calls:
                                line = STATUS.get(call["name"], call["name"])
                                st.write(line.format(query=call["args"].get("query", "")))
                        elif isinstance(msg, ToolMessage):
                            if msg.name == "search_policy":
                                retrieved.append(msg.content)
                        elif isinstance(msg, AIMessage) and msg.content:
                            answer = msg.content
                    if node == "verify" and update.get("messages"):
                        st.write("Checking the answer against the sources")
            status.update(label="Done", state="complete", expanded=False)

        st.markdown(answer)

        if retrieved:
            with st.expander("What it read"):
                for block in retrieved:
                    st.caption(block[:1200])

    st.session_state.log.append(("assistant", answer))
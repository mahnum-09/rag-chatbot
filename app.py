import uuid

import streamlit as st
import chat as rag


st.set_page_config(
    page_title=" AI Chatbot",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 950px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .hero {
        padding: 1.4rem 1.6rem;
        border-radius: 16px;
        background: linear-gradient(120deg, #172554, #1d4ed8);
        color: white;
        margin-bottom: 1.2rem;
    }
    .hero p {
        color: #e0e7ff;
        margin-bottom: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1> AI Chatbot</h1>
        <p>Ask questions about your resume and anomaly detection report.
        Powered by RAG, Gemini, and PostgreSQL.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Create a fresh browser-session conversation if needed.
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []

# Keep the RAG backend synchronized with the selected conversation.
rag.session_id = st.session_state.session_id
rag.conversation_history = [
    {"role": item["role"], "content": item["content"]}
    for item in st.session_state.messages
    if item["role"] in ("user", "assistant")
]

with st.sidebar:
    st.header("💬 Chat controls")

    if st.button("＋ New conversation", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        rag.session_id = st.session_state.session_id
        rag.conversation_history = []
        st.rerun()

    st.divider()
    st.subheader("Saved conversations")

    try:
        saved_conversations = rag.list_conversations()
    except Exception as error:
        saved_conversations = []
        st.warning(f"Could not load saved chats: {error}")

    if saved_conversations:
        # list_conversations rows: session_id, started_at, last_activity, message_count
        def conversation_label(row):
            sid, started_at, last_activity, message_count = row
            stamp = last_activity.strftime("%Y-%m-%d %H:%M") if last_activity else "Date unknown"
            return f"{stamp} · {message_count} messages · {str(sid)[:8]}"

        labels = [conversation_label(row) for row in saved_conversations]
        selected_label = st.selectbox(
            "Choose a saved chat",
            options=labels,
            key="saved_conversation_choice",
        )

        if st.button("Load selected conversation", use_container_width=True):
            selected_index = labels.index(selected_label)
            selected_id = str(saved_conversations[selected_index][0])

            try:
                loaded_messages = rag.load_history(selected_id)
                st.session_state.session_id = selected_id
                st.session_state.messages = [
                    {
                        "role": item["role"],
                        "content": item["content"],
                    }
                    for item in loaded_messages
                    if item.get("role") in ("user", "assistant")
                ]
                rag.session_id = selected_id
                rag.conversation_history = [
                    {"role": item["role"], "content": item["content"]}
                    for item in st.session_state.messages
                ]
                st.rerun()
            except Exception as error:
                st.error(f"Could not load this conversation: {error}")
    else:
        st.caption("No saved conversations found yet.")

    st.caption("Completed question-and-answer turns are saved in PostgreSQL.")
    st.divider()
    st.subheader("Try asking")

    examples = [
        "What anomaly detection project did I work on?",
        "Which threshold did I use?",
        "How many CSV files were combined?",
        "Explain the anomaly detection workflow.",
    ]

    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state.pending_question = example
            st.rerun()

    st.divider()
    st.caption("Sources are shown below answers when available.")

# Display messages for the current conversation.
for item in st.session_state.messages:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])
        if item.get("sources"):
            st.caption("Sources: " + ", ".join(item["sources"]))

question = st.chat_input("Ask a question about your documents...")

if "pending_question" in st.session_state:
    question = st.session_state.pop("pending_question")

if question:
    question = question.strip()

    if question:
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating answer..."):
                try:
                    # Ensure backend history includes the latest visible messages.
                    rag.session_id = st.session_state.session_id
                    rag.conversation_history = [
                        {"role": item["role"], "content": item["content"]}
                        for item in st.session_state.messages[:-1]
                        if item["role"] in ("user", "assistant")
                    ]

                    result = rag.answer_question(question)

                    if not isinstance(result, dict):
                        raise RuntimeError(
                            "chat.py answer_question() did not return a result. "
                            "Make sure you replaced it with the updated chat.py."
                        )

                    answer = result.get("answer", "").strip()
                    sources = result.get("sources", [])

                    if not answer:
                        answer = "I couldn't generate an answer. Please try again."

                    st.markdown(answer)

                    if sources:
                        st.caption("Sources: " + ", ".join(sources))

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        }
                    )

                except Exception as error:
                    st.error(f"Could not generate an answer: {error}")

        st.rerun()

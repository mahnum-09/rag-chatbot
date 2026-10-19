import uuid
import streamlit as st
import chat as rag

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
)

# Custom CSS for crisp Dark Mode and Minimalist Layout
st.markdown(
    """
    <style>
    /* Global App Background & Text Color */
    .stApp {
        background-color: #0e1117;
        color: #f3f4f6;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px sold rgba(255, 255, 255, 0.08);
        padding-top: 1rem;
    }

    /* Main container width */
    .block-container {
        padding-top: 3rem;
        max-width: 1000px;
    }

    /* Minimalist Centered Greeting */
    .welcome-container {
        text-align: center;
        margin-top: 15vh;
        margin-bottom: 2rem;
    }
    .welcome-container h1 {
        font-size: 2.5rem;
        font-weight: 500;
        color: #ffffff;
    }

    /* Sidebar Buttons (Links style) */
    .stSidebar .stButton button {
        background: transparent;
        border: none;
        color: #d1d5db;
        text-align: left;
        width: 100%;
        padding: 0.4rem 0.6rem;
        border-radius: 6px;
        font-size: 0.9rem;
        transition: background 0.15s ease;
    }
    .stSidebar .stButton button:hover {
        background-color: rgba(255, 255, 255, 0.08);
        color: #ffffff;
    }

    /* Chat Message Text and Background Fixes */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1rem;
        color: #f3f4f6 !important;
    }
    
    /* Ensure markdown text inside chat is fully visible */
    .stChatMessage p, .stChatMessage li {
        color: #f3f4f6 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []

# Synchronize backend
rag.session_id = st.session_state.session_id
rag.conversation_history = [
    {"role": item["role"], "content": item["content"]}
    for item in st.session_state.messages
    if item["role"] in ("user", "assistant")
]

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚡ AI Workspace")
    
    if st.button("✏️ New chat", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        rag.session_id = st.session_state.session_id
        rag.conversation_history = []
        st.rerun()

    st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.75rem; color: #9ca3af; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Recent History</p>", unsafe_allow_html=True)

    try:
        saved_conversations = rag.list_conversations()
    except Exception as error:
        saved_conversations = []

    if saved_conversations:
        def conversation_label(row):
            sid, started_at, last_activity, message_count = row
            stamp = last_activity.strftime("%b %d") if last_activity else "Recent"
            return f"💬 {stamp} ({message_count} msgs)"

        labels = [conversation_label(row) for row in saved_conversations]
        selected_label = st.selectbox(
            "Saved Chats",
            options=labels,
            label_visibility="collapsed",
            key="saved_conversation_choice",
        )

        if st.button("📂 Load Selected Chat", use_container_width=True):
            selected_index = labels.index(selected_label)
            selected_id = str(saved_conversations[selected_index][0])

            try:
                loaded_messages = rag.load_history(selected_id)
                st.session_state.session_id = selected_id
                st.session_state.messages = [
                    {"role": item["role"], "content": item["content"]}
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
                st.error(f"Error loading chat: {error}")
    else:
        st.caption("No history saved yet.")

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.75rem; color: #9ca3af; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>Quick Prompts</p>", unsafe_allow_html=True)

    examples = [
        "What project did I work on?",
        "Which threshold did I use?",
        "How many CSV files were combined?",
    ]

    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state.pending_question = example
            st.rerun()

# --- MAIN CHAT AREA ---

# Show centered welcome title only if conversation is empty
if not st.session_state.messages:
    st.markdown(
        """
        <div class="welcome-container">
            <h1>Hello, User</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Display message history
for item in st.session_state.messages:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])
        if item.get("sources"):
            st.caption("Sources: " + ", ".join(item["sources"]))

# Chat input bar at the bottom
question = st.chat_input("How can I help you today?")

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
            with st.spinner("Thinking..."):
                try:
                    rag.session_id = st.session_state.session_id
                    rag.conversation_history = [
                        {"role": item["role"], "content": item["content"]}
                        for item in st.session_state.messages[:-1]
                        if item["role"] in ("user", "assistant")
                    ]

                    result = rag.answer_question(question)
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
                    st.error(f"Error: {error}")

        st.rerun()
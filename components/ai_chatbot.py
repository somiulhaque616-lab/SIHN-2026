"""
OptiFreight AI — Chatbot UI Component
Integrated cleanly into the Streamlit layout without breaking CSS.
"""

import streamlit as st
from datetime import datetime
from services.gemini_service import (
    get_gemini_status,
    build_optifreight_context,
    generate_gemini_response,
)

QUICK_PROMPTS = [
    "Should I Charter Now?",
    "Explain the Freight Forecast",
    "Analyze Current Market",
    "Check Route Risk",
]

WELCOME_MESSAGE = (
    "Hello! I'm OptiFreight AI. How can I assist with your maritime decisions today?"
)


def init_chat_session():
    """Ensure session state variables for chatbot are initialized."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None


def clear_chat():
    """Clear all chat history."""
    st.session_state.chat_history = []


@st.fragment
def render_chatbot(all_data: dict):
    """
    Renders the AI chatbot at the bottom of the application.
    Uses native Streamlit containers to ensure 100% functionality.
    """
    init_chat_session()
    status_info = get_gemini_status()
    render_chatbot_css()

    st.markdown('<div class="ai-section-divider"></div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div>
                    <h3 style="margin:0; color:#fff; font-size: 1.2rem;">✦ OptiFreight AI</h3>
                    <div style="color:#00d4ff; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">Maritime Intelligence Assistant</div>
                </div>
                <div class="ai-status-badge {status_info['badge_class']}">{status_info['badge']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_main, col_side = st.columns([3, 1])

        with col_side:
            st.markdown('<div style="margin-bottom: 12px; font-size: 0.8rem; color:#94a3b8; font-weight:600;">SUGGESTED QUERIES</div>', unsafe_allow_html=True)
            for idx, prompt_text in enumerate(QUICK_PROMPTS):
                if st.button(f"💡 {prompt_text}", key=f"quick_prompt_{idx}", use_container_width=True):
                    st.session_state.pending_prompt = prompt_text
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Clear Chat", key="clear_chat_btn", use_container_width=True):
                clear_chat()
                st.rerun()

        with col_main:
            # Chat Display Area
            chat_container = st.container(height=400)
            with chat_container:
                if not st.session_state.chat_history:
                    st.markdown(
                        f"""
                        <div class="chat-bubble assistant-bubble welcome-bubble">
                            <div class="bubble-sender">OptiFreight AI</div>
                            <div class="bubble-content">{WELCOME_MESSAGE}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    for msg in st.session_state.chat_history:
                        sender = "You" if msg["role"] == "user" else "OptiFreight AI"
                        bubble_class = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
                        st.markdown(
                            f"""
                            <div class="chat-bubble {bubble_class}">
                                <div class="bubble-sender">{sender}</div>
                                <div class="bubble-content">{msg['content']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            # Input processing
            user_input_text = None
            if st.session_state.pending_prompt:
                user_input_text = st.session_state.pending_prompt
                st.session_state.pending_prompt = None

            # Chat Input Form
            with st.form(key="chat_input_form", clear_on_submit=True):
                col_in, col_send = st.columns([5, 1])
                with col_in:
                    form_text = st.text_input(
                        "Ask OptiFreight AI...",
                        placeholder="Type maritime query (e.g. Should I charter now?)...",
                        label_visibility="collapsed",
                        key="chat_text_input_field",
                    )
                with col_send:
                    submitted = st.form_submit_button("Send ➔", use_container_width=True)

            if submitted and form_text.strip():
                user_input_text = form_text.strip()

            if user_input_text:
                st.session_state.chat_history.append({"role": "user", "content": user_input_text})
                
                with st.spinner("OptiFreight AI is analyzing..."):
                    context_str = build_optifreight_context(all_data, st.session_state)
                    response_text = generate_gemini_response(
                        user_message=user_input_text,
                        chat_history=st.session_state.chat_history[:-1],
                        context_str=context_str,
                    )
                    st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                st.rerun()


def render_chatbot_css():
    st.markdown(
        """
        <style>
        .ai-section-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.4), transparent);
            margin: 40px 0 20px 0;
        }
        .ai-status-badge {
            font-size: 0.75rem;
            font-weight: 700;
            padding: 6px 12px;
            border-radius: 12px;
            display: inline-block;
        }
        .ai-status-badge.online {
            background: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .ai-status-badge.offline {
            background: rgba(245, 158, 11, 0.15);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .chat-bubble {
            border-radius: 12px;
            padding: 14px 18px;
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 16px;
            word-wrap: break-word;
            animation: fadeIn 0.3s ease;
        }
        .bubble-sender {
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }
        .user-bubble {
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.2);
            color: #ffffff;
            margin-left: 10%;
        }
        .user-bubble .bubble-sender {
            color: #00d4ff;
        }
        .assistant-bubble {
            background: rgba(17, 35, 64, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #e2e8f0;
            margin-right: 10%;
        }
        .assistant-bubble .bubble-sender {
            color: #14b8a6;
        }
        .welcome-bubble {
            border-color: rgba(0, 212, 255, 0.3);
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(17, 35, 64, 0.8) 100%);
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        /* Style Streamlit components inside chat area */
        div[data-testid="stForm"] {
            background: rgba(17, 35, 64, 0.4);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 12px;
            padding: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


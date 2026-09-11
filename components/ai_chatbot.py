"""
OptiFreight AI — Chatbot UI Component
Floating dark-navy cyan-glowing glassmorphism AI assistant panel.
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
    "Explain AI Recommendation",
]

WELCOME_MESSAGE = (
    "Hello! I'm OptiFreight AI. I can help you analyze freight markets, "
    "chartering decisions, route risks, procurement, forecasts, and maritime intelligence."
)


def init_chat_session():
    """Ensure session state variables for chatbot are initialized."""
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None


def toggle_chat():
    """Toggle chat panel open/closed state."""
    st.session_state.chat_open = not st.session_state.chat_open


def clear_chat():
    """Clear all chat history."""
    st.session_state.chat_history = []


def render_chatbot(all_data: dict):
    """
    Renders the floating chatbot toggle button and floating chat panel.
    Maintains dark navy glassmorphism aesthetic matching OptiFreight.
    """
    init_chat_session()
    status_info = get_gemini_status()

    # 1. Floating Toggle Button (Always Visible at Bottom-Right)
    btn_label = "✕ Close AI" if st.session_state.chat_open else "✦ OptiFreight AI"
    
    # We place the launcher floating in fixed position using CSS class wrapper
    st.markdown(
        f"""
        <div class="chatbot-launcher-container">
            <div class="chatbot-launcher-sub">Maritime Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Floating trigger column layout at the bottom right using st.popover or fixed container
    # Streamlit column overlay in sidebar or main page
    with st.container():
        # Render CSS styles for chatbot overlay
        render_chatbot_css()

        # Render floating toggle button
        col_space, col_btn = st.columns([1, 1])
        
        # Render Floating Chat Panel if chat_open is True
        if st.session_state.chat_open:
            render_chat_panel(all_data, status_info)

        # Floating trigger button placed in fixed container
        st.markdown('<div class="floating-chatbot-trigger">', unsafe_allow_html=True)
        if st.button(
            btn_label,
            key="toggle_chatbot_btn",
            use_container_width=True,
            on_click=toggle_chat,
        ):
            pass
        st.markdown('</div>', unsafe_allow_html=True)


def render_chat_panel(all_data: dict, status_info: dict):
    """Render the main floating chatbot panel when open."""
    st.markdown('<div class="chatbot-panel-wrapper">', unsafe_allow_html=True)
    
    # Header area
    st.markdown(
        f"""
        <div class="chatbot-header">
            <div class="header-left">
                <div class="chat-title">✦ OptiFreight AI</div>
                <div class="chat-subtitle">Maritime Intelligence Assistant</div>
            </div>
            <div class="header-right">
                <span class="ai-status-badge {status_info['badge_class']}">{status_info['badge']}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Top Controls (Clear Chat)
    col_c1, col_c2 = st.columns([3, 1])
    with col_c2:
        if st.button("🗑️ Clear Chat", key="clear_chat_btn", use_container_width=True):
            clear_chat()
            st.rerun()

    # Chat Messages Area
    st.markdown('<div class="chat-messages-container">', unsafe_allow_html=True)

    # Welcome message if chat history is empty
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
        
        # Quick prompts
        st.markdown('<div class="quick-prompts-label">Suggested Intelligence Queries:</div>', unsafe_allow_html=True)
        q_cols = st.columns(2)
        for idx, prompt_text in enumerate(QUICK_PROMPTS):
            col_target = q_cols[idx % 2]
            with col_target:
                if st.button(f"💡 {prompt_text}", key=f"quick_prompt_{idx}", use_container_width=True):
                    st.session_state.pending_prompt = prompt_text
                    st.rerun()
    else:
        # Display chat history
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

    st.markdown('</div>', unsafe_allow_html=True)

    # Process pending quick prompt if selected
    user_input_text = None
    if st.session_state.pending_prompt:
        user_input_text = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    # Input Form inside panel
    with st.form(key="chat_input_form", clear_on_submit=True):
        col_in, col_send = st.columns([4, 1])
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

    # If message received, process response
    if user_input_text:
        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": user_input_text})
        
        # Show thinking state and fetch response
        with st.spinner("OptiFreight AI analyzing market data..."):
            context_str = build_optifreight_context(all_data, st.session_state)
            response_text = generate_gemini_response(
                user_message=user_input_text,
                chat_history=st.session_state.chat_history[:-1],  # History without current prompt
                context_str=context_str,
            )
            st.session_state.chat_history.append({"role": "assistant", "content": response_text})
        
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_chatbot_css():
    """CSS styles for the chatbot component matching OptiFreight design tokens."""
    st.markdown(
        """
        <style>
        /* ── Floating Chatbot Button Launcher ── */
        .floating-chatbot-trigger {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 99999;
            width: 220px;
        }

        .floating-chatbot-trigger button {
            background: linear-gradient(135deg, #00d4ff 0%, #0077b6 100%) !important;
            color: #040d1a !important;
            font-weight: 800 !important;
            font-size: 0.95rem !important;
            border: 1px solid #00d4ff !important;
            border-radius: 30px !important;
            padding: 12px 20px !important;
            box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4), 0 0 15px rgba(0, 212, 255, 0.2) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        .floating-chatbot-trigger button:hover {
            transform: translateY(-3px) scale(1.03) !important;
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.6), 0 0 25px rgba(0, 212, 255, 0.3) !important;
            background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%) !important;
        }

        /* ── Floating Chatbot Panel Wrapper ── */
        .chatbot-panel-wrapper {
            position: fixed;
            bottom: 80px;
            right: 24px;
            width: 420px;
            max-width: calc(100vw - 32px);
            height: 620px;
            max-height: calc(100vh - 120px);
            background: rgba(7, 20, 38, 0.95) !important;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(0, 212, 255, 0.35);
            border-radius: 16px;
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.6), 0 0 25px rgba(0, 212, 255, 0.2);
            z-index: 99998;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            animation: chatPanelSlideUp 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            padding: 16px;
        }

        @keyframes chatPanelSlideUp {
            0% { opacity: 0; transform: translateY(20px) scale(0.96); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }

        /* Header */
        .chatbot-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(0, 212, 255, 0.2);
            margin-bottom: 12px;
        }
        .chat-title {
            font-size: 1.1rem;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.01em;
        }
        .chat-subtitle {
            font-size: 0.72rem;
            color: #00d4ff;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .ai-status-badge {
            font-size: 0.7rem;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 12px;
        }
        .ai-status-badge.online {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }
        .ai-status-badge.offline {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.4);
        }

        /* Messages Scroll Container */
        .chat-messages-container {
            flex: 1;
            overflow-y: auto;
            padding-right: 6px;
            margin-bottom: 12px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: 420px;
        }

        /* Scrollbar styling */
        .chat-messages-container::-webkit-scrollbar {
            width: 5px;
        }
        .chat-messages-container::-webkit-scrollbar-thumb {
            background: rgba(0, 212, 255, 0.3);
            border-radius: 4px;
        }

        /* Message Bubbles */
        .chat-bubble {
            border-radius: 12px;
            padding: 12px 14px;
            font-size: 0.85rem;
            line-height: 1.5;
            animation: fadeIn 0.25s ease forwards;
            word-wrap: break-word;
        }
        .bubble-sender {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }
        .user-bubble {
            background: rgba(0, 212, 255, 0.12);
            border: 1px solid rgba(0, 212, 255, 0.3);
            color: #ffffff;
            align-self: flex-end;
            margin-left: 24px;
        }
        .user-bubble .bubble-sender {
            color: #00d4ff;
        }
        .assistant-bubble {
            background: rgba(17, 35, 64, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #e2e8f0;
            align-self: flex-start;
            margin-right: 24px;
        }
        .assistant-bubble .bubble-sender {
            color: #14b8a6;
        }
        .welcome-bubble {
            border-color: rgba(0, 212, 255, 0.4);
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(17, 35, 64, 0.9) 100%);
        }

        .quick-prompts-label {
            font-size: 0.72rem;
            font-weight: 700;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin: 8px 0 6px 0;
        }

        /* Form input fixes in Streamlit */
        .chatbot-panel-wrapper [data-testid="stForm"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        .chatbot-panel-wrapper input[type="text"] {
            background: rgba(10, 27, 53, 0.9) !important;
            border: 1px solid rgba(0, 212, 255, 0.3) !important;
            border-radius: 8px !important;
            color: #ffffff !important;
            font-size: 0.85rem !important;
        }
        .chatbot-panel-wrapper input[type="text"]:focus {
            border-color: #00d4ff !important;
            box-shadow: 0 0 10px rgba(0, 212, 255, 0.3) !important;
        }

        /* Quick Prompt Buttons */
        .chatbot-panel-wrapper [data-testid="stButton"] button {
            background: rgba(0, 212, 255, 0.08) !important;
            border: 1px solid rgba(0, 212, 255, 0.25) !important;
            color: #e2e8f0 !important;
            font-size: 0.75rem !important;
            padding: 6px 10px !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
        }
        .chatbot-panel-wrapper [data-testid="stButton"] button:hover {
            background: rgba(0, 212, 255, 0.2) !important;
            color: #ffffff !important;
            border-color: #00d4ff !important;
        }

        /* Media Queries for Mobile Responsiveness */
        @media (max-width: 600px) {
            .chatbot-panel-wrapper {
                right: 16px;
                left: 16px;
                width: auto;
                bottom: 84px;
                height: 520px;
            }
            .floating-chatbot-trigger {
                right: 16px;
                bottom: 16px;
                width: 180px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

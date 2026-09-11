"""
OptiFreight AI — Gemini API Integration Service
Handles context building, Gemini API client setup, error handling, and response generation.
"""

import os
import logging
from datetime import datetime
import streamlit as st

# Configure logger
logger = logging.getLogger("optifreight_gemini")
logger.setLevel(logging.INFO)

# Models to attempt in order of preference
GEMINI_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-pro-preview",
    "gemini-flash-latest",
]


def get_api_key() -> str:
    """Retrieve Gemini API Key safely without exposing it."""
    # 1. Check Streamlit secrets
    try:
        if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass

    # 2. Check Environment Variables
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key and env_key.strip() and env_key != "YOUR_GEMINI_API_KEY_HERE":
        return env_key.strip()

    return ""


def get_gemini_status() -> dict:
    """Returns AI online/unavailable status and UI status badge info."""
    key = get_api_key()
    if key:
        return {
            "available": True,
            "badge": "● AI ONLINE",
            "badge_class": "online",
            "message": "Gemini API connected and active.",
        }
    else:
        return {
            "available": False,
            "badge": "● AI UNAVAILABLE",
            "badge_class": "offline",
            "message": "Gemini API is not configured. Set GEMINI_API_KEY in Streamlit Secrets.",
        }


def _fmt_status(status_obj) -> str:
    """Format DataStatus object, tuple, or string to clean uppercase text (LIVE, DEMO, MODEL, etc)."""
    if hasattr(status_obj, "value"):
        val = status_obj.value
        if isinstance(val, (tuple, list)):
            return str(val[0]).upper()
        return str(val).upper()
    if isinstance(status_obj, (tuple, list)):
        return str(status_obj[0]).upper()
    s = str(status_obj).replace("DataStatus.", "").upper()
    return s



def build_optifreight_context(all_data: dict, session_state) -> str:
    """
    Collects currently available application data into a structured context string for Gemini.
    Strictly excludes keys, secrets, or sensitive info.
    """
    live_mode = getattr(session_state, "live_mode", True)
    mode_str = "LIVE DATA MODE" if live_mode else "DEMO MODE"

    lines = [
        f"=== OPTIFREIGHT SYSTEM CONTEXT ===",
        f"System Mode: {mode_str}",
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
        "",
    ]

    # Freight Data Context
    freight_info = all_data.get("freight", {})
    freight_data = freight_info.get("data", {})
    freight_status = _fmt_status(freight_info.get("status", "DATA UNAVAILABLE"))
    lines.append(f"--- FREIGHT MARKET (Status: {freight_status}) ---")
    lines.append(f"Current Freight Rate: ${freight_data.get('current_rate', 'N/A')}/MT")
    lines.append(f"24h Rate Change: {freight_data.get('pct_change', 0):+.1f}%")
    lines.append(f"30-Day Projected Low: ${freight_data.get('projected_low', 'N/A')} ({freight_data.get('low_pct', 0):+.1f}%)")
    lines.append(f"30-Day Projected High: ${freight_data.get('projected_high', 'N/A')} ({freight_data.get('high_pct', 0):+.1f}%)")
    lines.append(f"AI Chartering Recommendation: {freight_data.get('recommendation', 'N/A')}")
    lines.append(f"AI Recommendation Confidence: {freight_data.get('confidence', 'N/A')}")
    lines.append(f"Expected 30-Day Movement: {freight_data.get('movement', 'N/A')}")
    lines.append(f"Estimated Savings per Voyage: $142,500")
    lines.append(f"Optimal Chartering Window: 14 Days")
    lines.append(f"Recommendation Rationale: {freight_data.get('reason', 'N/A')}")
    lines.append("")

    # Currency Context
    curr_info = all_data.get("currency", {})
    curr_status = _fmt_status(curr_info.get("status", "DATA UNAVAILABLE"))
    curr_rate = curr_info.get("data", {}).get("rate", "N/A")
    lines.append(f"--- CURRENCY (Status: {curr_status}) ---")
    lines.append(f"USD/INR Reference Exchange Rate: ₹{curr_rate}")
    lines.append("")

    # Weather Context
    weather_info = all_data.get("weather_sg", {})
    w_status = _fmt_status(weather_info.get("status", "DATA UNAVAILABLE"))
    w_data = weather_info.get("data", {})
    lines.append(f"--- WEATHER (Singapore Hub, Status: {w_status}) ---")
    lines.append(f"Temperature: {w_data.get('temperature', 'N/A')}°C")
    lines.append(f"Wind Speed: {w_data.get('wind_speed', 'N/A')} km/h")
    lines.append(f"Humidity: {w_data.get('humidity', 'N/A')}%")
    lines.append(f"Weather Risk Rating: {w_data.get('risk_label', 'N/A')}")
    lines.append("")

    # Marine Context
    marine_info = all_data.get("marine", {})
    m_status = _fmt_status(marine_info.get("status", "DATA UNAVAILABLE"))
    m_data = marine_info.get("data", {})
    lines.append(f"--- MARINE CONDITIONS (South China Sea, Status: {m_status}) ---")
    lines.append(f"Wave Height: {m_data.get('wave_height', 'N/A')} m")
    lines.append(f"Marine Navigation Risk: {m_data.get('risk_label', 'N/A')}")
    lines.append("")

    # Fuel / Bunker Context
    fuel_info = all_data.get("fuel", {})
    f_status = _fmt_status(fuel_info.get("status", "DATA UNAVAILABLE"))
    f_data = fuel_info.get("data", {})
    lines.append(f"--- BUNKER FUEL (VLSFO, Status: {f_status}) ---")
    lines.append(f"Price: ${f_data.get('price', 'N/A')} {f_data.get('unit', '')}")
    lines.append(f"Change: {f_data.get('change', 0):+.1f}%")
    lines.append("")

    # Port Congestion Context
    port_info = all_data.get("port", {})
    p_status = _fmt_status(port_info.get("status", "DATA UNAVAILABLE"))
    p_data = port_info.get("data", {})
    lines.append(f"--- PORT CONGESTION ({p_data.get('port_name', 'Shanghai')}, Status: {p_status}) ---")
    lines.append(f"Congestion Level: {p_data.get('congestion_level', 'N/A')}")
    lines.append(f"Average Wait Time: {p_data.get('wait_time_hours', 'N/A')} hours")
    lines.append(f"Vessels at Anchor: {p_data.get('vessels_waiting', 'N/A')}")
    lines.append("")

    # Geopolitical Risk Context
    news_info = all_data.get("news", {})
    n_status = _fmt_status(news_info.get("status", "DATA UNAVAILABLE"))
    n_data = news_info.get("data", {})
    lines.append(f"--- GEOPOLITICAL RISK (Status: {n_status}) ---")
    lines.append(f"Risk Level: {n_data.get('level', 'N/A')}")
    lines.append(f"Risk Drivers: {n_data.get('reason', 'N/A')}")
    lines.append("===================================")

    return "\n".join(lines)



def get_system_prompt(context_str: str) -> str:
    """Generates the System Prompt for Gemini with current context."""
    return f"""You are OptiFreight AI, a professional maritime freight intelligence assistant.
Subtitle: Maritime Intelligence Assistant

Your role is to help users understand freight markets, chartering decisions, route risks, weather, procurement, forecasting, and maritime intelligence.

Use the information provided by the OptiFreight application as your primary context.

{context_str}

CRITICAL RULES:
1. Never invent market data, prices, port conditions, weather conditions, vessel positions, or forecasts.
2. If data is unavailable, clearly state that it is unavailable.
3. Clearly distinguish between LIVE, DELAYED, MODEL, DEMO, REFERENCE, and DATA UNAVAILABLE information.
4. Never claim that a prediction is guaranteed.
5. When discussing chartering decisions, explain the reasoning and risks rather than presenting the recommendation as financial certainty.
6. Give concise, professional, executive-ready answers.
7. When useful, structure answers using:
   - **Situation**
   - **Analysis**
   - **Recommendation**
   - **Risk**
   - **Data Status**
8. You are an assistant for decision support, not a substitute for professional maritime, financial, or legal advice.
"""


def generate_gemini_response(user_message: str, chat_history: list, context_str: str) -> str:
    """
    Sends chat history and current user message to Gemini and returns the response string.
    Handles errors gracefully with clear user feedback and secure logging.
    """
    api_key = get_api_key()
    if not api_key:
        return (
            "⚠️ **Gemini API is not configured.**\n\n"
            "To activate OptiFreight AI, please configure your `GEMINI_API_KEY` in Streamlit Secrets (`.streamlit/secrets.toml`) or environment variables."
        )

    system_prompt = get_system_prompt(context_str)

    # 1. Try google.genai SDK (Official new SDK)
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        # Prepare conversation contents
        contents = []
        for msg in chat_history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            ))
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)]
        ))

        # Try models in order
        last_err = None
        for model_name in GEMINI_MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.4,
                        max_output_tokens=1024,
                    )
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                last_err = e
                logger.warning(f"Gemini model {model_name} failed: {str(e)[:100]}")
                continue

    except ImportError:
        logger.info("google.genai SDK not available, trying google.generativeai fallback.")
    except Exception as e:
        logger.error(f"Error initializing google.genai client: {str(e)[:150]}")

    # 2. Try google.generativeai SDK fallback
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        # Build contents structure for generativeai SDK
        formatted_history = []
        for msg in chat_history:
            role = "user" if msg["role"] == "user" else "model"
            formatted_history.append({"role": role, "parts": [msg["content"]]})

        last_err = None
        for model_name in GEMINI_MODELS:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_prompt
                )
                chat = model.start_chat(history=formatted_history)
                response = chat.send_message(user_message)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                last_err = e
                logger.warning(f"google.generativeai model {model_name} failed: {str(e)[:100]}")
                continue

    except Exception as e:
        logger.error(f"Error calling google.generativeai API: {str(e)[:150]}")

    # If all models/SDKs failed
    return "OptiFreight AI is temporarily unavailable. Please check the Gemini API configuration or network connection."

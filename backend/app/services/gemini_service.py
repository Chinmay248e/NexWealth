"""
Gemini Service — Server-side Gemini API client for Person 2 AI Financial Advisor.

Uses Google Generative Language REST endpoint with server-side API key protection.
Falls back safely to local analytics if Gemini is not configured or unavailable.
"""
import os
import json
from typing import Optional, List, Dict, Any
import httpx

from app.core.config import settings

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

SYSTEM_INSTRUCTION = """
You are NexAdvisor, the AI Financial Intelligence copilot for NexWealth.
All monetary figures are in Indian Rupees (INR / ₹) formatted with Indian numbering grouping (Lakhs, Crores).
You receive verified, calculated financial summaries for the authenticated user (Income, Expenses, Cashflow, Goals, Investments).
Your guidelines:
1. Provide concise, high-value financial insights based on the provided user metrics.
2. Highlight spending anomalies, savings headroom, tax optimization (Sections 80C, 80D, 80CCD), and goal timelines.
3. Distinguish factual figures from advisory recommendations. Never fabricate numbers.
4. Maintain a professional, encouraging, and sophisticated fintech advisor tone.
5. Remind users that advisory insights are informative analysis rather than certified investment guarantees.
"""


def call_gemini_advisor(
    prompt: str,
    context_str: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> Optional[str]:
    """
    Execute server-side call to Google Gemini API.
    Returns generated response text or None if Gemini is not configured/unreachable.
    """
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() == "" or api_key == "YOUR_GEMINI_API_KEY":
        return None

    url = f"{GEMINI_API_URL}?key={api_key.strip()}"

    contents = []

    # Add historical messages if provided
    if history:
        for msg in history[-6:]:  # Keep recent context window
            role = "user" if msg.get("role") == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.get("content", "")}]
            })

    # Add system context + user prompt
    full_user_prompt = f"### AUTHENTICATED USER FINANCIAL CONTEXT:\n{context_str}\n\n### USER QUESTION:\n{prompt}"
    contents.append({
        "role": "user",
        "parts": [{"text": full_user_prompt}]
    })

    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 800,
        },
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
            return None
    except Exception:
        # Fallback cleanly on network timeout or connection errors
        return None

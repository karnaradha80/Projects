"""
webhook_server.py
=================
FastAPI app that receives Twilio WhatsApp webhooks and responds
using Claude AI with tool use to control the Utilitics pipeline.

Setup:
  1. Copy .env.example to .env and fill in your keys
  2. Run:  uvicorn automation.webhook_server:app --port 8000 --reload
  3. Expose locally with:  ngrok http 8000
  4. Set Twilio sandbox webhook URL to:  https://<ngrok-url>/webhook

Supported WhatsApp commands (natural language):
  - "run pipeline"           → full pipeline
  - "run bronze"             → single step
  - "run sharing"            → delta sharing simulation
  - "status"                 → last run result
  - "switch to databricks"   → change runtime
  - "what's the runtime?"    → current mode
  - "help"                   → command list
"""

import os
import sys
import logging
import threading

# Add project root to path so automation.* imports work
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import PlainTextResponse
from twilio.rest import Client as TwilioClient
from twilio.request_validator import RequestValidator
import anthropic
from dotenv import load_dotenv

from automation.claude_tools import TOOLS, execute_tool, format_tool_result

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ============================================================
# Logging
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("webhook")


# ============================================================
# Config from environment
# ============================================================
TWILIO_ACCOUNT_SID   = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN    = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")  # sandbox default
ANTHROPIC_API_KEY    = os.environ.get("ANTHROPIC_API_KEY", "")
VALIDATE_TWILIO      = os.environ.get("VALIDATE_TWILIO_SIGNATURE", "true").lower() == "true"

# Warn loudly on missing keys at startup
if not TWILIO_ACCOUNT_SID:
    log.warning("TWILIO_ACCOUNT_SID not set — outbound messages will fail")
if not TWILIO_AUTH_TOKEN:
    log.warning("TWILIO_AUTH_TOKEN not set — Twilio client unavailable")
if not ANTHROPIC_API_KEY:
    log.warning("ANTHROPIC_API_KEY not set — Claude calls will fail")


# ============================================================
# Clients
# ============================================================
twilio_client    = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID else None
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

app = FastAPI(title="Utilitics ChatOps", version="1.0.0")

SYSTEM_PROMPT = """\
You are the Utilitics pipeline assistant. You control a data pipeline that processes \
utility meter data through Bronze → Silver → Gold layers using PySpark and Delta Lake.

You have tools to run the pipeline, check status, and switch runtimes. \
When a user asks you to do something pipeline-related, use the appropriate tool. \
Keep your replies short and clear — they appear on WhatsApp.

After a tool runs, summarise the result in 2–4 sentences max. \
Include whether it succeeded or failed, and any key numbers (records, elapsed time).

If the user says "help", list the available commands without using tools.
"""

HELP_TEXT = """\
*Utilitics Pipeline Bot* 🛠

Commands (natural language):
• *run pipeline* — full end-to-end run
• *run <step>* — generate / bronze / silver / gold / validate / sharing
• *run sharing* — delta sharing simulation
• *status* — last run result
• *switch to local* — use local PySpark
• *switch to databricks* — use Databricks CE
• *what's the runtime?* — current mode
• *help* — this message
"""


# ============================================================
# Core: ask Claude, execute any tool calls, return final text
# ============================================================
def ask_claude(user_message: str) -> str:
    """
    Send user_message to Claude with tools. If Claude calls a tool,
    execute it and feed the result back. Return the final text reply.
    """
    if not anthropic_client:
        return "[ERROR] ANTHROPIC_API_KEY not configured on server."

    messages = [{"role": "user", "content": user_message}]

    # Agentic loop — Claude may call multiple tools in sequence
    for _ in range(5):   # safety cap: max 5 tool calls
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        log.info("Claude stop_reason=%s", response.stop_reason)

        # Collect text blocks and tool_use blocks
        text_parts   = []
        tool_uses    = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_uses.append(block)

        # If no tool calls → we're done
        if not tool_uses:
            return "\n".join(text_parts).strip() or "Done."

        # Append Claude's response (with tool_use blocks) to messages
        messages.append({"role": "assistant", "content": response.content})

        # Execute each tool and build tool_result blocks
        tool_results = []
        for tu in tool_uses:
            log.info("Executing tool: %s  input=%s", tu.name, tu.input)
            result = execute_tool(tu.name, tu.input)
            log.info("Tool result: success=%s", result.get("success"))
            tool_results.append({
                "type":        "tool_result",
                "tool_use_id": tu.id,
                "content":     format_tool_result(result),
            })

        # Feed tool results back
        messages.append({"role": "user", "content": tool_results})

    return "Pipeline action completed."   # fallback after cap


# ============================================================
# Send WhatsApp reply via Twilio
# ============================================================
def send_whatsapp(to: str, body: str):
    if not twilio_client:
        log.error("Twilio client not configured — cannot send message")
        return
    try:
        msg = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=to,
            body=body[:1500],   # WhatsApp limit ~1600 chars
        )
        log.info("Sent WhatsApp SID=%s to=%s", msg.sid, to)
    except Exception as exc:
        log.error("Twilio send failed: %s", exc)


# ============================================================
# Twilio signature validation (optional but recommended)
# ============================================================
def validate_twilio_request(request: Request, form_data: dict) -> bool:
    if not VALIDATE_TWILIO:
        return True
    validator  = RequestValidator(TWILIO_AUTH_TOKEN)
    url        = str(request.url)
    signature  = request.headers.get("X-Twilio-Signature", "")
    return validator.validate(url, form_data, signature)


# ============================================================
# Webhook endpoint
# ============================================================
@app.post("/webhook", response_class=PlainTextResponse)
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(default=""),
    From: str = Form(default=""),
    To:   str = Form(default=""),
):
    form_data = dict(await request.form())

    if not validate_twilio_request(request, form_data):
        log.warning("Invalid Twilio signature from %s", From)
        raise HTTPException(status_code=403, detail="Invalid signature")

    user_text = Body.strip()
    log.info("Received from %s: %r", From, user_text)

    if not user_text:
        return ""

    # Short-circuit help without hitting Claude
    if user_text.lower() in ("help", "/help", "?"):
        send_whatsapp(From, HELP_TEXT)
        return ""

    # Long-running commands: ack immediately, process in background thread
    long_keywords = ("run pipeline", "run full", "run everything", "run all",
                     "run bronze", "run silver", "run gold", "run generate",
                     "run validate", "run sharing", "simulate sharing")
    is_long = any(kw in user_text.lower() for kw in long_keywords)

    if is_long:
        send_whatsapp(From, "Got it! Starting pipeline action — I'll reply when it's done ⏳")
        def background_task():
            reply = ask_claude(user_text)
            send_whatsapp(From, reply)
        threading.Thread(target=background_task, daemon=True).start()
    else:
        reply = ask_claude(user_text)
        send_whatsapp(From, reply)

    return ""


# ============================================================
# Health check
# ============================================================
@app.get("/health")
def health():
    return {
        "status":   "ok",
        "twilio":   bool(twilio_client),
        "anthropic": bool(anthropic_client),
    }


# ============================================================
# Dev runner
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("automation.webhook_server:app", host="0.0.0.0", port=8000, reload=True)

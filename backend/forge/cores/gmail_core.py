"""Gmail core — 2 hardcoded SMTP tools (official path, no browser login)."""

GMAIL_CORE_SOURCE = '''
@mcp.tool()
def gmail_send_email(to: str, subject: str, body: str = "") -> dict:
    """Send an email via Gmail SMTP (official API path — never browser login). Needs GMAIL_USER + GMAIL_APP_PASSWORD."""
    import os
    import smtplib
    from email.message import EmailMessage

    user = os.environ.get("GMAIL_USER", "")
    password = os.environ.get("GMAIL_APP_PASSWORD", "")
    if not user or not password:
        return {"ok": False, "error": "set GMAIL_USER and GMAIL_APP_PASSWORD env (Gmail app password) in your mcpServers env block"}
    try:
        message = EmailMessage()
        message["From"], message["To"], message["Subject"] = user, to, subject
        message.set_content(body or subject)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as smtp:
            smtp.login(user, password)
            smtp.send_message(message)
        return {"ok": True, "sent_to": to, "subject": subject}
    except Exception as err:
        return {"ok": False, "error": repr(err)}


@mcp.tool()
def gmail_notify_and_log(discount: float = 0.0, price: str = "") -> dict:
    """Send a discount alert email (to GMAIL_TO or GMAIL_USER) with the observed discount and price."""
    import os

    user = os.environ.get("GMAIL_USER", "")
    to = os.environ.get("GMAIL_TO", "") or user
    if not to:
        return {"ok": False, "error": "set GMAIL_USER / GMAIL_TO env so the alert has a recipient"}
    subject = "FORGE alert: RAM discount {0}% off".format(discount)
    body = "Discount observed: {0}%\\nPrice: {1}\\n\\n— sent by your unified-forge MCP server".format(discount, price or "n/a")
    return gmail_send_email(to, subject, body)
'''

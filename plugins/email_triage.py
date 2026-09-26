import imaplib
import email
import threading
import time
from email.header import decode_header
from core.llm_client import call_llm_text

PLUGIN = {
    "name": "email_triage",
    "description": (
        "Connects to an IMAP inbox to proactively monitor incoming emails, "
        "triage them by priority, and alert the user of urgent messages."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "email_address": {"type": "STRING", "description": "The email address to monitor"},
            "app_password": {"type": "STRING", "description": "The app password for IMAP access"},
            "imap_server": {"type": "STRING", "description": "IMAP server address (default: imap.gmail.com)"}
        },
        "required": ["email_address", "app_password"],
    },
}

def _monitor_inbox(email_addr, app_pw, imap_server, player):
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_addr, app_pw)
        mail.select("inbox")
        
        if player:
            player.write_log(f"📧 [EmailTriage] Connected to {email_addr}. Monitoring inbox...")
            
        while True:
            # Look for unseen emails
            status, messages = mail.search(None, 'UNSEEN')
            if status == "OK" and messages[0]:
                for num in messages[0].split():
                    status, msg_data = mail.fetch(num, '(RFC822)')
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            subject, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding if encoding else "utf-8")
                            from_ = msg.get("From")
                            
                            # Analyze priority via LLM
                            prompt = f"Analyze this email metadata and decide if it is URGENT (requires immediate interruption) or ROUTINE.\nFrom: {from_}\nSubject: {subject}\n\nReply with only 'URGENT' or 'ROUTINE'."
                            try:
                                priority = call_llm_text(prompt=prompt).strip().upper()
                                if "URGENT" in priority:
                                    if player:
                                        player.write_log(f"🚨 [EmailTriage] URGENT EMAIL from {from_}: {subject}")
                                        # In a full implementation, we could trigger a TTS speak event here
                                else:
                                    if player:
                                        player.write_log(f"📥 [EmailTriage] Routine email from {from_}: {subject}")
                            except Exception:
                                pass
            time.sleep(30) # Poll every 30 seconds
            
    except Exception as e:
        if player:
            player.write_log(f"⚠️ [EmailTriage] Error: {e}")

def run(parameters: dict, player=None, session_memory=None) -> str:
    email_address = parameters.get("email_address")
    app_password = parameters.get("app_password")
    imap_server = parameters.get("imap_server", "imap.gmail.com")
    
    if not email_address or not app_password:
        return "Email address and App Password are required."
        
    t = threading.Thread(target=_monitor_inbox, args=(email_address, app_password, imap_server, player), daemon=True)
    t.start()
    
    msg = f"Started email triage on {email_address}. I will monitor for urgent emails in the background."
    if player:
        player.write_log(f"PARIS: {msg}")
    return msg

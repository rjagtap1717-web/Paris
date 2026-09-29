import imaplib
import smtplib
import email
from email.message import EmailMessage
import threading
import time
from email.header import decode_header
from core.gemini import text

PLUGIN = {
    "name": "email_triage",
    "description": (
        "Connects to an IMAP/SMTP inbox to proactively monitor incoming emails, "
        "triage them by priority, or send outgoing emails securely in the background."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "'monitor' to watch inbox, 'send' to send an email."},
            "email_address": {"type": "STRING", "description": "Your email address"},
            "app_password": {"type": "STRING", "description": "The app password for IMAP/SMTP access"},
            "to_address": {"type": "STRING", "description": "Recipient email address (for send action)"},
            "subject": {"type": "STRING", "description": "Email subject (for send action)"},
            "body": {"type": "STRING", "description": "Email body content (for send action)"},
            "server": {"type": "STRING", "description": "Base server address (default: gmail.com)"}
        },
        "required": ["action", "email_address", "app_password"],
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
                            
                            prompt = f"Analyze this email metadata and decide if it is URGENT (requires immediate interruption) or ROUTINE.\nFrom: {from_}\nSubject: {subject}\n\nReply with only 'URGENT' or 'ROUTINE'."
                            try:
                                priority = text(contents=prompt).strip().upper()
                                if "URGENT" in priority:
                                    if player:
                                        player.write_log(f"🚨 [EmailTriage] URGENT EMAIL from {from_}: {subject}")
                                else:
                                    if player:
                                        player.write_log(f"📥 [EmailTriage] Routine email from {from_}: {subject}")
                            except Exception:
                                pass
            time.sleep(30)
            
    except Exception as e:
        if player:
            player.write_log(f"⚠️ [EmailTriage] Error: {e}")

def run(parameters: dict, player=None, session_memory=None) -> str:
    action = parameters.get("action", "monitor")
    email_address = parameters.get("email_address")
    app_password = parameters.get("app_password")
    base_server = parameters.get("server", "gmail.com")
    
    if not email_address or not app_password:
        return "Error: Email address and App Password are required."
        
    if action == "monitor":
        imap_server = f"imap.{base_server}"
        t = threading.Thread(target=_monitor_inbox, args=(email_address, app_password, imap_server, player), daemon=True)
        t.start()
        msg = f"Started background email monitoring on {email_address}."
        if player: player.write_log(f"PARIS: {msg}")
        return msg
        
    elif action == "send":
        to_address = parameters.get("to_address")
        subject = parameters.get("subject", "")
        body = parameters.get("body", "")
        
        if not to_address:
            return "Error: 'to_address' is required to send an email."
            
        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = email_address
            msg['To'] = to_address
            
            smtp_server = f"smtp.{base_server}"
            with smtplib.SMTP_SSL(smtp_server, 465) as server:
                server.login(email_address, app_password)
                server.send_message(msg)
                
            return f"Successfully sent email to {to_address} with subject '{subject}'."
        except Exception as e:
            return f"Error sending email: {str(e)}"
            
    return f"Unknown action: {action}. Please use 'monitor' or 'send'."

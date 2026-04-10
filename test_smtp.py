import os
from publisher_intel.utils.mailer import send_brief_email

# Optionally load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

subject = "SMTP Test Email"
body = "This is a test email sent from your PublisherIntel setup."
from_email = os.getenv("FROM_EMAIL", "tanishq.chhibber2003@gmail.com")
to_emails = ["tanishq.chhibber2003@gmail.com"]

send_brief_email(
    subject=subject,
    body=body,
    attachments=[],
    from_email=from_email,
    to_emails=to_emails,
    html=None
)
print("Test email sent!")

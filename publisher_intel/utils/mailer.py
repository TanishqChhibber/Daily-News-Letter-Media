import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import Iterable, List

import logging
import tldextract
logger = logging.getLogger(__name__)


def _get_env(name: str, default: str | None = None) -> str | None:
    val = os.getenv(name)
    return val if val is not None else default


def render_newsletter_html(stories):
    rows = ""
    for s in stories:
        url = s.get('url','')
        title = s.get('title','')
        published = s.get('published','')
        # Extract domain for source
        domain = tldextract.extract(url)
        domain_str = f"{domain.domain}.{domain.suffix}" if domain.domain and domain.suffix else url
        rows += f'''
        <tr>
            <td style="padding:18px 12px;border-bottom:1px solid #eee;background:#fff;">
                <a href="{url}" style="color:#1a0dab;font-size:1.15em;text-decoration:none;font-weight:600;">{title}</a><br>
                <span style="color:#555;font-size:0.97em;">{published}</span><br>
                <span style="color:#888;font-size:0.93em;">Source: <a href=\"{url}\" style=\"color:#0066cc;text-decoration:underline;\">{domain_str}</a></span>
            </td>
        </tr>
        '''
    return f'''
    <html>
    <body style="background:#f6f8fa;color:#222;font-family:Inter,sans-serif;padding:0;margin:0;">
      <table width="100%" cellpadding="0" cellspacing="0" style="max-width:640px;margin:40px auto;background:#fefefe;border-radius:12px;box-shadow:0 4px 24px #0001;">
        <tr>
          <td style="padding:32px 24px;text-align:center;">
            <h1 style="color:#0066cc;margin-bottom:24px;">📰 Publisher Tech Brief</h1>
            <table width="100%" cellpadding="0" cellspacing="0">
              {rows}
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    '''


def send_brief_email(
    subject: str,
    body: str,
    attachments: Iterable[str],
    from_email: str | None = None,
    to_emails: Iterable[str] | None = None,
    html: str | None = None,
) -> None:
    """Send an email with attachments via SMTP using environment variables.

    Required env vars:
    - SMTP_SERVER (e.g., smtp.gmail.com)
    - SMTP_PORT (e.g., 587)
    - SMTP_USER (SMTP login username)
    - SMTP_PASS (SMTP password or app password)

    Optional env vars:
    - FROM_EMAIL (defaults to SMTP_USER if not provided)
    - TO_EMAIL (comma-separated list; defaults to FROM_EMAIL)
    """
    smtp_server = _get_env('SMTP_SERVER')
    smtp_port = int(_get_env('SMTP_PORT', '587'))
    smtp_user = _get_env('SMTP_USER')
    smtp_pass = _get_env('SMTP_PASS')

    if not all([smtp_server, smtp_user, smtp_pass]):
        raise RuntimeError('SMTP env vars missing: SMTP_SERVER/SMTP_USER/SMTP_PASS')

    from_addr = from_email or _get_env('FROM_EMAIL') or smtp_user
    to_list_env = _get_env('TO_EMAIL')
    if to_emails:
        tos: List[str] = list(to_emails)
    elif to_list_env:
        tos = [e.strip() for e in to_list_env.split(',') if e.strip()]
    else:
        tos = [from_addr]

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ', '.join(tos)
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype='html')

    for path in attachments:
        try:
            with open(path, 'rb') as f:
                data = f.read()
            filename = os.path.basename(path)
            msg.add_attachment(data, maintype='application', subtype='octet-stream', filename=filename)
        except Exception as e:
            logger.error(f'Failed attaching {path}: {e}')

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls(context=context)
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        logger.info('Email sent to %s', msg['To'])

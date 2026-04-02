# routes/email_utils.py — Beautiful HTML email notifications

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from Config import EMAIL_USER, EMAIL_PASS

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465


import threading


def _send_impl(to_email, subject, html_body):
    """Internal implementation to send an HTML email."""
    msg = MIMEMultipart('alternative')
    msg['From'] = f'DonateWise <{EMAIL_USER}>'
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))
    try:
        # 🔒 Port 465 (SSL) is used for maximum compatibility
        import smtplib
        server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, timeout=10)
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email SUCCESS: Sent to {to_email}")
    except Exception as e:
        print(f"❌ Email FAILURE for {to_email}: {e}")


def _send(to_email, subject, html_body):
    """Sends the email synchronously for serverless compatibility."""
    _send_impl(to_email, subject, html_body)


def _base_template(icon, title, subtitle, body_rows, cta_text=None, cta_link=None, color='#4f46e5'):
    """Shared premium HTML email shell."""
    cta_html = ''
    if cta_text and cta_link:
        cta_html = f"""
        <div style="text-align:center; margin-top:28px;">
            <a href="{cta_link}"
               style="background:{color}; color:white; text-decoration:none;
                      padding:14px 36px; border-radius:100px; font-weight:700;
                      font-size:15px; display:inline-block; letter-spacing:0.3px;">
                {cta_text}
            </a>
        </div>"""
    rows_html = ''.join(f"""
        <tr>
            <td style="padding:8px 0; color:#64748b; font-size:13px; border-bottom:1px solid #f1f5f9;">
                <span style="font-weight:700; color:#1e293b;">{k}</span><br>{v}
            </td>
        </tr>""" for k, v in body_rows)

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td style="padding:40px 20px;">
      <table width="600" cellpadding="0" cellspacing="0" align="center"
             style="background:white;border-radius:24px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">

        <!-- HEADER -->
        <tr>
          <td style="background:linear-gradient(135deg,#0f172a,#1e293b);padding:40px 40px 32px;text-align:center;">
            <div style="font-size:3rem;margin-bottom:12px;">{icon}</div>
            <h1 style="color:white;margin:0;font-size:24px;font-weight:800;letter-spacing:-0.5px;">{title}</h1>
            <p style="color:rgba(255,255,255,0.5);margin:8px 0 0;font-size:14px;">{subtitle}</p>
          </td>
        </tr>

        <!-- BODY -->
        <tr>
          <td style="padding:36px 40px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              {rows_html}
            </table>
            {cta_html}
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td style="background:#f8fafc;padding:24px 40px;text-align:center;border-top:1px solid #e2e8f0;">
            <p style="color:#94a3b8;font-size:12px;margin:0;">
              © 2026 <strong style="color:#4f46e5;">DonateWise</strong> · Connecting donors with NGOs across Pune
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body></html>"""


# ── 1. DONATION CLAIMED
def send_claimed_notification(to_email, donor_name, donation_title, ngo_name, pickup_time):
    subject = f"📥 Your donation was claimed by {ngo_name}!"
    html = _base_template(
        icon='📥',
        title='Your Donation Was Claimed!',
        subtitle=f'Great news, {donor_name}! An NGO has accepted your donation.',
        body_rows=[
            ('Donation', donation_title),
            ('Claimed By', ngo_name),
            ('Scheduled Pickup', pickup_time),
            ('Status', '🟡 Scheduled — NGO will arrive shortly'),
        ],
        cta_text='Track Your Donation →',
        cta_link='http://localhost:5000/history',
        color='#4f46e5'
    )
    _send(to_email, subject, html)


# ── 2. DONATION DISPATCHED
def send_dispatched_notification(to_email, donor_name, donation_title, ngo_name):
    subject = f"🚚 {ngo_name} is on the way to pick up your donation!"
    html = _base_template(
        icon='🚚',
        title="The NGO Is On The Way!",
        subtitle=f"Hi {donor_name}, your donation is being picked up right now.",
        body_rows=[
            ('Donation', donation_title),
            ('NGO En Route', ngo_name),
            ('Status', '🔵 Dispatched — Live tracking available in app'),
        ],
        cta_text='Open Live Tracker →',
        cta_link='http://localhost:5000/history',
        color='#2563eb'
    )
    _send(to_email, subject, html)


# ── 3. DONATION FULFILLED
def send_fulfilled_notification(to_email, donor_name, donation_title, ngo_name):
    subject = f"🎉 Your donation reached the people who need it most!"
    html = _base_template(
        icon='🎉',
        title='Delivery Confirmed!',
        subtitle=f'Thank you, {donor_name}. You just changed someone\'s life.',
        body_rows=[
            ('Donation', donation_title),
            ('Delivered To', ngo_name),
            ('Status', '✅ Fulfilled — Impact recorded'),
            ('Next Step', 'Claim your Impact Certificate!'),
        ],
        cta_text='🏅 Claim Your Certificate →',
        cta_link='http://localhost:5000/history',
        color='#10b981'
    )
    _send(to_email, subject, html)

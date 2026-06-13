"""Transactional email content.

Plain functions returning (subject, html, text) — two emails don't justify a
template engine. Inline styles only (email clients ignore stylesheets).
"""

from html import escape

from app.modules.auth.models import OtpPurpose

_PURPOSE_COPY: dict[str, tuple[str, str]] = {
    # purpose -> (subject, lead line)
    OtpPurpose.REGISTRATION.value: (
        "Verify your email — LingosAI",
        "Use this code to verify your email address:",
    ),
    OtpPurpose.PASSWORD_RESET.value: (
        "Reset your password — LingosAI",
        "Use this code to reset your password:",
    ),
    OtpPurpose.LOGIN_STEP_UP.value: (
        "Your login code — LingosAI",
        "Use this code to confirm your login:",
    ),
}


def otp_email(
    *, code: str, purpose: OtpPurpose, ttl_minutes: int
) -> tuple[str, str, str]:
    subject, lead = _PURPOSE_COPY[purpose.value]
    text = (
        f"{lead}\n\n{code}\n\n"
        f"This code expires in {ttl_minutes} minutes. "
        "If you didn't request it, you can safely ignore this email."
    )
    html = f"""\
<div style="font-family:Arial,Helvetica,sans-serif;max-width:480px;margin:0 auto;padding:24px;">
  <h2 style="color:#1a2c4e;margin:0 0 16px;">LingosAI</h2>
  <p style="color:#3d4a63;font-size:15px;margin:0 0 20px;">{lead}</p>
  <p style="font-size:34px;font-weight:700;letter-spacing:10px;color:#1a2c4e;
            background:#f1f4fa;border-radius:10px;padding:18px 12px;text-align:center;margin:0 0 20px;">{code}</p>
  <p style="color:#6b7690;font-size:13px;margin:0;">
    This code expires in {ttl_minutes} minutes.
    If you didn't request it, you can safely ignore this email.
  </p>
</div>"""
    return subject, html, text


def account_exists_email() -> tuple[str, str, str]:
    """Sent when someone signs up with an already-verified email. The HTTP
    response stays generic (anti-enumeration); the real owner learns what
    happened by email instead."""
    subject = "You already have a LingosAI account"
    text = (
        "Someone (probably you) tried to sign up for LingosAI with this "
        "email address, but an account already exists.\n\n"
        "If it was you, just log in — or use “Forgot password” if "
        "you can't remember your password.\n\n"
        "If it wasn't you, no action is needed."
    )
    html = """\
<div style="font-family:Arial,Helvetica,sans-serif;max-width:480px;margin:0 auto;padding:24px;">
  <h2 style="color:#1a2c4e;margin:0 0 16px;">LingosAI</h2>
  <p style="color:#3d4a63;font-size:15px;margin:0 0 16px;">
    Someone (probably you) tried to sign up with this email address,
    but an account already exists.
  </p>
  <p style="color:#3d4a63;font-size:15px;margin:0 0 16px;">
    If it was you, just log in &mdash; or use &ldquo;Forgot password&rdquo;
    if you can't remember your password.
  </p>
  <p style="color:#6b7690;font-size:13px;margin:0;">If it wasn't you, no action is needed.</p>
</div>"""
    return subject, html, text


def contact_message_email(
    *, full_name: str, email: str, subject: str, message: str
) -> tuple[str, str, str]:
    """A visitor's contact-form submission, formatted for the support inbox.

    The visitor's address is set as the email's reply-to by the caller, so
    support can reply directly. User-supplied values are HTML-escaped to keep
    the message body inert.
    """
    mail_subject = f"New contact message: {subject}"
    text = (
        f"New contact form submission — LingosAI\n\n"
        f"Name:    {full_name}\n"
        f"Email:   {email}\n"
        f"Subject: {subject}\n\n"
        f"Message:\n{message}\n\n"
        f"Reply directly to this email to respond to {full_name}."
    )
    safe_name = escape(full_name)
    safe_email = escape(email)
    safe_subject = escape(subject)
    safe_message = escape(message).replace("\n", "<br>")
    html = f"""\
<div style="font-family:Arial,Helvetica,sans-serif;max-width:560px;margin:0 auto;padding:24px;">
  <h2 style="color:#1a2c4e;margin:0 0 8px;">LingosAI</h2>
  <p style="color:#6b7690;font-size:13px;margin:0 0 20px;">New contact form submission</p>
  <table style="width:100%;border-collapse:collapse;font-size:15px;color:#3d4a63;">
    <tr><td style="padding:6px 0;width:90px;color:#6b7690;">Name</td><td style="padding:6px 0;">{safe_name}</td></tr>
    <tr><td style="padding:6px 0;color:#6b7690;">Email</td><td style="padding:6px 0;"><a href="mailto:{safe_email}" style="color:#3056d3;">{safe_email}</a></td></tr>
    <tr><td style="padding:6px 0;color:#6b7690;">Subject</td><td style="padding:6px 0;">{safe_subject}</td></tr>
  </table>
  <p style="color:#1a2c4e;font-size:14px;font-weight:600;margin:20px 0 8px;">Message</p>
  <div style="background:#f1f4fa;border-radius:10px;padding:16px;color:#3d4a63;font-size:15px;line-height:1.6;">{safe_message}</div>
  <p style="color:#6b7690;font-size:13px;margin:20px 0 0;">Reply directly to this email to respond to {safe_name}.</p>
</div>"""
    return mail_subject, html, text

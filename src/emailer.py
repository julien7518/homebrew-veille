import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Sequence

from src.db import get_config
from src.fetcher import Package


def build_html(packages: Sequence[Package]) -> str:
    formulae = [p for p in packages if p.kind == "formula"]
    casks = [p for p in packages if p.kind == "cask"]
    date_str = datetime.now().strftime("%d/%m/%Y")

    def rows(items: Sequence[Package]) -> str:
        return "".join(
            f"""
            <tr>
                <td><strong>{p.name}</strong></td>
                <td>{p.version}</td>
                <td>{p.description}</td>
                <td><a href="{p.homepage}" target="_blank">Lien</a></td>
            </tr>"""
            for p in items
        )

    sections = ""
    if formulae:
        sections += f"""
        <h2>Formules ({len(formulae)})</h2>
        <table cellspacing="0" cellpadding="10" style="width:100%;border-collapse:collapse;">
            <thead><tr style="background:#f3f4f6;"><th>Nom</th><th>Version</th><th>Description</th><th>Site</th></tr></thead>
            <tbody>{rows(formulae)}</tbody>
        </table>"""
    if casks:
        sections += f"""
        <h2>Casks ({len(casks)})</h2>
        <table cellspacing="0" cellpadding="10" style="width:100%;border-collapse:collapse;">
            <thead><tr style="background:#f3f4f6;"><th>Nom</th><th>Version</th><th>Description</th><th>Site</th></tr></thead>
            <tbody>{rows(casks)}</tbody>
        </table>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f9fafb;margin:0;padding:0;">
<div style="max-width:680px;margin:0 auto;padding:24px;">
<div style="background:#1f2937;color:white;padding:24px;border-radius:12px 12px 0 0;">
<h1 style="margin:0;font-size:22px;">Veille Homebrew — {date_str}</h1>
<p style="margin:8px 0 0;opacity:.8;">{len(packages)} nouveau(x) paquet(s) détecté(s)</p>
</div>
<div style="background:white;padding:24px;border-radius:0 0 12px 12px;border:1px solid #e5e7eb;">
{sections}
<hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
<p style="color:#6b7280;font-size:13px;">Généré automatiquement le {date_str}</p>
</div>
</div>
</body>
</html>"""


def send_email(subject: str, html_body: str) -> None:
    smtp_host = get_config("smtp_host")
    smtp_port = int(get_config("smtp_port") or "587")
    smtp_user = get_config("smtp_user")
    smtp_password = get_config("smtp_password")
    email_from = get_config("email_from")
    email_to = get_config("email_to")

    if not all([smtp_host, smtp_user, smtp_password, email_from, email_to]):
        raise ValueError("Configuration SMTP incomplète")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email_from  # type: ignore[arg-type]
    msg["To"] = email_to  # type: ignore[arg-type]
    msg.attach(MIMEText(html_body, "html"))

    ctx = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:  # type: ignore[arg-type]
        server.starttls(context=ctx)
        server.login(smtp_user, smtp_password)  # type: ignore[arg-type]
        server.send_message(msg)

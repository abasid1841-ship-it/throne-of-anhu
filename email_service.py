"""SendGrid email service for device authorization emails."""

import os
import httpx
from typing import Optional


async def get_sendgrid_credentials() -> dict:
    """Fetch SendGrid credentials from Replit connector."""
    hostname = os.environ.get("REPLIT_CONNECTORS_HOSTNAME")
    
    repl_identity = os.environ.get("REPL_IDENTITY")
    web_repl_renewal = os.environ.get("WEB_REPL_RENEWAL")
    
    if repl_identity:
        x_replit_token = f"repl {repl_identity}"
    elif web_repl_renewal:
        x_replit_token = f"depl {web_repl_renewal}"
    else:
        raise Exception("X_REPLIT_TOKEN not found for repl/depl")
    
    if not hostname:
        raise Exception("REPLIT_CONNECTORS_HOSTNAME not found")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{hostname}/api/v2/connection?include_secrets=true&connector_names=sendgrid",
            headers={
                "Accept": "application/json",
                "X_REPLIT_TOKEN": x_replit_token
            }
        )
        data = response.json()
        
    connection = data.get("items", [{}])[0] if data.get("items") else {}
    settings = connection.get("settings", {})
    
    api_key = settings.get("api_key")
    from_email = settings.get("from_email")
    
    if not api_key or not from_email:
        raise Exception("SendGrid not connected or missing credentials")
    
    return {"api_key": api_key, "from_email": from_email}


async def send_device_auth_email(
    to_email: str,
    user_name: str,
    challenge_token: str,
    device_info: str,
    ip_address: str,
    base_url: str
) -> bool:
    """Send device authorization email with approve/deny links."""
    try:
        creds = await get_sendgrid_credentials()
        api_key = creds["api_key"]
        from_email = creds["from_email"]
        
        approve_url = f"{base_url}/auth/device/approve/{challenge_token}"
        deny_url = f"{base_url}/auth/device/deny/{challenge_token}"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Georgia', serif; background: #1a1a2e; color: #e8e8e8; padding: 40px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #16213e; border-radius: 12px; padding: 40px; border: 2px solid #d4af37; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .logo {{ font-size: 28px; color: #d4af37; font-weight: bold; }}
        .subtitle {{ color: #888; font-size: 14px; }}
        h1 {{ color: #d4af37; font-size: 24px; margin-bottom: 20px; }}
        .device-info {{ background: #0f0f23; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #d4af37; }}
        .device-info p {{ margin: 8px 0; color: #ccc; }}
        .device-info strong {{ color: #d4af37; }}
        .buttons {{ text-align: center; margin: 30px 0; }}
        .btn {{ display: inline-block; padding: 15px 40px; margin: 10px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; }}
        .btn-approve {{ background: #2d7a2d; color: white; }}
        .btn-deny {{ background: #8b2635; color: white; }}
        .warning {{ color: #ff6b6b; font-size: 14px; margin-top: 20px; text-align: center; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🦁 Throne of Anhu</div>
            <div class="subtitle">ABASID 1841</div>
        </div>
        
        <h1>New Device Login Attempt</h1>
        
        <p>Peace be unto you, <strong>{user_name}</strong>.</p>
        
        <p>Someone is attempting to access your Throne of Anhu account from a new device:</p>
        
        <div class="device-info">
            <p><strong>Device:</strong> {device_info}</p>
            <p><strong>IP Address:</strong> {ip_address}</p>
            <p><strong>Time:</strong> Just now</p>
        </div>
        
        <p>If this was you, click <strong>Approve</strong> to allow access. Your current device will be logged out.</p>
        
        <p>If this was NOT you, click <strong>Deny</strong> to block this attempt.</p>
        
        <div class="buttons">
            <a href="{approve_url}" class="btn btn-approve">✓ Approve Login</a>
            <a href="{deny_url}" class="btn btn-deny">✗ Deny (Not Me)</a>
        </div>
        
        <p class="warning">⚠️ This link expires in 15 minutes. If you did not request this, please secure your Google account.</p>
        
        <div class="footer">
            <p>The Throne of Anhu · ABASID 1841</p>
            <p>www.thecollegeofanhu.com</p>
        </div>
    </div>
</body>
</html>
"""
        
        text_content = f"""
Throne of Anhu - New Device Login Attempt

Peace be unto you, {user_name}.

Someone is attempting to access your account from a new device:
- Device: {device_info}
- IP Address: {ip_address}
- Time: Just now

To APPROVE this login (your current device will be logged out):
{approve_url}

To DENY this login (if this was NOT you):
{deny_url}

This link expires in 15 minutes.

The Throne of Anhu · ABASID 1841
www.thecollegeofanhu.com
"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "personalizations": [{"to": [{"email": to_email}]}],
                    "from": {"email": from_email, "name": "Throne of Anhu"},
                    "subject": "🦁 New Device Login - Approve or Deny",
                    "content": [
                        {"type": "text/plain", "value": text_content},
                        {"type": "text/html", "value": html_content}
                    ]
                }
            )
            
            if response.status_code in [200, 201, 202]:
                print(f"[EMAIL] Device auth email sent to {to_email}")
                return True
            else:
                print(f"[EMAIL] Failed to send email: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"[EMAIL] Error sending device auth email: {e}")
        return False

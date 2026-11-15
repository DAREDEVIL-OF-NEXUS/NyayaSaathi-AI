from typing import Tuple

def render_verification_email(user_name: str, code: str, verification_url: str) -> Tuple[str, str]:
    text_content = f"""Hello {user_name},

Thank you for registering with NyayaSaathi AI (न्यायसाथी AI) — India's Consumer Protection Platform.

Your 6-digit email verification code is: {code}

Alternatively, you can verify your account by visiting the link below:
{verification_url}

This verification code will expire in 30 minutes. If you did not create an account, please disregard this email.

Warm regards,
NyayaSaathi AI Team
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Verify your NyayaSaathi AI Account</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0b1120; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f8fafc;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding: 40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #0f172a; border-radius: 16px; border: 1px solid #1e293b; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
          <!-- Header -->
          <tr>
            <td style="padding: 30px; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border-bottom: 1px solid #334155;">
              <table width="100%">
                <tr>
                  <td>
                    <span style="font-size: 20px; font-weight: bold; color: #f59e0b; letter-spacing: -0.5px;">NyayaSaathi AI</span>
                    <span style="font-size: 13px; background: rgba(245, 158, 11, 0.15); color: #fbbf24; padding: 3px 8px; border-radius: 6px; margin-left: 8px; font-weight: 600;">न्यायसाथी</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding: 40px 30px;">
              <h2 style="color: #ffffff; font-size: 20px; margin-top: 0; margin-bottom: 16px;">Verify your Email Address</h2>
              <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6; margin-bottom: 24px;">
                Hello <strong>{user_name}</strong>,<br><br>
                Thank you for creating an account on NyayaSaathi AI. To complete your registration and secure your consumer grievance workspace, please enter this verification code:
              </p>
              <!-- Code Box -->
              <div style="background-color: #1e293b; border: 1px dashed #f59e0b; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 28px;">
                <span style="font-family: monospace; font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #f59e0b;">{code}</span>
              </div>
              <!-- CTA Button -->
              <div style="text-align: center; margin-bottom: 30px;">
                <a href="{verification_url}" style="background-color: #f59e0b; color: #020617; text-decoration: none; padding: 12px 28px; font-weight: bold; font-size: 14px; border-radius: 8px; display: inline-block;">Verify Account Online</a>
              </div>
              <p style="color: #64748b; font-size: 12px; line-height: 1.5; margin-bottom: 0;">
                This code will expire in 30 minutes. If you did not create a NyayaSaathi AI account, you can safely ignore this message.
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding: 20px 30px; background-color: #020617; border-top: 1px solid #1e293b; text-align: center; color: #64748b; font-size: 11px;">
              NyayaSaathi AI • Built for Indian Consumer Rights • Grounded in Consumer Protection Act, 2019
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    return text_content, html_content


def render_password_reset_email(user_name: str, reset_url: str) -> Tuple[str, str]:
    text_content = f"""Hello {user_name},

We received a request to reset your NyayaSaathi AI password.

Click or copy the link below to set a new password:
{reset_url}

This link will expire in 15 minutes. If you did not request a password reset, please secure your account immediately.

NyayaSaathi AI Security Team
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Reset your NyayaSaathi AI Password</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0b1120; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f8fafc;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding: 40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #0f172a; border-radius: 16px; border: 1px solid #1e293b; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
          <tr>
            <td style="padding: 30px; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border-bottom: 1px solid #334155;">
              <span style="font-size: 20px; font-weight: bold; color: #f59e0b;">NyayaSaathi AI</span>
            </td>
          </tr>
          <tr>
            <td style="padding: 40px 30px;">
              <h2 style="color: #ffffff; font-size: 20px; margin-top: 0; margin-bottom: 16px;">Password Reset Request</h2>
              <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6; margin-bottom: 28px;">
                Hello <strong>{user_name}</strong>,<br><br>
                We received a request to reset your NyayaSaathi AI password. Click the button below to choose a new password:
              </p>
              <div style="text-align: center; margin-bottom: 28px;">
                <a href="{reset_url}" style="background-color: #f59e0b; color: #020617; text-decoration: none; padding: 12px 28px; font-weight: bold; font-size: 14px; border-radius: 8px; display: inline-block;">Reset Password</a>
              </div>
              <p style="color: #64748b; font-size: 12px; line-height: 1.5; margin-bottom: 0;">
                This link will expire in 15 minutes. If you did not make this request, someone may be attempting to access your account. Your current password remains unchanged.
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding: 20px 30px; background-color: #020617; border-top: 1px solid #1e293b; text-align: center; color: #64748b; font-size: 11px;">
              NyayaSaathi AI Security & Authentication
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    return text_content, html_content


def render_security_alert_email(user_name: str, alert_type: str, details: str) -> Tuple[str, str]:
    text_content = f"""Security Notification for {user_name},

Alert Type: {alert_type}
Details: {details}

If you did not perform this action, please change your password and revoke all active sessions immediately.

NyayaSaathi AI Security Team
"""

    html_content = f"""<!DOCTYPE html>
<html>
<body style="background-color: #0b1120; font-family: sans-serif; color: #f8fafc; padding: 30px;">
  <div style="max-width: 600px; margin: auto; background-color: #0f172a; padding: 30px; border-radius: 12px; border: 1px solid #334155;">
    <h3 style="color: #f59e0b; margin-top: 0;">Security Alert: {alert_type}</h3>
    <p style="color: #cbd5e1; font-size: 14px;">Hello <strong>{user_name}</strong>,</p>
    <p style="color: #cbd5e1; font-size: 14px;">{details}</p>
    <p style="color: #94a3b8; font-size: 12px;">If this was you, you can safely ignore this alert. If not, please review your active sessions and reset your password.</p>
  </div>
</body>
</html>"""
    return text_content, html_content

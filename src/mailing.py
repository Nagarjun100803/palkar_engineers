import smtplib
from fastapi import HTTPException, status
from config import email_cred, app_cred
from email.message import EmailMessage


def create_and_send_reset_email(to_addr: str, token: str):
    try:
        
        with smtplib.SMTP('smtp.gmail.com', email_cred.email_server_port) as smtp:
            
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            smtp.login(user = email_cred.email_id, password = email_cred.email_password)
            print('Login into SMTP server Successfully')


            msg = EmailMessage()

            msg['From'] = email_cred.email_id
            msg['To'] = to_addr
            msg['Subject'] = 'Password reset request, please click the below link to reset the password.'
            
            html_content = f"""
            <html>
            <head>
                <style>
                    .email-container {{
                        font-family: Arial, sans-serif;
                        padding: 20px;
                        background-color: #f7f7f7;
                        color: #333;
                    }}
                    .email-header {{
                        text-align: center;
                        margin-bottom: 20px;
                    }}
                    .email-body {{
                        background-color: #ffffff;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                    }}
                    .email-footer {{
                        text-align: center;
                        margin-top: 20px;
                        font-size: 12px;
                        color: #999;
                    }}
                    .reset-button {{
                        display: inline-block;
                        padding: 10px 20px;
                        margin-top: 20px;
                        background-color: #4CAF50;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        font-size: 16px;
                    }}
                    .reset-button:hover {{
                        background-color: #45a049;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="email-header">
                        <h2>Password Reset Request</h2>
                    </div>
                    <div class="email-body">
                        <p>Hello,</p>
                        <p>You recently requested to reset your password. Click the button below to reset it.</p>
                        <p>If you did not request this, please ignore this email.</p>
                        <a href="{app_cred.app_host}:{app_cred.app_port}/reset_password?reset_token={token}" 
                        class="reset-button">Reset Password</a>
                    </div>
                    <div class="email-footer">
                        <p>If you are having trouble clicking the "Reset Password" button, copy and paste the URL below into your web browser:</p>
                        <p><a href="{app_cred.app_host}:{app_cred.app_port}/reset_password?reset_token={token}">
                            {app_cred.app_host}:{app_cred.app_port}/reset_password?reset_token={token}
                        </a></p>
                    </div>
                </div>
            </body>
            </html>
            """
            # msg.set_content(f'{app_cred.app_host}:/{app_cred.app_port}/reset_password?reset_token={token}')
            msg.set_content("This is an HTML email. Please view in an HTML-compatible email client.")
            msg.add_alternative(html_content, subtype='html')

            smtp.send_message(msg)
            print(f'email is sent to {to_addr}')

    except Exception as e:
        print('Failed to connect the SMTP Server')
        








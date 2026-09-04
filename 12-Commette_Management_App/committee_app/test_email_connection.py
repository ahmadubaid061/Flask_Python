import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()

MAIL_SERVER = os.environ.get("MAIL_SERVER")
MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

print("🔍 Testing Email Connection...")
print(f"   Server: {MAIL_SERVER}")
print(f"   Port: {MAIL_PORT}")
print(f"   Username: {MAIL_USERNAME}")

try:
    # Create connection
    print("\n📡 Connecting to Gmail...")
    server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=10)
    
    print("✅ Connected! Starting TLS...")
    server.starttls()
    
    print("🔐 Logging in...")
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    
    print("✅ Login successful!")
    
    # Send test email
    print("\n📧 Sending test email...")
    msg = MIMEText("This is a test email from Committee Manager")
    msg['Subject'] = "Test Email"
    msg['From'] = MAIL_USERNAME
    msg['To'] = MAIL_USERNAME
    
    server.send_message(msg)
    
    print("✅ Email sent successfully!")
    
    server.quit()
    print("\n✅ All checks passed! Email is working.")
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Check if 'Less secure app access' is ON")
    print("2. Check if 2-Step Verification is enabled")
    print("3. Make sure app password is correct (no spaces)")
    print("4. Check if firewall/antivirus is blocking port 587")
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_connection():
    """Test email connection and credentials"""
    
    # Get email credentials
    mail_sender = os.getenv('EMAIL_SENDER', 'potholedetection06@gmail.com')
    mail_password = os.getenv('EMAIL_PASSWORD', 'ywxcjunxmexdvcle')
    mail_receiver = 'suhastms2004@gmail.com'
    
    print(f"Testing email connection...")
    print(f"Sender: {mail_sender}")
    print(f"Receiver: {mail_receiver}")
    print(f"Password: {'*' * len(mail_password) if mail_password else 'NOT SET'}")
    
    # Create test message
    msg = MIMEMultipart()
    msg['From'] = mail_sender
    msg['To'] = mail_receiver
    msg['Subject'] = 'Test Email - Defense Detection System'
    
    body = "This is a test email to verify the email functionality is working correctly."
    msg.attach(MIMEText(body, 'plain'))
    
    # Test SMTP connection
    context = ssl.create_default_context()
    
    try:
        print("Attempting to connect to Gmail SMTP server...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            print("Connected to SMTP server successfully!")
            
            print("Attempting to login...")
            smtp.login(mail_sender, mail_password)
            print("Login successful!")
            
            print("Sending test email...")
            smtp.sendmail(mail_sender, mail_receiver, msg.as_string())
            print("✅ Test email sent successfully!")
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("Possible causes:")
        print("1. Incorrect email or password")
        print("2. 2-factor authentication enabled - need app password")
        print("3. Less secure app access disabled")
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def check_environment():
    """Check environment variables and files"""
    print("\n=== Environment Check ===")
    
    # Check for .env file
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ .env file found")
    else:
        print(f"❌ .env file not found")
        
    # Check environment variables
    email_sender = os.getenv('EMAIL_SENDER')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    print(f"EMAIL_SENDER: {'SET' if email_sender else 'NOT SET'}")
    print(f"EMAIL_PASSWORD: {'SET' if email_password else 'NOT SET'}")
    
    # Check attachment directories
    print("\n=== File Check ===")
    results_dir = "results"
    if os.path.exists(results_dir):
        print(f"✅ Results directory exists")
        
        image_path = "results/image_result.jpg"
        video_path = "results/processed.mp4"
        
        if os.path.exists(image_path):
            print(f"✅ Image result file exists: {image_path}")
        else:
            print(f"❌ Image result file missing: {image_path}")
            
        if os.path.exists(video_path):
            print(f"✅ Video result file exists: {video_path}")
        else:
            print(f"❌ Video result file missing: {video_path}")
    else:
        print(f"❌ Results directory missing: {results_dir}")

if __name__ == "__main__":
    print("=== Email Functionality Test ===")
    check_environment()
    print("\n=== SMTP Connection Test ===")
    test_email_connection()

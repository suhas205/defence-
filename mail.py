from email.message import EmailMessage
import ssl
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_email(cont_dic, mail_receiver, is_video=False):
    mail_sender = 'potholedetection06@gmail.com'
    mail_password = 'wkszzawgsrighwqi' 

    # Validate credentials
    if not mail_sender or not mail_password:
        print("❌ Email credentials not found in environment variables")
        print("💡 Please check your .env file and ensure EMAIL_SENDER and EMAIL_PASSWORD are set")
        return False

    print(f"📧 Preparing email from {mail_sender} to {mail_receiver}")

    # Create the multipart message
    msg = MIMEMultipart()
    msg['From'] = mail_sender
    msg['To'] = mail_receiver
    msg['Subject'] = 'Defense Detection Report'

    body = f"Targets detected at location: {cont_dic['location']}.\nTarget Type: {cont_dic['highway_type']}\nSize: {cont_dic['size']}\nPosition: {cont_dic['position']}\n\nPlease review the detection results."
    msg.attach(MIMEText(body, 'plain'))

    # Add attachments with better error handling
    attachment_added = False
    
    if is_video:
        video_path = "results/processed.mp4"
        if os.path.exists(video_path):
            try:
                with open(video_path, 'rb') as f:
                    video_data = f.read()
                    video_attachment = MIMEApplication(video_data, _subtype="mp4")
                    video_attachment.add_header('Content-Disposition', 'attachment', filename='detection_result.mp4')
                    msg.attach(video_attachment)
                    attachment_added = True
                    print(f"✅ Video attachment added: {video_path}")
            except Exception as e:
                print(f"⚠️ Failed to attach video: {e}")
        else:
            print(f"⚠️ Video file not found: {video_path}")
    else:
        image_path = "results/image_result.jpg"
        if os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as f:
                    img_data = f.read()
                    image = MIMEImage(img_data, name="detection_result.jpg")
                    msg.attach(image)
                    attachment_added = True
                    print(f"✅ Image attachment added: {image_path}")
            except Exception as e:
                print(f"⚠️ Failed to attach image: {e}")
        else:
            print(f"⚠️ Image file not found: {image_path}")

    # Establish a secure SSL connection and send the email
    context = ssl.create_default_context()
    try:
        print("🔐 Connecting to Gmail SMTP server...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            print("🔑 Attempting login...")
            smtp.login(mail_sender, mail_password)
            print("📤 Sending email...")
            smtp.sendmail(mail_sender, mail_receiver, msg.as_string())
            print(f"✅ Email sent successfully! Attachment: {'Yes' if attachment_added else 'No'}")
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Gmail authentication failed: {e}")
        print("💡 SOLUTION NEEDED:")
        print("   1. Enable 2-Factor Authentication on your Google account")
        print("   2. Generate an App Password for Mail")
        print("   3. Update EMAIL_PASSWORD in .env file with the App Password")
        print("   4. Or use a different email service (Outlook, etc.)")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error sending email: {e}")
        return False


def send_alert_image(image_path, mail_receiver, subject="Defense Detection Alert", body="Automatic alert: detection detected."):
    mail_sender = 'potholedetection06@gmail.com'
    mail_password = 'wkszzawgsrighwqi'
    if not mail_sender or not mail_password:
        return False
    msg = MIMEMultipart()
    msg['From'] = mail_sender
    msg['To'] = mail_receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    if os.path.exists(image_path):
        try:
            with open(image_path, 'rb') as f:
                img_data = f.read()
                image = MIMEImage(img_data, name=os.path.basename(image_path))
                msg.attach(image)
        except Exception as e:
            print(f"⚠️ Failed to attach alert image: {e}")
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(mail_sender, mail_password)
            smtp.sendmail(mail_sender, mail_receiver, msg.as_string())
        return True
    except Exception as e:
        print(f"❌ Unexpected error sending alert email: {e}")
        return False

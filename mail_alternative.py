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

def send_email_outlook(cont_dic, mail_receiver, is_video=False):
    """Alternative email function using Outlook/Hotmail SMTP"""
    # Get email credentials from environment variables
    mail_sender = os.getenv('OUTLOOK_SENDER','potholedetection06@gmail.com')
    mail_password = os.getenv('OUTLOOK_PASSWORD', 'wkszzawgsrighwqi')

    # Create the multipart message
    msg = MIMEMultipart()
    msg['From'] = mail_sender
    msg['To'] = mail_receiver
    msg['Subject'] = 'Defense Detection Report'

    body = f"Targets detected at location: {cont_dic['location']}.\nTarget Type: {cont_dic['highway_type']}\nSize: {cont_dic['size']}\nPosition: {cont_dic['position']}\n\nPlease review the detection results."
    msg.attach(MIMEText(body, 'plain'))

    if is_video:
        # Attach the processed video if it exists
        video_path = "results/processed.mp4"
        if os.path.exists(video_path):
            with open(video_path, 'rb') as f:
                video_data = f.read()
                video_attachment = MIMEApplication(video_data, _subtype="mp4")
                video_attachment.add_header('Content-Disposition', 'attachment', filename='detection_result.mp4')
                msg.attach(video_attachment)
    else:
        # Attach the detection image if it exists
        image_path = "results/image_result.jpg"
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                img_data = f.read()
                image = MIMEImage(img_data, name="detection_result.jpg")
                msg.attach(image)

    # Establish a secure SSL connection and send the email
    context = ssl.create_default_context()
    try:
        # Outlook SMTP settings
        with smtplib.SMTP('smtp-mail.outlook.com', 587) as smtp:
            smtp.starttls(context=context)
            smtp.login(mail_sender, mail_password)
            smtp.sendmail(mail_sender, mail_receiver, msg.as_string())
            print(f"Email sent successfully via Outlook with {'video' if is_video else 'image'} attachment!")
    except Exception as e:
        print(f"Error sending email via Outlook: {e}")

def send_email_fixed_gmail(cont_dic, mail_receiver, is_video=False):
    """Fixed Gmail function with better error handling"""
    # Get email credentials from environment variables
    mail_sender = os.getenv('EMAIL_SENDER', 'potholedetection06@gmail.com')
    mail_password = os.getenv('EMAIL_PASSWORD', 'wkszzawgsrighwqi')

    # Validate credentials
    if not mail_sender or not mail_password:
        print("❌ Email credentials not found in environment variables")
        return False

    # Create the multipart message
    msg = MIMEMultipart()
    msg['From'] = mail_sender
    msg['To'] = mail_receiver
    msg['Subject'] = 'Defense Detection Report'

    body = f"Targets detected at location: {cont_dic['location']}.\nTarget Type: {cont_dic['highway_type']}\nSize: {cont_dic['size']}\nPosition: {cont_dic['position']}\n\nPlease review the detection results."
    msg.attach(MIMEText(body, 'plain'))

    # Add attachments
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

    # Send email
    context = ssl.create_default_context()
    try:
        print(f"📧 Attempting to send email from {mail_sender} to {mail_receiver}")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(mail_sender, mail_password)
            smtp.sendmail(mail_sender, mail_receiver, msg.as_string())
            print(f"✅ Email sent successfully! Attachment: {'Yes' if attachment_added else 'No'}")
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Gmail authentication failed: {e}")
        print("💡 Solution: Use Gmail App Password instead of regular password")
        print("   1. Enable 2FA on your Google account")
        print("   2. Generate App Password for Mail")
        print("   3. Update EMAIL_PASSWORD in .env file")
        return False
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

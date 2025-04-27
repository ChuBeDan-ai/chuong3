import os
import shutil
import datetime
import schedule
import time
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
BACKUP_FOLDER = os.getenv("BACKUP_FOLDER")

def send_email(subject, body):
    """
    Hàm này gửi email thông báo với tiêu đề và nội dung cho trước.

    Tham số:
        subject (str): Tiêu đề của email.
        body (str): Nội dung của email.
    """
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("Email thông báo đã được gửi thành công.")
        return True
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")
        return False

def backup_databases():
    """
    Hàm này thực hiện backup các file database (.sql, .sqlite3) và gửi email thông báo.
    """
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    backed_up_files = []
    failed_files = []

    for filename in os.listdir('.'):
        if filename.endswith(".sql") or filename.endswith(".sqlite3"):
            source_path = os.path.join('.', filename)
            destination_path = os.path.join(BACKUP_FOLDER, f"{filename}_{timestamp}")
            try:
                shutil.copy2(source_path, destination_path)
                backed_up_files.append(filename)
                print(f"Đã backup thành công: {filename} -> {destination_path}")
            except Exception as e:
                failed_files.append(filename)
                print(f"Lỗi khi backup {filename}: {e}")

    if backed_up_files:
        subject = "Thông báo Backup Database Thành Công"
        body = f"Các file database sau đã được backup thành công vào lúc {now.strftime('%d/%m/%Y %H:%M:%S')}:\n" + "\n".join(backed_up_files)
        if failed_files:
            body += f"\n\nCác file sau backup thất bại:\n" + "\n".join(failed_files)
        send_email(subject, body)
    elif failed_files:
        subject = "Thông báo Backup Database Thất Bại"
        body = "Không có file database nào được backup thành công.\nCác file backup thất bại:\n" + "\n".join(failed_files)
        send_email(subject, body)
    else:
        print("Không tìm thấy file database nào để backup.")

schedule.every().day.at("00:00").do(backup_databases)

if __name__ == "__main__":
    print("Script backup database đang chạy...")
    while True:
        schedule.run_pending()
        time.sleep(1)

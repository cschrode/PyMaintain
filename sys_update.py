#!/usr/bin/python3

import apt
import subprocess
import time
from time import strftime
import os
import sys

def update_packages():
    print("Outdated Packages\n===========================")

    apt_cache = apt.Cache()
    apt_cache.update()
    apt_cache.open(None)
    apt_cache.upgrade()
    apt_cache.commit()

    for package in apt_cache.get_changes():
        print(package.sourcePackageName, package.isUpgradable)

def send_logs():
    os.system("/usr/sbin/logwatch > /tmp/logwatch.log")

    # Requirements
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication
    from email.utils import COMMASPACE, formatdate
    from email import encoders
    import smtplib
    import mimetypes

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    from_address = 'john@example.com'
    to_address = 'log.repository@example.com'
    subject_header = 'Webserver Backup & Log Report {}'.format(strftime("%m-%d-%Y"))
    attachment = '/tmp/logwatch.log'
    body = ''

    for line in open('/repo/last_update.log'):
        body += line

    m = MIMEMultipart()
    m["To"] = to_address
    m["From"] = from_address
    m["Subject"] = subject_header

    try:
        ctype, encoding = mimetypes.guess_type(attachment)
        print(ctype, encoding)

        maintype, subtype = ctype.split('/', 1)
        print(maintype, subtype)
    except:
        pass

    m.attach(MIMEText(body))

    msg = MIMEApplication(open(attachment, 'rb').read())
    msg.add_header('Content-Disposition', 'attachment; filename="{}"'.format(os.path.basename(attachment)))
    m.attach(msg)

    # Connect to Gmail
    outgoing = smtplib.SMTP(smtp_server, smtp_port) #port 465 or 587

    # Gmail uses SSL by default
    outgoing.ehlo()
    outgoing.starttls()
    outgoing.ehlo()

    # Authenticate
    outgoing.login(from_address, 'SECRET PASSWORD GOES HERE')

    # Send E-mail
    outgoing.sendmail(from_address, to_address, m.as_string())

    # Cleanup
    outgoing.quit()

def cleanup():
    path = '/repo/backup'
    now = time.time()

    seconds_per_day = 86400
    days = 31

    for backup in os.listdir(path):
        backup = os.path.join(path, backup)
        if os.stat(backup).st_mtime < now - (days * seconds_per_day):
            if os.path.isfile(backup):
                print("Deleting old backup: {}".format(backup))
                os.remove(backup)

def main():
    update_packages()
    cleanup()
    send_logs()

if __name__ == "__main__":
    main()

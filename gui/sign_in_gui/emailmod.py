import smtplib
import ssl
import uuid
from email.message import EmailMessage
import random
from credentials import email_password
from credentials import email_sender



def send_email_verefication(email_reciver):
    security_code=str(uuid.uuid4())
    half_length=len(security_code)//2
    security_code=security_code[:half_length]

    em=EmailMessage()
    em['from']=email_sender
    em['to']=email_reciver
    em['subject']='verification'
    ran=random.random()
    verfetication=str(random.randint(0,9999)).zfill(4)
    em.set_content(f'your verfication code is '+ verfetication)
    context=ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
        smtp.login(email_sender,email_password)
        smtp.sendmail(email_sender,email_reciver,em.as_string())
        print('sent')
    return verfetication

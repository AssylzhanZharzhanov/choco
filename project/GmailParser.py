import imaplib
import hashlib
import getpass
import email
import email.message
import time
import os.path
import subprocess
import re
import sys

server = 'imap.gmail.com'
login = "thementalistaz@gmail.com"
password = "redjohnispj"
attachment_dir = '/home/mrx/PycharmProjects/untitled1/docs'

class Parser:
    def __init__(self, name):
        self.name = name

    def getFilenames(self):
        fileNames =self.parse()
        return fileNames

    def get_attachment(self, msg, fileNames):
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            fileName = part.get_filename()
            fileName = email.header.make_header(email.header.decode_header(fileName))
            fileName = str(fileName)
            fileNames.append(fileName)
            if bool(fileName):
                filePath = os.path.join(attachment_dir, fileName)
                with open(filePath, 'wb') as f:
                    f.write(part.get_payload(decode=True))

    def parse(self):
        imap = imaplib.IMAP4_SSL(server)
        imap.login(login, password)
        status, select_data = imap.select('INBOX')
        status, search_data = imap.search(None, 'From', '"{}"'.format('asik.zharzhanov@gmail.com'))
        fileNames = []
        for i in reversed(search_data[0].split()):
            status, fetch_data = imap.fetch(i, '(RFC822)')
            msg = email.message_from_bytes(fetch_data[0][1])
            subtitle = email.header.make_header(email.header.decode_header(msg['Subject']))
            # print(msg)
            if (subtitle == self.name):
                self.get_attachment(msg, fileNames)
        return fileNames




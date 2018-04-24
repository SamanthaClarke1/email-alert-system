import smtplib
from string import Template
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import socket

opts, names, emails, template, s = ""

opts = get_settings("options.json")
names, emails = get_contacts("contacts.txt")
template = read_template("alert.txt")

setup_smtp(opts)

def send_alert(s, alert, status, names, emails, template, opts):
	for name, email in zip(names, emails):
		msg = MIMEMultipart()
		
		now = datetime.datetime.now()
		message = template.substitute(PERSON_NAME=name.title(), STATUS=status, ERROR=alert, ERROR_DATE=now.strftime("%d/%m/%Y %H:%M"))

		msg.From = opts.LOGIN.USER
		msg.To = email
		msg.Subject = "Automated Alert"

		msg.attach(MIMEText(message, 'plain'))

		s.send_message(msg)

		del msg # E F F I C I E N C Y

def setup_smtp(opts):
	srvr = smtplib.SMTP(host=opts.SERVER.ADDR, port=opts.SERVER.PORT)
	srvr.starttls()
	srvr.login(opts.LOGIN.USER, opts.LOGIN.PASS)

	return srvr

def get_settings(filename):
	data = {}
	with open(filename, mode='r', encoding='utf-8') as options_file:
		data = json.load(options_file)
	return data

def get_contacts(filename):
	names = []
	emails = []
	with open(filename, mode='r', encoding='utf-8') as contacts_file:
		for contact in conctacts_file:
			if(contact[0] != "#"):
				names.append(contact.split(" | ")[0])
				emails.append(contact.split(" | ")[1])
	return names, emails

def read_template(filename):
	with open(filename, mode='r', encoding='utf-8') as template_file:
		template = template_file.read()
	return Template(template)


def check_service_online(opts):
    captive_dns_addr = ""
    host_addr = ""

    try:
        captive_dns_addr = socket.gethostbyname("BlahThisDomaynDontExist22.com")
    except:
        pass

    try:
        host_addr = socket.gethostbyname(opts.SERVER.ADDR)

        if (captive_dns_addr == host_addr):
            return False

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((opts.SERVER.ADDR, opts.SERVER.PORT))
        s.close()
    except:
        return False

    return True

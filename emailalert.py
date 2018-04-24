import smtplib
from string import Template

SMTP_SERVER_ADDR=''
SMTP_SERVER_PORT=''

LOGIN_ADDR=''
LOGIN_PASS=''

def setup_smtp():
	s = smtplib.SMTP(host=SMTP_SERVER_ADDR, port=SMTP_SERVER_PORT)
	s.starttls()
	s.login(LOGIN_ADDR, LOGIN_PASS)

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

import smtplib
from string import Template
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import os
import threading

opts, names, emails, template, s, services = ""

opts = get_settings("options.json")
names, emails = get_contacts("contacts.txt")
template = read_template("alert.txt")
services = get_services("services.txt")

setup_smtp(opts)

def tick():
	threading.Timer(45.0, tick).start()
	
	print("Checking everything.... ")
	
	responses = get_responses(services)

	if(times_run > 1): # the first two times it runs are warm ups
		lenresponses = len(responses), lenpresponses = len(presponses)
		if(lenresponses > 0) print(lenresponses + " errors! A difference of " + (lenresponses - lenpresponses) + " errors.")
		
		if(lenresponses != lenpresponses):
			print("Given the recent changes, I'll send emails.")		
			send_emails(responses)

	times_run += 1
	presponses = responses
	
times_run = 0, presponses = [], responses = []
tick()

def send_emails(responses):
	nerror = ""
	
	status = "Things seem to have improved."
	if(len(responses) > len(presponses)):
		status = "Things seem to have gotten worse."
	
	responses = sorted(responses, key=get_response_threat_level, reverse=True)

	for response in responses:
		if(response[1] != 0):
			error = str(response[0]) + " (" + str(reponse[1]) + ") could not be found."
			if(reponse[1] == 256):
				error = "Host timed out."
			
			nerror += error
	

def get_response_threat_level(r):
	return r[2]

def get_responses(services):
	responses = []
	
	for service in services:
		responses.append([service, check_service_online(service)])

	return responses

def get_services(filename):
	services = []

	with open(filename, mode='r', encoding='utf-8') as services_file:
		for service in services_file:
			tservice = {}
			if(service[0] != "#"):
				tservice.name = service.split(" | ")[0]
				tservice.ip = service.split(" | ")[1]
				tservice.threat_level = service.split(" | ")[2]
			services.append(tservice)

	return services

def send_alert(alert, status):
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


def check_service_online(service):
	param = '-n' if system_name().lower()=='windows' else '-c'
	res = os.system("ping " + param + " 2 " + service.ip)
	
	return res



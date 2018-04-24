#### ENTER IMPORTS ####

import smtplib
from string import Template
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import threading
import platform
from subprocess import call

#### END IMPORTS, ENTER FUNCS ####

def send_emails(responses):
	nerror = ""
	
	status = "Things seem to have improved."
	if(len(responses) > len(presponses)):
		status = "Things seem to have gotten worse."
	
	responses = sorted(responses, key=get_response_threat_level, reverse=True)

	for response in responses:
		if(response[1] != 0):
			error = str(response[0]['name']) + " (" + str(reponse[0]['ip']) + ") could not be found."
			if(reponse[1] == 256):
				error = str(response[0]['name']) + " (" + str(reponse[0]['ip']) + ") timed out."
			
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

	with open(filename, mode='r') as services_file:
		for service in services_file:
			tservice = {}
			if(service[0] != "#"):
				tservice['name'] = service.split(" | ")[0]
				tservice['ip'] = service.split(" | ")[1]
				tservice['threat_level'] = service.split(" | ")[2]
				services.append(tservice)

	return services

def send_alert(alert, status):
	for name, email in zip(names, emails):
		msg = MIMEMultipart()
		
		now = datetime.datetime.now()
		message = template.substitute(PERSON_NAME=name.title(), STATUS=status, ERROR=alert, ERROR_DATE=now.strftime("%d/%m/%Y %H:%M"))

		msg.From = opts['LOGIN']['USER']
		msg.To = email
		msg.Subject = "Automated Alert"

		msg.attach(MIMEText(message, 'plain'))

		s.send_message(msg)

		del msg # E F F I C I E N C Y

def setup_smtp(opts):
	print("\nConnected to: " + str(opts['SERVER']['ADDR']) + " on port " + str(opts['SERVER']['PORT']) + "\n")
	srvr = smtplib.SMTP(host=str(opts['SERVER']['ADDR']), port=int(opts['SERVER']['PORT']))
	srvr.starttls()
	srvr.login(opts['LOGIN']['USER'], opts['LOGIN']['PASS'])

	return srvr

def get_settings(filename):
	data = {}
	with open(filename, mode='r') as options_file:
		data = json.load(options_file)
	return data

def get_contacts(filename):
	names = []
	emails = []
	with open(filename, mode='r') as contacts_file:
		for contact in contacts_file:
			if(contact[0] != "#"):
				names.append(contact.split(" | ")[0])
				emails.append(contact.split(" | ")[1])
	return names, emails

def read_template(filename):
	with open(filename, mode='r') as template_file:
		template = template_file.read()
	return Template(template)


def check_service_online(service):
	param = '-n' if platform.system().lower()=='windows' else '-c'
	res = call(["ping", param, "2", service['ip']])

	return res

def get_amt_errors(responses):
	total = 0
	for res in responses:
		if(res[1] != 0):
			total += 1
	return total

#### END FUNCS, ENTER MAIN PROGRAM ####

opts = ""
names = ""
emails = ""
template = "" 
s = "" 
services = ""

opts = get_settings("options.json")
names, emails = get_contacts("contacts.txt")
template = read_template("alert.txt")
services = get_services("services.txt")

setup_smtp(opts)

def tick(firsttime, presponses):
	print("\nChecking everything.... \n")
	
	responses = get_responses(services)
	threading.Timer(45.0, tick, args=(False,responses,)).start()

	if(not firsttime): # the first two times it runs are warm ups
		lenresponses = len(responses)
		errresponses = get_amt_errors(responses)
		lenpresponses = len(presponses)
		errpresponses = get_amt_errors(presponses)
		if(errresponses > 0):
			print(str(lenresponses) + " out of " + errresponses + " errors! A difference of " + str(lenresponses - lenpresponses) + " errors.")
		
		if(errresponses != errpresponses):
			print("Given the recent changes, I'll send emails.")		
			send_emails(responses)
	
	presponses = responses

presponses = []
responses = []
tick(True, [])

#### END MAIN PROGRAM ####

####       EOF        ####


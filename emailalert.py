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

def send_emails(responses, improved):
	nerror = ""
	
	status = "Things have gotten worse."
	if(improved):
		status = "Things have gotten better."
	
	responses = sorted(responses, key=get_response_threat_level, reverse=True)

	for response in responses:
		if(response[1] != 0):
			error = str(response[0]['name']) + " (" + str(response[0]['ip']) + ")   - -  could not be found."
			if(response[1] == 256):
				error = str(response[0]['name']) + " (" + str(response[0]['ip']) + ")    - -   timed out."
			
			nerror += error + "\n"
	
	send_alert(nerror, status)

def get_response_threat_level(r):
	return r[0]['threat_level']

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
	now = datetime.datetime.now()
	message = template.substitute(PERSON_NAME="everybody".title(), STATUS=status, ERROR=alert, ERROR_DATE=now.strftime("%d/%m/%Y %H:%M"))

	msg = MIMEText(message)

	msg.Subject = "Automated Alert"
	msg.From = "An evil cabal of robots"
	msg.To = "All those who will listen"

	print("Sending message to " + str(emails)) 
	s.sendmail(opts['LOGIN']['USER'], emails, msg.as_string())

	del msg # E F F I C I E N C Y

def setup_smtp(opts):
	print("\nConnected to: " + str(opts['SERVER']['ADDR']) + " on port " + str(opts['SERVER']['PORT']) + "\n")
	srvr = smtplib.SMTP(host=str(opts['SERVER']['ADDR']), port=int(opts['SERVER']['PORT']))
	srvr.starttls()
	srvr.login(opts['LOGIN']['USER'], opts['LOGIN']['PASS'])

	srvr.set_debuglevel(True)

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
	print("")
	param = '-n' if platform.system().lower()=='windows' else '-c'
	res = call(["ping", param, "1", service['ip']])

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

s = setup_smtp(opts)

def tick(firsttime, presponses):
	print("\nChecking everything.... \n")
	
	responses = get_responses(services)
	threading.Timer(30.0, tick, args=(False,responses,)).start()

	if(not firsttime): # the first two times it runs are warm ups
		lenresponses = len(responses)
		errresponses = get_amt_errors(responses)
		lenpresponses = len(presponses)
		errpresponses = get_amt_errors(presponses)
		if(errresponses > 0):
			print("\n" + str(errresponses) + " out of " + str(lenresponses) + " possible errors! A difference of " + str(errresponses - errpresponses) + " errors.")
		
		if(errresponses != errpresponses):
			print("Given the recent changes, I'll send emails.\n")		
			send_emails(responses, (errresponses < errpresponses))
	
	presponses = responses

presponses = []
responses = []
tick(True, [])

#### END MAIN PROGRAM ####

####       EOF        ####


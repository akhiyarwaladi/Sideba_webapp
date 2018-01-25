import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
def kirimEmail(pesan):
	fromaddr = "akiyar18@gmail.com"
	toaddr = ["akiyar18@gmail.com", "akiyar@apps.ipb.ac.id", "imas.sitanggang@apps.ipb.ac.id"]
	msg = MIMEMultipart()
	# msg['From'] = fromaddr
	# msg['To'] = toaddr
	msg['Subject'] = "Notifikasi SiDeba (Sistem Deteksi Banjir)"
	
	body = pesan
	msg.attach(MIMEText(body, 'plain'))

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, "Rickss12")
	text = msg.as_string()
	#text = pesan
	server.sendmail(fromaddr, toaddr, text)
	server.quit()
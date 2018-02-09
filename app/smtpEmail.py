import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

def kirimEmail(pesan):
	#fromaddr = "akiyar18@gmail.com"
	print("sending email")
	fromaddr = "sistem.otomatisasi8@gmail.com"
	#toaddr = ["akiyar18@gmail.com", "akiyar@apps.ipb.ac.id", "imas.sitanggang@apps.ipb.ac.id"]
	toaddr = ["syarif.budhiman@lapan.go.id","rokhis.khomarudin@lapan.go.id","ayom.widipaminto@lapan.go.id","rahmadi@lapan.go.id","bowo_lpn@yahoo.com","mpriyatna@yahoo.com","iskef55@gmail.com","dirkdoank@gmail.com", "akiyar18@gmail.com", "akiyar@apps.ipb.ac.id", "imas.sitanggang@apps.ipb.ac.id"]

	msg = MIMEMultipart()
	# msg['From'] = fromaddr
	# msg['To'] = toaddr
	msg['Subject'] = "Notifikasi SiDeba (Sistem Otomatisasi Deteksi Daerah Tergenang Banjir (SiDeba))"
	
	body = pesan
	msg.attach(MIMEText(body, 'plain'))

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, "8Pusfatj@")
	text = msg.as_string()
	#text = pesan
	server.sendmail(fromaddr, toaddr, text)
	print("email successfully send")
	server.quit()
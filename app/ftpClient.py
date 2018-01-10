from ftplib import FTP
import os
from redis import StrictRedis
import config
from datetime import datetime

def uploadFile():
	filename = 'Combinasi_654_Jabo_Lapan_modified.tif' #replace with your file in your home folder
	ftp.storbinary('STOR '+filename, open(filename, 'rb'))
	ftp.quit()

def downloadFile():
	redis = StrictRedis(host=config.REDIS_HOST)
	msg = str(datetime.now()) + '\t' + "Connecting to ftp server \n"
	redis.rpush(config.MESSAGES_KEY, msg)
	redis.publish(config.CHANNEL_NAME, msg)

	ftp = FTP( )
	ftp.connect(host='192.168.0.106', port=21, timeout=1246)
	ftp.login(user='banjir', passwd='lapan2017')
	ftp.retrlines('LIST')
	filesPreFlood = ftp.nlst('LC81190652016273LGN00')
	filesPostFlood = ftp.nlst('LC81190652017067RPI00')
	ftp.cwd('LC81190652016273LGN00')
	filesPreFlood = ftp.nlst()

	for file in filesPreFlood:
		print file
		msg = str(datetime.now()) + '\t' + "Downloading "+ str(file) + "\n"
		redis.rpush(config.MESSAGES_KEY, msg)
		redis.publish(config.CHANNEL_NAME, msg)
		filename = file #replace with your file in the directory ('directory_name')
		localfile = open(filename, 'wb')
		if(os.path.exists('C:/Apps/data/banjir/LC81190652016273LGN00/'+filename)):
			os.remove('C:/Apps/data/banjir/LC81190652016273LGN00/'+filename)

		ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
		localfile.close()


		os.rename(filename,'C:/Apps/data/banjir/LC81190652016273LGN00/'+filename)
		msg = str(datetime.now()) + '\t' + "Succesfully saved in "+ 'C:/Apps/data/banjir/LC81190652016273LGN00/'+filename + "\n"
		redis.rpush(config.MESSAGES_KEY, msg)
		redis.publish(config.CHANNEL_NAME, msg)

	ftp.cwd("../")
	ftp.cwd('LC81190652017067RPI00')
	filesPostFlood = ftp.nlst()
	for file in filesPostFlood:
		print file
		msg = str(datetime.now()) + '\t' + "Downloading "+ str(file) + "\n"
		redis.rpush(config.MESSAGES_KEY, msg)
		redis.publish(config.CHANNEL_NAME, msg)
		filename = file #replace with your file in the directory ('directory_name')
		localfile = open(filename, 'wb')
		if(os.path.exists('C:/Apps/data/banjir/LC81190652017067RPI00/'+filename)):
			os.remove('C:/Apps/data/banjir/LC81190652017067RPI00/'+filename)

		ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
		localfile.close()


		os.rename(filename,'C:/Apps/data/banjir/LC81190652017067RPI00/'+filename)
		msg = str(datetime.now()) + '\t' + "Succesfully saved in "+ 'C:/Apps/data/banjir/LC81190652017067RPI00/'+ filename + "\n"
		redis.rpush(config.MESSAGES_KEY, msg)
		redis.publish(config.CHANNEL_NAME, msg)

	ftp.quit()

	return "sukses"

#uploadFile()
#downloadFile()
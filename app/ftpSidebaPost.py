from ftplib import FTP
import os
from datetime import datetime
import shutil
import time
import smtpEmail as se
import config
from redis import StrictRedis
redis = StrictRedis(host=config.REDIS_HOST)


def connect_ftp():
	global ftp
	ftp = FTP( )
	ftp.connect(host=config.FTP_HOST, port=21, timeout=1246)
	ftp.login(user=config.FTP_USER, passwd=config.FTP_PASSWD)

def downloadFile(liScene):
	msg = str(datetime.now()) + '\t' + "Begin download post flood data ... \n"
	redis.rpush(config.MESSAGES_KEY, msg)
	redis.publish(config.CHANNEL_NAME, msg)

	boolScene = False
	sceneData = ""
	levelData = ""
	print "Sudah diproses " + str(liScene)
	tupDate = datetime.now()
	#print now.year, now.month, now.day, now.hour, now.minute, now.second # check every datetime detail
	##################### MULAI KONEKSI KE FTP #############################################
	#################### GANTI DENGAN CREDENTIAL SEBENARNYA ################################
	connect_ftp()
	#ftp.retrlines('LIST') # use to check file after connected
	########################################################################################
	# masuk ke folder landsat 8
	ftp.cwd('Landsat_8')
	tahun = str(tupDate.year - 1)
	hari = str(int(tupDate.strftime('%j')) + 258)
	print tahun
	print hari
	# masuk ke folder tahun
	ftp.cwd(tahun)
	# lihat isi di dalam folder tahun
	folderTahun = ftp.nlst()
	# jika folder hari ini belum ada looping terus
	while (hari not in folderTahun):
		print "Belum ada folder data hari ini ("+hari+")"
		se.kirimEmail("Belum ada folder data hari ini ("+hari+")")
		time.sleep(30)

		connect_ftp()

		ftp.cwd('Landsat_8')
		ftp.cwd(tahun)
		folderTahun = ftp.nlst()

	# masuk ke folder hari dalam format doy
	ftp.cwd(hari)
	# lihat isi di dalam folder hari format doy
	folderHari = ftp.nlst()
	# jika di dalam folder hari kosong looping terus
	while (len(folderHari) == 0):
		print "Belum ada data di dalam folder hari " + hari 
		se.kirimEmail("Belum ada data di dalam folder hari ini ("+hari+")")
		time.sleep(30)

		connect_ftp()

		ftp.cwd('Landsat_8')
		ftp.cwd(tahun)
		ftp.cwd(hari)
		folderHari = ftp.nlst()

	# looping setiap folder level data landsat
	for level in ftp.nlst():

		print level
		# masuk ke folder level yang tersedia
		ftp.cwd(str(level))
		folderLevel = ftp.nlst()

		# while (len(folderLevel) == 0):
		# 	print "Belum ada data di dalam folder level " + hari 
		# 	time.sleep(5)
		# 	folderLevel = ftp.nlst()

		levelData = str(level)
		# looping setiap folder scene yang ditemukan
		for scene in ftp.nlst():
			print scene
			sceneData = scene
			# jika scene termasuk kedalam list yang telah diproses
			if scene in liScene:
				print "scene " + str(scene) + " sudah diproses"
				# lanjut lihat folder scene yang lainnya
				continue;
			# jika tidak termasuk maka set boolean bahwa ada data yang akan diproses
			boolScene = True
			# jika folder data ada pada workstation
			if(os.path.exists('C:/data/banjir/postFlood/'+ scene)):
				# hapus data tersebut
				shutil.rmtree('C:/data/banjir/postFlood/'+ scene)
			# buat folder baru pada workstation untuk scene yang akan diproses
			os.makedirs('C:/data/banjir/postFlood/'+ scene)

			# masuk kedalam scene yang akan diproses
			ftp.cwd(scene)
			# jadikan list semua file yang ada dalam folder scenen untuk didownload
			filesPreFlood = ftp.nlst()
			# jika folder data belum lengkap
			if len(filesPreFlood) < 14:
				print "scene" + str(scene) + " data folder ini belum lengkap"
				# lanjut lihat folder scene yang lainnya 
				continue;
				
			filesPreFlood2 = [img for img in filesPreFlood if img.endswith("_B3.TIF") or img.endswith("_B4.TIF") or img.endswith("_B5.TIF") or 
			img.endswith("_BQA.TIF") or img.endswith("_MTL.txt")]
			print filesPreFlood2
			# looping setiap file yang ada
			for file in filesPreFlood2:
				print file

				msg = str(datetime.now()) + '\t' + "Downloading "+ str(file) + "\n"
				filename = file #replace with your file in the directory ('directory_name')
				localfile = open(filename, 'wb')

				# jika file ada dalam folder
				if(os.path.exists('C:/data/banjir/postFlood/'+ scene +'/'+filename)):
					# hapus file yang ada tersebut
					os.remove('C:/data/banjir/postFlood/'+ scene +'/'+filename)

				ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
				localfile.close()

				# pindahkan data dari local workspace ftp download ke tempat seharusnya
				os.rename(filename,'C:/data/banjir/postFlood/'+ scene +'/'+filename)

			# setelah selesai download satu scene langsung keluar loop
			break;
			# keluar dari folder scene
			ftp.cwd("../")
		# keluar dari folder level data landsat
		ftp.cwd("../")

	# jika ada scene yang akan diproses
	if(boolScene == True):
		# masuk ke folder scene dalam workstation
		os.chdir('C:/data/banjir/postFlood/'+ scene)
		# looping setiap file yang ada
		for filename in os.listdir('C:/data/banjir/postFlood/'+ scene):
			productID = filename.split(".")[0]
			extension = filename.split(".")[1]
			unique = filename.split(".")[0].split("_")[7]
			# ubah nama file tersebut dengan format [sceneID_band.ext]
			os.rename(filename, scene + "_" + unique + "." + extension)

	msg = str(datetime.now()) + '\t' + "Finished download post flood data ... \n"
	redis.rpush(config.MESSAGES_KEY, msg)
	redis.publish(config.CHANNEL_NAME, msg)

	# kembalikan nama scene dan boolean tanda ke program utama
	return sceneData, boolScene, tahun, hari, levelData
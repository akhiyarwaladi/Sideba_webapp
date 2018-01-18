from ftplib import FTP
import os
from datetime import datetime
import shutil
def downloadFile(liScene):
	boolScene = False
	print "Sudah diproses " + str(liScene)
	tupDate = datetime.now()
	#print now.year, now.month, now.day, now.hour, now.minute, now.second # check every datetime detail
	##################### MULAI KONEKSI KE FTP #############################################
	#################### GANTI DENGAN CREDENTIAL SEBENARNYA ################################
	ftp = FTP( )
	ftp.connect(host='localhost', port=21, timeout=1246)
	ftp.login(user='akhiyarwaladi', passwd='rickss12')
	#ftp.retrlines('LIST') # use to check file after connected
	########################################################################################
	# masuk ke folder landsat 8
	ftp.cwd('Landsat_8')
	# masuk ke folder tahun
	ftp.cwd(str(tupDate.year - 1))
	# masuk ke folder hari dalam format doy
	ftp.cwd(str(int(tupDate.strftime('%j')) + 273))
	# looping setiap folder level data landsat
	for level in ftp.nlst():
		print level
		# masuk ke folder level yang tersedia
		ftp.cwd(str(level))
		# looping setiap folder scene yang ditemukan
		for scene in ftp.nlst():
			print scene
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
			# looping setiap file yang ada
			for file in filesPreFlood:
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

	tahun = str(tupDate.year - 1)
	hari = str(int(tupDate.strftime('%j')) + 273)
	levelData = str(level)
	# kembalikan nama scene dan boolean tanda ke program utama
	return scene, boolScene, tahun, hari, levelData
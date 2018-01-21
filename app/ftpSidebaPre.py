from ftplib import FTP
import os
from datetime import datetime
import shutil
import pandas as pd
def parse_mtl(path, mtl):
    '''Traverse the downloaded landsat directory and read MTL file

        @type    path: c{str}
        @param   path: Path to landsat file directory
        @rtype   C{dict}
        @return  Dictionary
    '''

    # if path is None:
    #     path = "c:/landsat"

    
    # files = os.listdir(path)
    # mtl = [txt for txt in files if 'MTL.txt' in txt][0]
    lines = iter(open(os.path.join(path, mtl)).readlines())
    hdrdata= {}

    line = lines.next()

    while line:
        line=[item.strip() for item in line.replace('"','').split('=')]
        group=line[0].upper()
        if group in ['END;','END']:break
        value=line[1]
        if group in ['END_GROUP']:pass
        elif group in ['GROUP']:
            group=value
            subdata={}
            while line:
                line=lines.next()
                line = [l.replace('"','').strip() for l in line.split('=')]
                subgroup=line[0]
                subvalue=line[1]
                if subgroup == 'END_GROUP':
                    break
                elif line[1] == '(':
                    while line:
                        line=lines.next()
                        line = line.replace('"','').strip()
                        subvalue+=line
                        if line[-1:]==';':
                            subvalue=eval(subvalue.strip(';'))
                            break
                else:subvalue=subvalue.strip(';')
                subdata[subgroup]=subvalue
            hdrdata[group]=subdata
        else: hdrdata[group]=value.strip(');')
        line=lines.next()
    return hdrdata

def date_to_nth_day(date, format='%Y%m%d'):
    date = pd.to_datetime(date, format=format)
    new_year_day = pd.Timestamp(year=date.year, month=1, day=1)
    return (date - new_year_day).days + 1

def downloadFile(scene_id_post):

	print scene_id_post
	print scene_id_post[3:9]
	pathRowPost = scene_id_post[3:9]

	##################### Mulai koneksi ke ftp, ganti credential ########################
	ftp = FTP( )
	ftp.connect(host='localhost', port=21, timeout=1246)
	ftp.login(user='akhiyarwaladi', passwd='rickss12')
	#ftp.retrlines('LIST') # use to check file after connected
	#####################################################################################

	# masuk ke folder landsat 8
	ftp.cwd('Landsat_8')
	# masuk ke folder 2017
	ftp.cwd('2017')

	# untuk menyimpan besarnya cloud cover scene yang akan dipakai
	cloud_dict = {}
	# untuk menyimpan ID scene 
	cloud_dict_id = {}

	# looping dari doy musing kering yaitu 151 sampai 213, dapat disesuaikan kemudian
	for i in range(151, 213):
		# masuk ke folder hari doy satu persatu
		ftp.cwd(str(i))
		# looping setiap jenis level data yang tersedia
		for level in ftp.nlst():
			print level
			# masuk ke jenis level data
			ftp.cwd(str(level))
			# looping setiap folder scene yang tersedia
			for scene in ftp.nlst():
				# dapatkan pathrow dari scene yang tersedia
				pathRowPre = scene[3:9]
				print pathRowPre
				# jika pathrow dari post tidak sama dengan scene yang saat ini tersedia
				if (pathRowPost != pathRowPre):
					print "pathrow tidak sama"
					# cari scene yang lain / keluar dari folder scene
					continue;

				# jika pathrow sama, masuk ke folder scene 
				ftp.cwd(scene)
				# jadikan list setiap file yang ada
				filesPreFlood = ftp.nlst()

				# cari metadata file dari scene yang saat ini tersedia
				fileMtl = [txt for txt in filesPreFlood if 'MTL.txt' in txt][0]
				print fileMtl

				# donwload file metadata scene ini
				localfile = open(fileMtl, 'wb')
				ftp.retrbinary('RETR ' + fileMtl, localfile.write, 1024)
				localfile.close()

				# jika file metadata ada pada workstation, hapus file tersebut
				if(os.path.exists('C:/data/banjir/preFlood/' + fileMtl)):
					os.remove('C:/data/banjir/preFlood/' + fileMtl)
				# pindahkan file metadata ke workstation
				os.rename(fileMtl,'C:/data/banjir/preFlood/' + fileMtl)

				# parsing file metadata ke dictionary
				mtl = parse_mtl('C:/data/banjir/preFlood/', fileMtl)
				# dapatkan product id dari metadata
				product_id = str(mtl['L1_METADATA_FILE']['LANDSAT_PRODUCT_ID'])
				# dapatkan cloud cover dari metadata
				cloud_cover = str(mtl['IMAGE_ATTRIBUTES']['CLOUD_COVER_LAND'])

				print product_id
				print cloud_cover
				# masukkan cloud cover ke dictionary
				cloud_dict[product_id] = cloud_cover
				# masukkan scene id ke dictionary
				cloud_dict_id[product_id] = scene

				# keluar dari scene
				ftp.cwd("../")
			# keluar dari level
			ftp.cwd("../")
		# keluar dari hari doy
		ftp.cwd("../")

	print cloud_dict
	# dapatkan product id yang cloud covernya paling minimun dala dictionary
	bestPreFlood = min(cloud_dict, key=cloud_dict.get)
	# dapatkan scene id berdasarkan product id yang terbaik, karena folder ftp dalam bentuk scene id
	scene = cloud_dict_id[bestPreFlood]

	# split product id yang terbaik untuk mendapatkan detil folder
	bestPreFloodList = bestPreFlood.split("_")
	print date_to_nth_day(bestPreFloodList[3])

	# masuk ke folder hari dalam doy
	ftp.cwd(str(date_to_nth_day(bestPreFloodList[3])))
	# masuk ke folder level data
	ftp.cwd(bestPreFloodList[1])
	# masuk ke dalam folder scene
	ftp.cwd(scene)
	# jadikan list semua file dalam folder
	filesPreFlood = ftp.nlst()
	filesPreFlood2 = [img for img in filesPreFlood if img.endswith("_B3.TIF") or img.endswith("_B4.TIF") or img.endswith("_B5.TIF") or 
	img.endswith("_BQA.TIF") or img.endswith("_MTL.txt")]
	print filesPreFlood2

	# jika file sudah ada dalam workstation
	if(os.path.exists('C:/data/banjir/preFlood/'+ scene)):
		# hapus file tersebut
		shutil.rmtree('C:/data/banjir/preFlood/'+ scene)
	# buat folder baru dalam workstation
	os.makedirs('C:/data/banjir/preFlood/'+ scene)

	# looping setiap file dalam folder
	for file in filesPreFlood2:
		print file
		msg = str(datetime.now()) + '\t' + "Downloading "+ str(file) + "\n"
		filename = file #replace with your file in the directory ('directory_name')

		######################## Mulai download file##################################
		localfile = open(filename, 'wb')
		if(os.path.exists('C:/data/banjir/preFlood/'+ scene +'/'+filename)):
			os.remove('C:/data/banjir/preFlood/'+ scene +'/'+filename)

		ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
		localfile.close()
		##############################################################################

		# pindahkan dari local ke folder yang seharusnya
		os.rename(filename,'C:/data/banjir/preFlood/'+ scene +'/'+filename)

	#################### UBAH FORMAT NAMA FILE #####################################
	os.chdir('C:/data/banjir/preFlood/'+ scene)
	for filename in os.listdir('C:/data/banjir/preFlood/'+ scene):
		productID = filename.split(".")[0]
		extension = filename.split(".")[1]
		unique = filename.split(".")[0].split("_")[7]

		os.rename(filename, scene + "_" + unique + "." + extension)
	#################################################################################
	# kembali lagi ke folder aplikasi
	os.chdir("C:/Apps/Sideba_webapp")
	# kembalikan scene id ke program utama
	return scene
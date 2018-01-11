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

	tupDate = datetime.now()
	print tupDate.year
	print tupDate.strftime('%j')
	#print now.year, now.month, now.day, now.hour, now.minute, now.second # check every datetime detail
	ftp = FTP( )
	ftp.connect(host='localhost', port=21, timeout=1246)
	ftp.login(user='akhiyarwaladi', passwd='rickss12')
	#ftp.retrlines('LIST') # use to check file after connected
	ftp.cwd('Landsat_8')
	#ftp.cwd(str(tupDate.year))
	ftp.cwd('2017')
	#ftp.cwd(str(tupDate.strftime('%j')))
	cloud_dict = {}
	cloud_dict_id = {}

	for i in range(151, 213):
		ftp.cwd(str(i))
		for level in ftp.nlst():
			print level
			ftp.cwd(str(level))
			for scene in ftp.nlst():

				ftp.cwd(scene)
				filesPreFlood = ftp.nlst()

				fileMtl = [txt for txt in filesPreFlood if 'MTL.txt' in txt][0]
				print fileMtl
				localfile = open(fileMtl, 'wb')

				ftp.retrbinary('RETR ' + fileMtl, localfile.write, 1024)
				localfile.close()

				if(os.path.exists('C:/data/banjir/preFlood/' + fileMtl)):
					os.remove('C:/data/banjir/preFlood/' + fileMtl)
				os.rename(fileMtl,'C:/data/banjir/preFlood/' + fileMtl)

				mtl = parse_mtl('C:/data/banjir/preFlood/', fileMtl)
				product_id = str(mtl['L1_METADATA_FILE']['LANDSAT_PRODUCT_ID'])
				cloud_cover = str(mtl['IMAGE_ATTRIBUTES']['CLOUD_COVER_LAND'])

				print product_id
				print cloud_cover
				cloud_dict[product_id] = cloud_cover
				cloud_dict_id[product_id] = scene
				# for file in filesPreFlood:
				# 	print 'haha'
					# fileMtl = [txt for txt in filesPreFlood if 'MTL.txt' in txt][0]
					# mtl = parse_mtl(fileMtl)

					# cloud_cover = str(mtl['IMAGE_ATTRIBUTES']['CLOUD_COVER_LAND'])


					# msg = str(datetime.now()) + '\t' + "Downloading "+ str(file) + "\n"
					# filename = file #replace with your file in the directory ('directory_name')
					# localfile = open(filename, 'wb')
					# if(os.path.exists('C:/data/banjir/'+ scene +'/'+filename)):
					# 	os.remove('C:/data/banjir/'+ scene +'/'+filename)

					# ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
					# localfile.close()


					# os.rename(filename,'C:/data/banjir/'+ scene +'/'+filename)

				ftp.cwd("../")
			ftp.cwd("../")
		ftp.cwd("../")

	print cloud_dict
	bestPreFlood = min(cloud_dict, key=cloud_dict.get)
	bestPreFloodList = bestPreFlood.split("_")
	scene = cloud_dict_id[bestPreFlood]

	print date_to_nth_day(bestPreFloodList[3])
	print scene

	ftp.cwd(str(date_to_nth_day(bestPreFloodList[3])))
	ftp.cwd(bestPreFloodList[1])
	ftp.cwd(scene)
	filesPreFlood = ftp.nlst()

	if(os.path.exists('C:/data/banjir/preFlood/'+ scene)):
		shutil.rmtree('C:/data/banjir/preFlood/'+ scene)
	os.makedirs('C:/data/banjir/preFlood/'+ scene)

	for file in filesPreFlood:
		print file
		msg = str(datetime.now()) + '\t' + "Downloading "+ str(file) + "\n"
		filename = file #replace with your file in the directory ('directory_name')
		localfile = open(filename, 'wb')
		if(os.path.exists('C:/data/banjir/preFlood/'+ scene +'/'+filename)):
			os.remove('C:/data/banjir/preFlood/'+ scene +'/'+filename)

		ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
		localfile.close()


		os.rename(filename,'C:/data/banjir/preFlood/'+ scene +'/'+filename)


	os.chdir('C:/data/banjir/preFlood/'+ scene)

	for filename in os.listdir('C:/data/banjir/preFlood/'+ scene):
		productID = filename.split(".")[0]
		extension = filename.split(".")[1]
		unique = filename.split(".")[0].split("_")[7]

		os.rename(filename, scene + "_" + unique + "." + extension)
		# print productID
		# print extension
		# print unique

	os.chdir("C:/Apps/Sideba_webapp")
	return scene

# if __name__ == '__main__':
	
# 	downloadFile()
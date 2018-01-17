import time
from datetime import datetime
from celery import Celery
from flask import Flask, render_template, request, flash
from redis import StrictRedis
from socketio import socketio_manage
from socketio.namespace import BaseNamespace

from assets import assets
import config
import celeryconfig

import pandas as pd
import os
import arcpy
import data_process as dp
import predictCl as pc
import ftpClient as fc
import ftpSidebaPre as ftpPre
import ftpSidebaPost as ftpPost
from tqdm import *
import time
import urllib2
import shutil

redis = StrictRedis(host=config.REDIS_HOST)
redis.delete(config.MESSAGES_KEY)
# celery = Celery(__name__)
# celery.config_from_object(celeryconfig)

app = Flask(__name__)
app.config.from_object(config)
assets.init_app(app)

app.config['SECRET_KEY'] = 'top-secret!'

app.config['SOCKETIO_CHANNEL'] = 'tail-message'
app.config['MESSAGES_KEY'] = 'tail'
app.config['CHANNEL_NAME'] = 'tail-channel'

app.config['SOCKETIO_CHANNEL_2'] = 'val-message'
app.config['MESSAGES_KEY_2'] = 'val'
app.config['CHANNEL_NAME_2'] = 'val-channel'

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

def internet_on():
    for timeout in [1,5,10,15]:
        try:
            response=urllib2.urlopen('http://google.com',timeout=timeout)
            return True
        except urllib2.URLError as err: pass
    return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
		if(internet_on()):
			if redis.llen(config.MESSAGES_KEY):
				flash('Task is already running', 'error')

			# elif(redis.llen(config.MESSAGES_KEY) == 0):
			#     flash('Task is finished', 'success')

			else:
				tail.delay()
				flash('Task started', 'info')
		else:
			flash('Internet connection is bad. Please pay your internet bill :)','error')

    return render_template('index.html')

@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
    socketio_manage(request.environ, {
        '/tail': TailNamespace
    })
    return app.response_class()

@app.route('/stop', methods=['GET', 'POST'])
def stop():
    if request.method == 'POST':
        tail.delay()
    return render_template('index.html')    


@celery.task
def tail():
	while(1):
		############################## BUKA DATA LOG PROSES HARI INI #########################################
		log = pd.read_csv("logComplete.csv")
		liScene = log["scene"].tolist()
		liDate = log["dateComplete"].tolist()
		#######################################################################################################

		############################## DOWNLOAD SCENE SAAT BANJIR #############################################
		sceneIdPost, boolScene = ftpPost.downloadFile(liScene)
		print sceneIdPost
		print str(boolScene)
		#######################################################################################################

		if(boolScene == False):
			print "Data hari ini selesai diproses"
			time.sleep(1000)
		else:
			sceneIdPre = ftpPre.downloadFile(sceneIdPost)
			# os.chdir('C:/data/banjir/postFlood/'+ sceneIdPost)
			# for filename in os.listdir('C:/data/banjir/postFlood/'+ sceneIdPost):
			# 	productID = filename.split(".")[0]
			# 	extension = filename.split(".")[1]
			# 	unique = filename.split(".")[0].split("_")[7]

			# 	os.rename(filename, sceneIdPost + "_" + unique + "." + extension)
			# 	# print productID
			# 	# print extension
			# 	# print unique
			data_type = "LANDSAT_8"

			pre_flood = config.FOLDER_PREFLOOD + "/" + sceneIdPre
			post_flood = config.FOLDER_POSTFLOOD + "/" + sceneIdPost
			out_process = config.FOLDER_OUTPUT + "/" + sceneIdPost

			if(os.path.exists(out_process)):
				import shutil
				shutil.rmtree(out_process, ignore_errors=True)

			text_files = [f for f in os.listdir(pre_flood) if f.endswith('.TIF') or f.endswith('.tif')]
			inFC = os.path.join(pre_flood, text_files[0])

			SR = arcpy.Describe(inFC).spatialReference

			print(data_type)
			print(pre_flood)
			print(post_flood)
			print(out_process)

			masktype = "Cloud"
			confidence = "High"
			cummulative = 'false'

			print(masktype)
			print(confidence)

			deltaNDWI = '0.11'
			NDWIduring = '0.11'

			os.mkdir(out_process)
			some_list = [pre_flood, post_flood]
			df = pd.DataFrame(some_list, columns=["colummn"])
			df.to_csv(out_process+'/list.csv', index=False)
			dp.mask_cloud(pre_flood, masktype, confidence, cummulative, out_process)
			dp.mask_cloud(post_flood, masktype, confidence, cummulative, out_process)
			dp.process_landsat(pre_flood, SR, out_process, "_PreFlood", data_type, "")
			dp.process_landsat(post_flood, SR, out_process, "_PostFlood", data_type, "")

			dat = pd.read_csv(out_process+"/list.csv")
			pre_flood = dat["colummn"][0]
			post_flood = dat["colummn"][1]

			print("McFeeter")
			deltaNDWI = "0.228"
			NDWIduring = "0.548"

			dp.diffNDWI(out_process, os.path.basename(pre_flood), os.path.basename(post_flood))
			dp.pixelExtraction(out_process, os.path.basename(pre_flood), os.path.basename(post_flood), deltaNDWI, NDWIduring)
			dp.maskOutFinal(out_process, pre_flood)
			dp.final_spatial_filter(out_process, pre_flood)

			#dp.rasterToVector(out_process)
			#dp.layerToKml(out_process)

			####################### SAVE LOG DATA YANG TELAH SELESAI DIPROSES ########################################
			liScene.append(sceneIdPost)
			liDate.append(str(datetime.now()))

			print(liScene)
			print(liDate)

			serScene = pd.Series(liScene)
			serDate = pd.Series(liDate)

			print(serScene)
			print(serDate)
			log2 = pd.DataFrame()
			log2["scene"] = serScene
			log2["dateComplete"] = serDate

			print(log2.head(5))
			log2.to_csv("logComplete.csv", index=False)
			##########################################################################################################

			msg = str(datetime.now()) + '\t' + "Finished ... \n"

			redis.rpush(config.MESSAGES_KEY, msg)
			redis.publish(config.CHANNEL_NAME, msg)
			redis.delete(config.MESSAGES_KEY)

class TailNamespace(BaseNamespace):
    def listener(self):
		# Emit the backlog of messages
		messages = redis.lrange(config.MESSAGES_KEY, 0, -1)
		messages2 = redis.lrange(config.MESSAGES_KEY_2, 0, -1)

		self.emit(config.SOCKETIO_CHANNEL, ''.join(messages))
		self.emit(config.SOCKETIO_CHANNEL_2, ''.join(messages2))

		self.pubsub.subscribe(config.CHANNEL_NAME)
		self.pubsub.subscribe(config.CHANNEL_NAME_2)

		i=1
		for m in self.pubsub.listen():
			if m['type'] == 'message':
				self.emit(config.SOCKETIO_CHANNEL, m['data'])
				self.emit(config.SOCKETIO_CHANNEL_2, i)
				i = i+0.1

    def on_subscribe(self):
        self.pubsub = redis.pubsub()
        self.spawn(self.listener)

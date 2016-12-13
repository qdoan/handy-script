#/usr/bin/python
import os
import urllib
import requests
import cv2
import Queue
import threading
import time


STORAGE_PATH = "/home/quydm/Datasets/vgg_face_dataset/downloaded/"
DATA_PATH = "/home/quydm/Datasets/vgg_face_dataset/files/"

def download(file_url,file_path):
	try:
		request = requests.get(file_url)
		if request.status_code == 200:
			urllib.urlretrieve(file_url,file_path)
			return 0
		else:
			return -1
	except:
		pass

def extract(file_in,file_out,left,top,right,bottom):
	try:
		img = cv2.imread(file_in)
		crop_img = img[top:bottom,left:right]
		height,width,channels = crop_img.shape
		new_width = 128
		new_height = new_width * height / width
		crop_img = cv2.resize(crop_img,(new_width,new_height))
		cv2.imwrite(file_out,crop_img)
	except:
		pass

def process_file(file_path):
	with open(file_path) as reader:
		line_count = 0;
		for line in reader:
			line_count += 1
			if line_count % 100 == 0:
				print line_count
			data_of_line = line.split()
			file_id = f_name[0:-4]+"_"+data_of_line[0]
			file_url = data_of_line[1]
			file_path = STORAGE_PATH+file_id+".jpg"
			result = download(file_url,file_path)
			if result == -1:
				continue

			left = int(float(data_of_line[2]))
			top = int(float(data_of_line[3]))
			right = int(float(data_of_line[4]))
			bottom = int(float(data_of_line[5]))
			file_out = STORAGE_PATH+file_id+"_face.jpg"
			extract(file_path,file_out,left,top,right,bottom)
	print file_path

exitFlag = 0

class ProcessorThread(threading.Thread):
	def __init__(self, threadID, name, q):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.q = q
	def run(self):
		process_data(self.name,self.q)

def process_data(threadName, q):
	while not exitFlag:
		queueLock.acquire()
		if not workQueue.empty():
			file_path = q.get()
			queueLock.release()
			print "%s processing %s" % ( threadName, file_path)
			process_file(file_path)	
		else:
			queueLock.release()

		
if __name__ == '__main__':
	threadList = ['Thread-1', 'Thread-2', 'Thread-3']	
	threads = []
	queueLock = threading.Lock()
	workQueue = Queue.Queue(3000)
	threadID = 1
	for tName in threadList:
		thread = ProcessorThread(threadID,tName, workQueue)
		thread.start()
		threads.append(thread)
		threadID += 1


	done = {"Samaire_Armstrong.txt",
				"Zelda_Williams.txt",
				"Jacob_Vargas.txt",
				"Darren_Criss.txt",
				"Laverne_Cox.txt",
				"Wesley_Snipes.txt",
				"Eva_LaRue.txt",
				"Anita_Briem.txt",
				"Kelly_Bishop.txt",
				"Luke_Arnold.txt",
				"Kaya_Scodelario.txt",
				"Riley_Steele.txt"}
	
	queueLock.acquire()
	for f_name in os.listdir(DATA_PATH):
		if ( f_name not in done ):
			#print f_name
			workQueue.put(DATA_PATH+f_name)
	queueLock.release()
	while not workQueue.empty():
		pass
	exitFlag = 1
	for t in threads:
		t.join()
	print "Exit main threads"

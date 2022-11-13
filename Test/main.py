import socket
import sys
import threading

import scheduler

threadNum = 0

class DownLoaderThread(threading.Thread):

	def __init__(self,port,uri,buf):
		self.port = port
		self.uri = uri
		self.buf = buf
		threading.Thread.__init__(self)

	def downloadHTML(self,host,port,uri,buf):
		# create an INET, STREAMing socket
		try:
			StreamSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		except socket.error, msg:
			sys.sterr.write("[ERROR] %s\n" % msg[1])
			sys.exit(1)

		# now connect to the Web server on port 80
		try:
			StreamSock.connect((host,port))
		except socket.error, msg:
			sys.sterr.write("[ERROR] %s\n" % msg[1])
			sys.exit(2)

		# request HTML document
		StreamSock.send("GET %s HTTP/1.0\r\nHost: %s\r\n\r\n" % (uri, host))

		# receive HTML document
		data = StreamSock.recv(buf)
		HTML = ""
	
		while len(data):
			HTML = HTML + data
			data = StreamSock.recv(buf)
			if not data:
				print "Host has discontinued connection..."
				break

		# close socket
		StreamSock.close()

		# create a file in write mode
		fileName = host
		FILE = open(str(self.threadNum)+fileName+".html","w")
		FILE.writelines(HTML)
		FILE.close()

	def run(self):
		global threadNum
		threadNum = threadNum + 1
		self.threadNum = threadNum

		# make thread serve forever
		while True:

			# get host out of queue
			host = hostPool.get()

			print host + ' This is thread ' + str(self.threadNum) + ' speaking.\n'

			self.downloadHTML(host,self.port,self.uri,self.buf)

def schedule(domain,subdomain,absoluteURL):
	if(absoluteURL not in linksSeen):
		linksSeen[absoluteURL] = 1
		scheduler.push(domain,subdomain,absoluteURL)

# Main Function
if __name__ == '__main__':
	#host = ['www.google.com','www.bing.com','www.altavista.com','www.naver.com','www.daum.net']
	port = 80
	buf = 1024		# max size of data stream
	uri = "/index.html"

	# create queue to hold URLs for dispatching
	# hostPool = Queue.Queue(0)

	# create empty dictionary
	#hostPool = {}

	# create scheduler
	scheduler = scheduler.Scheduler()

	# start 3 threads
	'''for i in xrange(3):
		DownLoaderThread(port,uri,buf).start()'''

	# links seen dictionary
	linksSeen = {}
	'''Why only use the array (ideally, a dictionary would be even better) to filter things you've already visited? Add things to your array/dictionary as soon as you queue them up, and only add them to the queue if they're not already in the array/dict. Then you have 3 simple separate things:

	1.Links not yet seen (neither in queue nor array/dict)
	2.Links scheduled to be visited (in both queue and array/dict)
	3.Links already visited (in array/dict, not in queue)'''

	# scheduler URLs
	schedule('a.com','','http://a.com/')
	schedule('a.com','','http://a.com/a')
	schedule('a.com','1','http://1.a.com/')
	schedule('b.com','','http://b.com/')
	schedule('c.com','','http://c.com/')
	schedule('b.com','1','http://1.b.com/')
	schedule('ab.com','','http://ab.com/')
	schedule('b.com','','http://b.com/') # duplicate
	schedule('b.com','','http://b.com/a')
	schedule('b.com','1','http://1.b.com/') # duplicate
	schedule('b.com','','http://b.com/b')
	schedule('b.com','','http://b.com/c')
	schedule('b.com','b','http://b.b.com/')
	schedule('bb.com','','http://bb.com/')

	schedule('a.com','','http://a.com/') # duplicate
	schedule('456.com','','http://456.com/')
	schedule('123.com','','http://123.com/')
	schedule('456.com','as','http://as.456.com/')
	schedule('45.net','','45.net/')
	schedule('45.com','','45.com/')
	schedule('45.uk','','45.uk/')
	schedule('b.com','','http://b.com/456')
	schedule('c.com','','http://c.com/4543')
	schedule('b.com','1','http://1.b.com/index.htm')
	schedule('ab.com','','http://ab.com/dfd.pk')

	schedule('a.com','','http://a.com/f/s')
	schedule('a.com','','http://a.com/a/f')
	schedule('a.com','1','http://1.a.com/asw')
	schedule('b.com','','http://b.com/uyiy')
	schedule('c.com','','http://c.com/6fht')
	schedule('b.com','1','http://1.b.com/hvd')
	schedule('ab.com','','http://ab.com/%t.ghj')

	print "-------"

	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()
	print scheduler.pop()

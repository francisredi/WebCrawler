import Queue
import socket
import sys
import threading

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

# Main Function
if __name__ == '__main__':
	#host = ['www.google.com','www.bing.com','www.altavista.com','www.naver.com','www.daum.net']
	port = 80
	buf = 1024		# max size of data stream
	uri = "/index.html"

	# create queue to hold URLs for dispatching
	hostPool = Queue.Queue(0)

	# start 3 threads
	for i in xrange(3):
		DownLoaderThread(port,uri,buf).start()

	# dispatch URLs
	hostPool.put('www.google.com')
	hostPool.put('www.bing.com')
	hostPool.put('www.daum.net')
	hostPool.put('www.naver.com')
	hostPool.put('www.altavista.com')


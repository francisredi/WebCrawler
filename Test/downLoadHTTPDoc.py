import socket
import sys

def downloadHTML(host,port,uri,buf):
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

	return HTML

# Main Function
if __name__ == '__main__':
	host = "www.google.com"
	port = 80
	buf = 1024		# max size of data stream
	uri = "/index.html"

	HTML = downloadHTML(host,port,uri,buf)
	print HTML



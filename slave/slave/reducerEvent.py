# -*- coding: iso-8859-15 -*-
import sys
import asyncore
import asynchat
import string, socket
import json
import config
import async_httpSlave

webAgent=async_httpSlave

class reducer(asyncore.dispatcher):
    def __init__(self, port=config.slave_port):
        asyncore.dispatcher.__init__(self)
        self.total_hits = 0
        self.create_socket (socket.AF_INET, socket.SOCK_STREAM)
        # try to re-use a server port if possible
        try:
            self.socket.setsockopt (
                socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.socket.getsockopt (socket.SOL_SOCKET, socket.SO_REUSEADDR) | 1
                )
        except:
            pass

        self.bind(('', port))
        
        
        self.listen (1)
        print 'Crawler Slave Started on '+webAgent.machineName+':'+str(port)

    def handle_connect(self):
        pass

    def handle_accept (self):
        conn, addr = self.accept()
        print "incoming connection from %s:%d" % (addr[0], addr[1])
        self.total_hits = self.total_hits + 1
        try:
            processor (self, conn, addr)
        except:
            webAgent.dump()

    def handle_error (self):
        print 'error'
        self.close()
    
    def handle_close(self):
		print "Connection Closed"

class processor (asynchat.async_chat):
    
    ac_out_buffer_size=config.mr_msg_size
    
    def __init__ (self, server, conn, addr):
        asynchat.async_chat.__init__ (self, conn)
        self.server = server
        self.addr = addr

        self.buffer = ''
        self.set_terminator(config.mr_marker)

        
    def collect_incoming_data(self, data):
        """Buffer the data"""
        self.buffer+=data

    def found_terminator(self):
        print self.buffer
        signal,data=self.buffer.split('::',1)
        if (signal=="start"):
            webAgent.setup(data)
            self.push("list::"+config.mr_marker)
        elif (signal=="list"):
            webAgent.slaveSeed(data)
            self.push(webAgent.commit())
            print "****Done***"
            #self.handle_close()
        #self.server.close()
        self.buffer = ''

    def handle_close(self):
        print "Processor connection closed"
        self.close()

def start():
    reducer()
    asyncore.loop()
    

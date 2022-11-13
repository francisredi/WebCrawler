# -*- coding: iso-8859-15 -*-
import config
from collections import deque
import time
import sys
import reducerEvent

def test():
	a=reducerEvent.webAgent.urlinQueue
	b=reducerEvent.webAgent.master_urlinQueue
	a.append(["asas"])
	b.append(["bvbv"])
	print a.show()
	print b.show()
	
	exit (1)

if __name__=="__main__":
	
	#test()
	
	reducerEvent.start()

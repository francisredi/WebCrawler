import Queue
#import sys

class SubDomain:

	def __init__(self):
		self.subDomainIndexNum = 0
		self.subDomainValuePair = {}
		self.subDomainIndexQueue = Queue.Queue()
		self.subDomainIndexQueueSet = set([])
		self.subDomainKeyURLQueueMapper = {}

class Scheduler():

	def __init__(self):
		self.domainIndexNum = 0
		self.domainValuePair = {} # dictionary: domain --> domain index, e.g. (a.com --> 1)
		self.domainIndexQueue = Queue.Queue() # FIFO domain indices queue, e.g. (1 --> 2 --> 3 --> 4)
		self.domainIndexQueueSet = set([]) # fast way to determine what indices in queue without modifying queue
		self.domainKeySubDomainDictionary = {}

	def printContent(self):
		pass
		#print self.domainValuePair

		print "Domain Index Queue: ",
		while(not self.domainIndexQueue.empty()):
			print self.domainIndexQueue.get(), "->",

	# scheduler push operation assumes URL is in SeenDictionary at this point but not crawled yet
	def push(self,domain,subdomain,absoluteURL):

		# manage domain index
		if(self.domainValuePair.has_key(domain) == False):
			self.domainIndexNum+=1
			self.domainValuePair[domain] = self.domainIndexNum;
			self.domainKeySubDomainDictionary[self.domainIndexNum] = SubDomain()
		domainIndex = self.domainValuePair[domain]
		if(not domainIndex in self.domainIndexQueueSet):
			self.domainIndexQueueSet.add(domainIndex)
			self.domainIndexQueue.put(domainIndex)

		# manage subdomain index
		if(self.domainKeySubDomainDictionary[domainIndex].subDomainValuePair.has_key(subdomain) == False):
			self.domainKeySubDomainDictionary[domainIndex].subDomainIndexNum+=1
			self.domainKeySubDomainDictionary[domainIndex].subDomainValuePair[subdomain] = self.domainKeySubDomainDictionary[domainIndex].subDomainIndexNum
			self.domainKeySubDomainDictionary[domainIndex].subDomainKeyURLQueueMapper[self.domainKeySubDomainDictionary[domainIndex].subDomainIndexNum] = Queue.Queue()
		subDomainIndex = self.domainKeySubDomainDictionary[domainIndex].subDomainValuePair[subdomain]
		if(not subDomainIndex in self.domainKeySubDomainDictionary[domainIndex].subDomainIndexQueueSet):
			self.domainKeySubDomainDictionary[domainIndex].subDomainIndexQueueSet.add(subDomainIndex)
			self.domainKeySubDomainDictionary[domainIndex].subDomainIndexQueue.put(subDomainIndex)

		# add absolute URL address under subdomain index
		self.domainKeySubDomainDictionary[domainIndex].subDomainKeyURLQueueMapper[subDomainIndex].put(absoluteURL)
		#print domainIndex, subDomainIndex, absoluteURL, self.domainKeySubDomainDictionary[domainIndex].subDomainKeyURLQueueMapper[subDomainIndex].qsize()

		# end of push

	def pop(self):
		
		if(len(self.domainIndexQueueSet) > 0):

			# pop off domain index from domain index queue and set
			domainIndex = self.domainIndexQueue.get()
			self.domainIndexQueueSet.discard(domainIndex)
	
			# pop off subdomain index from subdomain index queue and set
			subDomainIndex = self.domainKeySubDomainDictionary[domainIndex].subDomainIndexQueue.get()
			self.domainKeySubDomainDictionary[domainIndex].subDomainIndexQueueSet.discard(subDomainIndex)

			# pop off absolute URL
			url = self.domainKeySubDomainDictionary[domainIndex].subDomainKeyURLQueueMapper[subDomainIndex].get()
			###print domainIndex, subDomainIndex, url, self.domainKeySubDomainDictionary[domainIndex].subDomainKeyURLQueueMapper[subDomainIndex].qsize()

			if((len(self.domainKeySubDomainDictionary[domainIndex].subDomainIndexQueueSet) > 0)or(self.domainKeySubDomainDictionary[domainIndex].subDomainKeyURLQueueMapper[subDomainIndex].qsize() > 0)):
				self.domainIndexQueue.put(domainIndex)
				self.domainIndexQueueSet.add(domainIndex)

				if(self.domainKeySubDomainDictionary[domainIndex].subDomainKeyURLQueueMapper[subDomainIndex].qsize() > 0):
					self.domainKeySubDomainDictionary[domainIndex].subDomainIndexQueue.put(subDomainIndex)
					self.domainKeySubDomainDictionary[domainIndex].subDomainIndexQueueSet.add(subDomainIndex)

			#print url, " ", self.domainIndexQueueSet, self.domainKeySubDomainDictionary[domainIndex].subDomainIndexQueueSet
			return url
		return ""

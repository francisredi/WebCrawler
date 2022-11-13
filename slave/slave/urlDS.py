import json
import config

DumpState=0

class URLDict:
    
    visitedURLs={}
    visitedURLsClone={}
    
    def __init__(self):
        1
        #print "*****************url Dictionary created********************"        
    
    def add(self,url,selfLinkId,Sitedby):
        global DumpState
        while (DumpState):
            1;
        #print "---------------------add-------------------"

        if (config.dbUsedforvisitedURLs==0):
            if (Sitedby==-2):
                self.visitedURLs[url]=['###Started###',selfLinkId,'<--']
            else:
                self.visitedURLs[url]=['###Started###',selfLinkId,'<--',Sitedby]
            
            #url:["### ####",self.linkid,<--,links
        else:
            print "db url dict add query"
            
    def append(self,url,Sitedby):
        global DumpState
        while (DumpState):
            1;
        if (config.dbUsedforvisitedURLs==0):
            self.visitedURLs[url].append(Sitedby)
    
    def copy(self):
        self.visitedURLsClone=self.visitedURLs.copy()
    
    def fetch(self):
        return self.visitedURLsClone.popitem()

    def notEmptyClone(self):
        return len(self.visitedURLsClone)
    
    def isknown(self,url):
        if (config.dbUsedforvisitedURLs==0):
            return url in self.visitedURLs
        else:
            print "db url dict search query"
    
    def cancel(self,url,reason):
        global DumpState
        while (DumpState):
            1
        if (config.dbUsedforvisitedURLs==0):
            self.visitedURLs[url][0]='###canceled:'+reason+'###'
        else:
            print "db url dict cancel query"
    
    def remove(self,url,Sitedby):
        global DumpState
        while (DumpState):
            1;
        if self.isknown(url):
            try:
                while (self.visitedURLs[url].index(Sitedby)):
                    self.visitedURLs[url].remove(Sitedby)
            except:
                return
    
    def completed(self,url,selfLinkId):
        global DumpState
        while (DumpState):
            1;
        print url
        #self.write("debug")
        if (config.dbUsedforvisitedURLs==0):
            self.visitedURLs[url][0]='###done###'
            self.visitedURLs[url][1]=selfLinkId
    
    def show(self):
        if (config.dbUsedforvisitedURLs==0):
            print "URL Dictionary"
            print self.visitedURLs
    
    def write(self,state):
        fo = open(config.bkdir+"/"+state+"/urlDict.txt", "w")
        json.dump(self.visitedURLs,fo);
        fo.close()
        
    def recover(self,state):
        fo = open(config.bkdir+"/"+state+"/urlDict.txt", "r")
        self.visitedURLs=json.load(fo)
        fo.close()
    
    def flush(self):
        while (len(self.visitedURLs)):
            self.visitedURLs.popitem()

urlDict=URLDict()

class currentURLDict:
    
    visitingURLs={}
    visitingURLsClone={}
    badcnt=0
    goodcnt=0
    
    def __init__(self):
        1
        #print "*****************Current url Dictionary created********************"        
    
    def add(self,url,list,linkId=-1):
        global DumpState
        while (DumpState):
            1;
        #print "---------------------add-------------------"
        #return
        self.visitingURLs[url]=[list,linkId]
    
    def update(self,url,linkId):
        global DumpState
        while (DumpState):
            1;
        self.visitingURLs[url][1]=linkId
    
    def copy(self):
        self.visitingURLsClone=self.visitingURLs.copy()
            
    def isknown(self,url):
        #return
        return url in self.visitingURLs
            
    def remove(self,url):
        global DumpState
        while (DumpState):
            1;
        #return
        print url
        if self.isknown(url):   #because remove causes problem, it seems some duplication occurs that forces to remove entry two time as two events were created
            self.visitingURLs.pop(url)
            self.goodcnt+=1
        else:
            print "pop in currentURL bug"
            exit(1)
            self.badcnt+=1
    
    def fetch(self):
        global DumpState
        while (DumpState):
            1;
        return self.visitingURLsClone.popitem()
        
    def notEmpty(self):
        return len(self.visitingURLs)
    
    def notEmptyClone(self):
        return len(self.visitingURLsClone)
    
    def showEntry (self,url):
        if (self.isknown(url)):
            print self.visitingURLs[url]
        else:
            print 'entry not found'
    def show(self):
        #return
        print "Current URL Dictionary"
        print self.visitingURLs
        print "Bad Requests: "+str(self.badcnt)
        print "Good Requests: "+str(self.goodcnt)
        
    def write(self,state):
        fo = open(config.bkdir+"/"+state+"/curUrlDict.txt", "w")
        json.dump(self.visitingURLs,fo);
        fo.close()
    
    def recover(self,state):
        fo = open(config.bkdir+"/"+state+"/curUrlDict.txt", "r")
        self.visitingURLs=json.load(fo)
        fo.close()
    
    def size(self):
        return len(self.visitingURLs)

    def flush(self):
        while (len(self.visitingURLs)):
            self.visitingURLs.popitem()
            
curUrlDict=currentURLDict()

class URLinQueue:
    
    def __init__(self):
        self.visitingURLs=[]
        #print "*****************URL In Queue created********************"        
    
    def append(self,list):
        global DumpState
        while (DumpState):
            1;
        #print "---------------------add-------------------"
        self.visitingURLs.append(list)

    def notEmpty(self):
        return len(self.visitingURLs)
            
    def popleft(self):
        global DumpState
        while (DumpState):
            1;
        return self.visitingURLs.pop(0)
    
    def show(self):
        print "URL in Queue"
        print self.visitingURLs
        
    def write(self,state):
        fo = open(config.bkdir+"/"+state+"/urlinQueue.txt", "w")
        json.dump(self.visitingURLs,fo);
        fo.close()
    
    def recover(self,state):
        fo = open(config.bkdir+"/"+state+"/urlinQueue.txt", "r")
        self.visitingURLs=json.load(fo)
        fo.close()
    
    def flush(self):
        while (len(self.visitingURLs)):
            self.visitingURLs.pop(0)


urlinQueue=URLinQueue()
master_urlinQueue=URLinQueue()


#Not Used
class badURLList:
    badList=[]
    def __init__(self):
        print "*****************Bad URL List created********************"        
    
    def add(self,url,path,reason):
        #print "---------------------add-------------------"
        if (config.dbUsedforBadURLs==0):
            self.badList.append(url,path,reason)
        else:
            print "db bad url add query"
    
    def show(self):
        if (config.dbUsedforvisitedURLs==0):
            print 'Bad URL List'
            print self.badList
            
#badurlList=badURLList()

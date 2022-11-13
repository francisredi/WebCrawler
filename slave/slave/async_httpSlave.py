# -*- coding: iso-8859-15 -*-
import sys
import asyncore
import string, socket
import os
import shutil
from BeautifulSoup import BeautifulSoup, SoupStrainer
import re
import json
import time
import config
import urlDS

eventPoolCnt=0
DumpState=urlDS.DumpState
urlinQueue=urlDS.urlinQueue
master_urlinQueue=urlDS.master_urlinQueue
curUrlDict=urlDS.curUrlDict
urlDict=urlDS.urlDict
#badurlList=urlDS.badurlList

state=0
links=0
linksCrawled=0
linksRegistered=0 #on failure delete all directories [linksRegister->links]
linkBase=0
startTime=0
machineName=socket.gethostname() # pass machine number or m1,m2 name

class async_httpSlave(asyncore.dispatcher):
    # asynchronous http client
    def __init__(self, host, hostlimited, hostList, preLinkID, depth, path ,slavemap):
        global eventPoolCnt,links,linkBase,curUrlDict,urlinQueue
        port=""
        try:

            if (eventPoolCnt==config.maxPoolSize):
                # for managing big list of seed urls @5:12pm oct 29 09 with Fr
                print "Postpone Inputseed: "+host+" "+path
                urlinQueue.append([host, hostlimited,hostList, preLinkID, depth, path])
                return
            else:
                eventPoolCnt+=1

            print "Host and Path "+host+" "+path
            
            self.urlBeingBrowsed=(host+path).lower()

            host,port=resolveHostPort(host) #port detection

            # converting .com/#main to .com/
            if not (path.find('#')==-1):
                path=path[:path.find('#')]
            
            print 'Host: '+host+', Path: '+path
            
            #default settings
            host=host.lower()
            path=path.lower()
            self.host = host
            self.hostlimited=hostlimited
            self.hostList=hostList
            self.port = str(port)
            self.preLinkID = preLinkID
            self.path = path
            self.depth = depth
            self.isHtml=0
            self.data=""
            self.slavemap=slavemap
            
            curUrlDict.add(self.urlBeingBrowsed,[self.host+":"+self.port,self.hostlimited,self.hostList,self.preLinkID,self.depth,self.path])
            
            #Checking Termination condition
            if links==config.maxLinks:
                print "Maximum Links found"
                urlDict.cancel(host+":"+port+path,'Max. links found')
                curUrlDict.remove(self.urlBeingBrowsed)
                eventPoolCnt-=1
                return      
        except:
            unknownBug(["Occured in first half of init "+str(sys.exc_info()),port,host, hostlimited,hostList, preLinkID, depth, path,self.linkno])
            return

        #Now init
        print "initiated"
        asyncore.dispatcher.__init__(self,map=slavemap)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.startTime=time.time()
            self.connect( (host, int(port)) )
        except:
            print 'Link down or not available'
            urlDict.cancel(host+":"+port+path,'Link down or not available '+str(sys.exc_info()))
            self.terminate()
            return
        
        try:
            self.buffer = bytes( "GET %s HTTP/1.0\r\nHost: %s\r\nUser-Agent: Educational Crawler\r\nContact: matifq@gmail.com\r\n\r\n" % (path,host) ) #check http header should insert web path path
            #print self.buffer
        except:
            print "HTTP Get Failed"
            bugStr="HTTP Get Failed "+str(sys.exc_info())
            print " >> "+self.host+":"+self.port+self.path
            print bugStr
            writeBug([bugStr,self.host+":"+self.port+self.path,[self.port,self.host, self.hostlimited,self.hostList, self.preLinkID, self.depth, self.path,self.linkno]])
            urlDict.cancel(host+":"+port+path,'HTTP Get Failed')
            self.terminate()
            return
        createPoolDir(links)            
        links+=1
        
        self.linkno=links+linkBase
        
        curUrlDict.update(self.urlBeingBrowsed,self.linkno)
        #print "passed for further events"

    def handle_connect(self):
        pass
        
    def handle_expt(self):
        # connection failed
        self.terminate()

    def handle_read(self):
        if (time.time()-self.startTime>config.timeout):
            urlDict.cancel(self.host+":"+self.port+self.path,'Timed out')
            self.terminate()
            return
        try:
            htmldata=self.recv(config.webpageSize)
        except:
            print "socket.error>> Asyncore Lib unhandled"
            writeBug(["socket.error>> Asyncore Lib unhandled "+str(sys.exc_info()),self.host+":"+self.port+self.path,[self.port,self.host, self.hostlimited,self.hostList, self.preLinkID, self.depth, self.path,self.linkno]])
            urlDict.cancel(self.host+":"+self.port+self.path,'socket.error>> Asyncore Lib unhandled')
            self.terminate()
            return
        if htmldata=="":
            return
        if (self.isHtml==0):
            try:
                i = string.index(htmldata, "\r\n\r\n")
            except ValueError:
                return
            self.data = htmldata[i+4:]
            self.isHtml=1;
        else:
            self.data+=htmldata;
            if (len(self.data) > config.webpageSize):
                self.isHtml=0
                return
        #print(self.data)

    def writable(self):
        return (len(self.buffer) > 0)

    def handle_write(self):
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]

    def handle_close(self):
        global eventPoolCnt,urlinQueue,machineName,curUrlDict,DumpState
        print "depth = "+str(self.depth)
        print "host ="+self.host
        if (self.isHtml==0):
            self.terminate()
            return

        #Writing content to file
        websiteUrl=self.host+":"+self.port+self.path #lowered chars
        print "website = "+websiteUrl
        webpath=str(self.linkno)#+" "+self.host
        webdir="/"+str(int(self.linkno/config.maxLinksperDirs))+" "+str(machineName)+"/"+webpath
        webpath=config.webdir+webdir
        
        
        if (os.path.isdir(webpath)!=True):
            os.makedirs(webpath)
            fo = open(webpath+"/linksinfo.txt", "wb")
            fo.write("0");
            fo.close()
        elif (os.path.isdir(webpath+"/content.txt")):
            os.remove(webpath+"/*.*")
        fo = open(webpath+"/content.txt", "wb")
        fo.write(self.data);
        fo.close()

        #Link information
        try:
            soup=SoupStrainer('a',href=re.compile(''))
            outlinks=[tag for tag in BeautifulSoup(self.data, parseOnlyThese=soup)]
        except:
            urlDict.cancel(self.host+":"+self.port+self.path,'BeautifulSoup Bug '+str(sys.exc_info()[0]))
            writeBug([self.urlBeingBrowsed,'BeautifulSoup Bug',str(sys.exc_info()[0])])
            self.terminate()
            return

        pageLinks=[]
        pagewithOutLinks=[]
        #print outlinks
        #print len(outlinks)
        for link in outlinks:
            try:
                #url if is mailto then skip it
                if  (int("%s"%(link['href']).find("mailto:"))==0):
                    print "not valid as its mailto url: "+"%s"%(link['href'])
                    continue
                #change at Oct 30 7:15 pm
                urlhost,urlport,urlpath=resolvetoHostPortPath(self.host,"%s"%(link['href'])) #lowered case
                
                if (isBadUrl(urlhost,urlport,urlpath,"%s"%(link['href']),self.linkno,self.depth+1)):
                    continue
                
                #community limited
                if (self.hostlimited):
                    isGood=1
                    if (self.hostlimited==1 or self.hostlimited==3 and self.host==urlhost):
                        isGood=1
                    elif (self.hostlimited==1 or self.hostlimited==2):
                        isGood=0
                        for hostname in self.hostList:
                            if (hostname==urlhost):
                                isGood=1
                                break
                        if (isGood==0):
                            #print "not lies in community "
                            continue
                    else:
                        continue
                        
                #print urlpath
                extInd=urlpath.rfind('.')+1
                # converting .com/#main to .com/
                if not (urlpath.find('#')==-1):
                    urlpath=urlpath[:urlpath.find('#')]
                if (urlDict.isknown(urlhost+":"+urlport+urlpath)):
                    #print "url is known to system already: "+urlhost+urlpath
                    urlDict.append(urlhost+":"+urlport+urlpath,self.linkno)
                    continue
                elif ((extInd)>0): #limit to supported extention only
                    isGood=0
                    for extension in config.extension:
                        if (extension==urlpath[extInd:]):
                            isGood=1
                            break
                        else:
                            if not(urlpath.find('?')==-1):
                                if (extension==urlpath[extInd:urlpath.find('?')]):
                                    isGood=1
                                    break
                    if (isGood==0):
                        #print "not valid extension of url: "+urlpath[extInd:]
                        continue
                urlDict.add(urlhost+":"+urlport+urlpath,-1,self.linkno) #unique outlinks adds here
                print "---->"+self.host+"  "+"%s"%(link['href'])
                pageLinks.append(hostandLink(self.host,"%s"%(link['href']))) #lowered case and unique
            except:
                writeBug(["Link cannot be extracted for crawling "+str(sys.exc_info()),websiteUrl,"%s"%(link['href'])])
                if (urlDict.isknown(urlhost+":"+urlport+urlpath)):
                    urlDict.cancel(urlhost+":"+urlport+urlpath,'Link cannot be extracted for crawling '+str(sys.exc_info()[0]))
                continue
        #print "Links done"
        pagewithOutLinks.append(self.host);
        pagewithOutLinks.append(pageLinks);
        fo = open(webpath+"/linksto.txt", "w")
        json.dump(pagewithOutLinks,fo);
        fo.close()
        fo = open(webpath+"/linksinfo.txt", "wb")
        fo.write(str(len(pageLinks)));
        fo.write("\n"+websiteUrl);
        fo.write("\n"+str(self.linkno));
        fo.close()
        urlDict.completed(websiteUrl,self.linkno)
        print "Completed "+websiteUrl
        print '==============================================='
        for page in pageLinks:
            master_urlinQueue.append([page[0],self.hostlimited,self.hostList,self.linkno,self.depth+1,page[1]])
        self.terminate()
        return
    
    def terminate(self):
        global eventPoolCnt,urlinQueue,curUrlDict,linksCrawled
        eventPoolCnt-=1
        #curUrlDict.show()
        print '##################----->'+self.urlBeingBrowsed
        curUrlDict.remove(self.urlBeingBrowsed)
        
        #lock condition
        if (urlinQueue.notEmpty()):
            #eventPoolCnt+=1
            paramsList=urlinQueue.popleft()
            try:
                async_httpSlave(paramsList[0],paramsList[1],paramsList[2],paramsList[3],paramsList[4],paramsList[5], self.slavemap)
            except:
                print "whats is this"
                exit(1)

            #We might not need this @29 Oct 8:00pm
            if (eventPoolCnt>config.maxPoolSize):
                    print "Locked needed"
                    print eventPoolCnt
                    exit(1)
        #init was called for none event
        self.close()
        print 'closing event, remaining # of events in pool: '+str(eventPoolCnt)
        
        linksCrawled+=1
        print 'links Crawled '+str(linksCrawled)

def dump():
    global linksCrawled,state,DumpState
    #return
    print 'Dumping for backup and recovery'
    #curUrlDict.show()
    #print urlinQueue
    #urlDict.show()
    print state
    DumpState=1
    #s = raw_input('--> ')
    #print state
    newState=str(state%2+1)
    print newState
    #s = raw_input('--> ')
    curUrlDict.write(newState)
    urlDict.write(newState)
    urlinQueue.write(newState)
    
    fo = open(config.bkdir+"/"+newState+"/info.txt", "w")
    fo.write(str(linksCrawled)+'\n');
    fo.write(str(links)+'\n');
    fo.write(str(time.time()-startTime));
    fo.close()
    
    fo = open(config.bkdir+"/state.txt", "r+")
    fo.write(newState);
    fo.close()
    state=int(newState)
    DumpState=0
    print "Dump Written"
    #exit(1)

def recoverInit():
    global startTime,links,linksCrawled,state
    rd_state=str(state)
    print 'Recovering state'
    urlDict.recover(rd_state)
    curUrlDict.recover(rd_state)
    urlinQueue.recover(rd_state)
    fo = open(config.bkdir+"/"+rd_state+"/info.txt", "r")
    linksCrawled=int(fo.readline());
    links=int(fo.readline());
    pretime=float(fo.readline());
    fo.close()
    print pretime
    startTime=pretime

def resumeRecovedState():
    
    global startTime,links,linksCrawled,state
    
    startTime=time.time()-startTime
    print startTime
    curUrlDict.copy()
    while (curUrlDict.notEmptyClone()):
        curUrlDictItem=curUrlDict.fetch()
        #print curUrlDictItem[0] #url uniqueness for index else it is not needed in this step
        params=curUrlDictItem[1][0] #async_httpSlave param
        #print params
        #print curUrlDictItem[1][1] #linkId extra param async_httpSlave
        async_httpSlave(params[0],params[1],params[2],params[3],params[4],params[5],1,curUrlDictItem[1][1])
    asyncore.loop()
    #recovery timestamp could be taken

def success():
    curUrlDict.write("0")
    urlDict.write("0")
    urlinQueue.write("0")
    
    fo = open(config.bkdir+"/"+"0"+"/info.txt", "w")
    fo.write(str(linksCrawled)+'\n');
    fo.write(str(links)+'\n');
    fo.write(str(time.time()-startTime));
    fo.close()
    
    turnoffState();
    
def turnoffState():    
    fo = open(config.bkdir+"/state.txt", "r+")
    fo.write('0');
    fo.close()

def writeBug(lst):
    #seems append manages atomicity
    print "bug: "+json.dumps(lst)
    fo = open(config.bkdir+"/bugsInLink.txt", "a")
    fo.write(json.dumps(lst));
    fo.write("\n")
    fo.close()
    #exit(1)

def unknownBug(lst):
    writeBug(lst)
    dump()
    exit(1)

def isBadUrl(host,port,path,url,preLinkID=0,depth=0):
    if (len(host)==0): # host name could not be found len(host)==0
        port=config.port
        writeBug(["bad URL <Null Host>",url, preLinkID])
        return 1
    elif depth==config.maxDepth:
        print "Maximum depth reached , "+str(depth)
        writeBug(['Max. depth reached',url, preLinkID])
        return 1

    #Checking for allowed protocol
    for protocol in config.protocol:
        if (host.find(protocol+"://")==0):
            host=host.replace(protocol+"://","",1)
    if not (host.find("://")== -1):
        print "Bad protocol cannot crawl "+host
        print host+":"+port+path
        writeBug(['Bad protocol',url, preLinkID])
        return 1
    else:
        return 0

def hostandLink(host, lnk):
    for protocol in config.protocol:
            if host.find(protocol+"://")==0:
                host=host.replace(protocol+"://","",1)
    if (lnk=='/'):
        if  not(host.find('/')==-1):
            
            #started change 4:58 pm oct 31 09
            protocolIndex=host.find('://')
            if (protocolIndex==-1):
                protocolIndex=-3
            #print str(protocolIndex)+"s "+host[protocolIndex+3:]
            lnk=host[protocolIndex+3:][host[protocolIndex+3:].find('/'):]
            host=host[:host[protocolIndex+3:].find('/')+protocolIndex+3]
            #ended change 4:58 pm oct 31 09
            
        return (host.lower(),lnk.lower())
    if (lnk.find("://")== -1):
        if lnk.find('/')==0:
            return host.lower(),lnk.lower()
        else:
            if (len(lnk)==0):
                return (host.lower(),lnk.lower())
            if (lnk[0]=='\n'):
                lnk=lnk[1:]
                while (len(lnk)>0):
                    if (lnk[0]==' '):
                        lnk=lnk[1:]
                        continue
                    else:
                        break
                if  not(host.find('/')==-1):
                    host=host[:host.find('/')]
                if (host[:-1]=='/' or lnk[0]=='/'):
                    return (host.lower(),lnk.lower())
                    
            return (host.lower(),'/'+lnk.lower())
    else:
        
        
        for protocol in config.protocol:
            if lnk.find(protocol+"://")==0:
                lnk=lnk.replace(protocol+"://","",1)
        if not (lnk.find('/')==-1):
            #started change 5:15 pm oct 31 09
            protocolIndex=lnk.find('://')
            if (protocolIndex==-1):
                protocolIndex=-3
            #print str(protocolIndex)+"s "+lnk[protocolIndex+3:]
            host=lnk[:lnk[protocolIndex+3:].find('/')+protocolIndex+3]
            lnk=lnk[lnk[protocolIndex+3:].find('/')+protocolIndex+3:]
            #ended change 5:15 pm oct 31 09
        else:
            host=lnk
            lnk='/'
        return (host.lower(),lnk.lower())

def resolveHostPort(urlhost):
    if (len(urlhost)==0):
        return urlhost,config.port
    protocolIndex=urlhost.find('://')
    if (protocolIndex==-1):
        protocolIndex=-3
    if  not (urlhost[protocolIndex+3:].find(':')==-1):
        urlport=str(urlhost[protocolIndex+3:].split(':')[1])
        urlhost=str(urlhost[:protocolIndex+3]+urlhost[protocolIndex+3:].split(':')[0])
    else:
        urlport=config.port
    return urlhost,urlport



def resolvetoHostPortPath(host, lnk):
    urlhost,urlpath=hostandLink(host, lnk) #lowered case
    urlhost,urlport=resolveHostPort(urlhost)
    return urlhost,urlport,urlpath

def initializeDirs():
    if (os.path.isdir(config.webdir)):
        shutil.rmtree(config.webdir)
    os.makedirs(config.webdir)
    if not(os.path.isdir(config.bkdir)):
        os.makedirs(config.bkdir)
    fo = open(config.bkdir+"/bugsInLink.txt", "w")
    fo.close()
    #else:
    #    if (os.path.isfile(config.bkdir+"/success.txt")):
    #        shutil.rmtree(config.bkdir)
    #        os.makedirs(config.bkdir)

def discoverState():
    global state
    fo = open(config.bkdir+"/state.txt", "r")
    state=int(fo.read());
    fo.close()

def createPoolDir(lnks):
    if (lnks%config.maxLinksperDirs==0):
        dir=config.webdir+'/'+str(lnks/config.maxLinksperDirs)+" "+str(machineName)
        if (os.path.isdir(dir)):
            shutil.rmtree(dir)
        os.makedirs(dir)

def absLink(host, lnk):
    if lnk.find("://")== -1:
        if lnk.find('/')==0:
            return (host+lnk)
        else:
            return (host+'/'+lnk)
    else:
        return lnk

def setup(data):
    global linkBase,links,linksCrawled,linksRegistered,eventPoolCnt,urlinQueue,master_urlinQueue,curUrlDict,urlDict
    
    info=data.split(':')
    linkBase=int(info[0])
    links=int(info[1])
    
    config.webpageSize=int(info[2])
    config.maxLinksperDirs=int(info[3])
    config.timeout=int(info[4])
    config.maxDepth=int(info[5])
    
    config.webdir=(info[6])
    config.port=str(info[7])
    
    config.protocol=json.loads(info[8])
    config.extension=json.loads(info[9])
    config.excludedURLs=json.loads(info[10])
    
    linksCrawled=links
    linksRegistered=links
    eventPoolCnt=0
    urlDict.flush()
    urlinQueue.flush()
    master_urlinQueue.flush()
    
    print linkBase
    print links
    
    if (links==0):
        initializeDirs()

def slaveSeed(data):
    print "Pool Size"
    print eventPoolCnt
    slavemap={}
    urlStructList=json.loads(data)
    #print urlListStruct
    for urlStruct in urlStructList:
        print urlStruct[0]
        urlhost,urlport=resolveHostPort(urlStruct[0]) #lowered case
        # converting .com/#main to .com/
        urlpath=urlStruct[5]
        if not (urlpath.find('#')==-1):
            urlpath=urlpath[:urlpath.find('#')]
        print "Going in "+urlhost+":"+urlport+urlpath
        urlDict.add(urlhost+":"+urlport+urlpath,-1,-2) #-2
        async_httpSlave(urlStruct[0],urlStruct[1],urlStruct[2],urlStruct[3],urlStruct[4],urlStruct[5],slavemap)
    
    loop_counter = 0

    asyncore.loop(map=slavemap)

def commit():
    global urlDict,urlinQueue,master_urlinQueue
    result="crawl::"+json.dumps(master_urlinQueue.visitingURLs)+"::"+json.dumps(urlDict.visitedURLs)+"::"+config.mr_marker
    #print json.dumps(master_urlinQueue.visitingURLs)
    #print urlDict.visitedURLs
    master_urlinQueue.flush()
    urlDict.flush()
    urlinQueue.flush()
    showAll()
    return result

def showAll():
    global curUrlDict,urlDict,urlinQueue,master_urlinQueue
    print "***********Show All**********"
    curUrlDict.show()
    urlDict.show()
    urlinQueue.show()
    master_urlinQueue.show()
    print "//////////////////////////////"

def looping_code():
    loop_counter = 0

    while asyncore.socket_map:

        loop_counter += 1

        print 'loop_counter=%s', loop_counter

        asyncore.loop(timeout=1, count=1)

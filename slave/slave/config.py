#Global standard configuration for slaves----------------------------
slave_port=1234
mr_msg_size=8192
mr_marker="\r\nvisioner\r\n"
mr_lnkOffsetFactor=10000000
#---------------------------------------------------------------------

#Master overwritten data----------------------------------------------
webpageSize=0
maxLinksperDirs=0
timeout=0
maxDepth=0

webdir=''
port=''

protocol=[]
extension=[]
excludedURLs=[]
#---------------------------------------------------------------------

#Slave specific depending upon its own--------------------------------
bkdir='bk'
maxPoolSize=200#30#15
#---------------------------------------------------------------------

#Should Obselete now--------------------------------------------------
maxLinks=1000000#1000000
dumpAfter=10000000 #dump for backup after x number urls
hostlimited=0 #0=all urls,1=list+self,2=list only 3=self
hostList=[""]
dbUsedforvisitedURLs=0
dbUsedforBadURLs=0 #not used so far
recover=0# recover it
#---------------------------------------------------------------------

#Semantics: Don't change anything from here
# 0 linkid means seedurl
# -1 linkid means no id assignment

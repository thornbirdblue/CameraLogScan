##########################################################################
#	CopyRight	(C)	VIVO,2030	All Rights Reserved!
#
#	Module:		Scan camera log 
#
#	File:		CameraLogScam.py
#
#	Author:		liuchangjian
#
#	Data:		2020-09-28
#
#	E-mail:		liuchangjian@vivo.com
#
###########################################################################

###########################################################################
#
#	History:
#	Name		Data		Ver		Act
#--------------------------------------------------------------------------
#	liuchangjian	2020-09-28	v1.0		create
#
###########################################################################

#!/bin/python
import sys,os,re,string,time,datetime

# default Configure File Name
DefaultConfigFile='configfile'
ConfigFile=''

ScanPath=''

# log var
debugLog = 0
debugLogLevel=(0,1,2,3)	# 0:no log; 1:op logic; 2:op; 3:verbose

class CameraLogFile:
        __filename=''
        __fd=''

        __loglines=0
        
        __beginTime=''
        __endTime=''
        
        __FlowsNum=0
        __CameraFlows=[]

        __ErrorFlowsNum=0
        __ErrorFlows=[]

        __Errflows=[]
        __errFlowsNum=0
        
        __ErrLogs=[]
        __ErrLogsNum=0

        __KeyWords=[]
        __KeyWordsNum=0

        def __init__(self,filename,fd):
            self.__filename=filename
            self.__fd=fd
            self.__loglines=0

        def __get_key (self,dict, value):
            return [k for k, v in dict.items() if v == value]

        def __CheckFlows(self,line,Flows):
            if debugLog >= debugLogLevel[-1]:
                print 'CheckFlow: '+line,Flows

            for key,values in Flows.items():
                for i in values.split(','):
                    pattern = re.compile(i)
                
                    m = re.search(pattern,line)

                    if m:
                        self.__FlowsNum += 1
                        
                        timeFormat = re.compile(r'\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}')
                        time = re.match(timeFormat,line)
                        
                        self.__CameraFlows.append(time.group()+' '+key)

                        if debugLog >= debugLogLevel[2]:
                            print 'Find Flows: '+i+'\n'+line


        def __CheckErrLogs(self,line,ErrLogs):
	    if debugLog >= debugLogLevel[-1]:
                print 'CheckErrLogs: '+line,ErrLogs

            for i in range(0,len(ErrLogs)):
                pattern = re.compile(ErrLogs[i])

                m = re.search(pattern,line)

                if m:
                    self.__ErrLogsNum += 1
                    self.__ErrLogs.append(line)
	            
                    if debugLog >= debugLogLevel[2]:
                        print 'Find ErrLogs: '+line
        
        def __CheckKeyWords(self,line,KeyWords):
	    if debugLog >= debugLogLevel[-1]:
                print 'CheckKeyWords: '+line,KeyWords

            for i in range(0,len(KeyWords)):
                pattern = re.compile(KeyWords[i])

                m = re.search(pattern,line)

                if m:
                    self.__KeyWordsNum += 1
                    self.__KeyWords.append(line)
                    
                    if debugLog >= debugLogLevel[-1]:
                        print 'WARN Find KeyWord: '+line

        def CheckLogs(self,Flows,ErrLogs,KeyWords):
	    if debugLog >= debugLogLevel[-1]:
                print 'CheckLogs: ',self.__filename
            
            while 1:
		line = self.__fd.readline()
			
		if not line:
                    if debugLog >= debugLogLevel[2]:
                        if self.__endTime !='':
                            print 'End Time:',self.__endTime
                        print '(INFO) Finish Parse file: '+self.__filename
                        print '(INFO) lines: ',self.__loglines,'\n'
		    break;

                timeFormat = re.compile(r'\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}')
                time = re.match(timeFormat,line)
		if time and self.__loglines == 0:
                    self.__beginTime = time.group()
	            if debugLog >= debugLogLevel[2]:
                       print 'Begin Time:',self.__beginTime
                else:
                    self.__endTime = time.group()

		if debugLog >= debugLogLevel[-1]:
	            print 'INFO: Read line --->'+line

                self.__CheckFlows(line,Flows)

                self.__CheckErrLogs(line,ErrLogs)

                self.__CheckKeyWords(line,KeyWords)
                
                self.__loglines += 1




#Global Data
class ScanFileType:
        __ScanFiles=()
        __Flows={}
        __ErrLogs=()
        __KeyWords=()

        def SetScanFiles(self,ScanFiles):
	    if debugLog >= debugLogLevel[-1]:
	        print '(INFO) Set ScanFiles : ',ScanFiles
            self.__ScanFiles=ScanFiles

        def SetErrLogs(self,ErrLogs):
	    if debugLog >= debugLogLevel[-1]:
	        print '(INFO) Set ErrLogs : ',ErrLogs
            self.__ErrLogs=ErrLogs

        def SetKeyWords(self,KeyWords):
	    if debugLog >= debugLogLevel[-1]:
	        print '(INFO) Set KeyWords : ',KeyWords
            self.__KeyWords=KeyWords

        def GetScanFiles(self):
	    if debugLog >= debugLogLevel[-1]:
	        print '(INFO) Get ScanFiles'
            return self.__ScanFiles

        def GetErrLogs(self):
	    if debugLog >= debugLogLevel[-1]:
	        print '(INFO) Get ErrLogs'
            return self.__ErrLogs

        def GetKeyWords(self):
	    if debugLog >= debugLogLevel[-1]:
	        print '(INFO) Get KeyWords '
            return self.__KeyWords

        def AddFlows(self,FlowName,Flows):
	    if debugLog >= debugLogLevel[-1]:
                print '(INFO) Add FlowName : ',FlowName,'Flows: ',Flows
            self.__Flows[FlowName] = Flows

        def GetFlows(self):
	    if debugLog >= debugLogLevel[-1]:
	        print '(INFO) Get Flows ',self.__Flows
            return self.__Flows

        def Dump(self):
            print 'ScanFiles: ',self.__ScanFiles
            print 'Flows: ',self.__Flows
            print 'ErrLogs: ',self.__ErrLogs
            print 'KeyWords: ',self.__KeyWords


#global var
ScanFiles = ScanFileType()
Files=[]

class ConfigFileType:
	'adb log dir info'
	# app log pattern
	appLogType = r'app_log_'
	
        __fd = ''

        # ConfigFile KeyWord
        __ScanFilesKey = 'Scan Files'
        __FlowNameKey = 'Flow Name'
        __ErrorLogsKey = 'Error Logs'
        __KeyWordsKey = 'KeyWords'
        __ConfigTags =(__ScanFilesKey,__FlowNameKey,__ErrorLogsKey,__KeyWordsKey)

	
	def __init__(self,fd):
            self.__fd = fd

	
	def Parse(self):
	    if debugLog >= debugLogLevel[-1]:
		print '(INFO) begin Parse Configfile!\n'

	    while 1:
		line = self.__fd.readline().split('\r')[0]
			
		if not line:
	            if debugLog >= debugLogLevel[2]:
                        ScanFiles.Dump()
			print '\n(INFO) Finish Parse file!\n'
		    break;

		if debugLog >= debugLogLevel[-1]:
		    print '(INFO) Read line is ----------------------------> '+line
	
                for i in range(0,len(self.__ConfigTags)):
                    
                    if debugLog >= debugLogLevel[-1]:
                        print '(INFO) Match Key: '+self.__ConfigTags[i]
                   
                    key = re.compile(self.__ConfigTags[i]+':')
		    
		    search = re.match(key,line)

	            if search:
		        if debugLog >= debugLogLevel[-1]:
			    print 'find Key is: '+search.group()

                        line=line.split(':',1)			
                        
                        if self.__ConfigTags[i] == self.__ScanFilesKey:
                            if not line[1]:
                                print 'ERROR configfile Format: '+line[1]
                            else:
                                ScanFiles.SetScanFiles(line[1].strip().split(','))

                        elif self.__ConfigTags[i] == self.__FlowNameKey:
                            flows= line[1].split(';')
		            
                            if debugLog >= debugLogLevel[-1]:
			        print '(INFO) Total Flows is: ',len(flows),flows

                            for i in range(0,len(flows)):
                                flow_name = flows[i].split('{')[0].strip()
                                flow=flows[i].split('{')[1].split('}')[0]
                                
                                if not flow_name:
                                    print 'ERROR configfile Format Flow: '+flow_name
                                else:
                                    ScanFiles.AddFlows(flow_name,flow)

                        elif self.__ConfigTags[i] == self.__ErrorLogsKey:
                            if not line[1]:
                                print 'ERROR configfile Format: '+line[1]
                            else:
                                ScanFiles.SetErrLogs(line[1].strip().split(','))

                        elif self.__ConfigTags[i] == self.__KeyWordsKey:
                            if not line[1]:
                                print 'ERROR configfile Format: '+line[1]
                            else:
                                ScanFiles.SetKeyWords(line[1].strip().split(','))
                        break
                    else:
		        if debugLog >= debugLogLevel[-1]:
                            print '\n(WARN) NO Match: '+self.__ConfigTags[i]+':'

def CameraFlowCheck(filename,fd):
    if debugLog >= debugLogLevel[-1]:
        print 'Scan Log:  '+filename

    LogFile = CameraLogFile(filename,fd)

    LogFile.CheckLogs(ScanFiles.GetFlows(),ScanFiles.GetErrLogs(),ScanFiles.GetKeyWords())

    Files.append(LogFile)


def ScanCameraLog(arg,dirname,files):
    if debugLog >= debugLogLevel[-1]:
        print 'Scan Camera Log:\n '
    
    if debugLog >= debugLogLevel[-1]:
	print dirname

    if debugLog >= debugLogLevel[2]:
        print ScanFiles.GetScanFiles()
    
    LogTypes = ScanFiles.GetScanFiles()

    for file in files:
        for i in range(0,len(LogTypes)):
	    if debugLog >= debugLogLevel[-1]:
                print "File Match Format: "+LogTypes[i]

	    logTypes = re.compile(LogTypes[i])

	    if debugLog >= debugLogLevel[-1]:
	        print file
		
	    m = re.match(logTypes,file)
	    if m:
	        path,name = os.path.split(dirname)

		if debugLog >= debugLogLevel[-1]:
	            print 'Find Dir: '+dirname
		
                if debugLog >= debugLogLevel[2]:
	            print 'Find Match File: '+file

                try:
		    fd = open(os.path.join(dirname,file),'rb')								# 2015-09-08 liuchangjian fix error code in file bug!!! change r to rb mode!
			
		    if debugLog >= debugLogLevel[-1]:
			print 'INFO: open file :'+os.path.join(dirname,file)

		    CameraFlowCheck(file,fd)

                    fd.close()

		except IOError:
		    print "open file ERROR: Can't open"+os.path.join(dirname,file)



def ParseConfigFile():
    global ConfigFile

    if not ConfigFile:
        print '(WARNING) Default ConfigFile: '+DefaultConfigFile
        ConfigFile = DefaultConfigFile

    if debugLog >= debugLogLevel[-1]:
	print 'Parse file: '+ConfigFile

    try:
	fd = open(ConfigFile,'rb')								# 2015-09-08 liuchangjian fix error code in file bug!!! change r to rb mode!
		
	if debugLog >= debugLogLevel[-1]:
		print 'INFO: open file :'+ConfigFile
        cf = ConfigFileType(fd)

        cf.Parse()

        fd.close()

    except IOError:
	print "ERROR: !!! Can't open "+ConfigFile+" File!!!"
	sys.exit()



def ParseArgv():
	if len(sys.argv) > appParaNum+1:
		HelpInfo()
		sys.exit()
	else:
		for i in range(1,len(sys.argv)):
			if sys.argv[i] == '-h':
				Usage()
				sys.exit()
			elif sys.argv[i] == '-d':
				if sys.argv[i+1]:
					debug = string.atoi(sys.argv[i+1],10)
					if type(debug) == int:
						global debugLog
						debugLog = debug						
						print 'Log level is: '+str(debugLog)
					else:
						print 'cmd para ERROR: '+sys.argv[i+1]+' is not int num!!!'
				else:
					CameraOpenKPIHelp()
					sys.exit()
			elif sys.argv[i] == '-o':
				if sys.argv[i+1]:
					global fileName
					fileName = sys.argv[i+1]
					print 'OutFileName is '+fileName
				else:
					Usage()
					sys.exit()
			elif sys.argv[i] == '-p':
				if sys.argv[i+1]:
					global ScanPath
					ScanPath = sys.argv[i+1]
					print 'Scan dir path is '+ScanPath
				else:
					Usage()
					sys.exit()
			elif sys.argv[i] == '-c':
				if sys.argv[i+1]:
				        global ConfigFile
					ConfigFile = sys.argv[i+1]
					print 'ConfigFile is '+ConfigFile
				else:
					Usage()
					sys.exit()
					
					
def Usage():
	print 'Command Format :'
	print '		CameraLogScan [-d 1/2/3] [-o outputfile] [-p path]  [-c configfile]| [-h]'

appParaNum = 6

if __name__ == '__main__':
	ParseArgv()

        ParseConfigFile()

	if not ScanPath.strip():
		spath = os.getcwd()
	else:
		spath = ScanPath
	
        print 'Scan DIR: '+spath+'\n'

        os.path.walk(spath,ScanCameraLog,())

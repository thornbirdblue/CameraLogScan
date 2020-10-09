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
#	liuchangjian	2020-09-30	v1.0		release first test version
#	liuchangjian	2020-10-08	v1.0		Add unzip function
#	liuchangjian	2020-10-08	v1.0		output txt file
#
###########################################################################

#!/bin/python
import sys,os,re,string,time,datetime
import zipfile

# default Configure File Name
DefaultConfigFile='configfile'
ConfigFile=''
ConfigFileSplitSym=','

ScanPath=''

DirDefine='bbk_log'
CamLogDirName='camera_log'
CamLogFileName='cam_log_'

# log var
debugLog = 0
debugLogLevel=(0,1,2,3)	# 0:no log; 1:op logic; 2:op; 3:verbose
unzip_files_ctrl = 1
fileName='CamLogScanResult.txt'

class CameraLogScan:
        Tags = 'CamScan'
        __dirname=''
        __filename=''
        __fd=''

        __logLines=0
        
        __beginTime=''
        __endTime=''
        
        __FlowsNum=0
        __CameraFlows=[]

        __ErrFlowsNum=0
        __ErrFlows=[]

        __ErrLogsNum=0
        __ErrLogs=[]

        __KeyWordsNum=0
        __KeyWords=[]

        def __init__(self,dirname,filename,fd):
            self.__dirname=dirname
            self.__filename=filename
            self.__fd=fd
            self.__logLines=0

        def __get_key (self,dict, value):
            return [k for k, v in dict.items() if v == value]

        def __CheckFlows(self,line,Flows):
            if debugLog >= debugLogLevel[-1]:
                print 'CheckFlow: '+line,Flows

            for key,values in Flows.items():
                for i in values.split(ConfigFileSplitSym):
                    pattern = re.compile(i)
                
                    m = re.search(pattern,line)

                    if m:
                        self.__FlowsNum += 1
                        
                        timeFormat = re.compile(r'\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}')
                        time = re.match(timeFormat,line)

                        if time:
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
                        print '(INFO) lines: ',self.__logLines,'\n'
		    break;

                timeFormat = re.compile(r'\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}')
                time = re.match(timeFormat,line)
		
                if time and self.__logLines == 0:
                    self.__beginTime = time.group()
	            if debugLog >= debugLogLevel[2]:
                       print 'Begin Time:',self.__beginTime
                else:
                    if time:
                        self.__endTime = time.group()

	            if debugLog >= debugLogLevel[-1]:
	                print 'INFO: Read line --->'+line

                self.__CheckFlows(line,Flows)

                self.__CheckErrLogs(line,ErrLogs)

                self.__CheckKeyWords(line,KeyWords)
                
                self.__logLines += 1

        def __SaveFile(self,filename,datas):
            if len(datas):
                try:
                    fd = open(os.path.join(self.__dirname,filename),'wt')
                
                    for i in range(0,len(datas)):
                        fd.write(datas[i]+'\n')
                except IOError:
                    print "Error: Can't open or write!!!"
                else:
                    fd.close()
                    print 'Save file: '+filename
            else:
	        if debugLog >= debugLogLevel[2]:
	            print '(WARN) Save File len is 0!'
                

            

        def SaveToFile(self,fd):
	    if debugLog >= debugLogLevel[-1]:
	        print 'SaveToFile:'

            if self.__logLines:
                fd.write(self.__filename+': '+str(self.__logLines)+'\n')

                fd.write('BeginTime: '+self.__beginTime+'\n')
                fd.write('EndTime  : '+self.__endTime+'\n')

                fd.write('1.ErrorFlowsNum: '+str(self.__ErrFlowsNum)+'\n')
                fd.write('2.KeyWordsNum: '+str(self.__KeyWordsNum)+'\n')
                fd.write('3.FlowsNum: '+str(self.__FlowsNum)+'\n')
                fd.write('\n')

                self.__SaveFile(self.Tags+'_ErrorFlows_'+self.__filename,self.__ErrFlows)
                self.__SaveFile(self.Tags+'_KeyWords_'+self.__filename,self.__KeyWords)
                self.__SaveFile(self.Tags+'_CameraFlows_'+self.__filename,self.__CameraFlows)

        def Dump(self):
	    if debugLog >= debugLogLevel[-1]:
	        print 'Dump:'

            if self.__logLines:
                print self.__filename+': '+str(self.__logLines)

                print 'BeginTime: '+self.__beginTime
                print 'EndTime  : '+self.__endTime+'\n'

                print '1.ErrorFlowsNum: '+str(self.__ErrFlowsNum)
                print '2.KeyWordsNum  : '+str(self.__KeyWordsNum)
                print '3.FlowsNum     : '+str(self.__FlowsNum)

        def getFileName(self):
	    return os.path.join(self.__dirname,self.__filename)

        def getLogLines(self):
	    return self.__logLines


#Global Data
class ScanFileType:
        __DefaultScanFiles=['cam_log_\\d']
        __DefaultFlows={'open': 'createDevice,m_createManagers'}
        __DefaultErrLogs=['[Offline_front2]release() -OUT-','Finger']
        __DefaultKeyWords=['takePicture','Record','ExynosCamera']

        __ScanFiles=[]
        __Flows={}
        __ErrLogs=[]
        __KeyWords=[]
        
        def SetDefaultValue(self):
            self.__ScanFiles = self.__DefaultScanFiles
            self.__Flows = self.__DefaultFlows
            self.__ErrLogs = self.__DefaultErrLogs
            self.__KeyWords = self.__DefaultKeyWords

        
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
Datas=[]

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
	            if debugLog >= debugLogLevel[1]:
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
                                ScanFiles.SetScanFiles(line[1].strip().split(ConfigFileSplitSym))

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
                                ScanFiles.SetErrLogs(line[1].strip().split(ConfigFileSplitSym))

                        elif self.__ConfigTags[i] == self.__KeyWordsKey:
                            if not line[1]:
                                print 'ERROR configfile Format: '+line[1]
                            else:
                                ScanFiles.SetKeyWords(line[1].strip().split(ConfigFileSplitSym))
                        break
                    else:
		        if debugLog >= debugLogLevel[-1]:
                            print '\n(WARN) NO Match: '+self.__ConfigTags[i]+':'

def CameraFlowCheck(dirname,filename,fd):
    if debugLog >= debugLogLevel[-1]:
        print 'Scan Log:  '+filename

    LogScan = CameraLogScan(dirname,filename,fd)

    LogScan.CheckLogs(ScanFiles.GetFlows(),ScanFiles.GetErrLogs(),ScanFiles.GetKeyWords())

    Datas.append(LogScan)

def unzip_camlog_file(name,dst_dir):
    CamLog = re.compile(CamLogFileName)

    m = re.search(CamLog,name)
    if m:
        
        r=zipfile.is_zipfile(name)

        if r:
            if debugLog >= debugLogLevel[1]:
                print "unzip CamLog file: "+name

            fz = zipfile.ZipFile(name,'r')    
        
            for name in fz.namelist():
                fz.extract(name,dst_dir)
        
            fz.close()
    else:
        if debugLog >= debugLogLevel[-1]:
	    print '(INFO) NOT Camera Log Dir: '+name


def unzip_file(zip_src,dst_dir):
    if debugLog >= debugLogLevel[-1]:
          print '(INFO) Unzip File: '+dst_dir+'/'+zip_src

    fz = zipfile.ZipFile(zip_src,'r')

    for name in fz.namelist():
        CamLogDir = re.compile(CamLogDirName)

        m = re.search(CamLogDir,name)
        if m:
            if debugLog >= debugLogLevel[1]:
                print "unzip CamLog Dir: "+name

            fz.extract(name,dst_dir)        
        else:
            if debugLog >= debugLogLevel[-1]:
	        print '(INFO) NOT Camera Log Dir: '+name
        
        unzip_camlog_file(name,os.path.dirname(name))
        
        CamLog = re.compile(CamLogFileName)
        m = re.match(CamLog,name)
        if m:
            if debugLog >= debugLogLevel[1]:
                print "unzip CamLog File: "+name
            fz.extract(name,dst_dir)        

    if debugLog >= debugLogLevel[2]:
        print "Finish Unzip file: "+zip_src+'\n'

    fz.close()

def ScanCameraLog(arg,dirname,files):
    if debugLog >= debugLogLevel[-1]:
        print 'Scan Camera Log:\n '
    
    if debugLog >= debugLogLevel[-1]:
	print dirname

    if debugLog >= debugLogLevel[2]:
        print "(INFO) Match File Type: ",ScanFiles.GetScanFiles()
    
    LogTypes = ScanFiles.GetScanFiles()

    for file in files:

        for i in range(0,len(LogTypes)):
	    if debugLog >= debugLogLevel[-1]:
                print "File Match Format: "+LogTypes[i]
        
            r=zipfile.is_zipfile(os.path.join(dirname,file))

            if r:
	        if debugLog >= debugLogLevel[2]:
                    print 'File '+file+' is zipfile,SKIP!'
                continue
            
	    logTypes = re.compile(LogTypes[i])

	    if debugLog >= debugLogLevel[-1]:
	        print file
		
	    m = re.match(logTypes,file)
	    if m:
	        path,name = os.path.split(dirname)

		if debugLog >= debugLogLevel[-1]:
	            print 'Find Dir: '+dirname
		
                if debugLog >= debugLogLevel[1]:
	            print 'Find Match File: '+file

                try:
		    fd = open(os.path.join(dirname,file),'rb')								# 2015-09-08 liuchangjian fix error code in file bug!!! change r to rb mode!
			
		    if debugLog >= debugLogLevel[-1]:
			print 'INFO: open file :'+os.path.join(dirname,file)

		    CameraFlowCheck(dirname,file,fd)

                    fd.close()

		except IOError:
		    print "open file ERROR: Can't open"+os.path.join(dirname,file)

def SaveData(filename,datas):
    if debugLog >= debugLogLevel[-1]:
        print 'SaveData Begin: ',filename

    try:
        fo = open(filename,"wt")

        fo.write('Scan Total Files: '+str(len(datas))+'\n')
        
        fo.write('Files:\n')
        for i in range(0,len(datas)):
            fo.write(datas[i].getFileName()+'\n')
        fo.write('\n\n')

        for i in range(0,len(datas)):
            datas[i].SaveToFile(fo)

    except IOError:
        print "Error: Can't open or write!!!"
    else:
        fo.close()

	if debugLog >= debugLogLevel[1]:
            print '\nSaveFile: ',filename

def DumpData(datas):
    print '\nOutput Result:'
    print 'Scan Total Files: '+str(len(datas))
    print 'Files:'
    for i in range(0,len(datas)):
        print datas[i].getFileName()
   
    print

    for i in range(0,len(datas)):
        datas[i].Dump()

def ZipFiles(args,dirname,files):
    for f in files:
        if debugLog >= debugLogLevel[2]:
            print 'File is : ',os.path.join(dirname,f)

        r=zipfile.is_zipfile(os.path.join(dirname,f))

        if r:
            unzip_file(os.path.join(dirname,f),dirname)
        else:
            if debugLog >= debugLogLevel[2]:
                print '(WARN) '+f+' is not zipfile!!!'

def ScanDir(Dir):
    CamDirs=[]
    print 'Scan DIR: '+Dir+'\n'

    # 2020-10-08 add unzip file start
    if unzip_files_ctrl:
        if debugLog >= debugLogLevel[1]:
	    print '(INFO) Unzip File!'
#        for root,dirs,files in os.walk(Dir):
        os.path.walk(Dir,ZipFiles,())
    # 2020-10-08 add end

    os.path.walk(Dir,ScanCameraLog,())

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
	print "WARN: !!! Can't open "+ConfigFile+" File!!! UseDefaultValue"
        global ScanFiles
        ScanFiles.SetDefaultValue()
        ScanFiles.Dump()


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
			elif sys.argv[i] == '-z':
				global unzip_files_ctrl
				unzip_files_ctrl = 1
				print 'Unzip files!'
					
def Usage():
	print 'Command Format :'
	print '		CameraLogScan [-d 1/2/3] [-o outputfile] [-p path]  [-c configfile] [-z(unzip zip files)]| [-h]'

appParaNum = 6

if __name__ == '__main__':
	ParseArgv()

        ParseConfigFile()

	if not ScanPath.strip():
		spath = os.getcwd()
	else:
		spath = ScanPath
	

        ScanDir(spath)
       
        if fileName:
            SaveData(fileName,Datas)
        else:
            DumpData(Datas)

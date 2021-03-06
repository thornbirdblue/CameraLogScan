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
#	liuchangjian	2020-10-09	v1.0		Modify Save file path to Log Dir
#	liuchangjian	2020-10-09	v1.0		release version 1.0
#	liuchangjian	2020-10-13	v1.1		Add Scan main_log_xxx file
#
###########################################################################

#!/bin/python
import sys,os,re,string,time,datetime
import zipfile

# default Configure File Name
SW_VERSION='1.1'

DefaultConfigFile='configfile'
ConfigFile=''
ConfigFileSplitSym=','

# ConfigFile Default Value:
#DefaultDirs=['APLog_','camera_log']
DefaultDirs=['camera_log']
DefaultScanFiles=['cam_log_\\d','main_log_']
DefaultFlows={'open': 'connect call,HAL3_camera_device_open,createDevice,m_vendorSpecificPreConstructor,m_createManagers,m_createThreads,m_vendorSpecificConstructor','initalize':'HAL3_camera_device_initialize,initializeDevice','configureStream':'HAL3_camera_device_configure_streams,configureStreams,m_setStreamInfo,m_constructFrameFactory,m_setExtraStreamInfo,configure_stream','flush':'HAL3_camera_device_flush,flush,m_stopPipeline,m_captureThreadStopAndInputQ,m_clearRequestList,m_clearList','close':'HAL3_camera_device_close,releaseDevice,release,m_captureThreadStopAndInputQ,m_destroyCaptureStreamQ,m_vendorSpecificDestructor,destroyDevice,m_deinitFrameFactory,m_stopFrameFactory'}
DefaultErrLogs=['Device Error Detected','ExynosCamera state is ERROR','HAL crash instead of DDK assert','DTP Detected','Flush For ESD HAL Recovery','E ExynosCameraMemoryAllocator','transitState into ERROR','service\(-1\)','Failed to m_getBayerBuffer','can.*t select bayer']
DefaultKeyWords=['createDevice','initializeDevice','configureStreams','configure_stream','flush','releaseDevice']

ScanPath=''

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
       
        __CameraFlowStep=''
        __FlowsNum=0
        __CameraFlows=[]
        __CameraFlowsLog=[]

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
            
            self.__CameraFlowStep=''
            self.__FlowsNum=0
            self.__CameraFlows=[]
            self.__CameraFlowsLog=[]

            self.__ErrFlowsNum=0
            self.__ErrFlows=[]

            self.__ErrLogsNum=0
            self.__ErrLogs=[]

            self.__KeyWordsNum=0
            self.__KeyWords=[]

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
                        if debugLog >= debugLogLevel[2]:
                            print 'Find Flows: '+i+'\n'+line

                        timeFormat = re.compile(r'\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}')
                        time = re.match(timeFormat,line)
                        
                        if self.__CameraFlowStep != key:
                            if debugLog >= debugLogLevel[2]:
                                print 'Change Flow '+key+' to '+self.__CameraFlowStep

                            self.__FlowsNum += 1
                            self.__CameraFlows.append(time.group()+' '+key+'\n')

                            self.__CameraFlowStep = key
                        
                        self.__CameraFlowsLog.append(line)


                        if debugLog >= debugLogLevel[2]:
                            print 'Not Finish '+key+'\n'


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
                    
                    if debugLog >= debugLogLevel[2]:
                        print '(WARN) Find KeyWord: '+line

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
                        fd.write(datas[i])
                except IOError:
                    print "Error: Can't open or write!!!"
                else:
                    fd.close()
                    print 'Save file: '+self.__dirname+'\\'+filename
            else:
	        if debugLog >= debugLogLevel[2]:
	            print '(WARN) Save File len is 0!'
                

            

        def SaveToFile(self,fd):
	    if debugLog >= debugLogLevel[-1]:
	        print 'SaveToFile:'

            if self.__logLines:
                fd.write(self.__dirname+'\n')
                fd.write(self.__filename+': '+str(self.__logLines)+'\n')

                fd.write('BeginTime: '+self.__beginTime+'\n')
                fd.write('EndTime  : '+self.__endTime+'\n')

                fd.write('1.ErrorFlowsNum: '+str(self.__ErrFlowsNum)+'\n')
                fd.write('2.FlowsNum     : '+str(self.__FlowsNum)+'\n')
                fd.write('3.ErrorLogsNum : '+str(self.__ErrLogsNum)+'\n')
                fd.write('4.KeyWordsNum  : '+str(self.__KeyWordsNum)+'\n')
                fd.write('\n')

                self.__SaveFile(self.Tags+'_ErrFlows_'+self.__filename,self.__ErrFlows)
                self.__SaveFile(self.Tags+'_ErrLogs_'+self.__filename,self.__ErrLogs)
                self.__SaveFile(self.Tags+'_KeyWords_'+self.__filename,self.__KeyWords)
                self.__SaveFile(self.Tags+'_CamFlows_'+self.__filename,self.__CameraFlows)
                self.__SaveFile(self.Tags+'_FlowsLog_'+self.__filename,self.__CameraFlowsLog)

        def Dump(self):
	    if debugLog >= debugLogLevel[-1]:
	        print 'Dump:'

            if self.__logLines:
                print self.__filename+': '+str(self.__logLines)

                print 'BeginTime: '+self.__beginTime
                print 'EndTime  : '+self.__endTime+'\n'

                print '1.ErrorFlowsNum: '+str(self.__ErrFlowsNum)
                print '2.FlowsNum     : '+str(self.__FlowsNum)
                print '3.ErrorLogsNum : '+str(self.__ErrLogsNum)
                print '4.KeyWordsNum  : '+str(self.__KeyWordsNum)

        def getFileName(self):
	    return os.path.join(self.__dirname,self.__filename)

        def getLogLines(self):
	    return self.__logLines


#Global Data
class ScanFileType:
        __ScanDirs=[]
        __ScanFiles=[]
        __Flows={}
        __ErrLogs=[]
        __KeyWords=[]
        
        def SetDefaultValue(self):
            global DefaultScanDirs,DefaultScanFiles,DefaultFlows,DefaultErrLogs,DefaultKeyWords
            self.__ScanDirs = DefaultDirs
            self.__ScanFiles = DefaultScanFiles
            self.__Flows = DefaultFlows
            self.__ErrLogs = DefaultErrLogs
            self.__KeyWords = DefaultKeyWords

        
        def SetScanDirs(self,ScanDirs):
	    if debugLog >= debugLogLevel[-1]:
	        print '(INFO) Set ScanDirs : ',ScanDirs
            self.__ScanDirs=ScanDirs

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

        def GetScanDirs(self):
	    if debugLog >= debugLogLevel[-1]:
	        print '(INFO) Get Scandirs'
            return self.__ScanDirs

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
            print 'ScanDirs: ',self.__ScanDirs
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
        __ScanDirsKey = 'Scan Dirs'
        __ScanFilesKey = 'Scan Files'
        __FlowNameKey = 'Flow Name'
        __ErrorLogsKey = 'Error Logs'
        __KeyWordsKey = 'KeyWords'
        __ConfigTags =(__ScanDirsKey,__ScanFilesKey,__FlowNameKey,__ErrorLogsKey,__KeyWordsKey)

	
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
                        
                        if self.__ConfigTags[i] == self.__ScanDirsKey:
                            if not line[1]:
                                print 'ERROR configfile Format: '+line[1]
                            else:
                                ScanFiles.SetScanDirs(line[1].strip().split(ConfigFileSplitSym))
                        elif self.__ConfigTags[i] == self.__ScanFilesKey:
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

def UnzipDir(fzip,DirName,name,DstDir):
    Dir = re.compile(DirName)

    m = re.search(Dir,name)
    if m:
        if debugLog >= debugLogLevel[1]:
            print "unzip Dir: "+name

        fzip.extract(name,DstDir)        
    else:
        if debugLog >= debugLogLevel[-1]:
            print '(INFO) NOT Dir: '+name



def UnzipDirs(zipSrc,DstDir,Dirs,Files):
    if debugLog >= debugLogLevel[-1]:
          print '(INFO) Unzip File: '+DstDir+'/'+zipSrc

    fz = zipfile.ZipFile(zipSrc,'r')

    for name in fz.namelist():
        for i in range(0,len(Dirs)):
            UnzipDir(fz,Dirs[i],name,DstDir)

        for i in range(0,len(Files)):
            UnzipDir(fz,Files[i],name,DstDir)

        unzip_camlog_file(name,os.path.dirname(name))
        
        CamLog = re.compile(CamLogFileName)
        m = re.match(CamLog,name)
        if m:
            if debugLog >= debugLogLevel[1]:
                print "unzip CamLog File: "+name
            fz.extract(name,dst_dir)        

    if debugLog >= debugLogLevel[2]:
        print "Finish Unzip file: "+zipSrc+'\n'

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
            UnzipDirs(os.path.join(dirname,f),dirname,ScanFiles.GetScanDirs(),ScanFiles.GetScanFiles())
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
        print '(WARN) Default ConfigFile: '+DefaultConfigFile
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
        print "(WARN) !!! Can't open "+ConfigFile+" File!!! \nUseDefaultValue:"
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
        print 'Version: '+SW_VERSION

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

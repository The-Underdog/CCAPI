#Public Domain
#Version 1.1

def NormaliseSlashes(FullFilename,OptionalForwardSlashToBack):
	
	if OptionalForwardSlashToBack is not None:
		
		return FullFilename.replace("\\","/");
	
	else:
		
		return FullFilename.replace("/","\\")

def DetectSlashes(FullFilename):
	DetectType = 0
	
	if '\\' in FullFilename:
		DetectType += 1
		
	if '/' in FullFilename:
		DetectType += 2

	return DetectType

def ExtractEndFilename(FullFilename):
	
	Normalised = NormaliseSlashes(FullFilename,True);
	
	DetectType = DetectSlashes(Normalised)
	
	if DetectType is 0:
		return Normalised
	elif DetectType is 1:
		return Normalised[Normalised.rindex('\\')+1:]
	elif DetectType is 2:
		return Normalised[Normalised.rindex('/')+1:]
	else:
		raise ValueError('FullFilename slashes were not normalised',FullFilename)	

def ExtractEXT(FullFilename):
	return FullFilename[FullFilename.rindex('.')+1:]

def RemoveEXT(FullFilename):
	return FullFilename[:FullFilename.rindex('.')]

def GetDefaultSlash(FullFilename):
	DetectType = DetectSlashes(FullFilename)
	
	if DetectType is 1:
		return '\\'
	else:
		return '/'


def AppendFileLine(Filename,LineToWrite,AppendNewLine=True):
	try:
		OpenFile = open(Filename,'a')
	except:
		raise ValueError('File could not be created!')
	
	if AppendNewLine:
		OpenFile.writelines(LineToWrite + '\n')
	else:
		OpenFile.writelines(LineToWrite)
	
	OpenFile.close()

def WriteFileLines(Filename,Lines,WriteMode='w',AppendNewLine=True):
	try:
		OpenFile = open(Filename,WriteMode)
	except:
		raise ValueError('File could not be created.!')
	
	for EachLine in Lines:
		if AppendNewLine:
			OpenFile.writelines(EachLine+'\n')
		else:
			OpenFile.writelines(EachLine)
	
	OpenFile.close()

def LoadFile(Filename):
	try:
		OpenFile = open(Filename,'r')
	except:
		raise ValueError('File '+Filename+' not found. Please create one!')
	
	Temp = OpenFile.read()
	OpenFile.close()
	return Temp

def LoadFileLines(Filename,StripWhiteSpace=False):

	try:
		OpenFile = open(Filename,'r')
	except:
		raise ValueError('File '+Filename+' not found. Please create one!')
	
	if StripWhiteSpace:
		Lines = [Iter.strip().split('\r\n') for Iter in OpenFile]
	else:
		Lines = [Iter.split('\r\n') for Iter in OpenFile]
	
	OpenFile.close()
	
	NewLines = []
	for EachLine in Lines:
		NewLines += EachLine
	
	return NewLines

def LoadDictionary(filename,SplitChars=':'):
	NewLines = LoadFileLines(filename)

	NewDictionary = {}
	
	for EachLine in NewLines:
		Temp = EachLine.split(SplitChars)
		try:	 
			NewDictionary[Temp[0]] = Temp[1]
		except:
			raise ValueError('Split error in ' + EachLine + '. Possibly missing a split char? In this case: ' + SplitChars)
			
	return NewDictionary

import requests
bimport sys
import os
import subprocess
from WikimediaDownloader import *
from FileIO import *

CurrentDirectory = os.path.dirname(os.path.abspath(__file__))
	
def CheckFileForURL(TargetURL,Filename):
	Lines = LoadFileLines(Filename,False)
	
	for Line in Lines:	
		if TargetURL in Line:
			return True
			
	return False
	
def AddURLToFile(TargetURL,Filename):
	AppendFileLine(Filename,TargetURL)
	
def MakeWikimediaCommonsRequest(SearchTerm,Limit):
	TargetUrl = (
	"https://en.wikipedia.org/w/api.php"
	"?action=query"
	"&generator=images"
	"&prop=imageinfo"
	"&gimlimit="+str(Limit)+
	"&redirects=1"
	"&list=search"
	"&srsearch="+urllib.parse.quote(SearchTerm)+
	"&srnamespace=6"
	"&iiprop=timestamp|user|userid|canonicaltitle|url|size|mime"
	"&format=json")

	return requests.get(TargetUrl).json();

def DownloadImage(TargetFile,TargetOutput,Width=None):
	
	TargetFileExt = TargetFile[TargetFile.rfind('.')+1:].lower()

	if "png" in TargetFileExt or "jpg" in TargetFileExt or "bmp" in TargetFileExt or "pdf" in TargetFileExt:	
		DownloadWikimediaImage(TargetFile,TargetOutput,Width)

while True:
	
	ImageDir = CurrentDirectory+"/Images"
	
	Len = len(sys.argv)
	
	if Len is 1:
		print("Format is: CCAPI.py \"search terms\" [maximum allowed queries to return]")
		exit()
	elif Len is 2:
	
		IncomingData = MakeWikimediaCommonsRequest(str(sys.argv[1]),10)
	
	elif Len is 3:
		
		IncomingData = MakeWikimediaCommonsRequest(str(sys.argv[1]),int(sys.argv[2]))
		
	for Entry in IncomingData["query"]["search"]:
		TargetFile = Entry['title'].replace("File:","")
		
		try:
			DownloadImage(TargetFile,ImageDir)
		
		except Exception as e:
			print("Uh oh Spaghettios! "+str(e))
			#raise Exception(e)
	
	exit()
	

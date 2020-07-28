import os
import re
from pdf2image import convert_from_path
import urllib
import requests
import xmltodict, json
import html2text
import PIL.Image
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

PIL.Image.MAX_IMAGE_PIXELS = None

G_H2T = html2text.HTML2Text()
G_H2T.ignore_links = True

DEFAULT_WIDTH = 100

class DownloadException(Exception):

	pass

class RequestedWidthBiggerThanSourceException(DownloadException):

	pass



def MakeThumbnailName(ImageName, Extension):
	
	FileName, _ = os.path.splitext(ImageName)
	
	if "jpeg" in Extension:
		return FileName + ".jpg"
	else:
		return FileName + "." + Extension

def MakeWikimediaRequest(URL,ImageName,TextMode=False):
	
	Response = requests.get(URL, headers={'User-Agent': 'Python urllib'}) #headers

	try:
		
		ExtensionType = Response.headers['Content-Type']
		
		if "/" not in ExtensionType:
			raise Exception("Could not find slash for extension: "+ExtensionType)
		
		Extension = ExtensionType[ExtensionType.find('/')+1:]
		
		if ";" in Extension:
			Extension = Extension[:Extension.find(';')]
		
		if TextMode is False:
			
			return Response.content, MakeThumbnailName(ImageName, Extension)
			
		else:
			
			return Response.text, MakeThumbnailName(ImageName, Extension)
	
	except Exception as e:
			
		raise Exception(e)
	
def GetThumbnailOfFileReq(ImageName, Width):
	
	URL = "http://commons.wikimedia.org/w/index.php?title=Special:FilePath&file=%s&width=%s" % (urllib.parse.quote(ImageName), Width)
	return MakeWikimediaRequest(URL,ImageName)
	
def GetFullSizeFileReq(ImageName):
	
	URL = "http://commons.wikimedia.org/w/index.php?title=Special:FilePath&file=%s" % (ImageName)
	return MakeWikimediaRequest(URL,ImageName)

def GetMetaDataImageReq(ImageName):
	
	URL = "https://tools.wmflabs.org/magnus-toolserver/commonsapi.php?image=%s" % (ImageName)
	return MakeWikimediaRequest(URL,ImageName,True) 

#response->licenses->license[iterable]->name
#response->file->author
# Image by [Name], distributed under [licence]
def ExtractWikimediaXMLMetadata(IncomingXMLAsString):

	JSONStringFromXML = json.dumps(xmltodict.parse(IncomingXMLAsString))
	
	JSONFromXML = json.loads(JSONStringFromXML)

	if JSONFromXML["response"]["licenses"] is None:
		
		Licence = None
	
	elif JSONFromXML["response"]["licenses"]["license"] is None:
		
		Licence = None
	
	elif type(JSONFromXML["response"]["licenses"]["license"]) is dict:
		
		Licence = JSONFromXML["response"]["licenses"]["license"]["name"]
		
	elif type(JSONFromXML["response"]["licenses"]["license"]) is list:
		
		Licence = JSONFromXML["response"]["licenses"]["license"][0]["name"]
	
	else:
		
		Licence = "Unknown type"
		
		print("Unknown type "+str(type(JSONFromXML["response"]["licenses"]["license"])))
	
	
	AuthorTemp = JSONFromXML["response"]["file"]["author"]
	
	Author = G_H2T.handle(AuthorTemp)
	
	return Author, Licence

#Position is a bracketed input of (X,Y), EG (10,20)
#Fill is a bracketed input of (R,B,G,[A]), EG (255,100,0,0)
def WriteTextToImage(ImageFilename,Text,CaptionPosition=(0,0),TextColour=(0,0,0,0),RectangleColour=(255,255,255,255)):
	
	CleanedText = Text.replace("\n", "")
	
	print(ImageFilename)
	
	TempImage = Image.open(ImageFilename)
	
	ImageWidth, ImageHeight = TempImage.size

	FontSizeIter = 1
	HalvedWidth = ImageWidth/2
	
	while True:
		TempFont = ImageFont.truetype("LeagueMono-Regular.ttf",FontSizeIter)
		TextWidth, TextHeight = TempFont.getsize(CleanedText)
		
		if TextWidth > HalvedWidth:
			break
		
		FontSizeIter += 1
	
	FontSizeIter -= 1
	TempFont = ImageFont.truetype("LeagueMono-Regular.ttf",FontSizeIter)
	TextWidth, TextHeight = TempFont.getsize(Text)
	
	BoxSize = (TextWidth, TextHeight)
	BoxImage = Image.new('RGBA', BoxSize, RectangleColour)
	TempImage.paste(BoxImage, CaptionPosition)
	
	TempDraw = ImageDraw.Draw(TempImage)
	TempDraw.text(CaptionPosition, CleanedText, font=TempFont, fill=TextColour)
	
	TempImage.save(ImageFilename)
	
def PDFToImage(PDFFilename,LicenceText):
	
	BaseFilename = PDFFilename[:PDFFilename.rfind('.')]
	
	PDFPages = convert_from_path(PDFFilename, 500)
	
	Iter = 0
	for APage in PDFPages:
	
		try:
			JPGFilename = BaseFilename+"_"+str(Iter)+".jpg"
			APage.save(JPGFilename,'JPEG')
			WriteTextToImage(JPGFilename,LicenceText)
		
		except Exception as e:
			print("PDFToImage: Skipped page "+str(Iter)+" due to an error: "+str(e))
		
		Iter += 1

	os.remove(PDFFilename)
	return JPGFilename
	
def DownloadWikimediaImage(ImageName, OutputPath, Width=None):
		
	ImageName = ImageName.strip().replace(' ', '_')
	
	XMLContent, OutputXMLName = GetMetaDataImageReq(ImageName)
	
	try:
		
		Author, Licence = ExtractWikimediaXMLMetadata(XMLContent)
	
	except Exception as e:
		
		raise Exception(e)
	
	if Author is not None and Licence is not None:
	
		LicenceText = "Image by "+Author+", distributed under a "+Licence+" license."
	
	elif Author is not None and Licence is None:
		
		LicenceText = "Image by "+Author
	
	elif Author is None and Licence is not None:
		
		LicenceText = "Distributed under a "+Licence+" license."
	
	else:
		
		LicenceText = None
	
	try:
		
		if isinstance(Width,int):
			
			ImageContent, OutputFileName = GetThumbnailOfFileReq(ImageName, Width)
			
		else:
		
			ImageContent, OutputFileName = GetFullSizeFileReq(ImageName)
		
	except Exception as e:
		
		raise Exception(e)
	
	OutputFilePath = os.path.join(OutputPath, OutputFileName)
	
	OutputFilePathExt = OutputFilePath[OutputFilePath.rfind('.')+1:]
	
	try:
		
		print("Writing image "+str(ImageName))
		
		with open(OutputFilePath, 'wb') as f:
			f.write(ImageContent)
		
		if LicenceText is not None:
			
			if "pdf" in OutputFilePathExt:
				
				PDFToImage(OutputFilePath,LicenceText)
				
			else:
			
				WriteTextToImage(OutputFilePath,LicenceText)
		
	except Exception as e:
		
		raise Exception(e)

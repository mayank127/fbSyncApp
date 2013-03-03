#!/usr/bin/python
# coding: utf-8

import facebook
import warnings
import os
import urllib
import urllib2
import pickle
import shutil
import glob
import sys
# Hide deprecation warnings. The facebook module isn't that up-to-date (facebook.GraphAPIError).
warnings.filterwarnings('ignore', category=DeprecationWarning)

#proxy settings
#setting proxy for urllib2
proxy = urllib2.ProxyHandler({'http': os.environ['http_proxy'],'https': os.environ['https_proxy']})
opener = urllib2.build_opener(proxy)
urllib2.install_opener(opener)
#setting proxy for urllib
proxies = {'http': os.environ['http_proxy'],'https': os.environ['https_proxy']}

# Parameters of your app and the id of the profile you want to mess with.
HOME = os.getenv("HOME")
FACEBOOK_APP_ID     = '219305061542308'
FACEBOOK_APP_SECRET = 'f61e54c1dfe3b7236085789a36a409e9'

#ACCESS_TOKEN
access_token_path = HOME + "/.fbSync/access_token"

if not os.path.exists(access_token_path):
	import accessToken

f_access_token = open(access_token_path,'rb')
ACCESS_TOKEN = f_access_token.read()
f_access_token.close()

graph = facebook.GraphAPI(ACCESS_TOKEN)

#Access Token Expiration
a = graph.extend_access_token(FACEBOOK_APP_ID,FACEBOOK_APP_SECRET)	

def getAlbumInfo(userid):
	"""Json of Album"""
	albums=graph.get_object(userid,fields='albums.fields(id,name,photos.fields(id,source),can_upload)')
	if 'albums' in albums.keys():
		return albums
	else:
		print "No Album Accessible of " + userid
		sys.exit(0)
	

def diff(a, b):
	b = set(b)
	return [aa for aa in a if aa not in b]

def downloadPhoto(src, path):
	f=open(path,'wb')
	f.write(urllib2.urlopen(src).read())
	f.close()

def facebookDownload(userid):
	print "Downloading photos of " + userid + "...."
	path=HOME + "/"+ userid
	try:
 		os.mkdir(path)
	except:
 		pass
 	albums=getAlbumInfo(userid)
 	#print albums
 	for album in albums['albums']['data']:
 		pathAlbum = path + "/" + album['name']
 		#print album
 		print "\tChecking Album " + album['name']
 		if os.path.exists(pathAlbum):
 			if 'photos' in album.keys():
	 			for photo in album['photos']['data']:
	 				pathPhoto=pathAlbum + "/" + photo['id'] + ".jpg"
	 				if not (os.path.exists(pathPhoto)):
	 					print "\t\tDownloading...", photo['id']
	 					downloadPhoto(photo['source'],pathPhoto)
	 				# else:
	 				# 	print "" #"Photo Available", pathPhoto
	 		else:
	 			print "\t\tEmpty Album " + album['name']
 		else:
 			print "\t\tCreating New Album..." + album['name']
 			os.mkdir(pathAlbum)
 			for photo in album['photos']['data']:
 				pathPhoto=pathAlbum + "/" + photo['id'] + ".jpg"
 				print "\t\tDownloading...", photo['id']
 				downloadPhoto(photo['source'],pathPhoto)


#facebookDownload('mayank127')

def uploadPhoto(albumPath, albumID, photoName):
	msg=raw_input("\t\tEnter Discription For Photo " + photoName + " : ")
	print "\t\tUploading...",photoName
	photoPath = albumPath + "/" + photoName
	f=open(photoPath, 'rb')
	ref=graph.put_photo(f, message=msg, album_id=albumID.__str__())
	f.close()
	os.rename(photoPath, albumPath + "/" + ref['id'] + ".jpg")

def uploadAlbum(album,userid):
	msg=raw_input("\tEnter Discription For Album " + album + " : ")
	ref = graph.put_object(userid, "albums", name=album ,message=msg)
	pathAlbum = HOME + "/" + userid + "/" + album
	for photo in os.listdir(pathAlbum):
		if photo[-4:] in ['.jpg','.png']:
			uploadPhoto(pathAlbum, ref['id'],photo)


def facebookUpload(userid):
	print "Uploading photos of " + userid + "...."
	path=HOME + "/"+ userid
 	albums=getAlbumInfo(userid)
 	albumList = [x['name'] for x in albums['albums']['data']]
	if os.path.exists(path):
		for album in os.listdir(path):
			if album in albumList:
				fbAlbum=albums['albums']['data'][albumList.index(album)]
				print "\tChecking for album " + album + "..."
				if fbAlbum['can_upload']:
					pathAlbum=path + "/" + album
					dirPhotoList=os.listdir(pathAlbum)
					dirPhotoList.sort()
					dirPhotoList=[[x[0:-4],x[-4:]] for x in dirPhotoList]
					#print dirPhotoList
					if 'photos' in fbAlbum.keys():
						fbPhotoList=[x['id'] for x in fbAlbum['photos']['data']]
						for photo,t in dirPhotoList:
							if not photo in fbPhotoList:
								if t in ['.jpg','.png']:
									uploadPhoto(pathAlbum, fbAlbum['id'],photo+t)
								else:
									print "\t\t" + photo + " is not of type jpg or png"
							# else:
							# 	print "" #Photo available"
					else:
						for photo,t in dirPhotoList:
							if t in ['.jpg','.png']:
								uploadPhoto(pathAlbum, fbAlbum['id'],photo+t)
							else:
								print "\t\t" + photo + " is not of type jpg or png"
				else:
					print "\tNot Enough Permissions/Space for album", album
			else:
				uploadAlbum(album, userid)
	else:
		print "No Username Folder Found"


def fbSync(userid):
	facebookDownload(userid)
	facebookUpload(userid)

def fbClone(userid):
	print "Cloning photos of " + userid + "...."
	facebookDownload(userid)
	path=HOME + "/"+ userid
	try:
 		os.mkdir(path)
	except:
 		pass
 	albums=getAlbumInfo(userid)
 	fbAlbumList = [x['name'] for x in albums['albums']['data']]
 	dirAlbumList = os.listdir(path)
 	for folder in diff(dirAlbumList,fbAlbumList):
 		print "\tDeleting folder not found on fb..." + folder
 		shutil.rmtree(path + "/" +folder)

 	for album in os.listdir(path):
		fbAlbum=albums['albums']['data'][fbAlbumList.index(album)]
		print "\tChecking for album " + fbAlbum['name'] + "..."
		pathAlbum=path + "/" + album
		dirPhotoList=os.listdir(pathAlbum)
		dirPhotoList=[x[0:-4] for x in dirPhotoList]
		if 'photos' in fbAlbum.keys():
			fbPhotoList=[x['id'] for x in fbAlbum['photos']['data']]
		else:
			fbPhotoList=[]
		for photo in diff(dirPhotoList, fbPhotoList):
			pathPhoto = pathAlbum + "/" + photo + "*"
			for filename in glob.glob(pathPhoto):
				print "Deleting photo..." + filename
				os.remove(filename)

if __name__ == '__main__':
	print "1 : Downloading from fb to local directory"
	print "2 : Uploading to fb from local directory"
	print "3 : Syncing your local directory with fb "
	print "4 : Cloning fb albums to your local directory "
	x = raw_input("Your Choice : ")
	FACEBOOK_USER_ID = raw_input("Enter any facebook Username : ")
	if x=='1':
		facebookDownload(FACEBOOK_USER_ID)
	elif x=='2':
		facebookUpload(FACEBOOK_USER_ID)
	elif x=='3':
		fbSync(FACEBOOK_USER_ID)
	elif x=='4':
		fbClone(FACEBOOK_USER_ID)
	else:
		print "Wrong option !!"	
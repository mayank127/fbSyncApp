import gtk 
import webkit
import re 
import os
view = webkit.WebView() 
FACEBOOK_APP_ID = '219305061542308'
sw = gtk.ScrolledWindow() 
sw.add(view) 
win = gtk.Window(gtk.WINDOW_TOPLEVEL) 
win.add(sw) 
win.show_all()

view.open("https://www.facebook.com/dialog/oauth?client_id=" + FACEBOOK_APP_ID + "&redirect_uri=https://www.facebook.com/connect/login_success.html&response_type=token&scope=user_photos%2Cfriends_photos%2Cphoto_upload%2Cpublish_stream")

HOME = os.getenv("HOME")
try:
	os.mkdir(HOME + "/.fbSync")
except:
	print ""

def update(view,frame):
	url=frame.get_uri()
	if 'access_token' in url:
		f = open(HOME + '/.fbSync/access_token','wb') 
		f.write(re.split('\&',re.split('\=',url)[1])[0]) 
		gtk.main_quit()

view.connect('load-committed', update) 
gtk.main()

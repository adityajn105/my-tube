from flask import Flask, render_template, request, jsonify, session
import pickle as pkl
import os

app = Flask(__name__)
usersfile = 'users.pkl'
playlist = 'playlist.pkl'

def getplaylist(user):
    return pkl.load(open(playlist,'rb'))[user]

def updateplaylist(user,code,title):
    ls = pkl.load(open(playlist,'rb'))
    ls[user][code] = title
    pkl.dump(ls,open(playlist,'wb'))

def removeVideo(user,code):
    ls = pkl.load(open(playlist,'rb'))
    if code not in ls[user]:
        return False
    else:
        ls[user].pop(code)
        pkl.dump(ls,open(playlist,'wb'))
        return True

def register(uname,pwd):
    users = pkl.load(open(usersfile,'rb'))
    if uname in users.keys() or pwd == '':
        return False
    else:
        ls = pkl.load(open(playlist,'rb'))
        ls[uname] = dict() 
        pkl.dump(ls,open(playlist,'wb'))
        users[uname] = pwd
        pkl.dump(users,open(usersfile,'wb'))
        return True

def login(uname,pwd):
    users = pkl.load(open(usersfile,'rb'))
    if uname in users.keys() and users[uname]==pwd:
        return True
    else:
        return False

@app.route('/')
def home():
    vid = request.args.get('url', None)
    playlist = request.args.get('playlist', None)
    if vid==None and playlist==None:
        vid = ""
    else:
        if playlist != None:
            print(playlist)
            vid=''
            if 'list=' in playlist:
                playlist = playlist.split("list=")[1]
                playlist = playlist.split('&')[0]
            else:
                playlist = playlist
        elif "v=" in vid:
            vid = vid.split('v=')[1]
            vid = vid.split('&')[0]
        else:
            vid = vid

    if 'uname' in session:
        uname = session['uname']
        plist = getplaylist(uname)
        if playlist==None:
            if vid=='' and len(plist) != 0:
                vid = list(plist.keys())[0]
                return render_template('youtube.html', data = {'vid':vid, 'playlist':None, 'title':plist[vid], 'login':uname, 'list':plist} )
            return render_template('youtube.html', data = {'vid':vid, 'playlist':None, 'title':'' ,'login':uname, 'list':plist} )
        else:
            return render_template('youtube.html', data = {'playlist':playlist, 'vid':vid,  'title':'' ,'login':uname, 'list':plist} )
    else:
        if playlist == None:
            return render_template('youtube.html',data = {'vid':vid, 'playlist' :None, 'title':'', 'error':None,'login':None} )
        else:
            return render_template('youtube.html',data = {'playlist':playlist, 'vid':vid, 'title':'', 'error':None,'login':None} )

@app.route('/logout')
def logout():
    session.pop('uname', None)
    return home()

@app.route('/add',methods= ['POST'])
def add():
    if request.method == 'POST':
        uname = session['uname']
        info = request.form
        code = info['code']
        title = info['title']
        if code!="":
            updateplaylist(uname,code,title)
            plist = getplaylist(uname)
            return render_template('youtube.html', data = {'vid':code, 'playlist':None, 'title':title, 'login':uname, 'list':plist} )
        else:
            session.pop('uname', None)
            return render_template('youtube.html',data = {'vid':'', 'playlist':None, 'title':'', 'error':"Wrong Code!! Login Again and continue", 'login':None} )
    else:
        return home()

@app.route('/remove/<code>',methods= ['GET'])
def remove(code):
    if 'uname' in session:
        if removeVideo(session['uname'], code):
            return home()
        else:
            session.pop('uname')
            return home()
    else:
        return home()

@app.route('/login', methods = ['POST'])
def loginuser():
    if request.method == 'POST':
        cred = request.form
        uname = cred['uname']
        pwd = cred['pwd']
        if login(uname,pwd):
            session['uname'] = uname
            return home()
        else:
            return render_template('youtube.html',data = {'vid':'','playlist':None,'title':'','error':"Invalid Credentials", 'login':None} )
    else:
        return home()


@app.route('/register', methods = ['POST'])
def registeruser():
    if request.method == 'POST':
        cred = request.form
        uname = cred['uname']
        pwd = cred['pwd']
        if register(uname,pwd):
            session['uname'] = uname
            return home()
        else:
            return render_template('youtube.html',data = {'vid':'','playlist':None, 'title':'' ,'error':"Username already registered or invalid password.", 'login':None} )
    else:
        return home()

@app.route('/<vid>')
def playVideo(vid):
    if 'uname' in session:
        uname = session['uname']
        plist = getplaylist(uname)
        if vid in plist.keys():
            return render_template('youtube.html', data = {'vid':vid,'playlist':None, 'title':plist[vid], 'login':uname, 'list':plist} )
        else:
            return render_template('youtube.html', data = {'vid':vid,'playlist':None, 'title':'Your Video', 'login':uname, 'list':plist} )
    else:
        return render_template('youtube.html', data = {'vid':vid,'playlist':None, 'title':'Your Video', 'login':None} )

if __name__ == "__main__":
    if not os.path.isfile(usersfile):
        print("Creating User Database!!")
        pkl.dump( dict(), open(usersfile,'wb') )
    if not os.path.isfile(playlist):
        print("Creating Playlist Database!!")
        pkl.dump( dict(), open(playlist,'wb') )
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(host = '0.0.0.0', port = int(5000))
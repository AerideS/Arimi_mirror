from flask import Flask, render_template, request, session
from firebaseAPI import *
from crawling_API import *
import os
import json

#주기적 실행을 위한 페키지
import schedule
import time

#멀티프로세싱을 위한 패키지
from multiprocessing import Process, Queue

check_first = True # 여러번 db 객체 초기화가 되는 걸 막기 위함

def crawling():
    while(True):
        global check_first
        if  check_first :
            cred = credentials.Certificate('./key.json')
            app = firebase_admin.initialize_app(cred)
            db = firestore.client()
            crawling_ref = db.collection("crawlingData")
            docs = crawling_ref.stream()
            check_first = False
        else :
            db = firestore.client() # 함수 재시작시 객체를 가져올 필요가 있음.
            crawling_ref = db.collection("crawlingData")
            docs = crawling_ref.stream()

        for doc in docs :
            s = doc.to_dict().get("url")
        
            c = crawling_page(s, 1, 1)
            j = json.loads(c)['data']

            for jn in j:
                print(jn['title'], sep=" ")
                print(jn['date'])

            db = crawlingData(s)
            for jn in j:
                db.addCrawling(jn['title'], jn['date'])
        time.sleep(60) # 60초 주기로 실행

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def sign_in(): #
    return render_template('signIn.html')

@app.route('/signUp')
def sing_up(): #
    return render_template('signUp.html')

@app.route('/home', methods=['POST', 'GET'])
def sign_in_done(): #
    result = request.form
    signInEmail = result.get('email')  #자바스크립트에서 보낸 이메일 주소 가져오기
    session['signInEmail'] = signInEmail  #세션에 이메일 주소 저장

    user_data = userData(signInEmail)
    
    if user_data.checkUserExist():
        try :
            docs_url = user_data.getUserURL()
            craw_data = crawlingData(docs_url[0]['url'])
            docs_craw = craw_data.getCrawling()

            docs = [docs_url, docs_craw]
        except IndexError :
            return render_template("home.html")
        return render_template("user.html", docs=docs)
    else:
        user_data.addUser()
        return render_template("home.html")

@app.route('/user', methods=['POST', 'GET'])
def add_url():
    result = request.form
    if result['URL'] == "" or result['Name'] == "":
        return render_template("home.html")
    
    signInEmail = session.get('signInEmail')
    user_data = userData(signInEmail)
    
    user_data.addUserURL(result['URL'], result['Name'])
    docs_url = user_data.getUserURL()
    craw_data = crawlingData(docs_url[0]['url'])
    docs_craw = craw_data.getCrawling()
    docs = [docs_url, docs_craw ]
    return render_template("user.html", docs=docs)

if __name__ == '__main__':
    # 멀티 프로세싱 
    th = Process(target=crawling)
    th.start()
    app.run(debug=True)


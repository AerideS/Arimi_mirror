from flask import Flask, render_template, request, session
from firebaseAPI import *
from crawling_API import *
import os
import json

# 분류 패키지
from operator import itemgetter

#주기적 실행을 위한 페키지
import schedule
import time

#멀티프로세싱을 위한 패키지
from multiprocessing import Process, Queue
from threading import Thread
import selenium

app = Flask(__name__)
app.secret_key = os.urandom(24)
check_first = True # 여러번 db 객체 초기화가 되는 걸 막기 위함
client = firebase_con()

def crawling():
    while(True):
        global check_first
        if  check_first :
            db = client.distClient()
            crawling_ref = db.collection("crawlingData")
            docs = crawling_ref.stream()
            check_first = False
        else :
            db = client.distClient() # 함수 재시작시 객체를 가져올 필요가 있음.
            crawling_ref = db.collection("crawlingData")
            docs = crawling_ref.stream()

        for doc in docs :
            s = doc.to_dict().get("url")
            print(s)
            try :
                c = crawling_page(s, 1, 1)
                j = json.loads(c)['data']
            except ValueError:
                print(ValueError)
                continue
            except selenium.common.exceptions.JavascriptException :
                print(selenium.common.exceptions.JavascriptException)
                continue

            #세부내용 출력
            # for jn in j:
            #     print(jn['title'], sep=" ")
            #     print(jn['date'])
            #     print(jn['link'])

            db = crawlingData(s, client.distClient())
            db.delCrawlingData()
            for jn in j:
                if(jn['date'] > 1701388800): # 가입 시간 입력할 것
                   db.addCrawling(jn['title'], jn['link'], jn['date'])
        time.sleep(3600) # 60초 주기로 실행

def get_crawlingData(docs_url, userDataDate):
    # 사용자가 저장한 url에 대하여 크롤링 데이터를 가져와 사용자 가입 시간 이후부터 시간순 정렬
    try:
        cnt = 0
        docs_craw = []
        start1 = time.time()
        for doc in docs_url:
            start = time.time()
            craw_data = crawlingData(doc['url'], client.distClient())
            crawling_data = craw_data.getCrawling()
            end = time.time()
            print('겟')
            print(end-start)
            for index, doc in enumerate(crawling_data):
                docs_craw.append(doc)
                cnt+=1
        print(cnt)
    except IndexError :
        #이미 userData에 존재하는 사용자가 로그인 했을 때 등록한 URL이 아무것도 없으면 home.html 랜더링함
        return render_template("home.html")
    if len(docs_craw) > 0 :
        docs_craw = sorted(docs_craw, key=itemgetter('date'), reverse=True)
    user_craw = []
    for data in docs_craw:
        if(data['date'] > userDataDate) :
            user_craw.append(data)
        else :
            continue

    for doc in user_craw :
        doc['date'] = datetime.fromtimestamp(doc['date']).strftime("%Y/%m/%d")

    end1 = time.time()
    print("총 걸린시간")
    print(end1-start1)
    return user_craw

@app.route('/')
def sign_in():
    return render_template('signIn.html')

@app.route('/signUp')
def sing_up():
    return render_template('signUp.html')

@app.route('/home', methods=['POST', 'GET'])
def sign_in_done():
    result = request.form
    signInEmail = result.get('email')  #자바스크립트에서 보낸 이메일 주소 가져오기
    session['signInEmail'] = signInEmail  #세션에 이메일 주소 저장
    print('user_id 잘 왔는지 확인:' + session.get('signInEmail')) #확인용

    user_data = userData(signInEmail, client.distClient())
    userDataDate = user_data.getUserSignUpDate()
    # 유저 가입 시간 이후 데이터만 출력
    
    if user_data.checkUserExist():
        docs_url = user_data.getUserURL()
        print(docs_url)
        docs_craw = get_crawlingData(docs_url, userDataDate)
        docs = [docs_url, docs_craw]
        end2 = time.time()
        return render_template("user.html", docs=docs)
    else:
        user_data.addUser()
        end = time.time()
        return render_template("home.html")

        

@app.route('/user', methods=['POST', 'GET'])
def add_url():
    result = request.form

    signInEmail = session.get('signInEmail')
    print('user_id 잘 왔는지 확인:' + signInEmail) #확인용
    user_data = userData(signInEmail, client.distClient())
    
    if 'DelURL' in result and result['DelURL'] != "":
        user_data.delUserURL(result['DelURL'])
    else:
        user_data.addUserURL(result['URL'], result['Name'])

    docs_url = user_data.getUserURL()
    print(docs_url) #확인용
    userDataDate = user_data.getUserSignUpDate()
    docs_craw = get_crawlingData(docs_url, userDataDate)
    docs = [docs_url, docs_craw]

    #확인용
    #print('-------------------------------------------------------------------------------------')
    #print(docs)
    #print('-------------------------------------------------------------------------------------')
    
    return render_template("user.html", docs=docs)

if __name__ == '__main__':
    #멀티 프로세싱 
    th1 = Thread(target=crawling)
    th1.start()
    th1.join()

    app.run(debug=True)
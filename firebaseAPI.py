import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime

certLoc = './flask/key.json'
projectID = "project-data-b3b34" # just ramdom value before define

class db_connect:

    def __init__(self, name):
        '''
        user_name or URL name
        '''
        self.objType = name

    def initCon(self) -> None: # complete
        '''
        DB와의 연결 초기화
        '''
        try:
            firebase_admin.get_app()
            firebase_admin.delete_app(firebase_admin.get_app())
        except ValueError:
            pass
            
        cred = credentials.Certificate(certLoc)
        firebase_admin.initialize_app(cred, {
            'databaseURL': projectID
        })

    def deleteDB(self, db, path, batch_size=10) -> None: # complete
        '''
        데이터베이스 삭제
        '''
        collection_ref = db.collection(path)
        docs = collection_ref.limit(batch_size).stream()
        deleted = 0

        for doc in docs:
            print(f'Deleting document {doc.id}')
            doc.reference.delete()
            deleted += 1

        if deleted >= batch_size:
            return self.deleteDB(path, batch_size)

        print(f'{deleted} documents deleted from {path}')

    def initDB(self) -> None: # complete
        '''
        DB 초기화
        '''
        self.initCon()
        db = firestore.client()
        self.deleteDB(db, 'userData')
        self.deleteDB(db, 'crawlingData')
        print("DB initialized")

    def showDB(self):
        self.initCon()
        db = firestore.client()
        collections = db.collections()
        print("We have ",end="")
        for collection in collections:
            print(f"{collection.id}, ", end="")

class crawlingData(db_connect):

    def __init__(self, url):
        super().__init__("crawling")
        self.urlAdr = url
        self.addURL()

    def delUrl(self): 
        '''
        url 삭제하기
        user가 존재하는 경우에는 삭제 불가
        '''
        if self.checkURLExist() is True:
            return False

        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("url") == self.urlAdr:                
                db.collection("crawlingData").document(doc.id).delete()
                del self
                return True
            
        return False

    def delUrlUser(self, user_name):
        '''
        하나의 Url 앞에 등록된 사용자 삭제하기 
        '''
        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("url") == self.urlAdr:
                data_array = doc.to_dict().get("users", [])
                for data, i in enumerate(data_array):
                    if data['id'] == user_name:
                        data_array.pop(i)
                        db.collection("crawlingData").document(doc.id).update({"users": data_array})
                        return True
                    
        return False


    def checkUrlUserEmpty(self):
        '''
        crawling data에서 user가 존재하는지 확인
        '''
        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("url") == self.urlAdr:
                data_array = doc.to_dict().get("users", [])
                if len(data_array) > 0:
                    return True
                return False
            
    def checkUrlCrawlingEmpty(self):
        '''
        crawling data에서 크롤링한 데이터가 존재하는지 확인 
        '''
        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("url") == self.urlAdr:
                data_array = doc.to_dict().get("users", [])
                if len(data_array) > 0:
                    return True
                return False
            

    def checkURLExist(self) -> bool:
        '''
        crawlingData에 URL이 등록되어 있는지확인
        '''
        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("url") == self.urlAdr:
                
                return True

        return False 
    
    def checkURLHasUser(self, user) -> bool:
        '''
        url 앞으로 user가 등록되어 있는지 확인
        '''
        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("url") == self.urlAdr:
                users = doc.to_dict().get("users")
                if users == None:
                    
                    return False

                for url_user in users:
                    if user == url_user:
                        
                        return True                    
                
                return False            
        
        return False 

    def addURL(self): # hasToBeChecked
        '''
        url을 DB에 추가
        '''    

        # 해당 URL에 대한 정보가 이미 존재하는 경우 pass
        if self.checkURLExist():         
            return
        
        self.initCon()
        db = firestore.client() 

        doc_ref = db.collection("crawlingData")
        doc = doc_ref.add({
            "url" : self.urlAdr,
            "data" : [],
            "users" : []
        })

    def addCrawling(self, title : str, addTime : datetime = datetime.datetime.now().timetuple()):
        '''
        크롤링 데이터 및 추가한 시간 정보 포함 저장
        별도로 datetime을 지정하지 않은 경우에는 크롤링 데이터를 추가한 시간이 등록됨
        url : str - 사용자의 아이디
        title : dict - 
        addTime : datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        '''    
        self.initCon()
        db = firestore.client() 
        new_data = {}
        new_data['date'] = addTime
        new_data['title'] = title
        same = True

        crawling_ref = db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            #print(doc.to_dict())
            if doc.to_dict().get("url") == self.urlAdr:
                same = False
                data_array = doc.to_dict().get("data", [])
                max_id = max([single_data['id'] for single_data in data_array], default=0)
                new_data['id'] = max_id + 1
                data_array.append(new_data)
                
                db.collection("crawlingData").document(doc.id).update({"data": data_array})

                break

        if same:
            new_data['id'] = 0
            doc_ref = db.collection("crawlingData").document(f'{self.urlAdr}')
            doc_ref.set({'url' : self.urlAdr,
                        'data' : [new_data],
                        'users' : []})
            
        print(f"Data added to {self.urlAdr}")        

    def getCrawling(self) -> dict: # complete
        '''
        해당 url에 해당하는 크롤링 데이터를 DB에서 전부 가져오기
        '''
        
        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("url") == self.urlAdr:
                #print(doc.to_dict().get("data"))
                print(f"Get data url : {self.urlAdr}")                
                return doc.to_dict().get("data") 
            
    def getURLUser(self): #hasToBeChecked
        '''
        하나의 url 앞에 등록된 user 목록 return
        '''
        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("url") == self.urlAdr:
                #print(doc.to_dict().get("data"))
                print(f"Get user data of url : {self.urlAdr}")
                
                return doc.to_dict().get("users")  

    def getURL(self): #hasToBeChecked
        '''
        
        '''
        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("crawlingData")
        docs = crawling_ref.stream()

        li = []
        for doc in docs:
            li.append(doc.to_dict().get("url"))
        return li
    def addURLUser(self, user): #hasToBeChecked
        '''
        하나의 url 앞에 사용자 추가
        '''

        if self.checkURLHasUser(self.urlAdr, user):
            return

        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            #print(doc.to_dict())
            if doc.to_dict().get("url") == self.urlAdr:
                data_array = doc.to_dict().get("users", [])
                data_array.append(user)
                
                db.collection("crawlingData").document(doc.id).update({"users": data_array})

                break    

class userData(db_connect):

    def __init__(self, user_name):
        super().__init__('user')
        self.user_name = user_name
        self.addUser()

    def checkUserExist(self) -> bool:
        '''
        user에 사용자가 존재하는지 확인 
        '''
        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("userData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("user_id") == self.user_name:
                
                return True

        return False 

    def checkUserHasURL(self, url) -> bool:
        '''
        user가 url을 등록하였는지 확인
        '''
        if self.checkUserExist() is False:
            return

        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("userData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("user_id") == self.user_name:
                urls = doc.to_dict().get("added_url")
                if urls == None:                    
                    return False
                
                for user_url in urls:                
                    if url == user_url['url']:                        
                        return True                    
                
                return False
        
        return False 
    
    def delUser(self):
        '''
        사용자 삭제
        1. 해당 사용자가 가진 url을 delUrluser로 삭제
        2. 사용자 삭제
        '''
        if self.checkUserExist() is False:
            return

        user_url = self.getUserURL(self.user_name)        
        for i in user_url:
            crawlingData(i).delUrlUser(user_url, self.user_name) 

        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("url") == self.urlAdr:                
                db.collection("crawlingData").document(doc.id).delete()
                break        

    def delUserURL(self, url):
        '''
        하나의 사용자 앞에 등록된 url 삭제하기 -> 중간고사 이후 해도 무관함 
        '''
        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("userData")
        docs = crawling_ref.stream()

        for doc in docs:
            #print(doc.to_dict())
            if doc.to_dict().get("user_id") == self.user_name:
                data_array = doc.to_dict().get("added_url", [])
                for data, i in enumerate(data_array):
                    if data['url'] == url:
                        data_array.pop(i)
                        break
                
                db.collection("userData").document(doc.id).update({"added_url": data_array})

                break

        return False

    def getUserURL(self):
        '''
        하나의 사용자 앞에 등록된 url 목록 return
        '''
        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("userData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("user_id") == self.user_name:
                #print(doc.to_dict().get("data"))
                print(f"Get user data : {self.user_name}")
                
                return doc.to_dict().get("added_url") 

    def addUser(self): # complete
        '''
        하나의 사용자 추가
        사용자 등록은 firestore authentification과 연동 고려중
        '''    

        if self.checkUserExist() is True:
            return

        self.initCon()
        db = firestore.client() 

        doc_ref = db.collection("userData").document(self.user_name)
        doc_ref.set({
            "user_id" : self.user_name,
            "added_url" : [],
            "signin_date" : int(datetime.datetime.now().timestamp())
        })  

    def addUserURL(self, url, tag = None): # complete
        '''
        하나의 사용자 앞에 url 및 사용자 지정 tag 추가
        tag는 입력하지 않을 시 url로 기본값 
        '''
        if tag == None:
            tag = self.user_name

        # 이미 사용자가 URL을 추가한 경우 등록된 tag만 수정한다 
        if self.checkUserHasURL(url):
            return

        new_data = {
            "url" : url,
            "tag" : tag
        }

        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("userData")
        docs = crawling_ref.stream()

        for doc in docs:
            #print(doc.to_dict())
            if doc.to_dict().get("user_id") == self.user_name:
                data_array = doc.to_dict().get("added_url", [])
                data_array.append(new_data)
                
                db.collection("userData").document(doc.id).update({"added_url": data_array})

                break

    def _changeSigninTime(self, time : str):
        '''
        디버그용
        사용자 가입 시기 인위적 변경
        '''
        self.initCon()
        db = firestore.client() 

        crawling_ref = db.collection("userData")
        docs = crawling_ref.stream()
        timestamp = int(datetime.strptime(time, "%Y-%m-%d").timestamp())

        for doc in docs:
            #print(doc.to_dict())
            if doc.to_dict().get("user_id") == self.user_name:
                
                db.collection("userData").document(doc.id).update({"signin_date": timestamp})

                break

if __name__ == "__main__":
    """
    test code!
    """

    # first = db_connect('db')
    # first.initDB()
    # odu3971 = userData('odu3971')
    # print(odu3971.getUserURL())

    aeroSpace = crawlingData('https://www.gnu.ac.kr/main/na/ntt/selectNttList.do?mi=1127&bbsId=1029')

    # print('addCrawling---------------')
    # aeroSpace.addCrawling('네이버 공지사항')

    # print('getCrawling---------------')
    # print(aeroSpace.getCrawling('www.naver.com'))

    # print('addUser---------------')
    # print(odu3971.addUser())

    # print('addUserURL---------------')
    # odu3971.addUserURL('https://www.gnu.ac.kr/main/na/ntt/selectNttList.do?mi=1127&bbsId=1029', "항공")

    #print('addURLUser---------------')
    #addURLUser('https://www.gnu.ac.kr/main/na/ntt/selectNttList.do?mi=1127&bbsId=1029', 'odu3971')

    # print('getUserURL---------------')
    # print(getUserURL('odu3971'))

    # print('getrURLUser---------------')
    # print(getrURLUser('www.naver.com'))
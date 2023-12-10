from firebase_admin import credentials
from firebase_admin import firestore
import firebase_admin
import datetime

certLoc = './flask/key.json'
projectID = "project-data-b3b34" # just ramdom value before define

class firebase_con:
    def __init__(self) -> None:
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
        self.client = firestore.client()

    def distClient(self):
        return self.client

class dbConnect:

    def __init__(self, name, client):
        '''
        user_name or URL name
        '''
        self.objType = name
        self.db = client
        
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
        self.deleteDB(self.db, 'userData')
        self.deleteDB(self.db, 'crawlingData')
        print("DB initialized")

    def showDB(self):
        collections = self.db.collections()
        print("We have : ",end="")
        for collection in collections:
            print(f'{collection.id}, ', end="")

    def addUser(self, user_name): # complete
        '''
        하나의 사용자 추가
        사용자 등록은 firestore authentification과 연동 고려중
        '''    

        if dbConnect.checkUserExist(self, user_name) is True:
            return False

        doc_ref = self.db.collection("userData").document(user_name)
        doc_ref.set({
            "user_id" : user_name,
            "added_url" : [],
            "signin_date" : int(datetime.datetime.now().timestamp())
        }) 
    
    def addURL(self, urlAdr):
        '''
        url을 DB에 추가
        '''    

        # 해당 URL에 대한 정보가 이미 존재하는 경우 pass
        if dbConnect.checkURLExist(self, urlAdr):         
            return False

        doc_ref = self.db.collection("crawlingData")
        doc = doc_ref.add({
            "url" : urlAdr,
            "data" : [
                {
                    "id" : 1,
                    "date" : datetime.datetime.now().timestamp(),
                    "title" : f'1 시간 이내 업데이트 예정 : {self.urlAdr}',
                    "specific_url" : self.urlAdr
                }
            ],
            "users" : []
        })
             
    def getWholeUrl(self): #hasToBeChecked
        '''
        등록된 모든 URL return
        '''
        crawling_ref = self.db.collection("crawlingData").get()

        return [i.to_dict().get("url") for i in crawling_ref]
    
    def getWholeUser(self): #hasToBeChecked
        '''
        등록된 모든 User return
        '''

        crawling_ref = self.db.collection("userData").get()

        return [i.to_dict().get("user_id") for i in crawling_ref]
    
    def checkUserExist(self, user_id) -> bool:

        '''
        user에 사용자가 존재하는지 확인 
        '''
        doc_ref = self.db.collection("userData").where("user_id", "==", user_id).get()
        
        if doc_ref:
            return True
        return False

    def checkURLExist(self, urlAdr) -> bool:
        '''
        URL이 등록되어 있는지확인
        '''  
        doc_ref = self.db.collection("crawlingData").where("url", "==", urlAdr).get()

        if doc_ref:
            return True
        return False

class crawlingData(dbConnect):

    def __init__(self, url, client):
        super().__init__("crawling", client)
        self.urlAdr = url
        super().addURL(self.urlAdr)

    def addCrawling(self, title : str, specific_url : str , addTime : datetime = datetime.datetime.now().timestamp()):
        '''
        크롤링 데이터 및 추가한 시간 정보 포함 저장
        별도로 datetime을 지정하지 않은 경우에는 크롤링 데이터를 추가한 시간이 등록됨
        url : str - 사용자의 아이디
        title : dict - 
        addTime : datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        '''    
        new_data = {}
        new_data['date'] = addTime
        new_data['title'] = title
        new_data['specific_url'] = specific_url
        same = True

        crawling_ref = self.db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("url") == self.urlAdr:
                same = False
                data_array = doc.to_dict().get("data", [])
                max_id = max([single_data['id'] for single_data in data_array], default=0)
                new_data['id'] = max_id + 1
                data_array.append(new_data)
                self.db.collection("crawlingData").document(doc.id).update({"data": data_array})
                break

        if same:
            new_data['id'] = 0
            doc_ref = self.db.collection("crawlingData").document(f'{self.urlAdr}')
            doc_ref.set({'url' : self.urlAdr,
                        'data' : [new_data],
                        'users' : []})
            
        print(f"Data added to {self.urlAdr}")        
                 
    def addURLUser(self, user):
        '''
        하나의 url 앞에 사용자 추가
        '''

        if self.checkURLHasUser(user):
            return
        
        crawling_ref = self.db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            #print(doc.to_dict())
            if doc.to_dict().get("url") == self.urlAdr:
                data_array = doc.to_dict().get("users", [])
                data_array.append(user)
                
                self.db.collection("crawlingData").document(doc.id).update({"users": data_array})

                break    

    def getCrawling(self) -> dict: # complete
        '''
        해당 url에 해당하는 크롤링 데이터를 DB에서 전부 가져오기
        '''

        crawling_ref = self.db.collection("crawlingData")
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

        crawling_ref = self.db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("url") == self.urlAdr:                
                return doc.to_dict().get("users")  
        
    def delUrl(self): 
        '''
        url 삭제하기
        user가 존재하는 경우에는 삭제 불가
        '''
        if self.checkURLExist() is False:
            return "NO URL"
        if self.checkUrlUserLeft() is True:
            return "User Left!"

        crawling_ref = self.db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("url") == self.urlAdr:                
                self.db.collection("crawlingData").document(doc.id).delete()
                del self
                return True
            
        return False

    def delCrawlingData(self):
        crawling_ref = self.db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("url") == self.urlAdr:                
                self.db.collection("crawlingData").document(doc.id).update({"data": []})
                break

    def delUrlUser(self, user):
        '''
        하나의 Url 앞에 등록된 사용자 삭제하기 
        '''

        if isinstance(user, userData):
            user = user.user_name

        crawling_ref = self.db.collection("crawlingData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("url") == self.urlAdr:
                data_array = doc.to_dict().get("users", [])
                print(data_array)
                for i, data in enumerate(data_array):
                    if data == user:
                        data_array.pop(i)
                        self.db.collection("crawlingData").document(doc.id).update({"users": data_array})
                        return True                    
        return False

    def checkUrlUserLeft(self):
        '''
        crawling data에서 user가 비어있는지 확인
        '''

        crawling_ref = self.db.collection("crawlingData")
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

        doc_ref = self.db.collection("crawlingData").where("url", "==", self.urlAdr).get()

        if len(doc_ref['data']) > 0:
            return True
        else:
            return False
            
    def checkURLHasUser(self, user_id) -> bool:
        '''
        url 앞으로 user가 등록되어 있는지 확인
        '''
        if isinstance(user_id, userData):
            user_id = user_id.user_name

        doc_ref = self.db.collection("crawlingData").where("url", "==", self.urlAdr).get()
        print(doc_ref[0].get("users"))
        if doc_ref:
            users = doc_ref[0].get("users")

            user_exists = any(user == user_id for user in users)

            if user_exists:
                return True
            else:
                return False
        else:
            return False
    
    def checkURLExist(self) -> bool:
        return super().checkURLExist(self.urlAdr)
    
class userData(dbConnect):

    def __init__(self, user_name, client):
        super().__init__('user', client)
        self.user_name = user_name
        self.addUser(self.user_name)

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

        crawling_ref = self.db.collection("userData")
        docs = crawling_ref.stream()

        for doc in docs:
            #print(doc.to_dict())
            if doc.to_dict().get("user_id") == self.user_name:
                data_array = doc.to_dict().get("added_url", [])
                data_array.append(new_data)
                
                self.db.collection("userData").document(doc.id).update({"added_url": data_array})

                break

    def getUserSignUpDate(self):

        crawling_ref = self.db.collection("userData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("user_id") == self.user_name:                
                return doc.to_dict().get("signin_date") 
            
    def getUserURL(self):
        '''
        하나의 사용자 앞에 등록된 url 목록 return
        '''

        crawling_ref = self.db.collection("userData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("user_id") == self.user_name:
                #print(doc.to_dict().get("data"))
                print(f"Get user data : {self.user_name}")
                
                return doc.to_dict().get("added_url") 

    def delUser(self):
        '''
        사용자 삭제
        1. 해당 사용자가 가진 url을 delUrluser로 삭제
        2. 사용자 삭제
        '''
        if self.checkUserExist() is False:
            return "user not exist"

        user_url = self.getUserURL()       
        for i in user_url:
            crawlingData(i['url'], self.db).delUrlUser(self.user_name)

        crawling_ref = self.db.collection("userData")
        docs = crawling_ref.stream()

        for doc in docs:
            if doc.to_dict().get("user_id") == self.user_name:                
                self.db.collection("userData").document(doc.id).delete()
                return True

    def delUserURL(self, url): #hastobechecked
        '''
        하나의 사용자 앞에 등록된 url 삭제하기 -> 중간고사 이후 해도 무관함 
        '''

        crawling_ref = self.db.collection("userData")
        docs = crawling_ref.stream()

        for doc in docs:
            #print(doc.to_dict())
            if doc.to_dict().get("user_id") == self.user_name:
                data_array = doc.to_dict().get("added_url", [])
                for i, data in enumerate(data_array):
                    if data['url'] == url:
                        data_array.pop(i)
                        break
                
                self.db.collection("userData").document(doc.id).update({"added_url": data_array})

                break

        return False
    
    def checkUserHasURL(self, url) -> bool:
        '''
        user가 url을 등록하였는지 확인
        '''
        if self.checkUserExist() is False:
            return "user not exists"

        doc_ref = self.db.collection("userData").where("user_id", "==", self.user_name).get()

        if doc_ref:
            added_urls = doc_ref[0].get("added_url")

            if any(added_url['url'] == url for added_url in added_urls):
                return True
            else:
                return False
        else:
            return False

    def checkUserExist(self) -> bool:
        return super().checkUserExist(self.user_name)
    
    def _changeSigninTime(self, time : str):
        '''
        디버그용
        사용자 가입 시기 인위적 변경
        "%Y-%m-%d"로 입력할 것
        '''

        if self.checkUserExist() is False:
            return "user not exist"

        crawling_ref = self.db.collection("userData")
        docs = crawling_ref.stream()
        timestamp = int(datetime.datetime.strptime(time, "%Y-%m-%d").timestamp())

        for doc in docs:
            #print(doc.to_dict())
            if doc.to_dict().get("user_id") == self.user_name:
                
                self.db.collection("userData").document(doc.id).update({"signin_date": timestamp})

                return True

if __name__ == "__main__":
    """
    test code!
    """
    client = firebase_con()
    test_URL = crawlingData("https://lib.gnu.ac.kr/index.html#/bbs/notice?offset=0&max=20", client.distClient())
    test_URL.delCrawlingData()

    # db = dbConnect('db', client.distClient())
    # test_user = userData('test_user', client.distClient())
    # test_URL = crawlingData("www.test.com", client.distClient())
    # print(test_user.getUserSignUpDate())

    # print("사용자 추가 : test_user")    
    # print("URL 추가 : test.com")    
    # print("사용자 존재? :", db.checkUserExist('test_user'))        
    # print("사용자 URL 가짐?: ", test_user.checkUserHasURL('www.test.com'))     
    # print("사용자 URL 추가: ", test_user.addUserURL('www.test.com', 'test'))    
    # print("사용자 URL 반환: ", test_user.getUserURL())    
    
    # print("사용자 URL 삭제: ", test_user.delUserURL('www.test.com'))    
    
    # print("사용자 URL 반환" ,test_user.getUserURL()) 
    
    # print("사용자 URL 추가 :" ,test_user.addUserURL('www.test.com', 'test'))
    
    # print("사용자 URL 반환 :" ,test_user.getUserURL())    
    
    # print("_changeSigninTime: ", test_user._changeSigninTime('1999-06-11'))
    
    # print("총 URL 반환: ", db.getWholeUrl())
    
    # print("총 USer 반환: ", db.getWholeUser())
    
    # print("크롤링 반환: ", test_URL.getCrawling())
    
    # print("크롤링 추가: ", test_URL.addCrawling('test', 'specific'))
    
    # print("크롤링 반환: ", test_URL.getCrawling())
    
    # print("URL 앞 사용자 반환: ", test_URL.getURLUser())
    
    # print("URL 앞 사용자 추가: ", test_URL.addURLUser("test_user"))
    
    # print("URL 앞 사용자 반환: ", test_URL.getURLUser())
    
    # print("크롤링 반환: ", test_URL.getCrawling())    
    
    # print("URL 앞 user 남음?: ", test_URL.checkUrlUserLeft())
    
    # print("URL 앞 crawling 남음?: ", test_URL.checkUrlCrawlingEmpty())
    
    # print("URL 앞 사용자 추가: ", test_URL.addURLUser("test_user"))
    
    # print("URL 앞 해당 user 등록?: ", test_URL.checkURLHasUser(test_user))
    
    # print("URL 존재?: ", test_URL.checkURLExist())
    
    # print("사용자 삭제: ", test_user.delUser())  
    
    # print("URL 삭제: ", test_URL.delUrl())
    
    # print("url 앞 사용자 삭제: ", test_URL.delUrlUser(test_user))
    
    # print("URL 삭제: ", test_URL.delUrl()) 
    
    
  

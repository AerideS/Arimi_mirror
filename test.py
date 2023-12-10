from firebaseAPI import *
from crawling_API import *
from google.cloud.firestore_v1 import Query
from google.cloud.firestore_v1.base_query import FieldFilter, BaseCompositeFilter


cred = credentials.Certificate('./key.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

doc_ref = db.collection('crawlingData')
docs = doc_ref.stream()

for doc in docs:
    data=doc.to_dict().get('data') 
    for i in range(10):
        time = data[i].get('date')
        if(time > 2099542000):
             print(data[i])
    






from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

'''
mongodb 개념

mysql : mongodb
db    : db
table : collection
row   : document
'''

# MongoDB 연결 URI
user = os.environ.get('MONGODB_USER')
password = os.environ.get('MONGODB_PASSWORD')
host = os.environ.get('MONGODB_HOST') # 탄력적ip사용해야할듯 ..
port = os.environ.get('MONGODB_PORT')
client = MongoClient(f'mongodb://{user}:{password}@{host}:{port}/?authSource=admin&retryWrites=true&w=majority')

# db 접근
db = client['lgu']

def mongodb_insert(collection, mydict):
    #collection 접근
    mycollection = db[f'{collection}']
    mycollection.insert_one(mydict)

    try : 
        print(f'{mydict} 데이터 삽입 성공!!')
    except Exception as e:
        print(f"{e} : 데이터 삽입에 실패했습니다... ㅠㅠ 확인 부탁해용")

def mongo_delete(collection):
    try:
        collection = db[collection]
        # 컬렉션의 모든 문서 삭제
        result = collection.delete_many({})
        print(f"{collection.name} 컬렉션의 데이터 삭제 성공! 삭제된 문서 수: {result.deleted_count}")
    except Exception as e:
        print(f"오류 발생: {str(e)}. 데이터 삭제 실패... ㅠㅠ 확인 부탁드립니다.")


def select(collection):
    mycollection = db[f'{collection}']
    select_data = mycollection.find()

    return select_data

def select_id_data(user):
    mycollection = db['chatbot']
    select_data = mycollection.find({"user": f"{user}"})
    return list(select_data)  # 커서를 리스트로 변환하여 반환

if __name__ == "__main__":
    data = select_id_data("wbsldj59")
    print({"data": data})  # 리스트 형태로 출력
    pass








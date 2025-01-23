from fastapi import Depends, status, FastAPI, Request, Form, HTTPException
from fastapi import Query
from fastapi.responses import JSONResponse
from DB.db_mysql import login_save,login,check_duplicate_id,get_schedule_details,get_filtered_schedule,select_id,update_password,select_competiton_all
from DB.db_mongodb import select
import os
from passlib.hash import bcrypt
from cryptography.fernet import Fernet
import bcrypt
from utils.util import web_apt_competition_simple,web_apt_competition,web_apt_unranked_simple,web_unranked_competition,web_upcoming_applications,web_upcoming_applications_simple
from utils.analysis import general_competition_graph,special_competition_graph
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel
# from rag import rag_chat
from scenario import get_scenario_response
from dotenv import load_dotenv
from rag import rag_chat

from scenario import get_scenario_response
from personalized_flow import get_personalized_response
from motor.motor_asyncio import AsyncIOMotorClient
import time
from DB.db_mongodb import select_id_data

load_dotenv()
ROOT_PATH = os.environ.get("ROOT_PATH")

app = FastAPI(root_path=ROOT_PATH)

# MongoDB 연결 설정
user = os.environ.get('MONGODB_USER')
password = os.environ.get('MONGODB_PASSWORD')
host = os.environ.get('MONGODB_HOST') # 탄력적ip사용해야할듯 ..
port = os.environ.get('MONGODB_PORT')
client = AsyncIOMotorClient(f'mongodb://{user}:{password}@{host}:{port}/?authSource=admin&retryWrites=true&w=majority')



db = client["lgu"]
collection = db["chatbot"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_dir = os.path.dirname(__file__)

encryption_key = Fernet.generate_key()  # 배포 환경에서는 고정된 키를 사용해야 함
cipher = Fernet(encryption_key)


SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def create_access_token(data : dict, expires_delta : timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp" : expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not contain user information",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/api/protected")
async def protected_api(current_user: str = Depends(get_current_user)):
    # 로그인 정보 가져오기 (예: 데이터베이스 호출)
    login_info = login()

    # current_user (ID)에 해당하는 사용자 필터링
    matched_user = login_info[login_info["id"] == current_user]

    # 사용자 정보 확인
    if matched_user.empty:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # 첫 번째 행을 딕셔너리로 변환
    user_data = matched_user.iloc[0].to_dict()

    return {"user": user_data}



@app.post("/api/id_search")
async def id_search(name: str = Form(...), email: str = Form(...)):
    try:
        # DB 쿼리 예제
        id = select_id(name, email)[0][0]  # `select_id`는 DB 검색 함수로 가정
        return {"id": id}
    except IndexError:
        return {"error": "ID를 찾을 수 없습니다. 입력 정보를 확인해주세요."}
    except Exception as e:
        return {"error": "서버 오류가 발생했습니다. 관리자에게 문의하세요."}

@app.put("/api/password_update")
async def id_search(
    name: str = Form(None),
    email: str = Form(None),
    id : str = Form(None),
    password : str = Form(None)
):
    try:
        update_password(name,id,email,password)
        return {
        "complete": "비밀번호 재설정이 성공적으로 완료됐습니다."
    }
    except Exception as e:
        return {
            "error": "입력된 정보가 정확하지 않습니다. 입력 정보를 확인해주세요."
        }




# api (calendar - db)
@app.get("/api/schedule")
async def api_events(
    start: str,
    end: str,
    special: bool = Query(False),
    priority1: bool = Query(False),
    priority2: bool = Query(False),
    unranked: bool = Query(False),
):
    """
    /api/schedule 엔드포인트 - 필터 조건을 통해 일정 가져오기
    """
    return get_filtered_schedule(
        start=start, 
        end=end, 
        special=special, 
        priority1=priority1, 
        priority2=priority2, 
        unranked=unranked,
    )

# api(claendar - detail)
@app.get("/api/schedule/{apartment_name}")
async def api_event_details(apartment_name: str):
    details = get_schedule_details(apartment_name)
    if not details:
        return {"error": "Event not found"}
    return details


# API



@app.post("/api/analysis")
async def analysis(
    region: str = Form(None),
    year: int = Form(None),
    home: str = Form(None),
):
    if region and year and home: 
        table = "competition"
        
        if home == "general":
            select = "general_supply_competition_rate"
        elif home == "special":
            select = "special_supply_competition_rate"
        else:
            return {"data": None}

        data = select_competiton_all(table, region, year, select)
        # print(data)

        return {"data": data.to_dict(orient="records")}  # JSON 변환하여 반환

    return {"data": None}





@app.get("/api/news")
async def get_news(request: Request):

    collection = 'news'
    data = select (collection)
    news = [{"tetle" :item['title'], "link" : item['link'],"description" : item['description'],"pubDate" : item['pubDate'], "image" : item['image']} for item in data]
    # print(news)
    return {"news": news}



@app.get("/api/upcoming")
async def get_upcoming(request: Request):

    table = "apt_housing_application_basic_info"
    apt_upcoming_data = web_upcoming_applications_simple(table)

    table = "unranked_housing_application_basic_info"
    unranked_upcoming_data = web_upcoming_applications_simple(table)
    
    return {"apt_upcoming_data" : apt_upcoming_data,
            "unranked_upcoming_data" : unranked_upcoming_data}


@app.get("/api/competition")
async def get_competition(request: Request):

    apt_grouped_data = web_apt_competition_simple()

    unranked_grouped_data = web_apt_unranked_simple()
    
    return {"apt_grouped_data" : apt_grouped_data,
            "unranked_grouped_data" : unranked_grouped_data}


@app.post("/api/login")
async def login_api(
    request: Request,
    id: str = Form(..., description="The user's ID"),  # Form 필드에 설명 추가
    password: str = Form(..., description="The user's password")  # Form 필드에 설명 추가
):

    login_info = login()
    matched_user = login_info[login_info["id"] == id]

    if matched_user.empty:
        return JSONResponse(
            {"error": "Invalid ID or password. Please try again."},
            status_code=400,
        )

    hashed_password = matched_user["password"].iloc[0]
    if not bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
        return JSONResponse(
            {"error": "Invalid ID or password. Please try again."},
            status_code=400,
        )
    
    user_data = matched_user.iloc[0].to_dict()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
    data={"sub" : user_data["id"]}, expires_delta = access_token_expires
)
    print(access_token)
    print(user_data["id"])
    return JSONResponse({"access_token": access_token, "token_type": "bearer"})



@app.post("/api/logout")
async def logout(current_user: str = Depends(get_current_user)):
    return {"message": "Successfully logged out"}
    



@app.get("/api/faq")
async def faq_api(
    request: Request,
):
    collection = 'faq'
    data = select (collection)
    terms = [(item['question'], item['answer']) for item in data]
    
    return {
        "terms": terms
    }






@app.get("/api/term")
async def term_api(request: Request):
    
    collection = 'term'
    data = select (collection)
    terms = [(item['term'], item['term_description']) for item in data]


    return ({
        "terms": terms
    })







@app.post("/api/join")
async def join(
    id: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    name: str = Form(...),
    resident_number: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    address: str = Form(...),
    bankbook: str = Form(...),
):
    if password != confirm_password:
        return {"error": "Passwords do not match."}

    if check_duplicate_id(id):
        return {"error": "The ID already exists. Please use a different ID."}

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    login_save(
        id=id,
        passwd=hashed_password,
        name=name,
        resident_number=resident_number,
        email=email,
        phone_number=phone_number,
        address=address,
        bankbook=bankbook,
    )

    return {"message": "회원가입이 완료되었습니다."}




@app.get("/api/detail/{apartment_name}")
async def get_competition_data(apartment_name: str):
    # 경쟁률
    apt_grouped_data = web_apt_competition()  
    unranked_grouped_data = web_unranked_competition()  

    # 다가오는 청약
    table_1 = "apt_housing_application_basic_info"
    apt_upcoming_data = web_upcoming_applications(table_1)
    table_2 = "unranked_housing_application_basic_info"
    unranked_upcoming_data = web_upcoming_applications(table_2)

    if any(group['apartment_name'] == apartment_name for group in apt_grouped_data):
        filtered_data = next((group for group in apt_grouped_data if group['apartment_name'] == apartment_name), None)
    elif any(group['apartment_name'] == apartment_name for group in unranked_grouped_data):
        filtered_data = next((group for group in unranked_grouped_data if group['apartment_name'] == apartment_name), None)

    elif any(data['apartment_name'] == apartment_name for data in apt_upcoming_data):
        filtered_data = next((data for data in apt_upcoming_data if data['apartment_name'] == apartment_name), None)
    elif any(data['apartment_name'] == apartment_name for data in unranked_upcoming_data):
        filtered_data = next((data for data in unranked_upcoming_data if data['apartment_name'] == apartment_name), None)

    if filtered_data:
        return JSONResponse(content={
            "apartment_name": apartment_name,
            "grouped_data": filtered_data['data']
        })
    else:
        return JSONResponse(content={
            "error": "Apartment not found"
        }, status_code=404)
    


class ChatRequest(BaseModel):
    message: str
    user_id: str







@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        user_message = request.message
        current_time = datetime.now()
        user_id = request.user_id

        # 시나리오 응답 확인
        scenario_response = get_scenario_response(user_message)

        if scenario_response:
            # 시나리오 봇 응답 저장
            await collection.insert_one({
                "user" : user_id,
                "유저": user_message,
                "봇": scenario_response["text"],
                "timestamp": current_time
            })

            return {
                "response": {
                    "role": "model",
                    "type": "scenario_button",  # 시나리오 버튼 타입 지정
                    "text": scenario_response["text"],
                    "buttons": scenario_response["buttons"],
                    "timestamp": int(time.time() * 1000)
                }
            }
        
        # 맞춤형 청약 플로우 응답 확인
        personalized_response = get_personalized_response(user_message)
        if personalized_response:

            await collection.insert_one({
                "user" : user_id,
                "유저": user_message,
                "봇": personalized_response["text"],
                "timestamp": current_time
            })
            return {
                "response": {
                    "role": "model",
                    "type": "scenario_button",
                    "text": personalized_response["text"],
                    "buttons": personalized_response.get("buttons", []),
                    "currentStep": personalized_response.get("currentStep"),
                    "totalSteps": personalized_response.get("totalSteps"),
                    "requiresInput": personalized_response.get("requiresInput", None),
                    "timestamp": int(time.time() * 1000)
                }
            }
        
        rag_response = rag_chat(user_message)

        # RAG 봇 응답 저장
        await collection.insert_one({
            "user" : user_id,
            "유저": user_message,
            "봇": rag_response,
            "timestamp": current_time
        })

        return {
            "response": {
                "role": "model",
                "text": rag_response,
                "timestamp": int(time.time() * 1000)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/log")
async def chat_log(request: ChatRequest):
    user_id = request.user_id  # 여기서 user_id를 추출
    print(f"Received user_id: {user_id}")
    # 데이터 처리 로직
    return {"data": []}
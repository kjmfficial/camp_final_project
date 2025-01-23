# from fastapi import FastAPI, Request, Form, HTTPException
# from fastapi import Query
# from fastapi.responses import HTMLResponse,RedirectResponse
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
# from typing import Optional
# from starlette.middleware.sessions import SessionMiddleware
# from DB.db_mysql import login_save,login,check_duplicate_id,get_schedule_details,get_filtered_schedule,select_id,update_password
# from DB.db_mongodb import select
# import os
# import json
# from typing import List, Dict
# from passlib.hash import bcrypt
# from cryptography.fernet import Fernet
# import bcrypt
# from utils.util import web_apt_competition_simple,web_apt_competition,web_apt_unranked_simple,web_unranked_competition,web_upcoming_applications,web_upcoming_applications_simple
# from utils.analysis import general_competition_graph,special_competition_graph

# app = FastAPI()

# base_dir = os.path.dirname(__file__)
# app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")
# templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

# app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# encryption_key = Fernet.generate_key()  # 배포 환경에서는 고정된 키를 사용해야 함
# cipher = Fernet(encryption_key)

# @app.get("/", response_class=HTMLResponse)
# async def main(request: Request):
#     # 세션에서 사용자 데이터 가져오기
#     user = request.session.get("user")

#     apt_grouped_data = web_apt_competition_simple()

#     unranked_grouped_data = web_apt_unranked_simple()

#     table = "apt_housing_application_basic_info"
#     apt_upcoming_data = web_upcoming_applications_simple(table)

#     table = "unranked_housing_application_basic_info"
#     unranked_upcoming_data = web_upcoming_applications_simple(table)

#     collection = 'news'
#     data = select (collection)
#     news = [(item['title'], item['link'], item['description'], item['pubDate'], item['image']) for item in data]

#     # 사용자 정보를 템플릿으로 전달
#     return templates.TemplateResponse("main.html", {
#         "request": request,
#         "user": user,
#         "news": news,
#         "apt_grouped_data": apt_grouped_data,
#         "unranked_grouped_data" : unranked_grouped_data,
#         "apt_upcoming_data" : apt_upcoming_data,
#         "unranked_upcoming_data" : unranked_upcoming_data
#     })

# @app.api_route("/join_membership", methods=["GET", "POST"], response_class=HTMLResponse)
# async def join_membership(
#     request: Request,
#     id: str = Form(None),
#     password: str = Form(None),
#     confirm_password: Optional[str] = Form(None),
#     name: str = Form(None),
#     resident_number: str = Form(None),
#     email: str = Form(None),
#     phone_number: str = Form(None),
#     address: str = Form(None),
#     bankbook: Optional[str] = Form(None),
# ):
#     full_email = email

#     if request.method == "GET":
#         return templates.TemplateResponse("join_membership.html", context={"request": request})

#     elif request.method == "POST":
#         # 비밀번호 확인
#         if password != confirm_password:
#             return templates.TemplateResponse(
#                 "join_membership.html",
#                 context={"request": request, "error": "Passwords do not match."},
#             )
        
#         # ID 중복 확인
#         if check_duplicate_id(id):
#             return templates.TemplateResponse(
#                 "join_membership.html",
#                 context={"request": request, "error": "The ID already exists. Please use a different ID."},
#             )

#         # 비밀번호 암호화
#         hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())




#         # 데이터 저장
#         login_save(
#             id=id,
#             passwd=hashed_password,  # 암호화된 비밀번호
#             name=name,
#             resident_number=resident_number,  # 암호화된 주민등록번호
#             email=full_email,
#             phone_number=phone_number,
#             address=address,
#             bankbook=bankbook,
#         )

#         return templates.TemplateResponse(
#             "login.html",
#             context={"request": request, "success": "가입이 완료되었습니다."},
#         )
    


# @app.api_route("/login", methods=["GET", "POST"], response_class=HTMLResponse)
# async def login_route(
#     request: Request,
#     id: str = Form(None),
#     password: str = Form(None),
# ):
#     login_info = login()  # DB에서 로그인 정보 가져오기

#     if request.method == "GET":
#         return templates.TemplateResponse("login.html", context={"request": request})

#     elif request.method == "POST":
#         # 1. ID 확인
#         matched_user = login_info[login_info["id"] == id]

#         if matched_user.empty:  # ID가 없을 경우
#             return templates.TemplateResponse(
#                 "login.html",
#                 context={
#                     "request": request,
#                     "error": "Invalid ID or password. Please try again.",
#                 },
#             )

#         # 2. 비밀번호 확인
#         hashed_password = matched_user["password"].iloc[0]
#         if not bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
#             return templates.TemplateResponse(
#                 "login.html",
#                 context={
#                     "request": request,
#                     "error": "Invalid ID or password. Please try again.",
#                 },
#             )

#         # 3. 세션 저장
#         user_data = matched_user.iloc[0].to_dict()
#         request.session["user"] = user_data

#         return RedirectResponse(url="/", status_code=303)


# @app.get("/logout", response_class=HTMLResponse)
# async def logout(request: Request):
#     # 세션에서 사용자 정보 제거
#     request.session.clear()
#     return RedirectResponse(url="/", status_code=303)


# @app.api_route("/id_search", methods=["GET", "POST"], response_class=HTMLResponse)
# async def id_search(
#     request: Request,
#     name: str = Form(None),
#     email: str = Form(None),
# ):
#     if request.method == "GET":
#         return templates.TemplateResponse("id_search.html", context={"request": request})

#     elif request.method == "POST":
#         try:
#             id = select_id(name,email)[0][0]
#             return templates.TemplateResponse("id_search.html",{
#             "request": request,
#             "id": id
#         })
#         except Exception as e:
#             error_message = f"An error occurred: {e}"
#             print(error_message)  # 서버 로그에 에러 출력
#             return templates.TemplateResponse("id_search.html", {
#                 "request": request,
#                 "error": "ID를 찾을 수 없습니다. 입력 정보를 확인해주세요."
#             })
            



# @app.api_route("/password_update", methods=["GET", "POST"], response_class=HTMLResponse)
# async def id_search(
#     request: Request,
#     name: str = Form(None),
#     email: str = Form(None),
#     id : str = Form(None),
#     password : str = Form(None)
# ):
#     if request.method == "GET":
#         return templates.TemplateResponse("password_update.html", context={"request": request})

#     elif request.method == "POST":
#         try:
#             update_password(name,id,email,password)

#             return templates.TemplateResponse("password_update.html",{
#             "request": request,
#             "complete": "비밀번호 재설정이 성공적으로 완료됐습니다."
#         })
#         except Exception as e:
#             error_message = f"An error occurred: {e}"
#             print(error_message)  # 서버 로그에 에러 출력
#             return templates.TemplateResponse("password_update.html", {
#                 "request": request,
#                 "error": "비밀번호를 찾을 수 없습니다. 입력 정보를 확인해주세요."
#             })





# @app.get("/chatbot", response_class=HTMLResponse)
# async def logout(request: Request):
#     # 세션에서 사용자 정보 제거
#     user = request.session.get("user")
    
#     return templates.TemplateResponse("chatbot.html", {
#         "request": request,
#         "user": user
#     })


# @app.get("/calendar", response_class=HTMLResponse)
# async def calendar(request: Request):
#     """
#     Renders the calendar HTML page.
#     """
#     return templates.TemplateResponse("calendar.html", {"request": request})

# @app.get("/term", response_class=HTMLResponse)
# async def term(request: Request):
    
#     collection = 'term'
#     data = select (collection)
#     terms = [(item['term'], item['term_description']) for item in data]


#     return templates.TemplateResponse("term.html", {
#         "request": request,
#         "terms": terms
#     })

# @app.get("/faq", response_class=HTMLResponse)
# async def term(request: Request):
    
#     collection = 'faq'
#     data = select (collection)
#     terms = [(item['question'], item['answer']) for item in data]


#     return templates.TemplateResponse("faq.html", {
#         "request": request,
#         "terms": terms
#     })

# @app.api_route("/analysis", methods=["GET", "POST"], response_class=HTMLResponse)
# async def analysis(
#     request: Request,
#     region: str = Form(None),
#     year: int = Form(None),
#     home: str = Form(None),
# ):
#     if request.method == "GET":
#         return templates.TemplateResponse(
#             "analysis.html", {"request": request, "graph": None}
#         )

#     if request.method == "POST":
#         if region and year and home:
#             # 청약 타입에 따라 적절한 그래프 생성
#             if home == "general":
#                 graph = general_competition_graph(region, year)
#                 home_type = "일반 공급"
#             elif home == "special":
#                 graph = special_competition_graph(region, year)
#                 home_type = "특별 공급"
#             else:
#                 graph = None
#                 home_type = "알 수 없음"

#             return templates.TemplateResponse(
#                 "analysis.html",
#                 {"request": request, "graph": graph, "home_type": home_type},
#             )

#         # 입력값이 부족할 경우
#         return templates.TemplateResponse(
#             "analysis.html", {"request": request, "graph": None}
#         )


# @app.get("/my_info",response_class=HTMLResponse)
# async def my_info(request:Request):

#     user = request.session.get("user")

#     return templates.TemplateResponse("my_info.html", {
#         "request": request,
#         "user": user
#     })


# @app.get("/competition/{apartment_name}", response_class=HTMLResponse)
# async def term(request: Request, apartment_name: str):
#     apt_grouped_data = web_apt_competition()  
#     unranked_grouped_data = web_unranked_competition()  
    
#     # apartment_name이 apt_grouped_data에 있는지 확인
#     if any(group['apartment_name'] == apartment_name for group in apt_grouped_data):
#         filtered_data = next((group for group in apt_grouped_data if group['apartment_name'] == apartment_name), None)
#     else:
#         filtered_data = next((group for group in unranked_grouped_data if group['apartment_name'] == apartment_name), None)

#     return templates.TemplateResponse("competition.html", {
#         "request": request,
#         "apartment_name": apartment_name,
#         "grouped_data": filtered_data['data']
#     })


# @app.get("/upcoming_applications/{apartment_name}", response_class=HTMLResponse)
# async def term(request: Request, apartment_name: str):

#     table_1 = "apt_housing_application_basic_info"
#     apt_upcoming_data = web_upcoming_applications(table_1)

#     table_2 = "unranked_housing_application_basic_info"
#     unranked_upcoming_data = web_upcoming_applications(table_2)
    

#     if any(data['apartment_name'] == apartment_name for data in apt_upcoming_data):
#         filtered_data = next((data for data in apt_upcoming_data if data['apartment_name'] == apartment_name), None)

#     else:
#         filtered_data = next((data for data in unranked_upcoming_data if data['apartment_name'] == apartment_name), None)

#     return templates.TemplateResponse("upcoming_applications.html", {
#         "request": request,
#         "apartment_name": apartment_name,
#         "grouped_data": filtered_data['data']
#     })


# # api (calendar - db)
# @app.get("/api/schedule")
# async def api_events(
#     start: str,
#     end: str,
#     special: bool = Query(False),
#     priority1: bool = Query(False),
#     priority2: bool = Query(False),
#     unranked: bool = Query(False),
# ):
#     """
#     /api/schedule 엔드포인트 - 필터 조건을 통해 일정 가져오기
#     """
#     return get_filtered_schedule(
#         start=start, 
#         end=end, 
#         special=special, 
#         priority1=priority1, 
#         priority2=priority2, 
#         unranked=unranked,
#     )

# # api(claendar - detail)
# @app.get("/api/schedule/{apartment_name}")
# async def api_event_details(apartment_name: str):
#     details = get_schedule_details(apartment_name)
#     if not details:
#         return {"error": "Event not found"}
#     return details



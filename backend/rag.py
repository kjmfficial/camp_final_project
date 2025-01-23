import json
import pandas as pd
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv
import gc
from DB.db_mysql import rag_data
from datetime import date,datetime

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.environ.get('OPEN_AI')

def chunk_text(text, max_chunk_size=1000, overlap=100):
    """긴 텍스트를 청크로 나누는 함수"""
    sentences = text.replace('\n', ' ').split('. ')
    sentences = [s + '.' for s in sentences if s]
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += " " + sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    if overlap > 0 and len(chunks) > 1:
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i-1]
            overlap_text = prev_chunk[-overlap:]
            chunks[i] = overlap_text + chunks[i]
    
    return chunks

def _process_faq_data(data):
    """FAQ 데이터 처리 함수"""
    processed = []
    if not isinstance(data, list):
        print("FAQ 데이터가 리스트 형식이 아닙니다.")
        return processed

    for item in data:
        try:
            question = item.get('question', '').strip()
            answer = item.get('answer', '').strip()
            if question and answer:
                processed.append({
                    'title': 'FAQ',
                    'content': f"Q: {question}\nA: {answer}",
                    'metadata': {
                        'question': question,
                        'type': 'faq'
                    },
                    'type': 'qa_content'
                })
        except Exception as e:
            print(f"FAQ 항목 처리 중 오류 발생: {str(e)}")
            continue
            
    return processed

def _process_document_data(data):
    """일반 문서 데이터 처리 함수"""
    processed = []
    if not isinstance(data, list):
        print("문서 데이터가 리스트 형식이 아닙니다.")
        return processed
    for doc in data:
        try:
            title = doc.get('title', '').strip()
            sections = doc.get('sections', [])
            if title and sections:
                for section in sections:
                    content = section.get('content', '').strip()
                    metadata = section.get('metadata', {})
                    if content:
                        processed.append({
                            'title': title,
                            'content': content,
                            'metadata': metadata,
                            'type': 'pdf_content'
                        })
                        
        except Exception as e:
            print(f"문서 처리 중 오류 발생: {str(e)}")
            continue
            
    return processed

def _process_csv_apt_data(csv_data):
    """CSV 데이터 처리 함수 (새로운 형식 지원)"""
    processed = []
    try:

        # CSV 데이터를 행 단위로 처리
        for _, row in csv_data.iterrows():
            # 필수 데이터 추출
            region = row.get('region', '정보 없음')
            housing_type = row.get('housing_type', '정보 없음')
            sale_or_lease = row.get('sale_or_lease', '정보 없음')
            apartment_name = row.get('apartment_name', '정보 없음')
            construction_company = row.get('construction_company', '정보 없음')
            contact = row.get('contact', '정보 없음')
            announcement_date = row.get('announcement_date', '정보 없음')
            application_period_start = row.get('application_period_start', '정보 없음')
            application_period_end = row.get('application_period_end', '정보 없음')
            result_announcement = row.get('result_announcement', '정보 없음')
            # 데이터 포맷 정의
            # print(row.get('apartment_name'))  # 해당 값을 출력하여 확인


            if isinstance(announcement_date, date):
                announcement_date = announcement_date.isoformat()
            if isinstance(application_period_start, date):
                application_period_start = application_period_start.isoformat()
            if isinstance(application_period_end, date):
                application_period_end = application_period_end.isoformat()
            if isinstance(result_announcement, date):
                result_announcement = result_announcement.isoformat()


            content = (
                f"지역: {region}\n"
                f"주택 유형: {housing_type}\n"
                f"분양/임대: {sale_or_lease}\n"
                f"아파트 이름: {apartment_name}\n"
                f"건설사: {construction_company}\n"
                f"연락처: {contact}\n"
                f"공고일: {announcement_date}\n"
                f"청약 접수 시작: {application_period_start}\n"
                f"청약 접수 종료: {application_period_end}\n"
                f"결과 발표: {result_announcement}"
            )

            # 처리된 데이터를 리스트에 추가
            processed.append({
                'title': f'{apartment_name}_기본정보_데이터',
                'content': content,
                'type': 'apt_csv',
                'metadata': {
                    'source_type': 'apt_csv',
                    'apartment_name' : apartment_name,
                    'start_date' : application_period_start,
                    'end_date' : application_period_end,
                    'result_date' : result_announcement,
                    'region': region,
                    'housing_type': housing_type,
                    'contact' : contact,
                    'has_table': True
                }
            })

    except Exception as e:
        print(f"APT 데이터 처리 중 오류 발생: {str(e)}")
    return processed

def _process_csv_unranked_data(csv_data):
    """CSV 데이터 처리 함수 (새로운 형식 지원)"""
    processed = []
    try:
        # CSV 데이터를 행 단위로 처리
        for _, row in csv_data.iterrows():
            # 필수 데이터 추출
            region = row.get('region', '정보 없음')
            subscription_type = row.get('subscription_type', '정보 없음')
            apartment_name = row.get('apartment_name', '정보 없음')
            construction_company = row.get('construction_company', '정보 없음')
            announcement_date = row.get('announcement_date', '정보 없음')
            application_period_start = row.get('application_period_start', '정보 없음')
            application_period_end = row.get('application_period_end', '정보 없음')
            result_announcement = row.get('result_announcement', '정보 없음')


            if isinstance(announcement_date, date):
                announcement_date = announcement_date.isoformat()
            if isinstance(application_period_start, date):
                application_period_start = application_period_start.isoformat()
            if isinstance(application_period_end, date):
                application_period_end = application_period_end.isoformat()
            if isinstance(result_announcement, date):
                result_announcement = result_announcement.isoformat()

            # 데이터 포맷 정의
            # print(row.get('apartment_name'))  # 해당 값을 출력하여 확인
            content = (
                f"지역: {region}\n"
                f"주택 유형: {subscription_type}\n"
                f"아파트 이름: {apartment_name}\n"
                f"건설사: {construction_company}\n"
                f"공고일: {announcement_date}\n"
                f"청약 접수 시작: {application_period_start}\n"
                f"청약 접수 종료: {application_period_end}\n"
                f"결과 발표: {result_announcement}"
            )

            # 처리된 데이터를 리스트에 추가
            processed.append({
                'title': f'{apartment_name}_기본정보_데이터',
                'content': content,
                'type': 'unranked_csv',
                'metadata': {
                    'source_type': 'unranked_csv',
                    'apartment_name' : apartment_name,
                    'start_date' : application_period_start,
                    'end_date' : application_period_end,
                    'result_date' : result_announcement,
                    'region': region,
                    'subscription_type': subscription_type,
                    'has_table': True
                }
            })

    except Exception as e:
        print(f"APT 데이터 처리 중 오류 발생: {str(e)}")
    return processed

def _process_csv_apt_competition_data(csv_data):
    """CSV 데이터 처리 함수 (새 데이터 형식 지원)"""
    processed = []
    try:
        # CSV 데이터를 행 단위로 처리
        for _, row in csv_data.iterrows():
            # 필수 데이터 추출 (새 데이터 구조에 맞게 수정)
            house_type = row.get('house_type', '정보 없음') or '정보 없음'
            apartment_name = row.get('apartment_name', '정보 없음') or '정보 없음'
            supply_units = row.get('supply_units', '정보 없음') or '정보 없음'
            rank = row.get('announcement_date', '정보 없음') or '정보 없음'  # 'announcement_date'로 수정
            rank_region = row.get('rank_region', '정보 없음') or '정보 없음'
            application_count = row.get('application_count', '정보 없음') or '정보 없음'
            competition_rate = row.get('competition_rate', '정보 없음') or '정보 없음'
            application_result = row.get('application_result', '정보 없음') or '정보 없음'
            region = row.get('region', '정보 없음') or '정보 없음'
            score_min = row.get('score_min', '정보 없음') or '정보 없음'
            score_max = row.get('score_max', '정보 없음') or '정보 없음'
            score_avg = row.get('score_avg', '정보 없음') or '정보 없음'

            # 데이터 포맷 정의
            content = (
                f"지역: {region}\n"
                f"아파트 이름: {apartment_name}\n"
                f"공급 세대수: {supply_units}\n"
                f"순위유형: {rank}\n"
                f"주소지 해당 여부: {rank_region}\n"
                f"청약 지원자 수: {application_count}\n"
                f"경쟁률: {competition_rate}\n"
                f"청약 진행도: {application_result}\n"
                f"최소점수: {score_min}\n"
                f"최대점수: {score_max}\n"
                f"평균점수: {score_avg}\n"
                f"타입: {house_type}\n"
            )

            # 처리된 데이터를 리스트에 추가
            processed.append({
                'title': f'{apartment_name}_경쟁률_데이터',
                'content': content,
                'type': 'apt_competition_csv',
                'metadata': {
                    'source_type': 'apt_competition_csv',
                    'apartment_name': apartment_name,
                    'region': region,
                    'competition_rate': competition_rate,
                    "house_type": house_type,
                    'has_table': True
                }
            })

    except Exception as e:
        print(f"APT 데이터 처리 중 오류 발생: {str(e)}")
    return processed


def load_all_data(file_paths):
    """모든 데이터를 로드하고 처리하는 함수"""
    processed_data = []
    
    # JSON 파일 처리
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):  # 파일 존재 여부 확인
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if 'FAQ_Crawling.json' in file_path:
                        faq_data = _process_faq_data(data)
                        processed_data.extend(faq_data)
                        print(f"FAQ 데이터 처리 완료: {len(faq_data)}개 항목")

            else:
                print(f"파일을 찾을 수 없습니다: {file_path}")
                    
        except Exception as e:
            print(f"파일 처리 중 오류 발생: {file_path} - {str(e)}")
    
    
    apt_data = rag_data("apt_housing_application_basic_info")
    apt_processed = _process_csv_apt_data(apt_data)
    processed_data.extend(apt_processed)
    # print(f"APT 파일 처리 완료: {apt_data} - {len(apt_processed)}개 항목")


    unranked_data = rag_data("unranked_housing_application_basic_info")
    unranked_processed = _process_csv_unranked_data(unranked_data)
    processed_data.extend(unranked_processed)
    # print(f"unranked 파일 처리 완료: {unranked_data} - {len(unranked_processed)}개 항목")

    # apt_competition_data = rag_data("apt_housing_competition_rate")
    # apt_competition_processed = _process_csv_apt_competition_data(apt_competition_data)
    # processed_data.extend(apt_competition_processed)
    # print(f"apt_competition 파일 처리 완료: {apt_competition_data} - {len(apt_competition_processed)}개 항목")
    

    # 처리된 데이터가 없는 경우 에러 발생
    if not processed_data:
        raise ValueError("처리된 데이터가 없습니다. 파일 경로와 데이터를 확인해주세요.")
        
    _print_processing_results(processed_data)
    return processed_data

def _print_processing_results(data):
    """처리 결과를 출력하는 함수"""
    print(f"\n=== 전체 데이터 처리 결과 ===")
    print(f"총 처리된 항목 수: {len(data)}")
    print(f"FAQ 항목 수: {sum(1 for item in data if item['type'] == 'qa_content')}")
    print(f"PDF 항목 수: {sum(1 for item in data if item['type'] == 'pdf_content')}")
    print(f"CSV 항목 수: {sum(1 for item in data if item['type'] == 'csv_content')}")

class RAGChatbot:
    def __init__(self, data):
        """챗봇 초기화"""
        self.data = data
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self._initialize_chromadb()
    
    def _initialize_chromadb(self):
        """ChromaDB 초기화 및 데이터 임베딩"""
        try:
            self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name='sentence-transformers/all-MiniLM-L6-v2'
            )
            self._setup_collection()
        except Exception as e:
            print(f"ChromaDB 초기화 중 오류 발생: {str(e)}")
            raise

    def _setup_collection(self):
        """컬렉션 설정"""
        try:
            # 컬렉션 이름만 반환
            collection_names = self.chroma_client.list_collections()

            # "documents"라는 이름의 컬렉션이 있는지 확인
            collection_exists = "documents" in collection_names
            
            if collection_exists:
                # 기존 컬렉션 가져오기
                self.collection = self.chroma_client.get_collection("documents")
                print("기존 임베딩 데이터를 불러왔습니다.")
            else:
                print("새로운 임베딩을 시작합니다...")
                self.collection = self._create_new_collection()
        except Exception as e:
            print(f"컬렉션 설정 중 오류 발생: {str(e)}")
            raise

    def _get_existing_collection(self):
        """기존 컬렉션 가져오기"""
        return self.chroma_client.get_collection(
            name="documents",
            embedding_function=self.embedding_function
        )

    def _create_new_collection(self):
        """새 컬렉션 생성 및 데이터 임베딩"""
        collection = self.chroma_client.create_collection(
            name="documents",
            embedding_function=self.embedding_function
        )
        
        documents = []
        metadatas = []
        ids = []
        
        # 데이터 유효성 검사 및 처리
        for i, item in enumerate(self.data):
            try:
                if item['type'] == 'pdf_content':
                    
                    header = item['metadata'].get('Header 1', '')
                    document_text = f"{header}\n{item['content']}" if header else item['content']
                else:
                    document_text = item['content']
                
                # 문서 텍스트가 비어있지 않은지 확인
                if document_text and document_text.strip():
                    documents.append(document_text)
                    metadatas.append({
                        "title": item.get('title', ''),
                        "content_type": item.get('type', ''),
                        **{k: v for k, v in item.get('metadata', {}).items()}
                    })
                    ids.append(str(i))

            except Exception as e:
                print(f"데이터 처리 중 오류 발생 (항목 {i}): {str(e)}")
        
        if not documents:
            raise ValueError("임베딩할 유효한 문서가 없습니다.")
        
        # 메모리 문제를 방지하기 위해 배치 처리
        # print(documents)

        batch_size = 30
        for i in range(0, len(documents), batch_size):
            batch_end = min(i + batch_size, len(documents))
            try:
                print(f"Batch {i}-{batch_end} 추가 시작...")
                
                # 데이터 검증
                for idx, (doc, meta, doc_id) in enumerate(zip(documents[i:batch_end], metadatas[i:batch_end], ids[i:batch_end])):
                    assert isinstance(doc, str) and doc.strip(), f"유효하지 않은 문서 ID: {doc_id}"
                    assert isinstance(meta, dict), f"유효하지 않은 메타데이터: {doc_id}"
                    assert isinstance(doc_id, str) and doc_id.strip(), f"유효하지 않은 ID: {doc_id}"
                print(i, batch_end)
                # 데이터 추가
                collection.add(
                    documents=documents[i:batch_end],
                    metadatas=metadatas[i:batch_end],
                    ids=ids[i:batch_end]
                )

                print(f"임베딩 진행 중... {batch_end}/{len(documents)}")
                print(f"Batch {i}-{batch_end} 추가 완료. 현재 컬렉션 문서 수: {collection.count()}")
                
                # 메모리 정리
                gc.collect()
            except Exception as e:
                print(f"Batch {i}-{batch_end} 처리 중 오류 발생: {str(e)}")
                continue

        print("임베딩 작업이 완료되었습니다.")
        return collection



    def find_most_similar_sections(self, query, top_k=500, title_weight=1.5, region_weight=1.2, competition_rate_weight=1.2, source_type_weight=2.0, start_weight=1.6):
        """
        유사 문서 검색 - '오늘', '가장 최근' 기준 및 경쟁률 데이터를 포함한 가중치 처리
        :param query: 검색할 쿼리
        :param top_k: 반환할 유사 문서 개수
        :param title_weight: 'title' 필드에 가중치를 적용할 값
        :param region_weight: 'region' 필드에 가중치를 적용할 값
        :param competition_rate_weight: 'competition_rate' 필드에 가중치를 적용할 값
        :param source_type_weight: 'source_type'이 unranked_csv 또는 apt_csv일 때 가중치를 적용할 값
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            similar_sections = []
            today = datetime.now()

            # '오늘', '가장 최근' 쿼리 여부 확인
            is_recent_query = any(keyword in query for keyword in ['오늘', '가장 최근', '최근'])
            is_day_query = any(keyword in query for keyword in ['청약일', '청약신청일'])

            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                # 기본 거리 계산
                base_distance = results['distances'][0][i]
                adjusted_distance = base_distance

                # 타이틀 유사도 계산
                if 'apartment_name' in metadata:
                    title = metadata['apartment_name'].lower()
                    query_lower = query.lower()

                    if query_lower in title:  # 정확 매칭 또는 포함 여부 확인
                        if query_lower == title:  # 완전 일치
                            adjusted_distance = 0.001  # 가장 높은 우선순위
                        else:  # 부분 일치
                            adjusted_distance /= title_weight

                # 지역 가중치
                if 'region' in metadata and query.lower() in metadata['region'].lower():
                    adjusted_distance /= region_weight

                # 날짜 관련 가중치
                if is_day_query and 'start_date' in metadata:
                    adjusted_distance /= start_weight

                # '오늘', '최근' 기준 추가
                if is_recent_query and 'start_date' in metadata:
                    try:
                        start_date = datetime.fromisoformat(metadata['start_date'])
                        days_difference = abs((today - start_date).days)
                        adjusted_distance /= (1 + 1 / (1 + days_difference))
                    except ValueError:
                        pass

                # 청약 신청 가능 여부 필터링
                start_date_str = metadata.get('start_date')
                end_date_str = metadata.get('end_date')

                try:
                    start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
                    end_date = datetime.fromisoformat(end_date_str) if end_date_str else None

                    # 청약 신청 가능한 항목만 추가
                    is_active = start_date and end_date and start_date <= today <= end_date
                    if is_active or not is_recent_query:
                        section_data = {
                            'title': metadata.get('title', '정보 없음'),
                            'content': doc,
                            'metadata': {k: v for k, v in metadata.items() if k not in ['title']},
                            'distance': adjusted_distance
                        }
                        similar_sections.append(section_data)
                except ValueError:
                    pass

            # 거리 기준으로 정렬 (낮을수록 유사)
            similar_sections.sort(key=lambda x: x['distance'])

            return similar_sections[:30]
        except Exception as e:
            print(f"유사 문서 검색 중 오류 발생: {str(e)}")
            raise


    def _prepare_context(self, sections):
        """컨텍스트 준비"""
        try:
            context = "관련 문서 정보:\n"
            for section in sections:
                similarity = 1 / (1 + section['distance'])
                if similarity > 0.3:  # 유사도 임계값
                    if section['metadata'].get('content_type') == 'qa_content':
                        context += f"FAQ 답변:\n{section['content']}\n\n"
                    elif section['metadata'].get('source_type') == 'apt_csv':
                        context += f"문서: {section['title']}\n"

                        # CSV 데이터 필드 매핑
                        metadata = section.get('metadata', {})
                        region = metadata.get('region', '정보 없음')
                        apartment_name = metadata.get('apartment_name', '정보 없음')
                        housing_type = metadata.get('housing_type', '정보 없음')
                        sale_or_lease = metadata.get('sale_or_lease', '정보 없음')
                        contact = metadata.get('contact', '정보 없음')
                        start_date = metadata.get('start_date', '정보 없음')
                        end_date = metadata.get('end_date', '정보 없음')
                        result_date = metadata.get('result_date', '정보 없음')

                        print(apartment_name)
                        
                        # 데이터 내용을 구성
                        context += (
                            f"주택명: {apartment_name}\n"
                            f"지역: {region}\n"
                            f"주택 유형: {housing_type}\n"
                            f"분양/임대: {sale_or_lease}\n"
                            f"연락처: {contact}\n"
                            f"청약 접수 시작: {start_date}\n"
                            f"청약 접수 종료: {end_date}\n"
                            f"결과 발표: {result_date}\n"
                            f"내용: {section['content']}\n\n"
                        )

                    elif section['metadata'].get('source_type') == 'unranked_csv':
                        context += f"문서: {section['title']}\n"

                        # CSV 데이터 필드 매핑
                        metadata = section.get('metadata', {})
                        apartment_name = metadata.get('apartment_name', '정보 없음')
                        region = metadata.get('region', '정보 없음')
                        subscription_type = metadata.get('subscription_type', '정보 없음')
                        start_date = metadata.get('start_date', '정보 없음')
                        end_date = metadata.get('end_date', '정보 없음')
                        result_date = metadata.get('result_date', '정보 없음')

                        # 데이터 내용을 구성
                        context += (
                            f"지역: {region}\n"
                            f"주택명: {apartment_name}\n"
                            f"주택 유형: {subscription_type}\n"
                            f"청약 접수 시작: {start_date}\n"
                            f"청약 접수 종료: {end_date}\n"
                            f"결과 발표: {result_date}\n"
                            f"내용: {section['content']}\n\n"
                        )

                    elif section['metadata'].get('source_type') == 'apt_competition_csv':
                        context += f"문서: {section['title']}\n"

                        # CSV 데이터 필드 매핑
                        metadata = section.get('metadata', {})
                        region = metadata.get('region', '정보 없음')
                        apartment_name = metadata.get('apartment_name', '정보 없음')
                        competition_rate = metadata.get('competition_rate', '정보 없음')
                        house_type = metadata.get('house_type', '정보 없음')

                        # 데이터 내용을 구성
                        context += (
                            f"주택명: {apartment_name}\n"
                            f"지역: {region}\n"
                            f"주택 유형: {house_type}\n"
                            f"경쟁률: {competition_rate}\n"
                            f"내용: {section['content']}\n\n"
                        )



            return context
        except Exception as e:
            print(f"컨텍스트 준비 중 오류 발생: {str(e)}")
            raise

    def _create_prompt(self, query, context):
        """프롬프트 생성"""
        return f"""아래는 한국 주택 청약과 관련된 문서에서 추출한 관련 정보와 사용자의 질문입니다. 
주어진 정보를 참고하여 사용자의 질문에 친절하게 답변해주세요.


모든 문장의 마지막에는 '~용'을 붙입니다
예시: '안녕하세용', '반가워용', '고마워용'
존댓말을 사용하되, 친근하고 부드러운 어조를 유지합니다.
예시: '도와드릴게용', '말씀해주세용'
'이에요/예요' 대신 '이에용/예용'을 사용합니다.
예시: '그건 어려울 것 같아용', '제가 할 수 있는 일이에용'
질문할 때는 '~용?'으로 끝냅니다.
예시: '무엇을 도와드릴까용?', '어떠셨나용?'

이에요. 혹은 요. 로 끝나는 문장 뒤에 용은 붙일 필요 없어.

## General
- Answer in Korean. However, please use English for jargon and important keywords, or write "Korean(English)".
- Always answer in markdown format. I mostly use markdown headings 2(##) and 4(####), with body content in bullets.
- Follow the commands step-by-step.
- Don't make mistakes.
- Never omit. show me everything, don't skip anything. Always describe the entire item and its data.
- Include footnotes in Obsidian(markdown) format
- Keep responses unique and free of repetition. 
- Never suggest seeking information from elsewhere.
- Always focus on the key points in my questions to determine my intent. 
- Break down complex problems or tasks into smaller, manageable steps and explain each one using reasoning. 
- Provide multiple perspectives or solutions. 
- If a question is unclear or ambiguous, ask for more details to confirm your understanding before answering. 
- Take a deep breath, and work on this step by step.
{context}

사용자 질문: {query}

답변:"""

    def _get_gpt_response(self, prompt):
        """GPT API를 통한 응답 생성"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # 수정된 모델명
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the given context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"GPT 응답 생성 중 오류 발생: {str(e)}")
            raise

    def generate_response(self, query):
        """응답 생성"""
        try:
            similar_sections = self.find_most_similar_sections(query)
            context = self._prepare_context(similar_sections)
            prompt = self._create_prompt(query, context)
            
            return self._get_gpt_response(prompt)
        except Exception as e:
            print(f"응답 생성 중 오류 발생: {str(e)}")
            raise

def rag_chat(chat_input):
    """채팅 인터페이스 함수"""
    try:
        # 실제 파일 경로 설정
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_paths = [
            os.path.join(base_dir, 'data', 'FAQ_Crawling.json'),
            # os.path.join(base_dir, 'data', 'pdf_to_parsing_1.json')
        ]

        
        # 모든 데이터 로드
        data = load_all_data(json_paths)
        chatbot = RAGChatbot(data)
        
        return chatbot.generate_response(chat_input)
        
    except Exception as e:
        error_message = f"오류가 발생했습니다: {str(e)}"
        print(error_message)
        return error_message

if __name__ == "__main__":
    try:
        # 실제 파일 경로 설정
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_paths = [
            # os.path.join(base_dir, 'data', 'FAQ_Crawling.json'),
            # os.path.join(base_dir, 'data', 'pdf_to_parsing_1.json')
        ]


        # 모든 데이터 로드
        data = load_all_data(json_paths)
        chatbot = RAGChatbot(data)
        
        print("챗봇이 준비되었습니다. 종료하려면 'quit'를 입력하세요.")
        while True:
            user_input = input("\n질문을 입력하세요: ")
            if user_input.lower() == 'quit':
                break
            
            try:
                response = chatbot.generate_response(user_input)
                print(f"\n질문: {user_input}")
                print(f"\n답변: {response}")
            except Exception as e:
                print(f"응답 생성 중 오류가 발생했습니다: {str(e)}")
                
    except Exception as e:
        print(f"초기화 중 오류가 발생했습니다: {str(e)}")
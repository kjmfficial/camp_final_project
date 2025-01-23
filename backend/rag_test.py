import json
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions

import os
from dotenv import load_dotenv

from DB.db_mysql import select_json

load_dotenv()

# mysql 연결 URI
OPEN_AI = os.environ.get('OPEN_AI')

 



def load_pdf_data(file_paths):
    """
    여러 형식의 JSON 파일을 로드하고 처리하는 함수
    """
    processed_data = []
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 첫 번째 형식: PDF 파싱된 데이터
                if isinstance(data, list) and data and isinstance(data[0], dict) and 'title' in data[0]:
                    for doc in data:
                        title = doc.get('title', '').strip()
                        sections = doc.get('sections', [])
                        
                        if title and sections:
                            for section in sections:
                                content = section.get('content', '').strip()
                                metadata = section.get('metadata', {})
                                if content:
                                    processed_data.append({
                                        'title': title,
                                        'content': content,
                                        'metadata': metadata,
                                        'type': 'pdf_content'
                                    })
                
                # 두 번째 형식: Q&A 형식 데이터
                elif isinstance(data, list) and data and isinstance(data[0], dict) and 'question' in data[0]:
                    for item in data:
                        question = item.get('question', '').strip()
                        answer = item.get('answer', '').strip()
                        if question and answer:
                            processed_data.append({
                                'title': 'FAQ',
                                'content': f"Q: {question}\nA: {answer}",
                                'metadata': {
                                    'question': question,
                                    'type': 'faq'
                                },
                                'type': 'qa_content'
                            })
                
        except FileNotFoundError:
            print(f"Warning: '{file_path}' 파일을 찾을 수 없습니다.")
        except json.JSONDecodeError:
            print(f"Warning: '{file_path}'가 유효하지 않은 JSON 형식입니다.")
    
    if not processed_data:
        raise ValueError("처리할 수 있는 데이터가 없습니다.")
    
    return processed_data

class RAGChatbot:
    def __init__(self, data):
        self.data = data
        self.openai_client = OpenAI(api_key=OPEN_AI)
        
        # Initialize ChromaDB with persistent directory
        self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db_1")
        
        # Create or get collection with sentence transformer embedding function
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name='sentence-transformers/distiluse-base-multilingual-cased-v2'
        )
        
        # Get list of existing collections
        existing_collections = self.chroma_client.list_collections()
        collection_exists = "documents" in existing_collections  # Check if "documents" exists
        
        if collection_exists:
            # Use existing collection
            self.collection = self.chroma_client.get_collection(
                name="documents",
                embedding_function=sentence_transformer_ef
            )
            print("기존 임베딩 데이터를 불러왔습니다.")
            
        else:
            # Collection doesn't exist, create new one
            print("새로운 임베딩을 시작합니다...")
            self.collection = self.chroma_client.create_collection(
                name="documents",
                embedding_function=sentence_transformer_ef
            )
            
            # Add documents to collection
            documents = []
            metadatas = []
            ids = []
            
            for i, item in enumerate(self.data):
                if item['type'] == 'pdf_content':
                    header = item['metadata'].get('Header 1', '')
                    document_text = f"{header}\n{item['content']}" if header else item['content']
                else:
                    document_text = item['content']
                
                documents.append(document_text)
                metadatas.append({
                    "title": item['title'],
                    "content_type": item['type'],
                    **item['metadata']
                })
                ids.append(str(i))
                
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print("임베딩이 완료되었습니다.")
    
    def find_most_similar_sections(self, query, top_k=3):
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        similar_sections = []
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            section_data = {
                'title': metadata['title'],
                'content': doc,
                'metadata': {k: v for k, v in metadata.items() if k not in ['title']},
                'distance': results['distances'][0][i]
            }
            similar_sections.append(section_data)
            
        return similar_sections
    
    def generate_response(self, query):
        similar_sections = self.find_most_similar_sections(query)
        
        context = "관련 문서 정보:\n"
        for section in similar_sections:
            similarity = 1 / (1 + section['distance'])
            if similarity > 0.3:
                if section['metadata'].get('content_type') == 'qa_content':
                    context += f"FAQ 답변:\n{section['content']}\n\n"
                else:
                    context += f"문서: {section['title']}\n"
                    if section['metadata'].get('Header 1'):
                        context += f"섹션: {section['metadata']['Header 1']}\n"
                    context += f"내용: {section['content']}\n\n"

        prompt = f"""아래는 한국 주택 청약과 관련된 문서에서 추출한 관련 정보와 사용자의 질문입니다. 
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

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the given context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    

def rag_chat(chat):
    try:

        apt_base=select_json("apt_housing_application_basic_info")
        apt_competiton=select_json("apt_housing_competition_rate")
        un_base=select_json("unranked_housing_application_basic_info")
        un_competion_1=select_json("unranked_housing_competition_rate_1")
        un_competion_2=select_json("unranked_housing_competition_rate_2")

        # 여러 JSON 파일 로드
        file_paths = [
            # './data/pdf_to_parsing.json',
            
            './data/FAQ_Crawling.json',
            './data/result.json',


            # './data/test_result_1.json',
            # './data/test_result_2.json',
            # './Cheongyak/data/processed_output.json'
        ]



        data = load_pdf_data(file_paths)

        
        # 챗봇 초기화
        chatbot = RAGChatbot(data)
        print("챗봇이 준비되었습니다. 종료하려면 'quit'를 입력하세요.")
        while True:
            user_input = chat
            if user_input.lower() == 'quit':
                break
                
            try:
                response = chatbot.generate_response(user_input)
                return response
            except Exception as e:
                print(f"응답 생성 중 오류가 발생했습니다: {str(e)}")
                
    except Exception as e:
        print(f"초기화 중 오류가 발생했습니다: {str(e)}")



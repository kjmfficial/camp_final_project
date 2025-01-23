import os
import json
import boto3
import nest_asyncio
from dotenv import load_dotenv
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader

load_dotenv()
nest_asyncio.apply()

# AWS S3 클라이언트 설정
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

# LlamaParse 설정
parser = LlamaParse(
    api_key=os.getenv('LLAMA_CLOUD_API_KEY'),  # API 키 추가
    result_type="markdown",
    num_workers=8,
    verbose=True,
    language="ko",
)

file_extraction = {".pdf": parser}

def download_from_s3(bucket_name, s3_key, local_path):
    """S3에서 파일을 다운로드합니다."""
    try:
        s3.download_file(bucket_name, s3_key, local_path)
        return True
    except Exception as e:
        print(f"Error downloading from S3: {e}")
        return False

def extract_pdf_content(pdf_path):
    try:
        documents = SimpleDirectoryReader(
            input_files=[pdf_path],
            file_extractor=file_extraction,
        ).load_data()
        
        full_content = " ".join([doc.to_langchain_format().page_content for doc in documents])
        return full_content
    
    except Exception as e:
        print(f"Error parsing {pdf_path}: {e}")
        return None

try:
    # S3 버킷 정보
    bucket_name = "lgu-final"
    s3_prefixes = ["apt/", "unranked/"]  # 두 개의 경로 설정
    
    # 임시 로컬 디렉토리 생성
    temp_directory = "/back/data/temp_pdfs"
    os.makedirs(temp_directory, exist_ok=True)
    
    json_data = []
    
    # 각 경로별로 처리
    for s3_prefix in s3_prefixes:
        print(f"Processing files in {s3_prefix}...")
        
        # S3 버킷 내 PDF 파일 리스트 가져오기
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_prefix)
        
        # 각 PDF 파일 처리
        for obj in response.get('Contents', []):
            if obj['Key'].endswith('.pdf'):
                # 로컬 파일 경로 설정
                pdf_filename = os.path.basename(obj['Key'])
                local_pdf_path = os.path.join(temp_directory, pdf_filename)
                
                print(f"Processing {pdf_filename}...")
                
                # S3에서 파일 다운로드
                if download_from_s3(bucket_name, obj['Key'], local_pdf_path):
                    # PDF 내용 추출
                    full_content = extract_pdf_content(local_pdf_path)
                    
                    # 내용 추출에 성공한 경우에만 JSON에 추가
                    if full_content:
                        json_data.append({
                            'source': s3_prefix,  # 파일 출처 추가
                            'title': pdf_filename,
                            'content': full_content
                        })
                    
                    # 임시 파일 삭제
                    os.remove(local_pdf_path)
    
    # JSON 파일로 저장
    output_file = "result.json"
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

    print(f"\nJSON 파일이 저장되었습니다: {output_file}")
    print(f"총 {len(json_data)}개의 PDF 파일이 처리되었습니다.")

    # 임시 디렉토리 삭제
    os.rmdir(temp_directory)

except Exception as e:
    print(f"Main Error: {e}")
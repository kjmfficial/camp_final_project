import boto3
from dotenv import load_dotenv
import os
import io
load_dotenv()

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')
BUCKET_NAME = os.environ.get("BUCKET_NAME")

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)

def s3_upload(data, file_path):
    try:
        if not data:
            raise ValueError("업로드할 데이터가 None입니다.")
        if not file_path:
            raise ValueError("S3 파일 경로가 None입니다.")
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("업로드할 데이터는 bytes 타입이어야 합니다.")

        # io.BytesIO로 바이너리 데이터를 파일처럼 처리
        with io.BytesIO(data) as file_obj:
            s3_client.upload_fileobj(file_obj, BUCKET_NAME, file_path)
        print(f"S3 업로드 성공: s3://{BUCKET_NAME}/{file_path}")
    except Exception as e:
        print(f"S3 업로드 실패: {e}")

def s3_delete_all():
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)

        # 버킷 비어있으면 실행 x
        if 'Contents' not in response:
            print("Bucket is already empty.")
            return

        # 모든 객체 삭제
        objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
        delete_response = s3_client.delete_objects(
            Bucket=BUCKET_NAME,
            Delete={
                'Objects': objects_to_delete,
                'Quiet': True
            }
        )

        # 삭제 성공 메시지 출력
        print(f"Deleted {len(objects_to_delete)} objects from bucket '{BUCKET_NAME}'.")

    except Exception as e:
        print(f"An error occurred: {e}")
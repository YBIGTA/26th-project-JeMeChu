import os
import glob
import sys
from argparse import ArgumentParser
from typing import Dict, Type
from review_analysis.preprocessing.base_processor import BaseDataProcessor
from review_analysis.preprocessing.NaverProcessor import NaverProcessor 
# from preprocessing.GoogleProcessor import GoogleProcessor  # 나중에 더 추가

# 1. 지원하는 리뷰 사이트별 전처리 클래스 매핑
PREPROCESS_CLASSES: Dict[str, Type[BaseDataProcessor]] = {
    "reviews_navertemp": NaverProcessor,  # 네이버 리뷰 추가 가능
    # "reviews_google": GoogleProcessor  # 구글 리뷰 추가 가능
    # 추가적인 사이트가 있으면 여기에 key-value 형식으로 추가
}

# 2. 리뷰 데이터 파일 자동 탐색
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 절대 경로
DATABASE_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "database")) # str임
if not os.path.exists(DATABASE_PATH):
    print(f"database dir not found: {DATABASE_PATH}")

REVIEW_COLLECTIONS = glob.glob(os.path.join(DATABASE_PATH, "reviews_*.csv"))
if not REVIEW_COLLECTIONS:
    print(f"no csv files found in database dir")
else:
    print("main.py 실행")

# 3. Argument Parser 생성 -> 명령어임
def create_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Preprocess and extract features from review datasets.")
    
    # 원하는 경로에 저장가능 -o
    # python main.py -c reviews_navertemp -o ../output/
    parser.add_argument(
        '-o', '--output_dir', type=str, required=False, default="../../database",
        help="Output file directory. Example: ../../database"
    )
    
    # 특정 reviews_*.csv 파일만 
    # python main.py -c reviews_navertemp
    parser.add_argument(
        '-c', '--preprocessor', type=str, required=False, choices=PREPROCESS_CLASSES.keys(),
        help=f"Choose a specific processor to use. Available choices: {', '.join(PREPROCESS_CLASSES.keys())}"
    )
    
    # 모든 reviews_*.csv 한꺼번에 
    # python main.py -a
    parser.add_argument(
        '-a', '--all', action='store_true',
        help="Run all data preprocessors. Default is False."
    )
    
    return parser

# 4. 전처리 실행 함수
def run_preprocessing(preprocessor_name: str, csv_file: str, output_dir: str):
    """
    주어진 CSV 파일을 해당 전처리 클래스로 처리하는 함수
    """
    if preprocessor_name in PREPROCESS_CLASSES:
        print(f"Processing {csv_file} with {preprocessor_name}...")

        # 클래스 인스턴스 생성 및 실행
        preprocessor_class = PREPROCESS_CLASSES[preprocessor_name]
        preprocessor = preprocessor_class(csv_file, output_dir)
        
        preprocessor.preprocess()
        preprocessor.feature_engineering()
        preprocessor.save_to_database()

        print(f"Completed: {csv_file} -> Saved to {output_dir}\n")
    else:
        print(f"Error: No matching processor found for {preprocessor_name}")

# 5. 메인 실행 로직
if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # 특정 리뷰 사이트만 실행하는 경우
    if args.preprocessor:
        csv_file = os.path.join("..", "..", "database", f"{args.preprocessor}.csv")
        if os.path.exists(csv_file):
            run_preprocessing(args.preprocessor, csv_file, args.output_dir)
        else:
            print(f"Error: {csv_file} not found. Please check the file name.")
            sys.exit(1)

    # 모든 리뷰 CSV 파일을 처리하는 경우
    elif args.all:
        for csv_file in REVIEW_COLLECTIONS:
            base_name = os.path.splitext(os.path.basename(csv_file))[0]
            run_preprocessing(base_name, csv_file, args.output_dir)

    # 옵션을 지정하지 않은 경우
    else:
        print("Please specify a preprocessor using '-c <processor>' or run all using '-a'.")
        parser.print_help()
        sys.exit(1)

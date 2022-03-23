# HongCrawler
------------------------
홍준표 국회의원의 [청년의 꿈](https://theyouthdream.com/) 게시글을 가져오는 크롤러입니다.

개인 연구용으로 제작했으며, 크롤러는 사이트 중 [답변완료](https://theyouthdream.com/qna/category/273) 페이지의 질문과 홍준표 의원의 답변을 가져옵니다.

### Data(csv)
- 글 제목
- 작성자
- 날짜
- 질문(작성자)
- 답변(홍준표 의원)

### Install
코드 받기
    
    git clone https://github.com/DaewonSeo/HongCrawler.git

라이브러리 설치
    
    pip install -r requirements.txt
파이썬 파일 실행
    
    python crawler.py

		

	

### Library
- requests
- beautiflsoup4
- lxml
- concurrent




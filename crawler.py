import csv
import logging
import os
import time
import requests
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from tqdm import tqdm


HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\
            AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/99.0.4844.51 Safari/537.36'
}

DATA_DIR = 'data'
CSV_FILE = os.path.join(DATA_DIR, 'dreamofyouth.csv')
logging.basicConfig(level=logging.INFO)

def run():
    try:
        os.mkdir(DATA_DIR)
    except FileExistsError:
        pass
    
    
    page = 1
    total = get_latest_post_id()
    recent = get_latest_saved_post_id()
    post_list = []
    while True:
        url_list = get_url_and_post_id(page, recent)
        # 가져올 게시글이 존재할 경우 프로그램 동작
        if url_list is not None:
            with ThreadPoolExecutor(max_workers=2) as exe:
                for post in exe.map(fetch_post, url_list):
                    if post is None:
                        continue
                    post_list.append(post)
                    logging.info(f'전체 {total} / {total - post["id"]} | {post["id"]} : {post["title"]} >> 스크랩 완료')
            page += 1
            time.sleep(5)
        # 가져올 게시글이 없는 경우 프로그램 종료
        else:
            break
    
    saved_post = len(post_list) # 저장될 게시글의 개수

    ## 스택을 활용해 가져온 순서의 반대인 오름차순으로 CSV File 저장
    for _ in tqdm(range(saved_post)):
        save_post(post_list.pop())
    logging.info(f'총 {saved_post}개의 게시글이 저장완료 되었습니다.')


def get_latest_post_id() -> int:
    """답변완료 상태의 가장 최신의 글 id 가져오기"""
    url = 'https://theyouthdream.com/qna/category/273'
    html = requests.get(url, headers=HEADERS).text
    soup = BeautifulSoup(html, 'lxml')
    href = soup.select_one('.app-board-section tbody > tr:nth-child(6) td.no').text
    post_id = int(href.strip())
    return post_id


def get_url_and_post_id(page_num: int, recent: int) -> List[Tuple] or None:
    """페이지별 post id 게시글 링크 가져오기"""
    url = f'https://theyouthdream.com/qna/category/273?page={page_num}'
    html = requests.get(url, headers=HEADERS).text
    soup = BeautifulSoup(html, 'lxml')
    url_list = []
    try:
        post_id = soup.select('.app-board-section tbody > tr > td.no')
        top_post_id = int(post_id[0].text.strip())
        if top_post_id > recent:
        # 공지사항 글을 제외한 해당 페이지의 모든 post url 가져오기 -> 최근 공지사항 증가로 인덱스 번호 변경
            urls = soup.select('.app-board-section tbody > tr > td.title > a')[5:]
            for p, u in zip(post_id, urls):
                url_list.append((int(p.text.strip()), u['href']))
            return url_list
        else:
            print('새로운 데이터가 없으므로, 파싱을 종료합니다.')
            return None

    except (AttributeError, IndexError):
        print('더이상 데이터가 존재하지 않습니다.')
        return None


def get_latest_saved_post_id() -> int:
    """저장된 CSV 파일에서 최신 글 id 가져오기"""
    if not os.path.isfile(CSV_FILE):
        return 0
    
    with open(CSV_FILE, 'r') as f:
        # 저장된 파일 제일 마지막 줄 접근
        last_line = f.readlines()[-1]
        # 마지막 줄 첫번째 인자(id)값 가져오기
        post_id = int(last_line.split(',')[0])
        return post_id
        

def fetch_post(url_list: Tuple) -> Dict[str, any] or None:
    url = f'https://theyouthdream.com{url_list[1]}'
    try:
        html = fetch_html(url)
    except ValueError:
        return None

    soup = BeautifulSoup(html, "lxml")
    title = query(soup, '.app-board-container h1')
    datetime = query(soup, '.app-profile-body > div > el-tooltip > div')
    question = query(soup, '.app-article-content.app-clearfix div.rhymix_content.xe_content')
    answer = query(soup, '#app-board-comment-list div.rhymix_content.xe_content')

    return {
        'id': url_list[0],
        'title': title,
        'datetime': datetime,
        'question': '' if question is None else clean_text(question.rstrip()),
        'answer': '' if answer is None else clean_text(answer.rstrip())
    }


def save_post(post: Dict[str, any]) -> None:
    """게시글을 CSV 파일로 작성"""
    cols = [
        'id', 'title', 'datetime', 'question', 'answer'
    ]
    # 파일이 없을 경우 새로 만들고 컬럼 저장
    if not os.path.isfile(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f, delimiter='///')
            w.writerow(cols)
    
    # 파일이 있으면 'a'로 열고 제일 마지막 줄부터 저장 시작
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter='///')
        w.writerow(post[col] for col in cols)


def fetch_html(url: str) -> str:
    """웹에서 가져온 html 결과 반환"""
    try:
        req = requests.get(url, headers=HEADERS)
        if req.status_code != 200:
            raise ValueError(f'invalid status code : {req.status_code}')
        html = req.text
        return html
    except requests.HTTPError as e:
        raise e
    
    except requests.ConnectionError:
        logging.info('30초간 정지 후 재가동합니다.')
        time.sleep(30)
        print(fetch_html(url))


def query(soup: BeautifulSoup, selector: str) -> str:
    try:
        return soup.select_one(selector).text
    except AttributeError:
        return None


def clean_text(text: str) -> str:
    return text.replace("\n", "").replace("\t", "")


if __name__ == "__main__":
    run()
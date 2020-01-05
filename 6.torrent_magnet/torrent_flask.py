import requests
from bs4 import BeautifulSoup
import re

from flask import Flask
# HTML 페이지를 렌더링 하기 위한 라이브러리
from flask import render_template
# HTML 페이지 FORM 에서 넘어온 데이터를 처리 하기 위한 라이브러리
from flask import request

app = Flask(__name__)


def search_google(keyword, start_page, end_page=None):
    '''구글에서 검색어를 검색해 마그넷 주소를 파싱하는 함수
    Args:
        keyword (str) : 검색어
    
    Returns:
        list : 마그넷주소가 있는 결과 리스트(제목, 마그넷주소)
    '''
    
    # 최종 결과를 리턴
    results = []

    # 검색어 뒤에 torrent 가 없으면 붙임
    if keyword.find("+torrent") < 0:
        keyword += "+torrent"

    # 구글 검색 URL 변수 설정
    url = "https://www.google.co.kr/search?q={0}&oq={0}&start={1}".format(keyword, start_page)
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"})
    bs = BeautifulSoup(r.text, "lxml")
    
    print(url, "분석중....")
    
    # end_page 가 None 이면 첫번째 페이지라고 가정
    if end_page is None:
        # 검색결과 Selector
        counts = bs.select("div#resultStats")[0].text
        
        # 검색결과 약 779,000개 (0.24초) 
        # 에서 779000 을 남기고 모두 제거
        counts = counts.replace("검색결과", "").replace("약", "").replace("개", "").replace(",", "").split("(")[0].strip()
        
        # 페이지당 10개씩 출력
        end_page = int(counts) / 10
        
        # 2 페이지 까지만 검색하게 함
        if end_page > 20:
            end_page = 20

    # 검색결과의 링크 주소 선택
    links = bs.select("div.g > div > div.rc > div.r > a")
    for a in links:
        # a 링크에 href 속성이 없으면 계속 반복
        if not a.has_attr('href'):
            continue

        try:
            # href 속성이 있다면 해당 페이지를 접속
            href = a["href"]
            text = a.select("h3")
            title = text[0].text

            # 링크 주소를 다시 접속
            r = requests.get(href)
            bs = BeautifulSoup(r.text, "lxml")
            
            # 페이지에서 magnet:?xt= 로 시작하는 모든 링크를 추출
            magnets = bs.find_all("a", href=re.compile(r'magnet:\?xt=*'))

            # magnet:?xt= 로 추출된 갯수가 0보다 크면
            if len(magnets) > 0:
                # A 태그에서 실제 링크주소(href) 를 추출
                magnet = magnets[0]["href"]
                # 최종 결과 리스트에 추가
                results.append({"title": title, "magnet": magnet})
        except:
            continue

    # 현재 페이지가 end_page 보다 작으면 페이징
    if start_page < end_page:
        start_page += 10
        # 재귀함수 호출하고 결과를 results 에 extend 시킴
        results.extend(search_google(keyword, start_page, end_page))
    
    # 최종 결과 리턴
    return results


# 루트 페이지 http://localhost:9988 접속시 호출되는 부분
@app.route("/", methods=["GET", "POST"])
def index():
    # HTML에서 검색을 했다면 form 에 keyword 값이 들어와야 함
    # HTML 에서 input type="text" 의 name 이 keyword 
    if "keyword" in request.form:
        # 키워드값을 구해 keyword 변수에 저장
        keyword = request.form["keyword"]
        # 키워드값으로 기존에 작성된 search_google 함수 호출
        magnets = search_google(keyword, 0)
    else:
        # 키워드가 없으면 최종 결과리스트에 빈리스트 설정
        magnets = []

    # 검색된 결과가 있다면
    if len(magnets) > 0:
        # index.html 을 렌더링 하는데 magnets 리스트를 magnets 라는 이름으로 넘김
        # 딕셔너리를 넘김
        # 아스트릭(*) 문자가 2개인건 magnets를 가변인지(키워드인자)로 넘기기 때문 
        # render_template 함수의 정해진 문법임
        return render_template("index.html", **{"magnets": magnets})
    else:
        return render_template("index.html")
    
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9988, debug=True)
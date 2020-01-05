# 크롤링에 필요한 라이브러리
import requests
from bs4 import BeautifulSoup
import re # 정규식 사용을 위한 라이브러리


def search_google(keyword, start_page, end_page=None):
    '''구글에서 검색어를 검색해 마그넷 주소를 파싱하는 함수
    Args:
        keyword (str) : 검색어
    
    Returns:
        list : 마그넷주소가 있는 결과 리스트(제목, 마그넷주소)
    '''
    
    # 최종 결과를 리턴할 리스트 변수
    results = []

    # 검색어 뒤에 torrent 가 없으면 붙입니다.
    if keyword.find("+torrent") < 0:
        keyword += "+torrent"

    # 구글 검색 URL 변수 설정
    url = "https://www.google.co.kr/search?q={0}&oq={0}&start={1}".format(keyword, start_page)
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"})
    bs = BeautifulSoup(r.text, "lxml")
    
    # 화면에 안내 출력
    print(url, "분석중....")
    
    # end_page 가 None 이면 첫번째 페이지라고 가정
    if end_page is None:
        # 검색결과 Selector
        counts = bs.select("div#resultStats")[0].text
        
        # 검색결과 약 779,000개 (0.24초) 
        # 에서 779000 을 남기고 모두 제거
        counts = counts.replace("검색결과", "").replace("약", "").replace("개", "").replace(",", "").split("(")[0].strip()
        
        # 구글은 페이지당 10개씩 출력
        end_page = int(counts) / 10
        
        # 2 페이지 까지만 검색하게 함
        if end_page > 20:
            end_page = 20

    # 개발자도구를 참고하여 검색결과의 링크 주소까지 선택하는 선택자를 찾을 수 있습니다.
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
                results.append((title, magnet))
        except:
            continue

    # 현재 페이지가 end_page 보다 작으면 페이징
    if start_page < end_page:
        start_page += 10
        # 재귀함수 호출하고 결과를 results 에 extend 시킴
        results.extend(search_google(keyword, start_page, end_page))
    
    # 최종 결과 리턴
    return results


# 검색어
keyword = "리눅스"
results = search_google(keyword, 0)

for r in results:
    print(r)
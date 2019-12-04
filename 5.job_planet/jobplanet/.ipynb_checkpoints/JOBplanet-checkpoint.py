"""
1. target_dir 아래 폴더에 쪼갠 csv 파일들을 위치시킨다.
2. cmd 창을 열어 JOBplanet.py를 실행시킨다.
3. 폴더 번호를 지정하면 해당 폴더에 있는 모든 csv파일을 담당하게 된다.
4. 결과물은 completed_dir에 sqlite db파일 하나로 저장된다. 즉, db1개 파일 > folder_n 테이블 > 리뷰들로 저장된다.
5. db 파일은 dbeaver 등으로 열어볼 수 있다.
* cmd창을 여러개 띄워 돌리고 싶다면 target_dir 아래에 폴더를 추가 생성해도 괜찮지만, 5개로도 충분할 것으로 보인다.

* 주의
프로그램 구동 중에는 target_dir 파일 안에 csv 파일을 추가하면 아니 된다!
"""
from settings import *    # 이 파일은 settings.py에 의존성을 가짐.
import csv  # pandas를 쓰지 않아 메모리 절약.
import sqlite3

#----- 시작
print(__doc__)
print("\n\n\n\n")

#-- 제반작업
# 현재 프로그램이 담당할 폴더 설정...
target_dir = os.path.join(os.getcwd(), "target_dir")    # target_dir 까지의 full 경로
print("#--- 현재 프로그램이 가동될 폴더를 선택하시오: ")
print(os.listdir(target_dir))

dir_num = int(input(">> "))        # dir_num번 폴더 설정값을 받는다
folder_dir = os.path.join(target_dir, os.listdir(target_dir)[dir_num])     # dir_num번 폴더 전체 경로
print("\n#--- 선택한 폴더 내에 위치한 파일 목록들을 확인한다... ")
print(os.listdir(folder_dir))
print()

# 테스트 메일 발송
print("*--- 완료 시 알람 메일을 설정? (N 이외의 문자 입력 시 활성화)")
is_sendMail = input(">> ")
if (is_sendMail != "N"):
    # 구글 사용자 정보 입력
    ID = input("gmail 아이디: ")
    PW = input("gmail 암호: ")
    addressTo = "{}@gmail.com".format(ID)
    sendTestMail(ID, PW, addressTo, folder_dir)  # 메일 발송

#--- DB 세션 만들기. DB 생성
db_path = os.path.join(os.getcwd(), "completed_dir", os.path.basename(folder_dir))  # db 경로
conn = sqlite3.connect(db_path)    # db 접속
db_name = os.path.basename(folder_dir)
createDB(conn, db_name)    # db 생성. 기존에 파일이 있으면 지우니 주의.

# ----- 크롤링 시작
# 창을 열고 로그인
driver = logIn(webdriver)

# 시간 기록
start_time = time.time()

#--- 실질적인 기능을 담당하는 부분
file_index = 0  # 몇 번째 파일인지 출력하기 위함.
for csv_splited in os.listdir(folder_dir):    # x번폴더 내의 파일 하나
    full_path = os.path.join(folder_dir, csv_splited) # 전체 경로

    # csv 파일 시작 메일 발송.
    if (is_sendMail != "N"):
        sendRunningMail(ID, PW, addressTo, folder_dir, csv_splited, file_index)  # csv 파일이 하나 끝날 때마다 보내질 메일

    file = open(full_path, encoding="utf-8")
    csv_file = csv.reader(file)
    next(csv_file, None)    # 1행 헤더 날리기
    print("#--- 파일 불러옴:", full_path)

    #--- 기업 반복
    for url_from_csv in csv_file:
        # 반복 시작
        page_num = 1    # 기업 내의 리뷰 페이징

        #--- 기업의 페이지 반복
        while 1:
            # 기업 url 및 페이지
            url = "{}/?page={}".format(url_from_csv[3], page_num)
            print("현재 url:", url)

            # 가져온 URL로 접근
            driver.get(url)

            # 전체 정보 수집 - 1 항목
            company = driver.title.split(" ")[0]    # 기업명. 추가적인 쿼리를 하지 않기 위해 title을 쪼갠다.
            article_group = driver.find_element_by_css_selector("div.section_group")    # 전체 글
            article_list = article_group.find_elements_by_css_selector("div.content_wrap")    # 글 뭉텅이들
            print("현재 기업명:", company)

            # 더 이상 글이 없으면 끝내기.
            if len(article_list) == 0:
                break

            #--- 한 글에 대한 작업 시작
            for article in article_list:

                # 글에 대한 기본 정보 - 4 항목. 누락 부분이 있을 수 있기에 다 가져온다.
                article_header = article.find_element_by_css_selector("div.content_top_ty2").text  # 글 헤더 부분.

                # 점수 부분 - 6 항목
                star_score = refine_text(article.find_element_by_css_selector("div.star_score"))  # 별점. 소수점이 없기를 기도함
                bar_scores = article.find_elements_by_css_selector("div.bl_score")  # 기타 5개 점수

                # 글 제목 부분 - 1 항목
                title = article.find_element_by_css_selector("h2.us_label").text  # 글의 제목

                # 글 본문 부분 - 3 항목
                article_body = article.find_elements_by_css_selector("dl.tc_list span") # 중복되므로 쿼리를 여러번 안하고 한번으로 끝낸다.

                merit = article_body[0].text # 장점
                demerit = article_body[1].text   # 단점
                try:
                    to_ceo = article_body[2].text   # 경영진에게 바라는 점. 혹시 모르니 안전장치.
                except:
                    to_ceo = "Null"

                # 기타 - 2 항목. 누락된 것 확인했으니 예외 걸어둠.
                try:
                    forecast = article.find_element_by_css_selector("p.etc_box strong").text  # 전망
                except:
                    forecast = "Null" # 없는 것 보았음.

                try:
                    recommend = article.find_element_by_css_selector("p.txt").text  # 추천 여부
                except:
                    recommend = "Null"

                # db에 넣기
                insertDB(conn, db_name,
                         company, article_header,
                         star_score, bar_scores[0], bar_scores[1], bar_scores[2], bar_scores[3], bar_scores[4],
                         title, merit, demerit, to_ceo,
                         forecast, recommend)

            # 페이지 증가
            page_num += 1
            print("#--- 페이지 하나 끝남----")

        print("#--- 기업 하나 끝남\n")
        print("#--- 경과 시간: {:.4f} sec".format(time.time() - start_time))

    print("#--- 분할된 파일 하나 끝남")
    print("#--- 경과 시간: {:.4f} sec".format(time.time() - start_time))
    file_index += 1 # 파일 넘버링.

#----- 담당 폴더 끝. 종료 보고
driver.close()  # 브라우저 종료
conn.close() # db 종료

print("\n\n--------------------------------------성공!--------------------------------------")
print("#--- 파일 저장됨. 경로: ", db_path)
print("#--- 총 경과 시간: {:.4f} sec".format(time.time() - start_time))

# 완료 메일 발송
if (is_sendMail != "N"):
    sendEndMail(ID, PW, addressTo, start_time, db_path)  # 종료 보고
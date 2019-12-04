# 함수는 여기에 다 정의해두었음. # selenium 제외하고는 모두 기본 라이브러리.
from selenium import webdriver
import re
from email.mime.text import MIMEText
import smtplib
import datetime
import os
import time

# 'style'tag에서 숫자만 가져오는 함수
# 인자는 html 엘리먼트를 받습니다.
def refine_text(element):
    element = element.get_attribute("style")
    regex = re.compile("\d{2,3}")
    return int(regex.search(element).group())


# 메일보내기.
# 구글 메일을 사용해서 보낼 것임
# https://myaccount.google.com/lesssecureapps 가서 "보안 수준이 낮은 앱 허용: 사용" 해야 함.
# docs: https://docs.python.org/3/library/smtplib.html
def sendEmail(ID, PW, addressTo, emailSubject, emailText):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)    # 구글 SMTP
        server.ehlo()   # say Hello
        server.starttls()  # TLS 사용시 필요
        server.login(ID, PW)    # 로그인.

        msg = MIMEText(emailText, "plain")   # 본문
        msg['To'] = addressTo # 받을 사람
        msg['Subject'] = emailSubject  # 제목

        server.sendmail(ID, addressTo, msg.as_string())    # 발송
        server.quit()
        print("#---메일 발송에 성공함!")
    except:
        print("*** 오타가 났거나 권한 에러가 발생했음. 'https://myaccount.google.com/lesssecureapps' 가서 '보안 수준이 낮은 앱 허용: 사용' 해야 함.")
        from sys import exit
        exit()


# DB 생성. 있으면 지운다. 주의.
def createDB(conn, db_name):
    conn.execute("DROP TABLE if exists {}".format(db_name))
    conn.execute("CREATE TABLE if not exists {} ("
                 "IDX INTEGER PRIMARY KEY, "
                 "company varchar(20), header varchar(50), "
                 "star_score int, bar_scores_1 int, bar_scores_2 int, bar_scores_3 int, bar_scores_4 int, bar_scores_5 int, "
                 "title tinytext, merit text, demerit text, to_ceo text, "
                 "forecast varchar(20), recommend varchar(20))".format(db_name))
    # 리턴값 없음.


# DB 집어넣기.
def insertDB(conn, db_name,
             company, header,
             star_score, bar_scores_1, bar_scores_2, bar_scores_3, bar_scores_4, bar_scores_5,
             title, merit, demerit, to_ceo,
             forecast, recommend):
    #--- db 넣기 전 전처리가 필요함... 특히 따옴표
    bar_scores_1 = refine_text(bar_scores_1)
    bar_scores_2 = refine_text(bar_scores_2)
    bar_scores_3 = refine_text(bar_scores_3)
    bar_scores_4 = refine_text(bar_scores_4)
    bar_scores_5 = refine_text(bar_scores_5)

    title = title.replace("\'", "\"")
    merit = merit.replace("\'", "\"")
    demerit = demerit.replace("\'", "\"")
    to_ceo = to_ceo.replace("\'", "\"")

    sql_sentence = "insert into {} (" \
                   "company, header, " \
                   "star_score, bar_scores_1, bar_scores_2, bar_scores_3, bar_scores_4, bar_scores_5," \
                   "title, merit, demerit, to_ceo, " \
                   "forecast, recommend" \
                   ")" \
                   "values (" \
                   "'{}', '{}', " \
                   "{}, {}, {}, {}, {}, {}," \
                   "'{}', '{}', '{}', '{}'," \
                   "'{}', '{}')".format(db_name,
                                        company, header,  # 헤더
                                        star_score, bar_scores_1, bar_scores_2, bar_scores_3, bar_scores_4, bar_scores_5,  # 별점
                                        title, merit, demerit, to_ceo,  # 장문
                                        forecast, recommend)  # 기타
    # print(sql_sentence)
    conn.execute(sql_sentence)  # 발송
    conn.execute("commit")      # 커밋
    print("#---행 추가됨:", title)


# 브라우저 제어. 목표 사이트에 로그인
def logIn(driver):
    print("#--- 브라우저를 열고 로그인 중...")
    driver = webdriver.Chrome('chromeDriver/chromedriver.exe')
    driver.implicitly_wait(3)
    driver.get('https://jobplanet.co.kr/users/sign_in')
    driver.find_element_by_name('user[email]').send_keys('jsp4434@kookmin.ac.kr')
    driver.find_element_by_name('user[password]').send_keys('ansthdgkqslek\n')
    return driver

# 제일 처음에 보내지는 테스트 발송용
def sendTestMail(ID, PW, addressTo, folder_dir):
    # 발송될 테스트 메일 설정
    emailSubject = "Jobplanet Starts...{}".format(folder_dir.split("\\")[-1])  # 제목이 아스키문자밖에 안되는 것 같음..
    emailText = "선택한 폴더명: {} \n" \
                "시작 시각: {} \n" \
                "시작 전 메일을 수신 여부를 테스트하기 위해 보내짐.".format(folder_dir, datetime.datetime.now())  # 시작시간 적기

    print("#--- 테스트 메일 발송...")
    sendEmail(ID, PW, addressTo, emailSubject, emailText)  # 발송
    input("메일이 제대로 왔는 지 확인했으면 아무 키나 눌러서 진행. (시간이 걸릴 수 있음)")


# csv 파일이 하나 끝날 때마다 보내질 메일
def sendRunningMail(ID, PW, addressTo, folder_dir, csv_splited, file_index):
    emailSubject = "Jobplanet Running: {}...".format(csv_splited)  # 제목이 아스키문자밖에 안되는 것 같음..
    emailText = "폴더명: {} \n" \
                "파일명: {} \n" \
                "진행 현황: {}/{} \n" \
                "현재 파일 시작 시각: {} \n" \
                "-----------------\n" \
                "상기 파일을 진행 중... 진행 또는 완료 메일이 오지 않는다면 프로그램 정지를 의심해야 함." \
        .format(folder_dir, csv_splited, file_index, len(os.listdir(folder_dir)), datetime.datetime.now())  # 시작시간 적기

    print("#--- 파일 시작 메일 발송...")
    sendEmail(ID, PW, addressTo, emailSubject, emailText)  # 발송


# 종료 시 보낼 메일
def sendEndMail(ID, PW, addressTo, start_time, db_path):
    emailSubject = "Jobplanet Ends Successfully...{}".format(db_path.split("\\")[-1])
    emailText = "성공적으로 마침!! \n" \
               "종료 시각: {} \n" \
               "프로그램 구동 시간: {:.4f} sec \n" \
               "저장된 파일 경로: {}\n" \
                "-------------------------\n" \
                "메일을 더 이상 이용하지 않는다면 'https://myaccount.google.com/lesssecureapps'에서 '보안 수준을 다시 강화할 것.\n" \
                "**- 완성된 db 파일을 다른 데로 옮긴 다음 다시 작업할 것!!!".format(datetime.datetime.now(), time.time() - start_time, db_path)

    sendEmail(ID, PW, addressTo, emailSubject, emailText)  # 발송
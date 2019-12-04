# -*- coding: utf-8 -*-
"""
Created on Wed May 15 17:09:24 2019

@author: JW.Jeon
"""


from selenium import webdriver
import time
import numpy as np
import pandas as pd
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.alert import Alert
import warnings
warnings.filterwarnings('ignore')


# 접속 및 로그인, iframe 전환
profile = webdriver.FirefoxProfile()
#profile.accept_untrusted_certs = True
profile.set_preference('security.mixed_content.block_active_content', False)
profile.set_preference('security.mixed_content.block_display_content', True)

driver = webdriver.Firefox(firefox_profile=profile,executable_path='C:/driver/geckodriver.exe')
#driver.get('https://www.ggi.co.kr/')
driver.get('http://www.ggauction.com/')

time.sleep(2)

driver.switch_to_frame("home")

id_key = driver.find_element_by_css_selector('input.loginbox:nth-child(3)')
id_key.send_keys('myid')

pw_key = driver.find_element_by_css_selector('#respass')
pw_key.send_keys('mypw')

time.sleep(1)

loginbtn = driver.find_element_by_css_selector('.smenu')
loginbtn.click()

time.sleep(1)

# 경고창 확인!!
try:
    alert = driver.switch_to_alert()
    alert.accept() 
    print("alert accepted")
except:
    pass
time.sleep(1)

# 경매검색 클릭
search = driver.find_element_by_css_selector('li.m_menu1:nth-child(1) > a:nth-child(1)')
search.click()

time.sleep(1)


################ 경매검색 페이지 ######################################

# 일월 클릭
driver.find_element_by_css_selector('#Radio5').click()

# 연립
driver.find_element_by_id('31').click()

# 다세대
driver.find_element_by_id('32').click()

# 연립(생활주택)
driver.find_element_by_id('H2').click()

# 다세대(생활주택)
driver.find_element_by_id('H3').click()

### 2017년 1월 1일 ~ 2018년 12월 31일 (일자 변경가능)
#driver.find_element_by_css_selector('#Select3 > option:nth-child(3)').click() # 2017년
#driver.find_element_by_css_selector('#Select4 > option:nth-child(1)').click() # 1월
#driver.find_element_by_css_selector('#Select5 > option:nth-child(1)').click() # 1일

#driver.find_element_by_css_selector('#Select6 > option:nth-child(2)').click()  # 2018년
#driver.find_element_by_css_selector('#Select10 > option:nth-child(12)').click() # 12월
#driver.find_element_by_css_selector('#Select13 > option:nth-child(31)').click() # 31일

#time.sleep(1)


#추가본
#조회 기간 설정(6개월이내는 전국 가능, 6개월 이상은 시군구만 가능)                                    
y_num = [1,2,3,4,5,6,7,8,9,10]
year = ['2019','2018','2017','2016','2015','2014','2013','2012','2011','2010']
year_dt = pd.DataFrame([y_num, year], index=['num','year']).T

st_date = input('시작 날짜를 기입하시오(예시:20180607) : ' )
end_date = input('종료 날짜를 기입하시오(예시:20180607) : ' )
                                                                
st_year = year_dt['num'][year_dt['year'] == st_date[:4]].iloc[0]
end_year = year_dt['num'][year_dt['year'] == end_date[:4]].iloc[0]

# 2017년 1월 1일 ~ 2018년 12월 31일 (일자 변경가능)
driver.find_element_by_css_selector('#Select3 > option:nth-child('+ str(st_year) +')').click() # 2018년
driver.find_element_by_css_selector('#Select4 > option:nth-child(' + str(int(st_date[4:6])) + ')').click() # 7월
driver.find_element_by_css_selector('#Select5 > option:nth-child(' + str(int(st_date[6:])) + ')').click() # 1일

driver.find_element_by_css_selector('#Select6 > option:nth-child('+ str(end_year) +')').click()  # 2018년
driver.find_element_by_css_selector('#Select10 > option:nth-child(' + str(int(end_date[4:6])) + ')').click() # 12월
driver.find_element_by_css_selector('#Select13 > option:nth-child(' + str(int(end_date[6:])) + ')').click() # 31일
time.sleep(1)


# 도시 가져오기
dosi_list = driver.find_elements_by_css_selector('#Select8')

# 서울(1), 경기(3), 인천(11) 선택 (서울시만 크롤링 할 예정이라 for loop 안돌림)
dosi_list[0].find_elements_by_tag_name('option')[11].click()


#driver.switch_to_window(driver.window_handles[0])
#driver.get_window_position(driver.window_handles[0])


# 도시 가져오기
#dosi_list = driver.find_elements_by_css_selector('#Select8')

# 서울 선택
#dosi_list[0].find_elements_by_tag_name('option')[1].click()

# 구 가져오기 - Dom 에러 발생해서 못씀

# 0 강남구, 1 강동구, 2 강북구, 3 강서구, 4 관악구, 5 광진구 ,6 구로구, 7 금천구, 8 노원구 ,9 도봉구
# 10 동대문구, 11 동작구, 12 마포구, 13 서대문구, 14 서초구, 15 성동구, 16 성북구, 17 송파구, 18 양천구
# 19 영등포구, 20 용산구, 21 은평구, 22 종로구, 23 중구, 24 중랑구

gu = driver.find_elements_by_css_selector('#Select9')
gu_list = gu[0].find_elements_by_tag_name('option')[1:-1]

# 구 이름 리스트 만들기!
gugu = []
gu_num = -1

for i in gu_list:
    gugu.append(i.text)

#gugu[0]

error_log = []
# 구 선택하기 2가 제일 처음!! ex) 강남구 - 2부터 시작해야 함
for i in range(2,len(gugu)+2):
    gu = driver.find_element_by_css_selector('#Select9 > option:nth-child({})'.format(i))
    gu.click()
    
    gu_num = gu_num + 1
    print('------------------------------------- {} 크롤링 시작------------------------------------'.format(gugu[gu_num]))
    #gu_num = gu_num + 1
    time.sleep(1)

    # 검색 클릭
    driver.find_element_by_css_selector('#sub_button2 > a:nth-child(1)').click()

    time.sleep(3)


    # 100개로 보기
    num_view_100 = driver.find_element_by_css_selector('#Table22 > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(3) > select:nth-child(1) > option:nth-child(8)')
    num_view_100.click()

    time.sleep(3)

    # 결과 담을 리스트 만들기
    result_list = []
    num = 0
    
    # 한 페이지에 보이는 물건 개수 파악 및 페이지 넘기기 (100개 이상시)
    num_btn = driver.find_elements_by_css_selector('#frmSearch2 > div:nth-child(12) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2)')
    nbt = len(num_btn[0].find_elements_by_tag_name('div'))
    for i in range(1,nbt+1):
        tt = driver.find_element_by_css_selector('#frmSearch2 > div:nth-child(12) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > div:nth-child({})'.format(i))
        tt.click()

        time.sleep(4)

        build_list = driver.find_elements_by_class_name('list_link')[1::2]
        
                
        for i in build_list:    
            i.click()
            
            num = num + 1
            
            time.sleep(4)

            # 빌딩정보 페이지로 전환
            driver.switch_to_window(driver.window_handles[1])
            driver.get_window_position(driver.window_handles[1])

            time.sleep(5)

################################################## 정보 수집 ####################################################
            try:
                # 경매번호 (ind)
                ind_1 = driver.find_element_by_css_selector('#wrap > table:nth-child(3) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > font:nth-child(1)')
                ind_2 = driver.find_element_by_css_selector('#wrap > table:nth-child(3) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > b:nth-child(2) > font:nth-child(2) > font:nth-child(1)')
    
                ind =  ind_1.text + ' ' + ind_2.text.split()[0] + '-' + ind_2.text.split()[2]
                
                # 주소 가져오기 - 도로명 주소 없는 경우도 있음
                address_1 = driver.find_elements_by_class_name('td_1')[0].text.split('\n')[0]
    
                if len(driver.find_elements_by_class_name('td_1')[0].text.split('\n')) == 1:
                    address_2 = 'None'
    
                else:
                    address_2 = driver.find_elements_by_class_name('td_1')[0].text.split('\n')[1].split(') ')[1]
    
                # 용도 가져오기
                use = driver.find_elements_by_class_name('td_1')[3].text
    
                # 감정가 , 감정일
                value = driver.find_elements_by_class_name('td_1')[6]
                ap_value = value.text.split()[0]
                # 감정일 없는 경우가 있어서 조건문 추가
                if len(value.text.split()) == 1:
                    ap_day = 'nan'
                else:
                    ap_day = '20'+value.text.split('(')[1].replace(')','').replace('.','-')
    
                # 최저가
                low_value = driver.find_elements_by_class_name('td_1')[9].text.split()[0]
    
                # 토지면적
                if driver.find_elements_by_class_name('td_1')[13].text[0] == '전':
                    area_ld = driver.find_elements_by_class_name('td_1')[13].text.replace('\n',' ')
    
                else:
                    area_ld = driver.find_elements_by_class_name('td_1')[10].text.split()[0]
    
    
                # 건물면적
                if driver.find_elements_by_class_name('td_1')[13].text[0] == '전':
                    area_bd = driver.find_elements_by_class_name('td_1')[13].text.replace('\n',' ')
    
                else:
                    area_bd = driver.find_elements_by_class_name('td_1')[13].text.split()[0]
    
                # 매각기일, 낙찰가 - 낙찰가 없음(취하)일 경우 price에 취하 표시
                sale_price = driver.find_elements_by_class_name('td_1')[5]
                day_sale = '20' + sale_price.text.split()[0].replace('.','-')
    
                ym = driver.find_elements_by_id('Table14')
    
                price = ym[2].text.split('매각가 ')[-1].split('\n')[0]
    
                if price.split()[0] == '감정가':
                    price = '취하'
    
    
                # 경매개시일
                day_open = '20' + driver.find_elements_by_class_name('td_1')[11].text.replace('.','-')
    
                # 배당종기일
                day_close = '20' + driver.find_elements_by_class_name('td_1')[14].text.replace('.','-')
    
                # 등기권리
    
                reg = driver.find_elements_by_id('Table20')[0].text
                
                # 소재지/감정요약
                appraisal = driver.find_element_by_id('Table12').text
    
                # 물건번호/면적
                area_info = driver.find_element_by_id('Table13').text
    
                # 감정가/최저가/과정
                pr_price = driver.find_elements_by_id('Table14')[2].text
    
                # 임차조사
                try:
                    les_1 = driver.find_element_by_id('Table15').text
                    les_2 = driver.find_element_by_id('Table19').text
                    lease_info = les_1 + '   <<<지지옥션 전입세대조사>>>' + les_2
                except:
                    lease_info = 'None'
                

###################################### 결과정리 및 창 닫기 ###########################################################################################
            
                result_list.append([ind,address_1,address_2,use,ap_value,ap_day,low_value,area_ld,area_bd,
                                day_sale,price,day_open,day_close,appraisal, area_info, pr_price, lease_info, reg])
    
    
                time.sleep(2)
    
                close_btn = driver.find_element_by_css_selector('#topmenu > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > a:nth-child(18)')
                close_btn.click()
    
                print('{}. {} 크롤링 완료'.format(num, address_1))
                time.sleep(2)
    
                # 창 전환
                driver.switch_to_window(driver.window_handles[0])
                driver.get_window_position(driver.window_handles[0])
    
                time.sleep(2)

            except:
                
                print('에러발생 : ' + str(num) + ':' + str(gugu[gu_num]))
                err_num = [str(num),gugu[gu_num]]
                error_log.append(err_num)
#                with open('에러log3.dat', 'a') as f:
#                    wr = csv.writer(f, lineterminator='\n', quoting=csv.QUOTE_NONE)
#                    wr.writerow(err_num)         

                driver.switch_to_window(driver.window_handles[0])
                driver.get_window_position(driver.window_handles[0])
    
                time.sleep(2)

    print('------------------------------------- 구 크롤링 완료 ------------------------------------')
    
    columns = ['ind','address_1','address_2','use','ap_value','ap_day','low_value','area_ld','area_bd',
                'day_sale','price','day_open','day_close','appraisal','area_info','pr_price','lease_info','reg']

    df = pd.DataFrame(result_list, columns=columns)

# 경로지정 해야함..
    df.to_csv('C:/Users/Bigvalue-Data/Desktop/연립다세대_경매_크롤링/{}_경매.csv'.format(gugu[gu_num]), encoding='cp949')
    
    print('------------------------------------- 저장완료 ------------------------------------')


#error_log



import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from setting_font import *  # 폰트 설정용
from sklearn.preprocessing import minmax_scale

# 파일 경로가져오기
def getPath(root_name, dir_num):
    file_list = []
    target_dir = os.path.join(root_name, os.listdir(root_name)[dir_num])
    for file in os.listdir(target_dir):
        file_list.append(os.path.join(target_dir, file))
#     print(file_list)
    return file_list

#--- 약간의 전처리.
def settingUpDataFrames(df):
    # 행 바꾸기
    df = df.T
    df.columns = df.iloc[0]
    df = df[1:]

    try: # index를 datetime으로
        df.index = pd.to_datetime(df.index)
    except:
        idx_list = []   # 정제된 문자열 담을 곳

        if df.index[0].find("H") != -1:   # 반기 데이터면...
            # print("case: 반기 데이터 -> ", df.index[0])
            for i in range(0, len(df.index)):
                y = pd.to_datetime(df.index[i], format="%Y_H%m").year
                m = pd.to_datetime(df.index[i], format="%Y_H%m").month * 6
                d = pd.to_datetime(df.index[i], format="%Y_H%m").day + 29

                # 연월일 추출하여 문자열로 만들고 다시 datetime으로 바꾸어 리스트 저장
                idx_list.append(pd.to_datetime("{}-{}-{}".format(y, m, d), format="%Y-%m-%d"))

        elif df.index[0].find("Q") != -1:   # 분기 데이터면...
            for i in range(0, len(df.index)):
                y = pd.to_datetime(df.index[i], format="%Y.Q%m").year
                m = pd.to_datetime(df.index[i], format="%Y.Q%m").month * 3
                d = pd.to_datetime(df.index[i], format="%Y.Q%m").day + 29

                idx_list.append(pd.to_datetime("{}-{}-{}".format(y, m, d), format="%Y-%m-%d"))

        elif len(df.index[0]) == 4:
            for i in range(0, len(df.index)):
                idx_list.append(pd.to_datetime("{}-01-01".format(df.index[i])))

        else:   # 예상치 못한 인덱스.
            print("!! 아래 DataFrame에서 Datetime 자료형으로 변환 중 오류 발생!!!")
            print("#--- 에러 로그 ----#")
            print("!! 0번째 인덱스", df.index[0])
            print("!! 0번째 인덱스 type", type(df.index[0]))
            raise ValueError

        df.index = idx_list
        print(df.index)

    print("#--- settingUpDataFrames: 완료")
    return df

# 파일 불러오는 부분
cwd = os.getcwd()  # 현재 디렉토리
data_dir = os.path.join(cwd, "data")

print("\n\n#--- 초기화 완료")

while 1:    # 반복시작
    print(os.listdir(data_dir))
    select_num = int(input("데이터셋 선택: >>"))

    dataset_dir = getPath(data_dir, select_num)
    dataset = [pd.read_csv(csvfile, engine="python", encoding="cp949") for csvfile in dataset_dir]

    selected_column_list = []
    for primary_df in dataset:
        print("#--- 1개 df 정제 시작")
        print("# 정제 전 -----")
        print(primary_df)
        print()

        df = settingUpDataFrames(primary_df)    # 데이터프레임 정제
        print("# 정제 후 -----")
        print(df)
        print()

        df = df.fillna(method="backfill")  # 뒷값으로 채우기
        print("# 결측치 처리 후 -----")
        print()
        print(df)

        col = df.columns
        df = pd.DataFrame(np.hstack([minmax_scale(df)]), columns=col)   # 스케일링
        print("# 스케일링 후-----")
        print(df)
        print()

        # 칼럼명 출력
        print("===================================")
        idx = 0 # 임시 칼럼 인덱스 . 보여주기용
        for i in col:
            print("{:2}번".format(idx), i)
            idx += 1

        # 칼럼 선택받기

        col_num = input("#---열 번호 입력. 공백으로 구분 >>")
        col_num = col_num.split()
        col_num = [int(c) for c in col_num]
        col = col[col_num]  # 인덱싱 따로.

        # 선택한 행렬을 담음.
        for col_name in col:
            print("추가 대상 >>>>> \t\t\t", col_name)
            selected_column_list.append(df[col_name])

    for selected_col in selected_column_list:
        selected_col.plot(kind="line")

    plt.legend(loc="best")
    plt.show()

    input("다시 시작하려면 아무 키나 누르시오")
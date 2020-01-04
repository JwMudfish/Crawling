import pandas as pd
import os

splitCSV_path = os.path.join(os.getcwd(), "target_dir")
print(os.listdir(splitCSV_path))    # 타겟 폴더에 있는 파일들 보여주기
review_count = int(input("잘라낼 리뷰 수 기준치를 숫자로 입력 (ex: 2000): "))

# 갯수만큼 다 돌려!!!
for list_num in range(0, len(os.listdir(splitCSV_path))):
    target_file = os.path.join(splitCSV_path, os.listdir(splitCSV_path)[list_num])
    # DataFrame으로 불러오기
    df = pd.read_csv(target_file, engine="python", index_col=0, encoding="utf-8")
    print(df.head())    # 확인용
    header = ["reviews", "company", "url"]

    sum_review = 0  # 총 리뷰수
    file_num = 1   # 파일 넘버링 시작
    new_df = pd.DataFrame(columns=header) # 새 데이터프레임

    for row_num in range(0, len(df)):
        sum_review += df.iloc[row_num, 0]    # 리뷰 수 더함
        # print(sum_review)
        new_df = new_df.append(df.iloc[row_num])      # 새 df에 행 전체를 추가

        if int(sum_review) >= review_count:
            csv_splited_path = os.path.join(os.getcwd(), "completed_dir",
                                            "{}_{}.{}".format(os.path.basename(target_file).split(".")[0], file_num, "csv"))
            fname = csv_splited_path
            new_df.to_csv(fname, encoding="utf-8")
            new_df = pd.DataFrame(columns=header)  # 새 데이터프레임
            sum_review = 0  # 초기화
            file_num += 1   # 넘버링
            print("{} 저장됨!------".format(fname))


        if row_num == len(df) - 1: # 마지막 loop 때...
            csv_splited_path = os.path.join(os.getcwd(), "completed_dir",
                                            "{}_{}.{}".format(os.path.basename(target_file).split(".")[0], file_num, "csv"))
            fname = csv_splited_path
            new_df.to_csv(fname, encoding="utf-8")
            print("{} 저장됨!------".format(fname))
            break
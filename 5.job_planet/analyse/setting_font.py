import matplotlib.font_manager as fm
from matplotlib import pyplot as plt

# 폰트 전역 설정. 안그러면 한글이 깨지드라고.
font_path = "c:/Windows/Fonts/malgun.ttf"
font_name = fm.FontProperties(fname=font_path, size=50).get_name()
plt.rc('font', family=font_name)
color_list = {"red": "#D67F6E", "banana": "#EDE9BA" , "yellow": "#ECC779", "green": "#A9BD8C", "blue": "#73A599"}
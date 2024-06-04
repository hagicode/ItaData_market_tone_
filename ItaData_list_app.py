import streamlit as st
import streamlit.components.v1 as stc
import pandas as pd
import numpy as np
import glob
import pathlib
from datetime import datetime
from datetime import timedelta
import os

# @st.cache_data
# def load_dataframe(f_):
#     df = pd.read_parquet(f_)
#     return df

#github
st.set_page_config(layout="wide")

import neologdn
def format_text(text):
  text = neologdn.normalize(text)
  return text

def is_int(s):
    try:
        int(s)
    except ValueError:
        return False
    else:
        return True

#ファイル検索
def seachfile(symbol,list_,date_str_):
    code = symbol
    l2 = list_
    date_str = date_str_
    if str(code).startswith('1'):
        filename = [f for f in l2 if "1000s" in f and date_str in f][0]
    elif str(code).startswith('2'):
        filename = [f for f in l2 if "2000s" in f and date_str in f][0]
    elif str(code).startswith('3'):
        filename = [f for f in l2 if "3000s" in f and date_str in f][0]
    elif str(code).startswith('4'):
        filename = [f for f in l2 if "4000s" in f and date_str in f][0]
    elif str(code).startswith('5'):
        filename = [f for f in l2 if "5000s" in f and date_str in f][0]
    elif str(code).startswith('6'):
        filename = [f for f in l2 if "6000s" in f and date_str in f][0]
    elif str(code).startswith('7'):
        filename = [f for f in l2 if "7000s" in f and date_str in f][0]
    elif str(code).startswith('8'):
        filename = [f for f in l2 if "8000s" in f and date_str in f][0]
    elif str(code).startswith('9'):
        filename = [f for f in l2 if "9000s" in f and date_str in f][0]    
    return filename

def ItaResize(df,ita_num=5):
    import numpy as np
    import pandas as pd

    df_Ita = df.copy()
    df_market = pd.DataFrame(df_Ita.loc[-1000].replace(-1000,"成行")).T
    df_Ita_ = df_Ita.iloc[1:]
    if df_Ita_["値段"].apply(lambda x: x.is_integer()).all():
        df_Ita_["値段"] = df_Ita_["値段"].astype(int)
    market_diff = (df_market["買数量"]-df_market["売数量"]).iloc[0]
    
    # 初期化
    ask_center = df_Ita_["売数量"].dropna(how = "any").index[-1]
    bid_center = df_Ita_["買数量"].dropna(how = "any").index[0]

    if ask_center >bid_center :

        first = bid_center
        end = ask_center

        df_w = df_Ita_.loc[first:end].copy()
        if market_diff>0:
            df_w.loc[first,"買数量"] += market_diff
        else:
            df_w.loc[end,"売数量"] += abs(market_diff)

        for x in range (first,end+1):
            #print(x,df_w['値段'].loc[x])
            if df_w['売数量'].loc[x:end].sum() > df_w['買数量'].loc[first:x].sum() and df_w['売数量'].loc[x+1:end].sum() < df_w['買数量'].loc[first:x+1].sum():

                # print("板中心値：",df_w['値段'].loc[x],",x=",x)
                # print("[中心よりも上(x)]  売数量:",df_w['売数量'].loc[x:end].sum(),"買数量:",df_w['買数量'].loc[first:x].sum())
                # print("[中心よりも下(x+1)]売数量:",df_w['売数量'].loc[x+1:end].sum(),"買数量:",df_w['買数量'].loc[first:x+1].sum())
                ask_center = x
                bid_center = x+1
                break
            else:
                ask_center = first
                bid_center = first+1

    #板が20本の時
    ask_max = ask_center-(ita_num-1)
    bid_max = bid_center+(ita_num-1)

    ask_over = df_Ita_.iloc[:ask_max]["売数量"].sum()
    ask_over_order = df_Ita_.iloc[:ask_max]["売件数"].sum()
    bid_under = df_Ita_.iloc[bid_max:]["買数量"].sum()
    bid_under_order = df_Ita_.iloc[bid_max:]["買件数"].sum()


    # 一番上に追加する行を定義します(OVER)
    top_row = pd.DataFrame({
        '売件数': [ask_over_order],
        '売数量': [ask_over],
        '値段': ["OVER"],
        '買数量': [np.nan],
        '買件数': [np.nan]
    }, index=[-1])

    # 一番下に追加する行を定義します(UNDER)
    bottom_row = pd.DataFrame({
        '売件数': [np.nan],
        '売数量': [np.nan],
        '値段': ["UNDER"],
        '買数量': [bid_under],
        '買件数': [bid_under_order]
    }, index=[1000])

    df___ = pd.concat([df_market,top_row, df_Ita_.iloc[ask_max:bid_max], bottom_row])
    df____ = df___.fillna(-1)
    df_____ = df____.astype({"売数量":int,"買数量":int,"売件数":int,"買件数":int}).replace(-1,"")
    
    #一般化したパラメータ
    market_div = df_market["買数量"].iloc[0]/df_market["売数量"].iloc[0]
 
    ask_total = df_Ita_.iloc[ask_max:bid_max]["売数量"].sum()+ask_over
    bid_total = df_Ita_.iloc[ask_max:bid_max]["買数量"].sum()+bid_under
    bid_over_ask = bid_total / ask_total

    bid_market_over_total= df_market["買数量"].iloc[0]/bid_total
    ask_market_over_total= df_market["売数量"].iloc[0]/ask_total

    div_data = pd.DataFrame({
    '成行比率(買/売)': market_div,
    '累計比率(買/売)': bid_over_ask,
    '成行/累計の比率(買)': bid_market_over_total,
    '成行/累計の比率(売)': ask_market_over_total,
    },index=["値"]).T.reset_index()
    
    return df_____ ,div_data


# 小数点以下1桁まで表示
def custom_format1(x):
    return '{:.1f}'.format(x) if isinstance(x, float) else str(x)
# 小数点以下2桁まで表示
def custom_format1_2(x):
    return '{:.2f}'.format(x) if isinstance(x, float) else str(x)

# 桁区切り表示
def custom_format2(x):
    return '{:,}'.format(x) if isinstance(x, int) else str(x)


#Ita
l2 = sorted(glob.glob('files/*s.parquet', recursive=True))
#st.write(l2)

# Github
# https://www.jpx.co.jp/markets/statistics-equities/misc/01.html
url = 'https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls'
df_jpx = pd.read_excel(url)
df_jpx = df_jpx.iloc[:, [1, 2, 3, 9]]
database = df_jpx.copy()
database_org = database.astype(str)

DB_serch = database_org.copy()
#DB_serch["銘柄名"] = [format_text(txt).casefold() for txt in DB_serch["銘柄名"]]

st.divider()
col1_,col2_ = st.columns(2)
with col1_:
#アップロードリスト
    st.write("じぶんの銘柄リストから絞込む")
    st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">1列目に銘柄コードが来るように記載ください。文字列は無視されます。</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">活用例：四季報・株探などファンダで絞込んだリスト／自分の取引銘柄など</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("マイリストアップロード", type='csv') 
    if uploaded_file is not None:
        upload_df = pd.read_csv(uploaded_file,index_col=None,header=None)
        mycode_lists_org = upload_df.iloc[:,0].astype(str)
        mycode_lists = mycode_lists_org.tolist()
        #mycode_lists = [int(s) for s in mycode_lists_org if is_int(s)]
        #mylist_button = st.radio("マイリストでの絞込み",    ('無', '有'), horizontal=True)


# 日付と時間を結合してdatetimeオブジェクトを作成
with col2_:
    newest_date = os.path.basename(l2[-1])[:6]
    # 文字列を日付と時間に分割
    date_str = st.text_input("日付(yymmdd)",newest_date)
    date = datetime.strptime(date_str, '%y%m%d').date()
    
    #日付のデータに対して存在するtimelistを作成し表示
    p1000 = pathlib.Path(seachfile("1000", l2, date_str))
    df_p1000 = pd.read_parquet(p1000)
    timelist = [i.strftime('%H:%M') for i in df_p1000.index.get_level_values(1).unique()]
    
    time_str = st.select_slider(
    "板データ時刻",
    options=timelist)
    time = datetime.strptime(time_str, '%H:%M').time()
    
    # 日付と時間を適切な形式に変換
    datetime_obj = datetime.combine(date, time)
    
    # その他の設定
    st.write("その他設定")
    ItaSize_str = st.text_input("板サイズ(携帯版20行)","10")
    ItaSize_str_ = round(int(ItaSize_str)/2)
    FontSize_str = st.radio('板の文字サイズ',['小', '中',"大"],horizontal=True,index=1)
    if FontSize_str == "小":
        thFont = '11px'
        tdFont = '9px'
    elif FontSize_str == "中":
        thFont = '13px'
        tdFont = '11px'
    elif FontSize_str == "大":
        thFont = '15px'
        tdFont = '13px'            

#update_date = os.path.split(p)[1].replace("_df_dayIta_all.parquet","")
#st.write("データ更新日：" + update_date)
#st.write(p)
#df = pd.read_parquet("files/" + "240522_df_day.parquet")
# df = pd.read_parquet(p)
# #df_Ita = df.loc["1301"].loc["2024-05-22 09:50:00"]


# style1
th_props1 = [
('font-size', thFont),
('text-align', 'center'),
('font-weight', 'bold'),
('color', '#6d6d6d'),
('background-color', '#e6e6e6')
]
                            
td_props1 = [
('font-size', tdFont),
('text-align', 'left')
]
                                
styles1 = [
dict(selector="th", props=th_props1),
dict(selector="td", props=td_props1)
]

# style2
th_props2 = [
('font-size', thFont),
('text-align', 'center'),
('font-weight', 'bold'),
('color', '#6d6d6d'),
('background-color', '#f7ffff')
]
                            
td_props2 = [
('font-size', tdFont),
('text-align', 'left')
]
                                
styles2 = [
dict(selector="th", props=th_props2),
dict(selector="td", props=td_props2)
]

hide_table_row_index = """
<style>
thead tr th:first-child {display:none}
tbody th {display:none}
table.dataframe td {text-align: right}
</style>
"""

st.markdown(hide_table_row_index, unsafe_allow_html=True)
num_for = len(mycode_lists)//5+1

for i in range(num_for):
    st.divider()
    cols = st.columns(5)
    col_index = 0  # 列インデックスを初期化

    start = i * 5
    end = (i+1)*5               
    for code in mycode_lists[start:end]:
        p = pathlib.Path(seachfile(code, l2, date_str))
        df_p = pd.read_parquet(p)
        name = DB_serch[DB_serch["コード"] == code]["銘柄名"].iloc[0].replace("ホールディングス","　ＨＤ")
        ShowedTime = datetime_obj
        Ita = ItaResize(df_p.loc[code].loc[ShowedTime], ItaSize_str_)

        # 現在の列オブジェクトを取得
        current_col = cols[col_index]

        try:
            # 現在の列にコンテンツを表示
            with current_col:
                st.write(f"{code}: {name} ")
                st.write(f"[{datetime_obj}]")
                st.table(Ita[0].style.set_table_styles(styles2).format(custom_format1).format(custom_format2))
                st.table(Ita[1].style.set_table_styles(styles2).format(custom_format1_2))

            # 次の列に移動
            col_index += 1

            # 列インデックスが5に達したらリセット
            if col_index == 5:
                col_index = 0

        except:
            with current_col:
                st.write("データなし")

            # 次の列に移動
            col_index += 1

            # 列インデックスが5に達したらリセット
            if col_index == 5:
                col_index = 0


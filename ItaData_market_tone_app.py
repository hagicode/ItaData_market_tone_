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

#Ita
l2 = sorted(glob.glob('files/*.parquet', recursive=True))
#st.write(l2)

# Github
# https://www.jpx.co.jp/markets/statistics-equities/misc/01.html
url = 'https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls'
df_jpx = pd.read_excel(url)
df_jpx = df_jpx.iloc[:, [1, 2, 3, 9]]
database = df_jpx[df_jpx["市場・商品区分"] != "ETF・ETN"]
database_org = database.astype(str)


DB_serch = database_org.copy()
DB_serch["銘柄名"] = [format_text(txt).casefold() for txt in DB_serch["銘柄名"]]


col1_,col2_ = st.columns(2)
with col1_:
    st.cache_data.clear()

    input_txt = st.text_input('銘柄コードを入力 or 部分一致の検索', '8058')
    format_input = format_text(input_txt).casefold()
    
    DB_result = database[(DB_serch['コード'].str.contains(str(format_input)))|(DB_serch['銘柄名'].str.contains(str(format_input)))]
    db_result_org = database_org.loc[DB_result.index]
    st.table(db_result_org)
    if len(db_result_org) == 0:
        st.write("一致する銘柄はありません")
    if len(db_result_org) > 1:
        st.write("1銘柄になるように入力してください")
    if len(db_result_org) == 1:
        symbols = db_result_org.iloc[0,0]
        name = db_result_org.iloc[0,1]
        st.write(f"[・TradingViewで開く](https://jp.tradingview.com/chart/?symbol=TSE%3A{symbols})")
        st.write(f"[・株探で確認する](https://kabutan.jp/stock/chart?code={symbols})")
    code = symbols

with col2_:
    # 文字列を日付と時間に分割
    date_str = st.text_input("日付(yymmdd)","240522")
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
# 日付と時間を適切な形式に変換
date = datetime.strptime(date_str, '%y%m%d').date()


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



#update_date = os.path.split(p)[1].replace("_df_dayIta_all.parquet","")
#st.write("データ更新日：" + update_date)
#st.write(p)
#df = pd.read_parquet("files/" + "240522_df_day.parquet")
# df = pd.read_parquet(p)
# #df_Ita = df.loc["1301"].loc["2024-05-22 09:50:00"]

#関数化
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

    div_data = pd.DataFrame({
    '成行比率(買/売)': market_div,
    '累計比率(買/売)': bid_over_ask,
    },index=["値"]).T.reset_index()
    
    return df_____ ,div_data


time_str = st.select_slider(
    "板データ時刻",
    options=["08:45","08:50","08:55","09:00","09:05", "09:10","09:15","09:20","09:25","09:30","09:35","09:40","09:45","09:50","09:55","10:00"])

time = datetime.strptime(time_str, '%H:%M').time()
# 日付と時間を結合してdatetimeオブジェクトを作成
datetime_obj = datetime.combine(date, time)




# style
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

# style
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



# 小数点以下1桁まで表示
def custom_format1(x):
    return '{:.1f}'.format(x) if isinstance(x, float) else str(x)
# 小数点以下2桁まで表示
def custom_format1_2(x):
    return '{:.2f}'.format(x) if isinstance(x, float) else str(x)

# 桁区切り表示
def custom_format2(x):
    return '{:,}'.format(x) if isinstance(x, int) else str(x)


hide_table_row_index = """
<style>
thead tr th:first-child {display:none}
tbody th {display:none}
table.dataframe td {text-align: right}
</style>
"""


# # 目次の作成
# st.title("目次")
# st.markdown("- 海運業\n- セクション2")


# # セクション1
# st.header("海運業")
# st.write("ここに内容を記述します。")

st.write("海運業")
#dfは9000sのみ
l_kaiun = ["9101","9104","9107"]
p_9000 = pathlib.Path(seachfile("9101",l2,date_str))
df_9000 = pd.read_parquet(p_9000)
col1,col2,col3,col4,col5 = st.columns(5)
st.markdown(hide_table_row_index, unsafe_allow_html=True)
with col1:
    code1 = l_kaiun[0]
    ShowedTime1 = datetime_obj
    Ita1 = ItaResize(df_9000.loc[code1].loc[ShowedTime1],ItaSize_str_)
    try:
        st.write("銘柄コード：",code1,"時刻",ShowedTime1)
        st.table(Ita1[0].style.set_table_styles(styles2).format(custom_format1).format(custom_format2))
        st.table(Ita1[1].style.set_table_styles(styles2).format(custom_format1_2))
    except:
        st.write("時刻データなし")

with col2:
    code2 = l_kaiun[1]
    ShowedTime2 = datetime_obj
    Ita2 = ItaResize(df_9000.loc[code2].loc[ShowedTime1],ItaSize_str_)
    try:
        st.write("銘柄コード：",code2,"時刻",ShowedTime2)
        st.table(Ita2[0].style.set_table_styles(styles2).format(custom_format1).format(custom_format2))
        st.table(Ita2[1].style.set_table_styles(styles2).format(custom_format1_2))
    except:
        st.write("時刻データなし")

with col3:
    code3 = l_kaiun[2]
    ShowedTime3 = datetime_obj
    Ita3 = ItaResize(df_9000.loc[code3].loc[ShowedTime1],ItaSize_str_)
    try:
        st.write("銘柄コード：",code3,"時刻",ShowedTime3)
        st.table(Ita3[0].style.set_table_styles(styles2).format(custom_format1).format(custom_format2))
        st.table(Ita3[1].style.set_table_styles(styles2).format(custom_format1_2))
    except:
        st.write("時刻データなし")

with col4:
    # ShowedTime4 = datetime_obj + timedelta(minutes=5)
    # st.write("銘柄コード：",code,"時刻",ShowedTime4)
    # st.table(ItaResize(df.loc[ShowedTime4],ItaSize_str_).style.set_table_styles(styles1).format(custom_format1).format(custom_format2))
    pass
with col5:
    pass
    # ShowedTime5 = datetime_obj + timedelta(minutes=10)
    # st.write("銘柄コード：",code,"時刻",ShowedTime5)
    # st.table(ItaResize(df.loc[ShowedTime5],ItaSize_str_).style.set_table_styles(styles1).format(custom_format1).format(custom_format2))


# # セクション2
# st.header("セクション2")
# st.write("ここに別の内容を記述します。")

st.write("電力")
#dfは9000sのみ
l_denryoku = ["9501","9503","9508","9509"]
# p_9000 = pathlib.Path(seachfile("9101",l2,date_str))
# df_9000 = pd.read_parquet(p_9000)
col1,col2,col3,col4,col5 = st.columns(5)
st.markdown(hide_table_row_index, unsafe_allow_html=True)
with col1:
    code1 = l_denryoku[0]
    ShowedTime1 = datetime_obj
    Ita1 = ItaResize(df_9000.loc[code1].loc[ShowedTime1],ItaSize_str_)
    try:
        st.write("銘柄コード：",code1,"時刻",ShowedTime1)
        st.table(Ita1[0].style.set_table_styles(styles2).format(custom_format1).format(custom_format2))
        st.table(Ita1[1].style.set_table_styles(styles2).format(custom_format1_2))
    except:
        st.write("時刻データなし")

with col2:
    code2 = l_denryoku[1]
    ShowedTime2 = datetime_obj
    Ita2 = ItaResize(df_9000.loc[code2].loc[ShowedTime1],ItaSize_str_)
    try:
        st.write("銘柄コード：",code2,"時刻",ShowedTime2)
        st.table(Ita2[0].style.set_table_styles(styles2).format(custom_format1).format(custom_format2))
        st.table(Ita2[1].style.set_table_styles(styles2).format(custom_format1_2))
    except:
        st.write("時刻データなし")

with col3:
    code3 = l_denryoku[2]
    ShowedTime3 = datetime_obj
    Ita3 = ItaResize(df_9000.loc[code3].loc[ShowedTime1],ItaSize_str_)
    try:
        st.write("銘柄コード：",code3,"時刻",ShowedTime3)
        st.table(Ita3[0].style.set_table_styles(styles2).format(custom_format1).format(custom_format2))
        st.table(Ita3[1].style.set_table_styles(styles2).format(custom_format1_2))
    except:
        st.write("時刻データなし")

with col4:
    code4 = l_denryoku[3]
    ShowedTime4 = datetime_obj
    Ita4 = ItaResize(df_9000.loc[code4].loc[ShowedTime1],ItaSize_str_)
    try:
        st.write("銘柄コード：",code4,"時刻",ShowedTime3)
        st.table(Ita4[0].style.set_table_styles(styles2).format(custom_format1).format(custom_format2))
        st.table(Ita4[1].style.set_table_styles(styles2).format(custom_format1_2))
    except:
        st.write("時刻データなし")
with col5:
    code5 = l_denryoku[4]
    ShowedTime5 = datetime_obj
    Ita5 = ItaResize(df_9000.loc[code5].loc[ShowedTime1],ItaSize_str_)
    try:
        st.write("銘柄コード：",code5,"時刻",ShowedTime3)
        st.table(Ita5[0].style.set_table_styles(styles2).format(custom_format1).format(custom_format2))
        st.table(Ita5[1].style.set_table_styles(styles2).format(custom_format1_2))
    except:
        st.write("時刻データなし")












#col6.dataframe(ItaResize(df.loc["2024-05-22 09:25:00"]),hide_index=True, width=100, height=150)

# import streamlit as st
# from memory_profiler import memory_usage
# import pandas as pd
# import time

# # メモリ使用状況を測定する関数
# def measure_memory(func):
#     mem_usage = memory_usage(func, interval=0.1, timeout=1)
#     return mem_usage


# # データフレームを表示する関数
# def display_dataframe(df, time_str):
#     col1,col2,col3,col4,col5,col6 = st.columns(6)
#     col1.dataframe(df.loc["1301"].loc[time_str])
#     col2.dataframe(df.loc["1301"].loc[time_str])
#     col3.dataframe(df.loc["1301"].loc[time_str])
#     col4.dataframe(df.loc["1301"].loc[time_str])
#     col5.dataframe(df.loc["1301"].loc[time_str])
#     col6.dataframe(df.loc["1301"].loc[time_str])

# # メモリ使用状況を測定
# mem_usage_load = measure_memory(load_dataframe)
# df = load_dataframe(file_)

# # 各時間帯のデータフレームを表示し、その都度メモリ使用状況を測定
# times = ["2024-05-22 09:00:00", "2024-05-22 09:05:00", "2024-05-22 09:10:00", "2024-05-22 09:15:00", "2024-05-22 09:20:00", "2024-05-22 09:25:00"]
# for time_str in times:
#     mem_usage_display = measure_memory(lambda: display_dataframe(df, time_str))
#     display_dataframe(df, time_str)

#     # メモリ使用状況を表示
#     st.line_chart(mem_usage_load + mem_usage_display)

#アップロードリスト
# with st.expander("じぶんの銘柄リストから絞込む"):
#     st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">1列目に銘柄コードが来るように記載ください。文字列は無視されます。</p>', unsafe_allow_html=True)
#     st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">活用例：四季報・株探などファンダで絞込んだリスト／自分の取引銘柄など</p>', unsafe_allow_html=True)
#     uploaded_file = st.file_uploader("マイリストアップロード", type='csv')
#     if uploaded_file is not None:
#         upload_df = pd.read_csv(uploaded_file)
#         mycode_lists_org = upload_df.iloc[:,0]
#         mycode_lists = [int(s) for s in mycode_lists_org if is_int(s)]
#         mylist_button = st.radio("マイリストでの絞込み",    ('無', '有'), horizontal=True)

#         if mylist_button =='有':
#             for code in mycode_lists:
#                 df_Ita = df.loc[code].loc["2024-05-22 09:50:00"]
#                 st.dataframe(df_Ita,use_container_width=True)




#screening_file = p
#df = pd.read_excel(screening_file,sheet_name="Sheet1",index_col=0 )

# #ローカル用
# file_ = nb_path_date+"/"+"240522_df_dayIta_all.parquet"
# df = pd.read_parquet(file_)
# update_date = os.path.basename(screening_file).replace("_df_dayIta_all.parquet","")
# st.write("データ更新日：" + update_date)



# method_menu = ["Granvil", "PerfectOrder", "全モ", "All Data"]
# method = option_menu("手法選択", options= method_menu,
#     #icons=['house', 'gear', 'gear'],
#     menu_icon="cast", default_index=0, orientation="horizontal")

# #アップロードリスト
# with st.expander("じぶんの銘柄リストから絞込む"):
#     st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">1列目に銘柄コードが来るように記載ください。文字列は無視されます。</p>', unsafe_allow_html=True)
#     st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">活用例：四季報・株探などファンダで絞込んだリスト／自分の取引銘柄など</p>', unsafe_allow_html=True)
#     uploaded_file = st.file_uploader("マイリストアップロード", type='csv')
#     if uploaded_file is not None:
#         upload_df = pd.read_csv(uploaded_file)
#         mycode_lists_org = upload_df.iloc[:,0]
#         mycode_lists = [int(s) for s in mycode_lists_org if is_int(s)]
#         mylist_button = st.radio("マイリストでの絞込み",    ('無', '有'), horizontal=True)

#         if mylist_button =='有':
#             df = df[df['ticker'].isin(mycode_lists)]

# st.divider()
# st.markdown('<p style="font-family:sans-serif; color:black; font-size: 20px;">テクニカル</p>', unsafe_allow_html=True)
# st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">プライスアクション・移動平均線</p>', unsafe_allow_html=True)
# default_button = st.radio("設定例",    ('Granvil_example', 'PerfectOrder_example'),horizontal=True)
# st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">デモ用にSMA5,25,75の設定にしています。</p>', unsafe_allow_html=True)


# col1,col2,col3 = st.columns([1,2,1])

# #マルチセレクトで抽出可能なカラムから選択肢を作成
# multi_selectbox_columns = df.filter(like="R@",axis=1).columns
# select_option = sorted(list(df[multi_selectbox_columns].stack().unique()))

# multi_selectbox_columns2 = df.filter(like="MA@",axis=1).columns
# SO2 = sorted(list(df[multi_selectbox_columns2].stack().unique()))

# so2 = ([s for s in SO2 if '傾き正' in s]
#         +[s for s in SO2 if 'V字に反転' in s]
#         +[s for s in SO2 if '収束' in s]
#         +[s for s in SO2 if '乖離小' in s]
#         +[s for s in SO2 if 'ローソク足内' in s]
#         +[s for s in SO2 if '下髭内' in s]
#         +[s for s in SO2 if '連日推移' in s]
#         +[s for s in SO2 if 'PO' in s]
#         +[s for s in SO2 if '>' in s])

# select_option2 = so2 + list(set(SO2) - set(so2))

# multi_selectbox_columns3 = df.filter(like="Vol@",axis=1).columns
# select_option3 = sorted(list(df[multi_selectbox_columns3].stack().unique()))



# if default_button =='Granvil_example':
#   with col1:
#       mul_sel = st.multiselect("ローソク足・プライスアクション", (select_option),default=["陽線"],key="multiselect") #選択項目

#   with col2:
#       mul_sel2 = st.multiselect("移動平均線との関係", (select_option2),default=["SMA25:傾き正","SMA25 > 75","SMA5:V字に反転"],key="multiselect2")#選択項目

#   with col3:
#       mul_sel3 = st.multiselect("出来高", (select_option3),default=["出来高前日比プラス"],key="multiselect3")#選択項目

# elif default_button =='PerfectOrder_example':
#   with col1:
#       mul_sel = st.multiselect("ローソク足・プライスアクション", (select_option),default=["当日下髭"],key="multiselect") #選択項目
#   with col2:
#       mul_sel2 = st.multiselect("移動平均線との関係", (select_option2),default=["SMA5,25,75_PO_start"],key="multiselect2")#選択項目
#   with col3:
#       mul_sel3 = st.multiselect("出来高", (select_option3),key="multiselect3")#選択項目

# # else:
# #   with col1:
# #       mul_sel = st.multiselect("ローソク足・プライスアクション", (select_option),default=["陽線"],key="multiselect") #選択項目
# #   with col2:
# #       mul_sel2 = st.multiselect("移動平均線との関係", (select_option2),default=["SMA25:傾き正","SMA25 > 75"],key="multiselect2")#選択項目
# #   with col3:
# #       mul_sel3 = st.multiselect("出来高", (select_option3),default=["出来高前日比プラス"],key="multiselect3")#選択項目



# st.button("Clear selection", on_click=clear_multi)
# st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">設定変更後にdefault条件に戻したい場合はブラウザを再読込みしてください。<br>その場合Storage Listも初期化されます。</p>', unsafe_allow_html=True)


# #選択された項目
# mul_sel_all = mul_sel + mul_sel2 + mul_sel3

# #選択された項目を含む列
# select_columns = df.columns[df.isin(mul_sel).sum(axis=0)>0].tolist() + df.columns[df.isin(mul_sel2).sum(axis=0)>0].tolist() + df.columns[df.isin(mul_sel3).sum(axis=0)>0].tolist()

# #押しの深さ
# dip_slider_bottun = st.radio("押しの深さ", (["下落幅%(5日間の高値)","下落幅%(25日間の高値)","全モ下落幅%"]),horizontal=True)
# if dip_slider_bottun != "全モ下落幅%":
#     dip_slider_list = [round(df[dip_slider_bottun].quantile(i),1) for i in np.linspace(0,1,21)]
#     dip_slider=st.select_slider("指定範囲/※分位数での5%区切り", options=dip_slider_list,value=(dip_slider_list[0],dip_slider_list[-1]))
# else:
#     dip_slider_list = [round(df[(df["全モ"]==1)][dip_slider_bottun].quantile(i),1) for i in np.linspace(0,1,21)]
#     dip_slider=st.select_slider("指定範囲/※分位数での5%区切り", options=dip_slider_list,value=(dip_slider_list[0],dip_slider_list[-1]))


# #ソート
# st.divider()
# st.markdown('<p style="font-family:sans-serif; color:black; font-size: 20px;">その他項目</p>', unsafe_allow_html=True)
# col4,col5,col6 = st.columns([2,3,2])

# with col4:
#     sort_option = ["ticker","close","volume","vol/sigma"]
#     sort1 = st.radio("並替基準", (sort_option),horizontal=True) #先頭がdefault
#     sort2 = st.radio("昇順・降順", (["昇順","降順"]),horizontal=True)

# with col5:
#     #スライダー
#     slider_bottun = st.radio("数値項目", (["close","volume","vol/sigma"]),horizontal=True)
#     slider_list = [round(df[slider_bottun].quantile(i),1) for i in np.linspace(0,1,21)]
#     slider=st.select_slider("指定範囲/※分位数での5%区切り", options=slider_list,value=(slider_list[0],slider_list[-1]))

# with col6:
#     #その他
#     EPS_growth = st.radio("売上高/EPS成長率(予)(%)", (["全データ","未発表は含まない"]),horizontal=True)
#     if EPS_growth == "未発表は含まない":
#         growth =(df["EPS成長率(予)(%)"] != "未")
#     else:
#         growth =(df["EPS成長率(予)(%)"] != "") #ダミー

#     #値上がり率ランキング
#     rank =st.radio("値上り/値下り率ランキング", (["全データ","上位(10日以内)","上位(25日以内)"]),horizontal=True)
#     if rank != "全データ":
#         rank_tag = (df["値上り/値下り率" + rank] == 1)
#     else:
#         rank_tag = (df["値上り/値下り率上位(10日以内)"] != "") #ダミー

# st.markdown("---")


# with st.expander('条件をtxtファイルに保存・貼付け'):
#     if len(mul_sel_all)>0:
#         text_contents = str(method) + "/" + str(mul_sel_all)
#         st.download_button(label='条件をtxtファイルに保存', data = text_contents ,file_name='condition.txt',mime='text/csv',)
#     else:
#         st.info('条件を設定するとダウンロードボタンが出ます', icon="ℹ️")

#     input_condition =st.text_input('保存したtxtファイルの文字列を貼付けてください', '', key = "input_txt")
#     st.button("Clear input text", on_click=clear_input)
#     st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">記載形式を間違えるとエラーとなります。</p>', unsafe_allow_html=True)

#     if len(input_condition)>0:
#         #文字列から条件を切り出し
#         method = input_condition.split("/")[0].split(",")[0]
#         mul_sel_all = eval(input_condition.split("/")[1])

#         #選択された項目を含む列
#         select_columns = df.columns[df.isin(mul_sel_all).sum(axis=0)>0].tolist()

# #選択された項目で抽出したデータフレーム

# if method == "All Data" :
#     if sort2 == "昇順":
#         #data = df[(df[select_columns].isin(mul_sel_all).sum(axis=1)==len(select_columns))].drop(multi_selectbox_columns, axis=1).drop(multi_selectbox_columns2, axis=1).drop(multi_selectbox_columns3, axis=1).drop(method_menu, axis=1, errors='ignore')
#         data = df[(df[select_columns].isin(mul_sel_all).sum(axis=1)==len(select_columns))][growth][rank_tag][(slider[0] < df[slider_bottun])&(df[slider_bottun]< slider[1])][(dip_slider[0] < df[dip_slider_bottun])&(df[dip_slider_bottun]< dip_slider[1])].drop(multi_selectbox_columns, axis=1).drop(multi_selectbox_columns2, axis=1).drop(multi_selectbox_columns3, axis=1).drop(method_menu, axis=1, errors='ignore').drop(["全モ日数","下落幅%(5日間の高値)","下落幅%(25日間の高値)","全モ下落幅%","値上り/値下り率上位(10日以内)","値上り/値下り率上位(25日以内)"], axis=1, errors='ignore').sort_values(sort1)
#     else:
#         data = df[(df[select_columns].isin(mul_sel_all).sum(axis=1)==len(select_columns))][growth][rank_tag][(slider[0] < df[slider_bottun])&(df[slider_bottun]< slider[1])][(dip_slider[0] < df[dip_slider_bottun])&(df[dip_slider_bottun]< dip_slider[1])].drop(multi_selectbox_columns, axis=1).drop(multi_selectbox_columns2, axis=1).drop(multi_selectbox_columns3, axis=1).drop(method_menu, axis=1, errors='ignore').drop(["全モ日数","下落幅%(5日間の高値)","下落幅%(25日間の高値)","全モ下落幅%","値上り/値下り率上位(10日以内)","値上り/値下り率上位(25日以内)"], axis=1, errors='ignore').sort_values(sort1, ascending=False)
# else:
#     if sort2 == "昇順":
#         #data = df[(df[method]>0)&(df[select_columns].isin(mul_sel_all).sum(axis=1)==len(select_columns))].drop(multi_selectbox_columns, axis=1).drop(multi_selectbox_columns2, axis=1).drop(multi_selectbox_columns3, axis=1).drop(method_menu, axis=1, errors='ignore')
#         data = df[(df[method]>0)&(df[select_columns].isin(mul_sel_all).sum(axis=1)==len(select_columns))][growth][rank_tag][(slider[0] < df[slider_bottun])&(df[slider_bottun]< slider[1])][(dip_slider[0] < df[dip_slider_bottun])&(df[dip_slider_bottun]< dip_slider[1])].drop(multi_selectbox_columns, axis=1).drop(multi_selectbox_columns2, axis=1).drop(multi_selectbox_columns3, axis=1).drop(method_menu, axis=1, errors='ignore').drop(["全モ日数","下落幅%(5日間の高値)","下落幅%(25日間の高値)","全モ下落幅%","値上り/値下り率上位(10日以内)","値上り/値下り率上位(25日以内)"], axis=1, errors='ignore').sort_values(sort1)
#     else:
#         data = df[(df[method]>0)&(df[select_columns].isin(mul_sel_all).sum(axis=1)==len(select_columns))][growth][rank_tag][(slider[0] < df[slider_bottun])&(df[slider_bottun]< slider[1])][(dip_slider[0] < df[dip_slider_bottun])&(df[dip_slider_bottun]< dip_slider[1])].drop(multi_selectbox_columns, axis=1).drop(multi_selectbox_columns2, axis=1).drop(multi_selectbox_columns3, axis=1).drop(method_menu, axis=1, errors='ignore').drop(["全モ日数","下落幅%(5日間の高値)","下落幅%(25日間の高値)","全モ下落幅%","値上り/値下り率上位(10日以内)","値上り/値下り率上位(25日以内)"], axis=1, errors='ignore').sort_values(sort1, ascending=False)

# st.subheader('データリスト:' + str(len(data)) + "銘柄")
# st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">20個程度まで絞ってください。キリバンや出来高偏差のフィルタには表内機能で可能です。<br>ソートも可能ですが、ChartBarの順番には反映されません。</p>', unsafe_allow_html=True)


# gb = GridOptionsBuilder.from_dataframe(data)
# #gb.configure_grid_options(rowHeight=30)
# #https://www.ag-grid.com/javascript-data-grid/column-groups/
# gb.configure_side_bar()
# gb.configure_pagination(paginationPageSize=30)
# gb.configure_selection(selection_mode = 'multiple', use_checkbox=True)
# gb.configure_default_column(filterable=True,sortable=True,enablePivot = False, enableValue = False)
# gb.configure_column("ticker", headerCheckboxSelection = True, headerCheckboxSelectionFilteredOnly=True)#めちゃ大事

# gridOptions = gb.build()
# selects =AgGrid(data,theme="streamlit",
#     gridOptions=gridOptions,
#     fit_columns_on_grid_load=True
#     ).selected_rows


# #data = grid_response['data']
# #selects = grid_response['selected_rows']


# num=len(selects)

# if "storage_list" not in st.session_state:
#   st.session_state["storage_list"] = []

# with st.sidebar:
#     st.header("Storage List")
#     st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">リストの確認とダウンロード</p>', unsafe_allow_html=True)
#     if st.button(label="show"):
#         storaged_data = [code for code in st.session_state["storage_list"]]
#         storage_df = df.copy().set_index("ticker").loc[storaged_data][["name"]]
#         st.table(storage_df)

#         storage_df["Kabutan"]=[f"https://kabutan.jp/stock/chart?code={code_}" for code_ in storage_df.index.tolist()]


#         if len(storage_df)>0:
#             st.download_button(
#                 label="Download data as CSV",
#                 data=storage_df.to_csv().encode('shift_jis'),
#                 file_name='selected.csv',
#                 mime='text/csv',
#                 )

#     st.header("Chart Bar")
#     st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">サイドバーのサイズでチャートサイズを変えられます<br>他のMAの組合せや詳細を確認したいときはKabutanURLへ</p>', unsafe_allow_html=True)
#     if num > 0 :

#         for i, selcect in enumerate(selects):
#             code = selects[i]["ticker"]
#             stock_name = selects[i]["name"]
#             Kessan_schedule = selects[i]["決算発表日"]

#             st.write(f"{code} {stock_name}",f"([株探](https://kabutan.jp/stock/chart?code={code})/[TradingView](https://jp.tradingview.com/chart/?symbol=TSE%3A{code}))")

#             if Kessan_schedule is not None :
#                 st.write(f"決算発表日(予) {Kessan_schedule}")
#                 st.markdown('<p style="font-family:sans-serif; color:blue; font-size: 10px;">予定日は掲載後に変更される可能性があります。</p>', unsafe_allow_html=True)
#             else:
#                 Kessan_schedule = "未定"
#                 st.write(f"決算発表日(予) {Kessan_schedule}")

#             img=f"https://www.kabudragon.com/chart/s={code}/e={update_date}.png/"
#             cache_image(img) #cache

#             #html_code =  f'<iframe src="//www.invest-jp.net/blogparts/stocharmini/{code}/d/1/160" width="160" height="300" style="border:none;margin:0;" scrolling="no"></iframe><div style="font-size:7pt;">by <a href="https://www.invest-jp.net/" target="_blank">株価チャート</a>「ストチャ」</div>'
#             #stc.html(html_code,height = 500)

#             if st.button(label=f"Storage / Remove {code}"):
#                 if code not in st.session_state["storage_list"]:
#                     st.session_state["storage_list"].append(code)
#                     storaged_data = [code for code in st.session_state["storage_list"]]
#                     st.write(str(storaged_data))
#                 else:
#                     st.session_state["storage_list"].remove(code)
#                     st.write(str(code) + "removed!")
#                     storaged_data = [code for code in st.session_state["storage_list"]]
#                     st.write(str(storaged_data))
#     else:
#         pass

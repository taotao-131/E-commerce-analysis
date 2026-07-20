import streamlit as st
import pandas as pd
import os


# =====================
# 页面设置
# =====================

st.set_page_config(
    page_title="电商用户行为分析系统",
    layout="wide"
)


# =====================
# 获取项目根目录
# =====================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)



DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)


# =====================
# 页面标题
# =====================

st.title("🛒 电商用户行为分析系统")

st.write(
    "基于淘宝用户行为数据的数据分析平台"
)


# =====================
# 加载用户画像
# =====================

user_profile_path = os.path.join(
    DATA_DIR,
    "user_profile.csv"
)


if os.path.exists(user_profile_path):

    user_profile = pd.read_csv(
        user_profile_path
    )

else:

    st.error(
        "没有找到 user_profile.csv，请检查 data 文件夹"
    )

    st.stop()



# =====================
# 用户指标
# =====================

st.subheader("📊 用户概况")


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "用户总数",
        len(user_profile)
    )


with col2:

    high_value = (
        user_profile['level']
        == "高价值用户"
    ).sum()


    st.metric(
        "高价值用户",
        high_value
    )


with col3:

    potential = (
        user_profile['level']
        == "潜力用户"
    ).sum()


    st.metric(
        "潜力用户",
        potential
    )



# =====================
# 用户价值分布
# =====================

st.subheader(
    "👥 用户价值分布"
)


level_count = (
    user_profile['level']
    .value_counts()
)


st.bar_chart(
    level_count
)



# =====================
# 热门商品
# =====================

st.subheader(
    "🔥 热门商品TOP10"
)


top_items_path = os.path.join(
    DATA_DIR,
    "top10_items.csv"
)



if os.path.exists(top_items_path):

    top_items = pd.read_csv(
        top_items_path
    )


    st.bar_chart(
        top_items
    )


else:

    st.warning(
        "暂未找到 top10_items.csv"
    )



# =====================
# 用户画像展示
# =====================

st.subheader(
    "用户画像数据预览"
)


st.dataframe(
    user_profile.head(20)
)# =====================
# 用户行为分析
# =====================

st.subheader(
    "📈 用户行为分布"
)


behavior_count = pd.read_csv(
    os.path.join(
        DATA_DIR,
        "behavior_count.csv"
    )
)


st.bar_chart(
    behavior_count.set_index("behavior")
)
st.subheader(
    "🛒 购买转化率"
)


pv_count = 89716263
buy_count = 2015839


conversion_rate = (
    buy_count / pv_count * 100
)


st.metric(
    "浏览到购买转化率",
    f"{conversion_rate:.2f}%"
)
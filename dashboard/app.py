from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="电商用户行为分析", page_icon="🛒", layout="wide")

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    behavior = pd.read_csv(DATA_DIR / "behavior_count.csv")
    top_items = pd.read_csv(DATA_DIR / "top10_items.csv")

    required_behavior_columns = {"behavior", "count"}
    required_item_columns = {"item_id", "pv_count"}
    if not required_behavior_columns.issubset(behavior.columns):
        raise ValueError("behavior_count.csv 必须包含 behavior 和 count 两列。")
    if not required_item_columns.issubset(top_items.columns):
        raise ValueError("top10_items.csv 必须包含 item_id 和 pv_count 两列。")

    behavior["count"] = pd.to_numeric(behavior["count"], errors="raise")
    top_items["pv_count"] = pd.to_numeric(top_items["pv_count"], errors="raise")
    return behavior, top_items


def format_number(value: int | float) -> str:
    return f"{value:,.0f}"


st.title("🛒 电商用户行为分析")
st.caption("基于用户行为汇总数据，快速查看转化路径与热门商品表现。")

try:
    behavior_data, top_items_data = load_data()
except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
    st.error(f"数据加载失败：{error}")
    st.stop()

behavior_labels = {"pv": "浏览", "fav": "收藏", "cart": "加购", "buy": "购买"}
behavior_data["行为"] = behavior_data["behavior"].map(behavior_labels).fillna(behavior_data["behavior"])
counts = behavior_data.set_index("behavior")["count"]
page_views = int(counts.get("pv", 0))
purchases = int(counts.get("buy", 0))
carts = int(counts.get("cart", 0))
conversion_rate = purchases / page_views if page_views else 0
cart_conversion_rate = purchases / carts if carts else 0

metric_columns = st.columns(4)
metric_columns[0].metric("总行为次数", format_number(behavior_data["count"].sum()))
metric_columns[1].metric("浏览次数", format_number(page_views))
metric_columns[2].metric("购买次数", format_number(purchases))
metric_columns[3].metric("浏览至购买转化率", f"{conversion_rate:.2%}")

left_column, right_column = st.columns(2)
with left_column:
    st.subheader("行为分布")
    behavior_chart = px.bar(
        behavior_data,
        x="行为",
        y="count",
        color="行为",
        text_auto=",.0f",
        labels={"count": "次数", "行为": "行为类型"},
    )
    behavior_chart.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(behavior_chart, use_container_width=True)

with right_column:
    st.subheader("购买转化漏斗")
    funnel_order = ["pv", "fav", "cart", "buy"]
    funnel_data = pd.DataFrame(
        {
            "行为": [behavior_labels[item] for item in funnel_order if item in counts],
            "次数": [int(counts[item]) for item in funnel_order if item in counts],
        }
    )
    funnel_chart = px.funnel(funnel_data, y="行为", x="次数", text="次数")
    funnel_chart.update_layout(margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(funnel_chart, use_container_width=True)

st.subheader("转化洞察")
insight_columns = st.columns(3)
insight_columns[0].metric("加购至购买转化率", f"{cart_conversion_rate:.2%}")
insight_columns[1].metric("加购行为占比", f"{carts / page_views:.2%}" if page_views else "暂无数据")
insight_columns[2].metric("收藏行为占比", f"{int(counts.get('fav', 0)) / page_views:.2%}" if page_views else "暂无数据")

st.subheader("热门商品 Top 10")
top_items_display = top_items_data.sort_values("pv_count", ascending=False).copy()
top_items_display["item_id"] = top_items_display["item_id"].astype(str)
items_chart = px.bar(
    top_items_display,
    x="pv_count",
    y="item_id",
    orientation="h",
    text_auto=",.0f",
    labels={"pv_count": "浏览次数", "item_id": "商品 ID"},
)
items_chart.update_layout(yaxis={"categoryorder": "total ascending"}, margin=dict(t=20, b=20, l=20, r=20))
st.plotly_chart(items_chart, use_container_width=True)

with st.expander("查看原始汇总数据"):
    st.dataframe(behavior_data[["行为", "count"]], use_container_width=True, hide_index=True)
    st.dataframe(top_items_display, use_container_width=True, hide_index=True)

st.download_button(
    "下载热门商品数据",
    data=top_items_display.to_csv(index=False).encode("utf-8-sig"),
    file_name="top10_items.csv",
    mime="text/csv",
)

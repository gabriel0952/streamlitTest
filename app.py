import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import unquote
import json

# 設置頁面配置
st.set_page_config(
    page_title="圖表生成器",
    layout="wide",
    initial_sidebar_state="expanded"
)

def parse_data(data_str):
    if not data_str:
        return None
    try:
        return json.loads(unquote(data_str))
    except json.JSONDecodeError:
        try:
            return pd.read_csv(pd.compat.StringIO(unquote(data_str))).to_dict(orient='list')
        except Exception as e:
            st.error(f"無法解析數據: {str(e)}")
            return None

def create_chart(chart_type, data):
    if data is None:
        return None
    
    df = pd.DataFrame(data)
    
    if df.empty:
        st.error("數據為空")
        return None
    
    # 設置圖表主題和樣式
    template = "plotly_white"
    color_sequence = px.colors.qualitative.Pastel
    
    if chart_type == 'pie':
        if len(df.columns) < 2:
            st.error("餅圖需要至少兩列數據")
            return None
        fig = px.pie(
            df,
            values=df.columns[1],
            names=df.columns[0],
            template=template,
            color_discrete_sequence=color_sequence
        )
    elif chart_type in ['line', 'curve']:
        if len(df.columns) < 2:
            st.error("線圖需要至少兩列數據")
            return None
        fig = px.line(
            df,
            x=df.columns[0],
            y=df.columns[1:],
            template=template,
            color_discrete_sequence=color_sequence
        )
        if chart_type == 'curve':
            fig.update_traces(mode='lines+markers', line_shape='spline')
    elif chart_type == 'bar':
        if len(df.columns) < 2:
            st.error("條形圖需要至少兩列數據")
            return None
        fig = px.bar(
            df,
            x=df.columns[0],
            y=df.columns[1:],
            template=template,
            color_discrete_sequence=color_sequence
        )
    elif chart_type == 'scatter':
        if len(df.columns) < 2:
            st.error("散點圖需要至少兩列數據")
            return None
        fig = px.scatter(
            df,
            x=df.columns[0],
            y=df.columns[1],
            template=template,
            color_discrete_sequence=color_sequence
        )
    else:
        st.error(f"不支持的圖表類型: {chart_type}")
        return None
    
    # 更新圖表布局
    fig.update_layout(
        font_family="sans serif",
        title_font_family="sans serif",
        title_font_color="#262730",
        legend_title_font_color="#262730",
        legend_title_font_size=12,
        legend_font_size=11,
        margin=dict(t=50, l=50, r=50, b=50)
    )
    
    # 更新軸線樣式
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='#E0E0E0',
        linecolor='#E0E0E0',
        linewidth=1
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='#E0E0E0',
        linecolor='#E0E0E0',
        linewidth=1
    )
    
    return fig

def main():
    params = st.query_params
    data_str = params.get('data', '')
    initial_chart_type = params.get('type', 'bar')
    
    default_data = {
        "類別": ["A", "B", "C", "D", "E"],
        "數值": [23, 45, 56, 78, 90]
    }
    
    st.sidebar.title("圖表設置")
    chart_type = st.sidebar.selectbox(
        "選擇圖表類型",
        ["bar", "line", "curve", "pie", "scatter"],
        index=["bar", "line", "curve", "pie", "scatter"].index(initial_chart_type),
        format_func=lambda x: {
            'bar': '長條圖',
            'line': '折線圖',
            'curve': '曲線圖',
            'pie': '圓餅圖',
            'scatter': '散點圖'
        }.get(x, x)
    )
    
    if data_str:
        data = parse_data(data_str)
    else:
        data = default_data
        st.info("使用默認數據。您可以通過 URL 參數提供自己的數據。")
        st.caption("例如: ?data={\"類別\":[\"A\",\"B\",\"C\"],\"數值\":[30,50,20]}&type=pie")
    
    if data:
        fig = create_chart(chart_type, data)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.sidebar.title("當前設置")
    with st.sidebar.expander("數據內容", expanded=False):
        if data_str:
            st.json(json.loads(unquote(data_str)))
        else:
            st.info("使用默認數據")
    
    st.sidebar.info(f"圖表類型：{chart_type}")

if __name__ == "__main__":
    main()
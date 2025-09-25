import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import platform

# 한글 폰트 설정
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin': # Mac
    plt.rc('font', family='AppleGothic')
else: # Linux
    plt.rc('font', family='NanumGothic')

# 마이너스 폰트 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

# Load Data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('경제활동_통합.csv')
        return df
    except FileNotFoundError:
        st.error("'경제활동_통합.csv' 파일을 찾을 수 없습니다. app.py와 같은 폴더에 있는지 확인해주세요.")
        return None

df = load_data()

if df is not None:
    st.title("대한민국 경제활동 데이터 분석")

    # --- Sidebar Filters ---
    st.sidebar.header("데이터 필터")

    # Year filter
    all_years = sorted(df['년도'].unique())
    selected_years = st.sidebar.multiselect('년도 선택', all_years, default=all_years)

    # Region filter
    # '계' is the total, might want to exclude it from default selection for clearer comparison
    all_regions = sorted(df['지역'].unique())
    default_regions = [region for region in all_regions if region != '계']
    selected_regions = st.sidebar.multiselect('지역 선택', all_regions, default=default_regions)

    # Filter dataframe based on selection
    filtered_df = df[(df['년도'].isin(selected_years)) & (df['지역'].isin(selected_regions))]

    # --- Main Page ---

    st.header("필터링된 데이터")
    st.write(f"총 {len(filtered_df)}개의 데이터")
    st.dataframe(filtered_df)

    # --- Key Statistics ---
    with st.expander("📈 주요 통계 보기"):
        st.write(filtered_df.describe())

    st.header("데이터 시각화")

    # --- Bar Chart ---
    with st.container():
        st.subheader("📊 지역별 데이터 비교 (막대 그래프)")
        
        # Ensure there's data to plot
        if not filtered_df.empty and len(selected_years) > 0:
            # Select metric for bar chart
            bar_metric = st.selectbox(
                '비교할 지표를 선택하세요:',
                ['경제활동인구 (천명)', '취업자 (천명)', '실업자 (천명)'],
                key='bar_metric'
            )
            
            # Select a single year for comparison
            comp_year = st.selectbox('비교할 연도를 선택하세요:', selected_years, key='comp_year')

            year_df = filtered_df[filtered_df['년도'] == comp_year]

            if not year_df.empty:
                fig, ax = plt.subplots(figsize=(12, 8))
                sns.barplot(data=year_df, x='지역', y=bar_metric, ax=ax)
                plt.xticks(rotation=45, ha='right')
                plt.title(f'{comp_year}년 지역별 {bar_metric}')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("선택한 연도에 대한 데이터가 없습니다.")
        else:
            st.info("데이터를 먼저 선택해주세요.")


    # --- Line Chart ---
    with st.container():
        st.subheader("📉 연도별 추세 분석 (라인 그래프)")
        
        if not filtered_df.empty and len(selected_regions) > 0:
            # Select metric for line chart
            line_metric = st.selectbox(
                '분석할 지표를 선택하세요:',
                ['경제활동인구 (천명)', '취업자 (천명)', '실업자 (천명)'],
                key='line_metric'
            )
            
            # Select a single region for trend analysis
            trend_region = st.selectbox('분석할 지역을 선택하세요:', selected_regions, key='trend_region')

            region_df = filtered_df[filtered_df['지역'] == trend_region]

            if not region_df.empty:
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.lineplot(data=region_df, x='년도', y=line_metric, marker='o', ax=ax)
                plt.title(f'{trend_region}의 연도별 {line_metric} 변화 추이')
                plt.xticks(sorted(region_df['년도'].unique())) # Ensure all years are shown as ticks
                plt.grid(True)
                st.pyplot(fig)
            else:
                st.warning("선택한 지역에 대한 데이터가 없습니다.")
        else:
            st.info("데이터를 먼저 선택해주세요.")


    # --- Correlation Heatmap ---
    with st.container():
        st.subheader("🔥 상관관계 히트맵")
        
        if not filtered_df.empty:
            # Select only numeric columns for correlation
            numeric_cols = filtered_df.select_dtypes(include=['number']).columns.tolist()
            
            if len(numeric_cols) > 1:
                corr = filtered_df[numeric_cols].corr()
                
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
                plt.title('주요 지표 간 상관관계')
                st.pyplot(fig)
            else:
                st.warning("상관관계를 계산하기에 숫자 열이 부족합니다.")
        else:
            st.info("데이터를 먼저 선택해주세요.")

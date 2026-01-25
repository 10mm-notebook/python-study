import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# --- 1. 기본 페이지 설정 ---
st.set_page_config(page_title="AI 주식 분석기", layout="wide")
st.title("🤖 AI 기반 K-Means & t-SNE 주식 유형 분석")
st.write("KOSPI 재무 지표 데이터를 기반으로 주식들을 자동 그룹화하고, AI 애널리스트가 각 그룹의 특징과 투자 전략을 분석해줍니다.")

# --- 2. 사이드바 ---
with st.sidebar:
    st.header("1. OpenAI API 키")
    # 환경변수에서 API 키 읽기 (우선순위)
    env_api_key = os.getenv("OPENAI_API_KEY")
    
    if env_api_key and env_api_key != "your_openai_api_key_here":
        st.info("✅ .env 파일에서 API 키를 불러왔습니다.")
        api_key = env_api_key
    else:
        api_key = st.text_input("OpenAI API 키를 입력하세요.", type="password", help="API 키는 분석에만 사용되며 저장되지 않습니다. 또는 .env 파일에 OPENAI_API_KEY를 설정할 수 있습니다.")
    
    st.header("2. 데이터 업로드")
    uploaded_file = st.file_uploader("CSV 파일을 업로드하세요.", type=["csv"])
    
    st.header("3. 군집화 설정")
    default_features = ['시가총액', '거래량', 'PER', 'ROE']
    available_features = []
    max_k = st.slider("Elbow Method 최대 K값", 2, 20, 10)
    
    # 특성 설명을 위한 딕셔너리
    feature_descriptions = {
        '시가총액': '기업의 총 가치를 나타내며, 주가에 총 발행 주식 수를 곱한 값입니다. 기업의 규모를 나타내는 대표적인 지표입니다.',
        '거래량': '특정 기간 동안 거래된 주식의 총량입니다. 시장의 관심도를 나타내며, 거래량이 많을수록 유동성이 풍부하다고 해석됩니다.',
        'PER': '주가수익비율 (Price-to-Earnings Ratio)로, 주가를 주당순이익(EPS)으로 나눈 값입니다. 기업의 수익성 대비 주가가 고평가되었는지 저평가되었는지 판단하는 지표입니다.',
        'ROE': '자기자본이익률 (Return on Equity)로, 기업이 자기자본을 이용하여 얼마나 효율적으로 이익을 창출했는지를 나타냅니다. 높을수록 수익성이 좋다고 평가됩니다.',
        'PBR': '주가순자산비율 (Price-to-Book Ratio)로, 주가를 주당순자산(BPS)으로 나눈 값입니다. 기업의 자산 가치 대비 주가 수준을 판단하는 데 사용됩니다.',
        'EPS': '주당순이익 (Earnings Per Share)으로, 기업의 순이익을 총 발행 주식 수로 나눈 값입니다. 1주당 창출하는 이익의 크기를 나타냅니다.',
        'DPS': '주당배당금 (Dividends Per Share)으로, 1주당 지급되는 배당금의 액수입니다. 기업의 주주 환원 정책을 보여주는 지표입니다.',
        'BPS': '주당순자산 (Book-value Per Share)으로, 기업의 총자산에서 부채를 뺀 순자산을 총 발행 주식 수로 나눈 값입니다. 기업의 재무 안정성을 나타냅니다.'
    }
    
    with st.expander("💡 각 Feature 설명 보기"):
        for feature, desc in feature_descriptions.items():
            st.markdown(f"**{feature}**: {desc}")

    st.info("**Pro-Tip:** '시가총액', '거래량' 등 규모 관련 특성을 제외하고 'PER', 'ROE' 등 질적 특성만으로 분석하면 새로운 관점의 그룹을 발견할 수 있습니다.")

    st.header("4. 데이터 정제 설정")
    remove_outliers_option = st.checkbox("이상치 자동 제거 (IQR 방식)", value=True)

# --- 3. 데이터 전처리 함수 ---
@st.cache_data
def preprocess_data(df, features_to_use, remove_outliers):
    df_clean = df[features_to_use].copy()
    for col in features_to_use:
        if df_clean[col].dtype == 'object':
            df_clean[col] = df_clean[col].str.replace(',', '', regex=False)
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

    df_clean.dropna(inplace=True)
    if df_clean.empty: return None, None, None, 0

    initial_rows = len(df_clean)
    if remove_outliers:
        # 이상치를 한 번에 모아서 제거하기 위한 로직
        outlier_indices = set()
        for col in features_to_use:
            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 2.5 * IQR
            upper_bound = Q3 + 2.5 * IQR
            # 해당 특성에서 이상치인 행의 인덱스를 찾음
            col_outliers = df_clean[(df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)].index
            # 전체 이상치 인덱스 집합에 추가 (중복은 자동으로 처리됨)
            outlier_indices.update(col_outliers)
        
        # 식별된 모든 이상치를 마지막에 한 번에 제거
        df_clean = df_clean.drop(index=outlier_indices)
        outliers_removed = initial_rows - len(df_clean)
        if initial_rows > 0:
            removal_rate = outliers_removed / initial_rows
            if removal_rate > 0.2:  # 20% 이상 제거시 경고
                st.warning(f"⚠️ 전체 데이터의 {removal_rate:.1%}가 이상치로 제거되었습니다. 임계값 조정을 고려해보세요.")
    else:
        outliers_removed = 0

    if df_clean.empty: return None, None, None, outliers_removed

    df_for_scaling = df_clean.copy()
    log_transform_cols = ['시가총액', '거래량', '자산총계', '매출액']
    for col in log_transform_cols:
        if col in df_for_scaling.columns:
            df_for_scaling[col] = df_for_scaling[col].apply(lambda x: np.log1p(x) if x > 0 else 0)

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(df_for_scaling)
    return df_clean, features_scaled, df_clean.index, outliers_removed

# --- 4. 최적 K 탐색 함수 ---
@st.cache_data
def find_optimal_k(_scaled_data, max_k_val):
    inertias = []
    for k in range(1, max_k_val + 1):
        kmeans = KMeans(n_clusters=k, init='k-means++', random_state=42, n_init=10).fit(_scaled_data)
        inertias.append(kmeans.inertia_)
    try:
        deltas = [inertias[i] - inertias[i+1] for i in range(len(inertias)-1)]
        delta_deltas = [deltas[i] - deltas[i+1] for i in range(len(deltas)-1)]
        optimal_k = delta_deltas.index(max(delta_deltas)) + 2
    except: optimal_k = 4
    fig = go.Figure(data=go.Scatter(x=list(range(1, max_k_val + 1)), y=inertias, mode='lines+markers'))
    fig.add_vline(x=optimal_k, line_width=2, line_dash="dash", line_color="red", annotation_text=f"알고리즘 추천 K = {optimal_k}")
    fig.update_layout(title='<b>Elbow Method</b>', xaxis_title='군집 수(K)', yaxis_title='이너셔(Inertia)')
    return fig, optimal_k

# --- 5. GPT 분석 함수 ---
@st.cache_data
def analyze_clusters_with_gpt(cluster_summary_df, top_stocks_per_cluster):
    client = OpenAI(api_key=api_key)
    summary_md = cluster_summary_df.to_markdown()
    
    prompt = f"""
    당신은 유능한 주식 애널리스트입니다. 아래는 K-Means 군집화로 도출된 주식 클러스터들의 평균 재무 지표와 각 클러스터의 대표 종목입니다.

    **[클러스터별 평균 재무 지표]**
    {summary_md}

    **[클러스터별 대표 종목]**
    {top_stocks_per_cluster}

    **[분석 요청]**
    위 데이터를 바탕으로, 각 클러스터의 특징을 초보자도 이해하기 쉽게 분석하고, 어떤 성향의 투자자에게 적합할지 추천 리포트를 작성해주세요. 아래 형식을 반드시 지켜주세요.

    --- 
    ### 🤖 AI 애널리스트 리포트

    **그룹 0: (그룹의 특징을 한 문장으로 요약. 예: 안정적인 대형 가치주)**
    *   **특징:** (구체적인 재무 지표를 근거로 그룹의 특징을 2-3가지 서술)
    *   **투자자 추천:** (어떤 투자 성향의 사람에게 이 그룹의 주식들이 매력적일지 서술)
    *   **대표 종목:** (해당 그룹의 대표 종목 2-3개를 언급)

    **그룹 1: (그룹의 특징을 한 문장으로 요약)**
    *   **특징:** ...
    *   **투자자 추천:** ...
    *   **대표 종목:** ...

    (이하 그룹 수만큼 반복)
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"GPT 분석 중 오류가 발생했습니다: {e}"

# --- 6. 메인 로직 ---
if uploaded_file is not None:
    if not api_key:
        st.warning("OpenAI API 키를 사이드바에 입력해주세요. API 키가 없으면 AI 분석 기능을 사용할 수 없습니다.")
    
    try:
        df_raw = pd.read_csv(uploaded_file, encoding='utf-8')
        with st.sidebar:
            features_selected = st.multiselect("군집화에 사용할 특성을 선택하세요.", options=[c for c in df_raw.columns if c != '종목명'], default=[f for f in default_features if f in df_raw.columns])

        if features_selected:
            df_clean, data_scaled, processed_indices, outliers_count = preprocess_data(df_raw, features_selected, remove_outliers_option)
            if df_clean is not None and not df_clean.empty:
                if remove_outliers_option: st.success(f"이상치 제거 완료: 총 {outliers_count}개의 이상치를 분석에서 제외했습니다.")
                
                st.header("📊 1. 최적의 군집 수 (K) 결정")
                elbow_fig, suggested_k = find_optimal_k(data_scaled, max_k)
                st.plotly_chart(elbow_fig, use_container_width=True)
                st.markdown("--- ")
                st.subheader("분석에 사용할 군집 수(K)를 직접 입력하세요.")
                manual_k = st.number_input("K 값 입력", 2, 20, suggested_k)

                kmeans = KMeans(n_clusters=manual_k, init='k-means++', random_state=42, n_init=10).fit(data_scaled)
                df_result = df_raw.loc[processed_indices].copy()
                df_result['cluster'] = kmeans.labels_.astype(str)

                st.header(f"📈 2. K = {manual_k}일 때의 군집화 결과 분석")
                cluster_summary = df_clean.assign(cluster=kmeans.labels_).groupby('cluster')[features_selected].mean()
                st.subheader("각 그룹의 평균적인 특징")
                st.dataframe(cluster_summary.style.background_gradient(cmap='viridis'))

                # GPT 분석 섹션
                if st.button("🤖 AI로 결과 분석하기", help="클러스터링 결과를 GPT에 전송하여 그룹별 특징과 투자 전략을 분석합니다."):
                    if not api_key: st.error("OpenAI API 키를 먼저 입력해야 합니다.")
                    else:
                        top_stocks = {f"그룹 {i}": df_result[df_result['cluster'] == str(i)]['종목명'].head(5).tolist() for i in range(manual_k)}
                        with st.spinner('AI 애널리스트가 리포트를 작성하고 있습니다...'):
                            gpt_report = analyze_clusters_with_gpt(cluster_summary, top_stocks)
                            st.info(gpt_report)

                st.header("✨ 3. 종합 군집 시각화")
                # (이하 시각화 로직은 이전과 동일)
                n_features = data_scaled.shape[1]
                if n_features >= 4:
                    st.subheader("t-SNE 3D 시각화 (4개 이상 특성)")
                    with st.spinner('고차원 데이터를 3D 공간으로 변환중 (t-SNE)...'):
                        tsne = TSNE(
                            n_components=3, 
                            random_state=42, 
                            perplexity=min(30, max(5, len(df_result)//4)),
                            max_iter=1000,  # 기본값 조정
                            learning_rate='auto'  # 자동 학습률
                        )
                        features_3d = tsne.fit_transform(data_scaled)
                        df_result['x'], df_result['y'], df_result['z'] = features_3d[:, 0], features_3d[:, 1], features_3d[:, 2]

                        fig = px.scatter_3d(df_result, x='x', y='y', z='z', color='cluster', hover_name='종목명', hover_data=features_selected, title='t-SNE로 차원 축소된 3D 군집 분포')
                        st.plotly_chart(fig, use_container_width=True)
                elif n_features == 3:
                    st.subheader("3D 특성 직접 시각화")
                    x_axis, y_axis, z_axis = features_selected[0], features_selected[1], features_selected[2]
                    fig = px.scatter_3d(df_result, x=x_axis, y=y_axis, z=z_axis, color='cluster', hover_name='종목명', hover_data=features_selected, title=f'{x_axis}, {y_axis}, {z_axis} 기준 3D 군집 분포')
                    st.plotly_chart(fig, use_container_width=True)
                elif n_features == 2:
                    st.subheader("2D 특성 직접 시각화")
                    x_axis, y_axis = features_selected[0], features_selected[1]
                    df_result_scaled = df_result.copy()
                    df_result_scaled[features_selected] = data_scaled 
                    fig = px.scatter(df_result, x=x_axis, y=y_axis, color='cluster', hover_name='종목명', hover_data=features_selected, title=f'{x_axis}와 {y_axis} 기준 군집 분포')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.subheader("1D 특성 분포 시각화")
                    x_axis = features_selected[0]
                    fig = px.histogram(df_result, x=x_axis, color='cluster', marginal="box", hover_name='종목명', title=f'{x_axis}의 그룹별 분포')
                    st.plotly_chart(fig, use_container_width=True)

                st.header("📂 4. 각 그룹에 속한 종목 리스트")
                for i in sorted(df_result['cluster'].unique()):
                    with st.expander(f"**그룹 {i}**에 속한 종목들 (총 {len(df_result[df_result['cluster'] == i])}개)"):
                        st.dataframe(df_result[df_result['cluster'] == i].head(20))
            else:
                st.error("데이터 전처리 후 분석할 데이터가 없습니다.")
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
else:
    st.info("사이드바에 API 키를 입력하고, KOSPI 데이터 CSV 파일을 업로드하여 분석을 시작하세요.")
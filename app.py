import streamlit as st
import pandas as pd
from datetime import date

# 1. 앱 페이지 설정
st.set_page_config(page_title="SH Networks Analyzer", layout="wide")
st.title("🏗️ SH네트워크: 신탁재건축 정밀 수지 분석 시스템")

# 오늘 날짜
today = date.today().strftime('%Y-%m-%d')
st.caption(f"접수번호: SH-{today}-01 | 대표이사 유성호")

# 2. 고정 실무 데이터 (성호 대표님 사업지)
LAND_AREA = 5054.0
GROSS_AREA = 25122.15
FAR = 299.0
INIT_ASSET_TOTAL = LAND_AREA * 3900.6 # 약 1,971억 원

# 3. 사이드바: 입력 변수
with st.sidebar:
    st.header("⚙️ 사업지 변수 조절")
    # 슬라이더 값들
    c_cost = st.slider("평당 공사비 (만원)", 650, 850, 732)
    s_price = st.slider("평당 일반분양가 (만원)", 3800, 4800, 4212)
    m_ratio = st.slider("조합원 분양가 비율 (%)", 70, 90, 79)
    trust_fee_rate = st.number_input("신탁 보수율 (%)", 0.0, 3.0, 1.0, step=0.1)

# 4. 계산 엔진 (Logic)
supply_area = LAND_AREA * (FAR / 100)
# 매출 (조합원 79% : 일반 21% 가정)
rev_member = (supply_area * 0.79) * (s_price * (m_ratio / 100))
rev_general = (supply_area * 0.21) * s_price
total_rev = rev_member + rev_general

# 비용 (공사비 + 신탁보수 + 기타사업비)
total_c_cost = GROSS_AREA * c_cost
trust_fee = total_rev * (trust_fee_rate / 100)
other_costs = 2150000.0 # 고정 기타사업비 (약 215억)
total_exp = total_c_cost + trust_fee + other_costs

# 비례율
p_rate = (total_rev - total_exp) / INIT_ASSET_TOTAL * 100

# 5. 메인 화면 구성
tab1, tab2 = st.tabs(["📊 사업성 대시보드", "📉 민감도 테이블"])

with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("예상 비례율", f"{p_rate:.2f}%", delta=f"{p_rate - 96.01:.2f}%")
    col2.metric("총 매출 (종후자산)", f"{total_rev/10000:.1f} 억")
    col3.metric("총 사업비", f"{total_exp/10000:.1f} 억")
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("💰 비용 세부 항목")
        cost_df = pd.DataFrame({
            "항목": ["공사비", "신탁보수", "기타사업비"],
            "금액(억)": [total_c_cost/10000, trust_fee/10000, other_costs/10000]
        })
        st.bar_chart(cost_df, x="항목", y="금액(억)")
    
    with c2:
        st.subheader("📝 전문가 진단")
        if p_rate > 96.01:
            st.success("✅ 현재 사업지 기준보다 수익성이 개선되었습니다.")
        else:
            st.error("⚠️ 현재 사업지 기준보다 수익성이 하락했습니다. 비용 관리가 필요합니다.")

with tab2:
    st.subheader("🎲 공사비 vs 분양가 민감도 분석")
    st.write("공사비(가로)와 분양가(세로) 변화에 따른 비례율 변화표입니다.")
    
    # 민감도 데이터 생성 (오류 방지를 위해 단순 리스트로 작성)
    cost_range = [c_cost - 20, c_cost, c_cost + 20]
    price_range = [s_price - 100, s_price, s_price + 100]
    
    sens_data = []
    for p in price_range:
        row = []
        for c in cost_range:
            t_rev = (supply_area * 0.79 * p * (m_ratio/100)) + (supply_area * 0.21 * p)
            t_exp = (GROSS_AREA * c) + (t_rev * (trust_fee_rate/100)) + other_costs
            t_p_rate = (t_rev - t_exp) / INIT_ASSET_TOTAL * 100
            row.append(f"{t_p_rate:.1f}%")
        sens_data.append(row)
    
    df_final = pd.DataFrame(
        sens_data, 
        index=[f"분양가 {p}만" for p in price_range],
        columns=[f"공사비 {c}만" for c in cost_range]
    )
    st.dataframe(df_final, use_container_width=True)

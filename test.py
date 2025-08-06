import streamlit as st
import time

# --- 페이지 설정 (선택사항) ---
st.set_page_config(
    page_title="Streamlit 버튼 제어 예제",
    layout="centered"
)

st.title("📄 과제 제출 시스템")
st.write("Submit 또는 Grade 버튼을 누르면 3초간 처리 후 버튼이 다시 활성화됩니다.")

# --- 1. st.session_state에 '상태' 변수 초기화 ---
# 'processing'이라는 상태 변수가 세션에 없으면 False로 만들어줍니다.
# 이 변수가 버튼의 활성화/비활성화와 스피너 표시 여부를 제어하는 열쇠입니다.
if 'processing' not in st.session_state:
    st.session_state.processing = False

# --- 2. 비동기 작업을 흉내 낼 함수 ---
# 실제로는 이 부분에 데이터 처리, API 호출, 모델 예측 등의 코드가 들어갑니다.
def long_running_task(task_name, duration):
    """지정된 시간(초) 동안 대기하며 작업을 흉내 내는 함수"""
    st.write(f"⏳ '{task_name}' 작업 시작...")
    time.sleep(duration)
    st.write(f"✅ '{task_name}' 작업 완료!")


# --- 3. UI 요소 배치 ---
# st.columns를 사용해 버튼을 나란히 배치합니다.
col1, col2 = st.columns(2)

with col1:
    # Submit 버튼
    # disabled 매개변수에 session_state 값을 연결하는 것이 핵심입니다.
    if st.button("Submit", use_container_width=True, disabled=st.session_state.processing):
        st.session_state.processing = True  # 버튼을 누르면 상태를 True로 변경
        st.rerun()  # 스크립트를 즉시 재실행하여 UI를 갱신 (버튼 비활성화)

with col2:
    # Grade 버튼
    if st.button("Grade", use_container_width=True, disabled=st.session_state.processing):
        st.session_state.processing = True  # 버튼을 누르면 상태를 True로 변경
        st.session_state.last_action = "Grade" # 어떤 버튼이 눌렸는지 기록 (선택사항)
        st.rerun()


# --- 4. 'processing' 상태일 때 실제 작업 수행 ---
# st.session_state.processing이 True일 때만 이 블록이 실행됩니다.
if st.session_state.processing:
    # st.spinner를 사용해 사용자에게 로딩 중임을 알립니다.
    with st.spinner("요청을 처리하는 중입니다... 잠시만 기다려주세요."):
        # 실제 작업 수행
        # 어떤 버튼이 눌렸는지에 따라 다른 작업을 수행하게 할 수도 있습니다.
        # 여기서는 간단히 하나의 작업만 수행합니다.
        long_running_task("데이터 제출", 3)

    st.success("모든 요청이 성공적으로 처리되었습니다!")

    # 작업이 모두 끝나면 다시 상태를 False로 되돌립니다.
    st.session_state.processing = False
    
    # 마지막으로 스크립트를 다시 실행해 UI를 원래 상태(버튼 활성화)로 복원합니다.
    st.rerun()
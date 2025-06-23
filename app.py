import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

# --- PDF 출력을 위한 한글 폰트 등록 ---
# Streamlit Cloud 환경에서 PDF에 한글을 올바르게 표시하려면,
# 'NanumGothic.ttf'와 같은 한글 폰트 파일이 app.py와 동일한 디렉토리에 있어야 합니다.
# 폰트 파일이 없으면 PDF에서 한글이 깨지거나 표시되지 않을 수 있습니다.
try:
    # 폰트 파일이 현재 스크립트와 같은 디렉토리에 있는지 확인합니다.
    pdfmetrics.registerFont(TTFont('NanumGothic', 'NanumGothic.ttf'))
    KOREAN_FONT_REGISTERED = True
except Exception as e:
    # 폰트 로드 실패 시 사용자에게 경고 메시지를 표시합니다.
    st.warning(f"PDF 출력 시 한글 폰트 로드 오류: {e}. 'NanumGothic.ttf' 파일이 같은 폴더에 없거나 손상되었을 수 있습니다. PDF에서 한글이 올바르게 표시되지 않을 수 있습니다.")
    KOREAN_FONT_REGISTERED = False

# --- 세션 상태 초기화 ---
# 앱의 여러 화면 간에 사용자 입력을 유지하기 위해 세션 상태 변수를 초기화합니다.
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1 # 현재 앱 화면 단계를 나타냅니다.
if 'writer_character' not in st.session_state:
    st.session_state.writer_character = "" # 편지를 쓰는 '나'를 저장합니다.
if 'selected_character' not in st.session_state:
    st.session_state.selected_character = "" # 편지를 받을 등장인물 이름을 저장합니다.
if 'event_description' not in st.session_state:
    st.session_state.event_description = "" # 등장인물이 겪은 사건 설명을 저장합니다.
if 'selected_emojis' not in st.session_state:
    st.session_state.selected_emojis = [] # 선택된 감정 이모지 목록을 저장합니다.
if 'shared_feelings' not in st.session_state:
    st.session_state.shared_feelings = "" # 등장인물에게 나누고 싶은 마음을 저장합니다.
if 'letter_intro' not in st.session_state:
    st.session_state.letter_intro = "" # 편지 - 첫인사
if 'letter_event_detail' not in st.session_state:
    st.session_state.letter_event_detail = "" # 편지 - 일어난 사건
if 'letter_my_thoughts_actions' not in st.session_state:
    st.session_state.letter_my_thoughts_actions = "" # 편지 - 일어난 사건에 대한 자신의 생각이나 행동
if 'letter_shared_feelings_detail' not in st.session_state:
    st.session_state.letter_shared_feelings_detail = "" # 편지 - 나누려는 마음
if 'letter_closing' not in st.session_state:
    st.session_state.letter_closing = "" # 편지 - 끝인사
if 'letter_writer_name' not in st.session_state:
    st.session_state.letter_writer_name = "" # 편지를 쓴 사람
if 'check_event_detail' not in st.session_state:
    st.session_state.check_event_detail = None # 점검 1: 일어난 사건 자세히 밝혔나요?
if 'check_express_feelings' not in st.session_state:
    st.session_state.check_express_feelings = None # 점검 2: 나누려는 마음 잘 표현했나요?
if 'check_easy_expression' not in st.session_state:
    st.session_state.check_easy_expression = None # 점검 3: 읽을 사람을 생각해 알기 쉬운 표현을 썼나요?


# --- 화면 이동 헬퍼 함수 ---
# '다음 화면' 또는 '이전 화면' 버튼 클릭 시 세션 상태를 업데이트하여 화면을 전환합니다.
def next_step():
    st.session_state.current_step += 1

def prev_step():
    st.session_state.current_step -= 1

# 특정 단계로 바로 이동하는 함수
def go_to_step(step_number):
    st.session_state.current_step = step_number

# --- PDF 생성 함수 ---
# reportlab 라이브러리를 사용하여 작성된 편지 내용을 PDF 파일로 생성합니다.
def generate_pdf(recipient_character, event_desc, selected_emojis, shared_feelings_summary,
                 intro, event_detail, my_thoughts, shared_feelings_detail, closing, writer_name):
    buffer = io.BytesIO() # PDF 데이터를 저장할 메모리 버퍼를 생성합니다.
    doc = SimpleDocTemplate(buffer, pagesize=letter) # PDF 문서 객체를 생성합니다.
    styles = getSampleStyleSheet() # 기본 스타일 시트를 가져옵니다.

    # 한글 폰트가 등록되었는지 확인하고, 적절한 폰트 스타일을 적용합니다.
    korean_style = styles['Normal']
    if KOREAN_FONT_REGISTERED:
        korean_style.fontName = 'NanumGothic' # 등록된 나눔고딕 폰트 사용
    else:
        korean_style.fontName = 'Helvetica' # 폰트가 없을 경우 기본 폰트 (한글 깨짐 가능성 있음)
    korean_style.fontSize = 12
    korean_style.leading = 16 # 줄 간격 설정

    elements = [] # PDF에 추가될 요소들의 리스트

    # 편지 제목 (받는 사람)
    elements.append(Paragraph(f"<b>{recipient_character}에게</b>", korean_style))
    elements.append(Spacer(1, 0.3 * inch)) # 제목 아래 여백 추가

    # 편지 내용 (각 파트별로 추가)
    if intro:
        elements.append(Paragraph(f"{intro}", korean_style))
        elements.append(Spacer(1, 0.1 * inch))
    if event_detail:
        elements.append(Paragraph(f"{event_detail}", korean_style))
        elements.append(Spacer(1, 0.1 * inch))
    if my_thoughts:
        elements.append(Paragraph(f"{my_thoughts}", korean_style))
        elements.append(Spacer(1, 0.1 * inch))
    if shared_feelings_detail:
        elements.append(Paragraph(f"{shared_feelings_detail}", korean_style))
        elements.append(Spacer(1, 0.1 * inch))
    if closing:
        elements.append(Paragraph(f"{closing}", korean_style))
        elements.append(Spacer(1, 0.2 * inch))

    # 글을 쓴 사람 (마지막에 추가)
    if writer_name:
        elements.append(Paragraph(f"<b>{writer_name}</b>", korean_style))
        elements.append(Spacer(1, 0.5 * inch))


    # --- 편지 작성 참고 정보 (PDF 하단에 추가) ---
    elements.append(Paragraph("--- 편지 작성 참고 정보 ---", korean_style))
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(Paragraph(f"<b>편지를 쓰는 사람:</b> {st.session_state.writer_character}", korean_style)) # 세션 상태에서 가져옴
    elements.append(Paragraph(f"<b>편지를 받는 사람:</b> {recipient_character}", korean_style))
    elements.append(Paragraph(f"<b>일어난 사건 요약:</b> {event_desc}", korean_style))
    elements.append(Paragraph(f"<b>등장인물의 감정:</b> {' '.join(selected_emojis)}", korean_style))
    elements.append(Paragraph(f"<b>나누고자 하는 마음 요약:</b> {shared_feelings_summary}", korean_style))


    doc.build(elements) # 정의된 요소들로 PDF 문서를 빌드합니다.
    buffer.seek(0) # 버퍼의 읽기/쓰기 위치를 처음으로 되돌립니다.
    return buffer # PDF 데이터가 담긴 버퍼를 반환합니다.

# --- 메인 스트림릿 앱 레이아웃 ---
# Streamlit 페이지의 기본 설정 (제목, 레이아웃)을 지정합니다.
st.set_page_config(page_title="「까만 달걀」을 읽고 등장인물에게 마음을 나누는 글쓰기 앱", layout="centered")

# 앱 제목 및 설명 변경
st.title("「까만 달걀」을 읽고 등장인물에게 마음을 나누는 글쓰기 앱")
st.write("책 속 등장인물의 감정을 이해하고, 내 마음을 전하는 글을 써 보세요.")

# 현재 화면 단계를 시각적으로 표시하는 내비게이션 바 (버튼으로 변경)
nav_titles = {
    1: "편지를 쓰는 '나'는 누구인가요?",
    2: "마음을 전하고 싶은 등장인물을 선택해요",
    3: "일어난 사건을 떠올려요",
    4: "나누려는 마음을 생각해요",
    5: "나누려는 마음을 담아 글을 써보세요"
}

nav_cols = st.columns(5) # 각 화면에 해당하는 5개의 컬럼 생성

for i, col in enumerate(nav_cols, 1):
    with col:
        # 현재 화면은 비활성화된 (클릭 불가능한) 버튼으로 표시하여 현재 위치를 강조
        st.button(
            nav_titles[i],
            on_click=go_to_step,
            args=(i,),
            disabled=(i == st.session_state.current_step),
            key=f"nav_button_{i}" # 고유한 키 부여
        )

st.markdown("---") # 내비게이션 바 아래 구분선

# --- 화면 1: 편지를 쓰는 '나'는 누구인가요? ---
if st.session_state.current_step == 1:
    st.header("1. 편지를 쓰는 '나'는 누구인가요?")
    writer_options = ["나", "아랑이", "아랑이의 어머니", "재현", "재현이의 아버지", "성구", "달이", "운철이", "달이의 아버지"]
    # 편지를 쓰는 주체 선택을 위한 selectbox 위젯
    st.session_state.writer_character = st.selectbox(
        "편지를 쓰는 주체를 선택하세요.",
        writer_options,
        index=writer_options.index(st.session_state.writer_character) if st.session_state.writer_character in writer_options else 0,
        key="writer_select"
    )
    st.markdown("---")
    # '다음 화면'으로 이동하는 버튼 (오른쪽에 배치)
    col1, col2 = st.columns(2)
    with col2:
        st.button("다음 화면", on_click=next_step, help="다음 단계인 '마음을 전하고 싶은 등장인물을 선택해요' 화면으로 이동합니다.")

# --- 화면 2: 마음을 전하고 싶은 등장인물을 선택해요 ---
elif st.session_state.current_step == 2:
    st.header("2. 마음을 전하고 싶은 등장인물을 선택해요")
    characters = ["아랑", "아랑이의 어머니", "재현", "재현이의 아버지", "성구", "달이", "운철이"] # "달이의 아버지"는 받는 대상에서는 제외
    # 편지를 받을 등장인물 선택을 위한 selectbox 위젯
    st.session_state.selected_character = st.selectbox(
        "편지를 받을 대상(등장인물)을 선택하세요.", # 제목 변경
        characters,
        index=characters.index(st.session_state.selected_character) if st.session_state.selected_character in characters else 0,
        key="recipient_select"
    )
    st.markdown("---")
    # '이전 화면'과 '다음 화면' 버튼
    col1, col2 = st.columns(2)
    with col1:
        st.button("이전 화면", on_click=prev_step, help="이전 단계인 '편지를 쓰는 '나'는 누구인가요?' 화면으로 돌아갑니다.")
    with col2:
        st.button("다음 화면", on_click=next_step, help="다음 단계인 '일어난 사건을 떠올려요' 화면으로 이동합니다.")


# --- 화면 3: 일어난 사건을 떠올려요 ---
elif st.session_state.current_step == 3:
    st.header("3. 일어난 사건을 떠올려요")
    st.write("등장인물이 겪은 상황이나 사건을 떠올려 적어주세요.")
    # 사건/상황 내용을 입력하는 text_area 위젯
    st.session_state.event_description = st.text_area(
        "사건/상황 내용",
        value=st.session_state.event_description, # 세션 상태 값으로 초기화
        height=150, # 텍스트 영역의 높이 설정
        key="event_text_area",
        placeholder="예: 아랑이가 낱말 카드를 만들어 엄마에게 한국말을 알려줬을 때" # 입력 예시
    )

    st.write("그 상황에서 등장인물의 마음은 어땠을까요? 감정을 이모지로 표현하고 선택해 보세요. (여러 개 선택 가능)")
    # 감정 이름과 해당 이모지 매핑 딕셔너리
    emotions = {
        "무섭다": "😨", "슬프다": "😢", "외롭다": "😔", "짜증나다": "😤", "화나다": "😡",
        "신나다": "🤩", "행복하다": "😊", "당황하다": "😳", "미안하다": "🙏", "창피하다": "😳",
        "억울하다": "😩", "즐겁다": "😄", "답답하다": "😐", "걱정되다": "😟", "설레다": "💖",
        "샘나다": "😒", "실망하다": "😞", "울고싶다": "😭", "부끄럽다": "😳", "재미있다": "😂",
        "편안하다": "😌", "기쁘다": "🥳", "얄밉다": "😠", "속상하다": "💔", "뿌듯하다": "👍",
        "우울하다": "😔", "서운하다": "😔", "만족하다": "😌", "불안하다": "😬", "놀라다": "😲",
        "쓸쓸하다": "🍂", "신경질나다": "😠", "아쉽다": "😟", "약오르다": "😤", "후회되다": "🤦‍♀️"
    }
    # 멀티셀렉트 박스에 표시될 옵션 (예: "무섭다 😨")
    emoji_options_for_display = [f"{name} {emoji}" for name, emoji in emotions.items()]

    # 감정 선택을 위한 multiselect 위젯
    st.session_state.selected_emojis = st.multiselect(
        "등장인물의 감정을 선택하세요.",
        options=emoji_options_for_display,
        default=st.session_state.selected_emojis, # 이전에 선택된 값들로 기본 설정
        key="emotion_multiselect"
    )

    st.markdown("---")
    # '이전 화면'과 '다음 화면' 버튼 (각각 왼쪽, 오른쪽에 배치)
    col1, col2 = st.columns(2)
    with col1:
        st.button("이전 화면", on_click=prev_step, help="이전 단계인 '마음을 전하고 싶은 등장인물을 선택해요' 화면으로 돌아갑니다.")
    with col2:
        st.button("다음 화면", on_click=next_step, help="다음 단계인 '나누려는 마음을 생각해요' 화면으로 이동합니다.")

# --- 화면 4: 나누려는 마음을 생각해요 ---
elif st.session_state.current_step == 4:
    st.header("4. 나누려는 마음을 생각해요")
    st.write("등장인물에게 어떤 마음을 나누고자 하는지, 어떤 마음을 전달하고 싶은지 작성해 보세요.")
    # 나누고 싶은 마음을 입력하는 text_area 위젯
    st.session_state.shared_feelings = st.text_area(
        "나누고 싶은 마음",
        value=st.session_state.shared_feelings, # 세션 상태 값으로 초기화
        height=150,
        key="shared_feelings_text_area",
        placeholder="예: 아랑이가 엄마를 향한 자신의 마음을 깨닫고 한국말을 가르쳐준 행동에 잘했다고 칭찬을 해주고 싶어요."
    )

    st.markdown("---")
    # '이전 화면'과 '다음 화면' 버튼
    col1, col2 = st.columns(2)
    with col1:
        st.button("이전 화면", on_click=prev_step, help="이전 단계인 '일어난 사건을 떠올려요' 화면으로 돌아갑합니다.")
    with col2:
        st.button("다음 화면", on_click=next_step, help="다음 단계인 '나누려는 마음을 담아 글을 써 보세요.' 화면으로 이동합니다.")

# --- 화면 5: 나누려는 마음을 담아 글을 써 보세요. ---
elif st.session_state.current_step == 5:
    st.header("5. 나누려는 마음을 담아 글을 써 보세요.")
    st.write(f"이제 {st.session_state.selected_character}에게 편지를 써 보세요. 왼쪽에 제시된 힌트를 참고하여 작성할 수 있습니다.")

    # 편지 내용 입력 영역과 힌트 영역을 컬럼으로 분리하여 나란히 표시
    col_hints, col_letter = st.columns([1, 4]) # 힌트 컬럼을 편지 컬럼보다 좁게 설정

    with col_hints:
        # 각 힌트와 입력 칸의 위치를 맞추기 위한 미세 조정 (trial and error 기반)
        # `st.markdown(f"{st.session_state.selected_character}에게")`의 높이와 간격을 고려
        # text_area 높이를 80으로 늘려 힌트 정렬에 더 유연하게 대응
        st.markdown("<div style='height: 70px;'></div>", unsafe_allow_html=True) # "받는이에게" 줄과 "첫인사" 힌트 간격
        st.markdown("<b>첫인사</b>", unsafe_allow_html=True)
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True) # `letter_intro` text_area 높이 (80px) 고려하여 중앙 정렬

        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True) # 이전 text_area 높이 (80px)를 반영하여 다음 힌트 위치 조정
        st.markdown("<b>일어난 사건</b>", unsafe_allow_html=True)
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True) # `letter_event_detail` text_area 높이 (80px) 고려하여 중앙 정렬

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True) # 이전 text_area 높이 (80px)를 반영하여 다음 힌트 위치 조정
        st.markdown("<b>일어난 사건에 대한<br>자신의 생각이나 행동</b>", unsafe_allow_html=True) # 2줄 힌트 (40px)
        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True) # 2줄 힌트를 text_area 중앙 (80px)에 맞추기 위해 조정 ( (80-40)/2 = 20 )

        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True) # 이전 text_area 높이 (80px)를 반영하여 다음 힌트 위치 조정
        st.markdown("<b>나누려는 마음</b>", unsafe_allow_html=True)
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True) # `letter_shared_feelings_detail` text_area 높이 (80px) 고려하여 중앙 정렬

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True) # 이전 text_area 높이 (80px)를 반영하여 다음 힌트 위치 조정
        st.markdown("<b>끝인사</b>", unsafe_allow_html=True)
        st.markdown("<div style='height: 20x;'></div>", unsafe_allow_html=True) # `letter_closing` text_area 높이 (80px) 고려하여 중앙 정렬

    with col_letter:
        st.markdown(f"{st.session_state.selected_character}에게") # 받는 사람 이름은 일반 텍스트로 표시

        st.session_state.letter_intro = st.text_area(
            "첫인사를 작성해 보세요.",
            value=st.session_state.letter_intro,
            height=80, # 높이 조정
            key="letter_intro_area",
            label_visibility="collapsed" # 레이블 숨김 (힌트가 대신 역할)
        )
        st.session_state.letter_event_detail = st.text_area(
            "일어난 사건을 자세히 작성해 보세요.",
            value=st.session_state.letter_event_detail,
            height=80, # 높이 조정
            key="letter_event_detail_area",
            label_visibility="collapsed"
        )
        st.session_state.letter_my_thoughts_actions = st.text_area(
            "일어난 사건에 대한 자신의 생각이나 행동을 작성해 보세요.",
            value=st.session_state.letter_my_thoughts_actions,
            height=80, # 높이 조정
            key="letter_my_thoughts_actions_area",
            label_visibility="collapsed"
        )
        st.session_state.letter_shared_feelings_detail = st.text_area(
            "나누려는 마음을 작성해 보세요.",
            value=st.session_state.letter_shared_feelings_detail,
            height=80, # 높이 조정
            key="letter_shared_feelings_detail_area",
            label_visibility="collapsed"
        )
        st.session_state.letter_closing = st.text_area(
            "끝인사를 작성해 보세요.",
            value=st.session_state.letter_closing,
            height=80, # 높이 조정
            key="letter_closing_area",
            label_visibility="collapsed"
        )
        st.session_state.letter_writer_name = st.text_input(
            "글을 쓴 사람", # '글을 쓴 사람'은 힌트가 아닌 label로 표시
            value=st.session_state.letter_writer_name,
            key="letter_writer_name_input",
            placeholder="예: OO이가,OOO 드림"
        )


    st.markdown("---")
    st.subheader("나누려는 마음 글쓰기를 점검해 봅시다")

    # 점검 항목 1
    st.session_state.check_event_detail = st.radio(
        "1) 일어난 사건을 자세히 밝혔나요?",
        options=["예", "아니오"],
        # 첫 로드 시 기본값 설정 (None이면 '예'로 초기화)
        index=["예", "아니오"].index(st.session_state.check_event_detail) if st.session_state.check_event_detail in ["예", "아니오"] else 0,
        key="check_event_detail_radio",
        horizontal=True
    )
    if st.session_state.check_event_detail == "아니오":
        st.info("💡 일어난 사건을 다시 한번 떠올려 읽을 사람이 이해하기 쉽게 자세히 씁니다.")

    # 점검 항목 2
    st.session_state.check_express_feelings = st.radio(
        "2) 나누려는 마음을 잘 표현했나요?",
        options=["예", "아니오"],
        index=["예", "아니오"].index(st.session_state.check_express_feelings) if st.session_state.check_express_feelings in ["예", "아니오"] else 0,
        key="check_express_feelings_radio",
        horizontal=True
    )
    if st.session_state.check_express_feelings == "아니오":
        st.info("💡 나누려는 마음을 자세하게 나타냅니다.")

    # 점검 항목 3
    st.session_state.check_easy_expression = st.radio(
        "3) 읽을 사람을 생각해 알기 쉬운 표현을 썼나요?",
        options=["예", "아니오"],
        index=["예", "아니오"].index(st.session_state.check_easy_expression) if st.session_state.check_easy_expression in ["예", "아니오"] else 0,
        key="check_easy_expression_radio",
        horizontal=True
    )
    if st.session_state.check_easy_expression == "아니오":
        st.info("💡 읽을 사람을 위해 정확하고 쉬운 표현을 씁니다.")

    all_checked_yes = (
        st.session_state.check_event_detail == "예" and
        st.session_state.check_express_feelings == "예" and
        st.session_state.check_easy_expression == "예"
    )

    st.markdown("---")
    col_save, col_print_btn = st.columns(2)

    with col_save:
        if st.button("저장"):
            st.success("편지 내용이 앱 내에 임시 저장되었습니다. (앱을 새로고침하거나 닫으면 내용이 사라질 수 있습니다.)")

    with col_print_btn:
        # PDF 출력 버튼 활성화 조건을 설정합니다.
        # 모든 점검 항목이 '예'이고, 필수 편지 내용 칸이 모두 채워져 있을 때 활성화됩니다.
        if all_checked_yes and \
           st.session_state.writer_character and \
           st.session_state.selected_character and \
           st.session_state.event_description and \
           st.session_state.shared_feelings and \
           st.session_state.letter_intro and \
           st.session_state.letter_event_detail and \
           st.session_state.letter_my_thoughts_actions and \
           st.session_state.letter_shared_feelings_detail and \
           st.session_state.letter_closing and \
           st.session_state.letter_writer_name:

            pdf_buffer = generate_pdf(
                st.session_state.selected_character,
                st.session_state.event_description,
                st.session_state.selected_emojis,
                st.session_state.shared_feelings,
                st.session_state.letter_intro,
                st.session_state.letter_event_detail,
                st.session_state.letter_my_thoughts_actions,
                st.session_state.letter_shared_feelings_detail,
                st.session_state.letter_closing,
                st.session_state.letter_writer_name
            )
            st.download_button(
                label="PDF 출력",
                data=pdf_buffer,
                file_name=f"{st.session_state.selected_character}_편지.pdf",
                mime="application/pdf",
                help="작성된 편지를 PDF 파일로 다운로드합니다."
            )
        else:
            # 모든 점검 항목이 '예'가 아니면 경고 메시지 표시
            if not all_checked_yes:
                st.warning("답변한 내용을 참고해 글을 고쳐 써 봅시다. 모든 점검 항목을 '예'로 선택해야 PDF를 출력할 수 있습니다.")
            # 필수 편지 내용이 누락된 경우 안내 메시지 표시
            else:
                st.info("PDF 출력을 위해 모든 필수 항목(편지를 쓰는 '나', 등장인물, 사건, 나누려는 마음 요약, 편지 세부 내용)을 작성하고 점검 사항을 확인해주세요.")


    st.markdown("---")
    # 마지막 화면의 '이전 화면' 버튼 (오른쪽에 배치)
    col1, col2 = st.columns(2)
    with col1:
        st.button("이전 화면", on_click=prev_step, help="이전 단계인 '나누려는 마음을 생각해요' 화면으로 돌아갑니다.")


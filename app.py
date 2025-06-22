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
if 'selected_character' not in st.session_state:
    st.session_state.selected_character = "" # 선택된 등장인물 이름을 저장합니다.
if 'event_description' not in st.session_state:
    st.session_state.event_description = "" # 등장인물이 겪은 사건 설명을 저장합니다.
if 'selected_emojis' not in st.session_state:
    st.session_state.selected_emojis = [] # 선택된 감정 이모지 목록을 저장합니다.
if 'shared_feelings' not in st.session_state:
    st.session_state.shared_feelings = "" # 등장인물에게 나누고 싶은 마음을 저장합니다.
if 'letter_content' not in st.session_state:
    st.session_state.letter_content = "" # 사용자가 작성한 편지 내용을 저장합니다.

# --- 화면 이동 헬퍼 함수 ---
# '다음 화면' 또는 '이전 화면' 버튼 클릭 시 세션 상태를 업데이트하여 화면을 전환합니다.
def next_step():
    st.session_state.current_step += 1

def prev_step():
    st.session_state.current_step -= 1

# --- PDF 생성 함수 ---
# reportlab 라이브러리를 사용하여 작성된 편지 내용을 PDF 파일로 생성합니다.
def generate_pdf(character, event, feelings_emojis, shared_feelings, letter_content):
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

    # 편지 제목 추가
    elements.append(Paragraph(f"<b>편지 - {character}에게</b>", korean_style))
    elements.append(Spacer(1, 0.3 * inch)) # 제목 아래 여백 추가

    # 편지 내용 추가 (줄바꿈 유지)
    letter_lines = letter_content.split('\n')
    for line in letter_lines:
        elements.append(Paragraph(line.strip() or " ", korean_style)) # 각 줄을 Paragraph로 추가, 빈 줄도 공백으로 처리

    elements.append(Spacer(1, 0.5 * inch)) # 편지 내용과 참고 정보 사이 여백

    # 편지 작성에 참고된 정보 추가
    elements.append(Paragraph("--- 편지 작성 참고 정보 ---", korean_style))
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(Paragraph(f"<b>선택된 등장인물:</b> {character}", korean_style))
    elements.append(Paragraph(f"<b>일어난 사건:</b> {event}", korean_style))
    elements.append(Paragraph(f"<b>등장인물의 감정:</b> {' '.join(feelings_emojis)}", korean_style))
    elements.append(Paragraph(f"<b>나누고자 하는 마음:</b> {shared_feelings}", korean_style))

    doc.build(elements) # 정의된 요소들로 PDF 문서를 빌드합니다.
    buffer.seek(0) # 버퍼의 읽기/쓰기 위치를 처음으로 되돌립니다.
    return buffer # PDF 데이터가 담긴 버퍼를 반환합니다.

# --- 메인 스트림릿 앱 레이아웃 ---
# Streamlit 페이지의 기본 설정 (제목, 레이아웃)을 지정합니다.
st.set_page_config(page_title="『까만 달걀』 교육용 앱", layout="centered")

st.title("『까만 달걀』 교육용 앱")
st.write("초등학교 6학년을 위한 교육용 앱입니다.")
st.write("도서 『까만 달걀』을 읽고, 책 속 등장인물에게 편지를 쓰며 공감 능력과 감정 표현 능력을 길러보세요.")

# 현재 화면 단계를 시각적으로 표시하는 내비게이션 바
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4) # 각 화면에 해당하는 4개의 컬럼 생성

for i in range(1, 5):
    with globals()[f"nav_col{i}"]:
        if i == st.session_state.current_step:
            # 현재 화면은 파란색 볼드체로 표시
            st.markdown(f"**<span style='color: blue;'>화면 {i}</span>**", unsafe_allow_html=True)
        else:
            # 다른 화면은 일반 텍스트로 표시
            st.markdown(f"화면 {i}")

st.markdown("---") # 내비게이션 바 아래 구분선

# --- 화면 1: 등장인물을 선택해요 ---
if st.session_state.current_step == 1:
    st.header("1. 등장인물을 선택해요")
    characters = ["아랑", "아랑이의 어머니", "재현", "재현이의 아버지", "성구", "달이", "운철이"]
    # 등장인물 선택을 위한 selectbox 위젯
    st.session_state.selected_character = st.selectbox(
        "편지를 쓸 등장인물을 선택하세요.",
        characters,
        # 이전에 선택된 값이 있다면 그 값을 기본으로 설정, 없다면 첫 번째 항목을 기본으로 설정
        index=characters.index(st.session_state.selected_character) if st.session_state.selected_character in characters else 0,
        key="character_select"
    )
    st.markdown("---")
    # '다음 화면'으로 이동하는 버튼 (오른쪽에 배치)
    col1, col2 = st.columns(2)
    with col2:
        st.button("다음 화면", on_click=next_step, help="다음 단계인 '일어난 사건을 떠올려요' 화면으로 이동합니다.")

# --- 화면 2: 일어난 사건을 떠올려요 ---
elif st.session_state.current_step == 2:
    st.header("2. 일어난 사건을 떠올려요")
    st.write("등장인물이 겪은 상황이나 사건을 떠올려 적어주세요.")
    # 사건/상황 내용을 입력하는 text_area 위젯
    st.session_state.event_description = st.text_area(
        "사건/상황 내용",
        value=st.session_state.event_description, # 세션 상태 값으로 초기화
        height=150, # 텍스트 영역의 높이 설정
        key="event_text_area",
        placeholder="예: 아랑이가 엄마에게 거짓말을 하고 혼자 학교에 갔을 때" # 입력 예시
    )

    st.write("그 상황에서 등장인물의 마음은 어땠을까요? 감정을 이모지로 표현하고 선택해 보세요. (여러 개 선택 가능)")
    # 감정 이름과 해당 이모지 매핑 딕셔너리
    emotions = {
        "무섭다": "😨", "슬프다": "😢", "외롭다": "😔", "짜증나다": "😤", "화나다": "😡",
        "신나다": "🤩", "행복하다": "😊", "당황하다": "😳", "미안하다": "🙏", "창피하다": "😳", # 창피하다 이모지 수정
        "억울하다": "😩", "즐겁다": "😄", "답답하다": "😐", "걱정되다": "😟", "설레다": "💖",
        "샘나다": "😒", "실망하다": "😞", "울고싶다": "😭", "부끄럽다": "😳", "재미있다": "😂", # 부끄럽다 이모지 수정
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
        st.button("이전 화면", on_click=prev_step, help="이전 단계인 '등장인물을 선택해요' 화면으로 돌아갑니다.")
    with col2:
        st.button("다음 화면", on_click=next_step, help="다음 단계인 '나눌 마음을 생각해요' 화면으로 이동합니다.")

# --- 화면 3: 나눌 마음을 생각해요 ---
elif st.session_state.current_step == 3:
    st.header("3. 나눌 마음을 생각해요")
    st.write("등장인물에게 어떤 마음을 나누고자 하는지, 어떤 마음을 전달하고 싶은지 작성해 보세요.")
    # 나누고 싶은 마음을 입력하는 text_area 위젯
    st.session_state.shared_feelings = st.text_area(
        "나누고 싶은 마음",
        value=st.session_state.shared_feelings, # 세션 상태 값으로 초기화
        height=150,
        key="shared_feelings_text_area",
        placeholder="예: 아랑이의 용기에 박수를 보내주고 싶어요."
    )

    st.markdown("---")
    # '이전 화면'과 '다음 화면' 버튼
    col1, col2 = st.columns(2)
    with col1:
        st.button("이전 화면", on_click=prev_step, help="이전 단계인 '일어난 사건을 떠올려요' 화면으로 돌아갑니다.")
    with col2:
        st.button("다음 화면", on_click=next_step, help="다음 단계인 '나누려는 마음을 담아 글을 써 보세요.' 화면으로 이동합니다.")

# --- 화면 4: 나누려는 마음을 담아 글을 써 보세요. ---
elif st.session_state.current_step == 4:
    st.header("4. 나누려는 마음을 담아 글을 써 보세요.")
    st.write("이제 편지를 써 보세요. 왼쪽에 제시된 힌트를 참고하여 작성할 수 있습니다.")

    # 편지 내용 입력 영역 초기화 로직
    # 만약 편지 내용이 아직 비어있거나, 이전 화면에서 넘어온 기본 형식과 다르면 초기 형식을 설정합니다.
    # 이렇게 하면 사용자가 이미 내용을 작성했을 경우 덮어쓰지 않고 이어서 쓸 수 있습니다.
    initial_template = (
        f"{st.session_state.selected_character}에게\n" # 1행: 받는 사람
        "\n" # 2행: 첫인사 힌트용 공백
        "\n" # 3행: 일어난 사건 힌트용 공백
        "\n"
        "\n"
        "\n" # 6행: 나의 생각/마음 힌트용 공백
        "\n"
        "\n" # 9행: 끝인사 힌트용 공백
        "\n"
        "\n"
    )
    # 편지 내용이 비어있거나, 이전 내용이 첫인사 템플릿과 동일하다면 템플릿으로 초기화
    if not st.session_state.letter_content.strip() or st.session_state.letter_content.strip() == initial_template.strip():
        st.session_state.letter_content = initial_template.strip()

    # 편지 내용 입력 영역과 힌트 영역을 컬럼으로 분리하여 나란히 표시
    col_hints, col_letter = st.columns([1, 4]) # 힌트 컬럼을 편지 컬럼보다 좁게 설정

    with col_hints:
        # 각 힌트와 텍스트 에리어 라인에 맞추기 위한 수동적인 높이 조정
        st.markdown("<div style='height: 1.2em;'></div>", unsafe_allow_html=True) # '----에게' 라인 맞춤
        st.markdown("<b>첫인사</b>", unsafe_allow_html=True) # 2번째 줄에 맞춤
        st.markdown("<div style='height: 2.5em;'></div>", unsafe_allow_html=True) # 3번째 줄 맞춤 여백
        st.markdown("<b>일어난 사건</b>", unsafe_allow_html=True) # 3번째 줄에 맞춤
        st.markdown("<div style='height: 5.5em;'></div>", unsafe_allow_html=True) # 6번째 줄 맞춤 여백
        st.markdown("<b>일어난 사건에 대한 나의 생각이나 마음<br>(나누려는 마음)</b>", unsafe_allow_html=True) # 6번째 줄에 맞춤, <br>로 줄바꿈
        st.markdown("<div style='height: 5em;'></div>", unsafe_allow_html=True) # 9번째 줄 맞춤 여백
        st.markdown("<b>끝인사</b>", unsafe_allow_html=True) # 9번째 줄에 맞춤

    with col_letter:
        st.session_state.letter_content = st.text_area(
            "편지 내용",
            value=st.session_state.letter_content, # 세션 상태 값으로 초기화
            height=400, # 편지 작성 영역의 높이
            key="letter_text_area",
            help="여기에 편지 내용을 작성해 주세요."
        )

    st.markdown("---") # 액션 버튼들 위 구분선

    # '저장' 및 'PDF 출력' 버튼
    col_save, col_print_btn = st.columns(2)
    with col_save:
        if st.button("저장"):
            # 현재 앱에서는 세션 상태에 저장하는 것으로 처리합니다.
            # 실제 배포 환경에서는 데이터베이스 등에 저장 로직을 추가할 수 있습니다.
            st.success("편지 내용이 앱 내에 임시 저장되었습니다. (앱을 새로고침하거나 닫으면 내용이 사라질 수 있습니다.)")
    with col_print_btn:
        # PDF 출력 버튼 활성화 조건을 설정합니다.
        # 등장인물이 선택되었고, 사건 설명이 있으며, 편지 내용이 기본 템플릿 이상으로 작성되었을 때 활성화됩니다.
        if st.session_state.selected_character and \
           st.session_state.event_description and \
           st.session_state.letter_content.strip() != initial_template.strip(): # 템플릿 내용만 있을 경우 PDF 출력 비활성화
            pdf_buffer = generate_pdf(
                st.session_state.selected_character,
                st.session_state.event_description,
                st.session_state.selected_emojis,
                st.session_state.shared_feelings,
                st.session_state.letter_content
            )
            # PDF 다운로드 버튼을 제공합니다.
            st.download_button(
                label="PDF 출력", # 사용자에게 보이는 버튼 텍스트
                data=pdf_buffer, # 다운로드할 데이터 (PDF 버퍼)
                file_name=f"{st.session_state.selected_character}_편지.pdf", # 다운로드될 파일 이름
                mime="application/pdf", # 파일의 MIME 타입
                help="작성된 편지를 PDF 파일로 다운로드합니다."
            )
        else:
            st.info("PDF 출력을 위해 모든 필수 항목(등장인물, 사건, 편지 내용)을 작성해주세요.")

    st.markdown("---")
    # 마지막 화면의 '이전 화면' 버튼 (오른쪽에 배치)
    col1, col2 = st.columns(2)
    with col1:
        st.button("이전 화면", on_click=prev_step, help="이전 단계인 '나눌 마음을 생각해요' 화면으로 돌아갑니다.")

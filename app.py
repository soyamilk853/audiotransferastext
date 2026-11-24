import os
import tempfile
import uuid

import streamlit as st
import whisper
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt


st.set_page_config(
    page_title="MP3 語音轉文字",
    page_icon="🎧",
    layout="centered",
)

st.title("🎧 MP3 語音轉文字")
st.caption(
    "上傳 MP3 檔案，使用 OpenAI Whisper 轉換為文字，"
    "並下載為 Word (.docx) 文件。"
)


@st.cache_resource(show_spinner="正在載入 Whisper 模型，請稍候……")
def load_whisper_model(model_name: str):
    return whisper.load_model(model_name)


def format_timestamp(seconds: float) -> str:
    total_seconds = int(seconds)
    minutes, secs = divmod(total_seconds, 60)
    return f"{minutes:02d}:{secs:02d}"


def create_word_document(
    full_text: str,
    segments: list,
    source_filename: str,
    model_name: str,
    language: str,
) -> str:
    doc = Document()

    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Microsoft JhengHei"
    normal_style.font.size = Pt(12)

    title = doc.add_heading("語音轉文字紀錄", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()
    doc.add_paragraph(f"音檔來源：{source_filename}")
    doc.add_paragraph(f"辨識模型：Whisper {model_name}")
    doc.add_paragraph(f"指定語言：{language if language else '自動偵測'}")
    doc.add_paragraph()

    doc.add_heading("完整文字內容", level=1)
    doc.add_paragraph(full_text)

    if segments:
        doc.add_page_break()
        doc.add_heading("逐句文字與時間戳", level=1)

        for segment in segments:
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])

            paragraph = doc.add_paragraph()
            timestamp_run = paragraph.add_run(
                f"[{start_time} - {end_time}] "
            )
            timestamp_run.bold = True
            paragraph.add_run(segment["text"].strip())

    output_path = os.path.join(
        tempfile.gettempdir(),
        f"語音轉文字_{uuid.uuid4().hex[:8]}.docx",
    )
    doc.save(output_path)
    return output_path


with st.sidebar:
    st.header("轉錄設定")

    model_name = st.selectbox(
        "Whisper 模型",
        options=["tiny", "base", "small", "medium", "large-v3"],
        index=1,
        help=(
            "tiny/base 較快；small 兼顧速度與準確度；"
            "medium/large-v3 較準確但較慢、較耗資源。"
        ),
    )

    language = st.selectbox(
        "音訊語言",
        options=[
            "自動偵測",
            "zh",
            "en",
            "ja",
            "ko",
            "yue",
        ],
        index=1,
        help="中文普通話建議選 zh；粵語可嘗試 yue，但辨識效果視音訊而定。",
    )

    include_timestamps = st.checkbox(
        "在 Word 中加入逐句時間戳",
        value=True,
    )

    st.divider()
    st.info(
        "提示：Streamlit Community Cloud 免費方案資源有限。\n\n"
        "建議先用 `base` 或 `small`；長音檔或需要高準確度時，"
        "建議部署到有 GPU 的伺服器。"
    )


uploaded_file = st.file_uploader(
    "請上傳 MP3 檔案",
    type=["mp3"],
    accept_multiple_files=False,
)

if uploaded_file is None:
    st.info("請先上傳一個 MP3 檔案。")
    st.stop()

st.success(f"已上傳：{uploaded_file.name}")

if st.button("開始轉換為文字", type="primary", use_container_width=True):
    selected_language = None if language == "自動偵測" else language

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = os.path.join(temp_dir, uploaded_file.name)

        with open(audio_path, "wb") as audio_file:
            audio_file.write(uploaded_file.getbuffer())

        try:
            model = load_whisper_model(model_name)

            with st.spinner("正在進行語音辨識，請稍候……"):
                transcribe_options = {}

                if selected_language:
                    transcribe_options["language"] = selected_language

                result = model.transcribe(
                    audio_path,
                    verbose=False,
                    **transcribe_options,
                )

            full_text = result.get("text", "").strip()
            segments = result.get("segments", [])

            if not full_text:
                st.warning("未能從音檔辨識出文字，請確認音訊是否清晰。")
                st.stop()

            st.subheader("轉錄結果")
            st.text_area(
                "文字內容",
                value=full_text,
                height=320,
            )

            st.download_button(
                label="下載 Word 文件 (.docx)",
                data=open(
                    create_word_document(
                        full_text=full_text,
                        segments=segments if include_timestamps else [],
                        source_filename=uploaded_file.name,
                        model_name=model_name,
                        language=selected_language,
                    ),
                    "rb",
                ).read(),
                file_name=f"{os.path.splitext(uploaded_file.name)[0]}_語音轉文字.docx",
                mime=(
                    "application/vnd.openxmlformats-officedocument"
                    ".wordprocessingml.document"
                ),
                use_container_width=True,
            )

        except Exception as error:
            st.error(f"轉錄失敗：{error}")

# audiotransferastext
To transfer audio in to text (Traditional Text)

# MP3 語音轉文字 Streamlit App

上傳 MP3，使用 OpenAI Whisper 將語音轉為文字，並下載為 Word (.docx)。

## 功能

- 上傳 MP3 檔案
- 選擇 Whisper 模型
- 指定或自動偵測語言
- 顯示轉錄文字
- 產生並下載 Word 文件
- 可選擇加入逐句時間戳

## 本機執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 部署到 Streamlit Community Cloud

1. 將本專案上傳至 GitHub。
2. 前往 Streamlit Community Cloud。
3. 選擇「New app」。
4. 選擇 GitHub 儲存庫、分支與 `app.py`。
5. 點選「Deploy」。

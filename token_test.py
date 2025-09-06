# pip install tiktoken
import tiktoken

encoding = tiktoken.encoding_for_model('gpt-4o')
text = "今からtiktokenのトークンカウントテストを行います"
tokens = encoding.encode(text)
print(len(text))  # 28
print(tokens)  # [2500, 382, 261, 1746, 395, 260, 8251, 2488, 13]
print(len(tokens))  # 9
<source src="https://s3-us-west-2.amazonaws.com/assets.streamlit.io/videos/hero-video.mp4">
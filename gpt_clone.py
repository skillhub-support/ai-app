import os
import streamlit as st
from openai import OpenAI
import tiktoken

def init_page():
    st.set_page_config(page_title="AI Chat App", page_icon="🤖")
    st.header("🤖 AI Chat App")

def get_openai_client():
    """OpenAIクライアントを初期化（Secrets または 環境変数からキーを取得）"""
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def select_model():
    model = st.sidebar.radio("Choose a model:", ("GPT-4.1", "GPT-4.1-mini"))
    if model == "GPT-4.1":
        model_name = "gpt-4.1"
    else:
        model_name = "gpt-4.1-mini"

    temperature = st.sidebar.slider("Temperature:", min_value=0.0, max_value=2.0, value=0.0, step=0.01)

    return model_name, temperature

def get_token_count(messages, model_name, response_text=""):
    """手動でトークン数を計算"""
    try:
        # モデルに応じたエンコーダーを取得!!
        if "gpt-4" in model_name.lower():
            encoding = tiktoken.encoding_for_model("gpt-4")
        else:
            encoding = tiktoken.get_encoding("cl100k_base")

        # メッセージをテキストに変換
        full_text = ""
        for msg in messages:
            if isinstance(msg, dict) and 'content' in msg:
                full_text += msg['content'] + "\n"

        input_tokens = len(encoding.encode(full_text))
        output_tokens = len(encoding.encode(response_text)) if response_text else 0

        return input_tokens, output_tokens, input_tokens + output_tokens
    except Exception as e:
        st.sidebar.error(f"Token count error: {e}")
        return 0, 0, 0

def init_messages():
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    if clear_button or "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        st.session_state.tokens = []

def display_tokens():
    tokens = st.session_state.get('tokens', [])
    st.sidebar.markdown("## Token Usage")

    if tokens:
        # 合計トークン数を計算
        total_prompt_tokens = sum(token_info['prompt_tokens'] for token_info in tokens)
        total_completion_tokens = sum(token_info['completion_tokens'] for token_info in tokens)
        total_tokens = sum(token_info['total_tokens'] for token_info in tokens)

        st.sidebar.markdown("**Total Tokens**")
        st.sidebar.markdown(f"- Input: {total_prompt_tokens:,}")
        st.sidebar.markdown(f"- Output: {total_completion_tokens:,}")
        st.sidebar.markdown(f"- Total: {total_tokens:,}")

        # 最新の3件のみ表示（重複を避けるため）
        if len(tokens) > 1:
            st.sidebar.markdown("**Recent Queries**")
            recent_tokens = tokens[-3:] if len(tokens) > 3 else tokens
            for i, token_info in enumerate(recent_tokens):
                query_num = len(tokens) - len(recent_tokens) + i + 1
                st.sidebar.markdown(f"**Query {query_num}:**")
                st.sidebar.markdown(f"  - Input: {token_info['prompt_tokens']:,}")
                st.sidebar.markdown(f"  - Output: {token_info['completion_tokens']:,}")
                st.sidebar.markdown(f"  - Total: {token_info['total_tokens']:,}")
    else:
        st.sidebar.markdown("**Total Tokens**")
        st.sidebar.markdown("- Input: 0")
        st.sidebar.markdown("- Output: 0")
        st.sidebar.markdown("- Total: 0")

def main():
    init_page()
    model_name, temperature = select_model()
    init_messages()
    display_tokens()

    # チャット履歴を表示
    messages = st.session_state.get('messages', [])
    for message in messages[1:]:  # システムメッセージ以外を表示
        if message["role"] == "assistant":
            with st.chat_message('assistant'):
                st.markdown(message["content"])
        elif message["role"] == "user":
            with st.chat_message('user'):
                st.markdown(message["content"])

    # ユーザー入力
    if user_input := st.chat_input("聞きたいことを入力してね！"):
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            # OpenAI APIの直接ストリーミング
            client = get_openai_client()
            stream = client.chat.completions.create(
                model=model_name,
                messages=st.session_state.messages,
                temperature=temperature,
                stream=True
            )
            response = st.write_stream(stream)

        # 手動でトークン数を計算
        input_tokens, output_tokens, total_tokens = get_token_count(
            st.session_state.messages, model_name, response
        )

        # トークン情報を保存
        token_info = {
            'prompt_tokens': input_tokens,
            'completion_tokens': output_tokens,
            'total_tokens': total_tokens
        }
        st.session_state.tokens.append(token_info)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

if __name__ == "__main__":
    main()

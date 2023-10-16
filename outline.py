import streamlit as st
import openai
from dotenv import load_dotenv
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
import os

def get_bibtex_entries(bib_docs):
    entries = []
    for bib in bib_docs:
        bib_content = bib.read().decode()
        parser = bibtexparser.bparser.BibTexParser(common_strings=True)
        bib_database = bibtexparser.loads(bib_content, parser=parser)
        entries.extend(bib_database.entries)  # 直接添加字典格式的条目到列表
    return entries


def filter_bibtex_entries(bibtex_entries):
    """过滤bibtex_entries, 只保留author, abstract和note字段"""
    filtered_entries = []
    for entry in bibtex_entries:
        filtered_entry = {}
        for key in ["author", "abstract", "note"]:
            if key in entry:
                filtered_entry[key] = entry[key]
        filtered_entries.append(filtered_entry)
    return filtered_entries

def generate_response_with_chat_model(prompt, selected_model):
    # 初始化messages列表，如果尚未在session_state中初始化
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [{"role": "system", "content": "您是一名教授。"}]

    # 添加用户的新消息到聊天历史
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    # 保留最近的2条消息
    st.session_state.chat_history = st.session_state.chat_history[-2:]
    
    response = openai.ChatCompletion.create(
        model=selected_model,
        messages=st.session_state.chat_history,
        n=1  # 请求1个可能的答案
    )

    # 添加模型的响应到聊天历史
    answer = [choice.message['content'] for choice in response.choices][0]
    st.session_state.chat_history.append({"role": "assistant", "content": answer})

    return answer

def generate_paper_outline(bibtex_info, selected_model):
    # 使用bibtex_info和ChatGPT生成论文大纲
    # 这里您可以根据bibtex_info的内容来定制outline_prompt
    outline_prompt = f"为我生成一个基于以下信息的论文大纲：{bibtex_info}"
    outline = generate_response_with_chat_model(outline_prompt, selected_model)
    return outline.split('\n')  # 假设大纲的每一部分都是按行分隔的

def main():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    st.set_page_config(page_title="交互式论文生成器", page_icon=":books:")
    st.write("### 交互式论文生成器 :books:")
    
    with st.sidebar:
        # 添加模型选择功能
        model_options = ["gpt-4", "gpt-3.5-turbo-16k"]
        selected_model = st.selectbox("选择您的模型:", model_options)
        
    with st.sidebar:
        st.subheader("您的文档")
        bib_docs = st.file_uploader("在此上传您的BibTeX文件:", type=["bib"], accept_multiple_files=True)
        reset_button = st.button("重置所有内容")
        if reset_button:
            keys_to_delete = ["previous_content", "chat_history"]
            for key in keys_to_delete:
                if key in st.session_state:
                    del st.session_state[key]
            st.experimental_rerun()

    if bib_docs:
        bibtex_entries = get_bibtex_entries(bib_docs)
        filtered_entries = filter_bibtex_entries(bibtex_entries)
        # 将filtered_entries转换为字符串，以便传递给generate_paper_outline函数
        bibtex_info = '\n'.join([str(entry) for entry in filtered_entries])

        # 生成论文大纲
        if st.button("生成论文大纲"):
            st.session_state.outline = generate_paper_outline(bibtex_info, selected_model)


        # 如果大纲已经生成，为每一部分添加按钮
        if "outline" in st.session_state:
            for index, section in enumerate(st.session_state.outline):
                # 使用章节的索引作为按钮的键
                if st.button(f"生成 {section} 的内容", key=f"btn_{index}"):
                    section_content = generate_response_with_chat_model(section, selected_model)
                    st.write(section_content)


if __name__ == '__main__':
    main()

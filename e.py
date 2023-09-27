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

def generate_response_with_chat_model(prompt):
    # 初始化messages列表，如果尚未在session_state中初始化
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [{"role": "system", "content": "您是一名教授。"}]

    # 添加用户的新消息到聊天历史
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    # 保留最近的2条消息
    st.session_state.chat_history = st.session_state.chat_history[-2:]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=st.session_state.chat_history,
        n=1  # 请求1个可能的答案
    )

    # 添加模型的响应到聊天历史
    answer = [choice.message['content'] for choice in response.choices][0]
    st.session_state.chat_history.append({"role": "assistant", "content": answer})

    return answer


def generate_paper_part(part_name, paper_requirements, bibtex_entries, previous_content="", extra_info="", word_limit=None):
    prompt = f'为要求为{paper_requirements}的论文生成{part_name}'

    if part_name == "introduction":
        filtered_entries = filter_bibtex_entries(bibtex_entries)
        prompt += f', 使用参考文献的摘要和作者: {filtered_entries}'
    elif part_name == "creation":
        prompt += f', 根据文章的introduction: {previous_content["introduction"]}, 为了弥补之前研究的不足，我们提出三个创新点，请分别列出'
    elif part_name == "related_work":
        filtered_entries = filter_bibtex_entries(bibtex_entries)
        prompt += f', 请归纳好相关部分，可以引用参考文献: {filtered_entries}，将这些总结成几部分，分别详细描述这几部分的发展状况'

    elif part_name == "method":
        prompt += f', 基于在creation部分提到: {previous_content["creation"]}扩展，详细描述我们的创新性'
    elif part_name == "conclusion":
        prompt += f', 请根据introduction: {previous_content["introduction"]} 和使用的方法{previous_content["method"]}来写'
    elif part_name == "discussion":
        prompt += f', 根据以上生成的所有内容提供见解和讨论'
    elif part_name == "abstract":
        prompt += f', 考虑论文的创新点: {previous_content["creation"]}和文章的introduction: {previous_content["introduction"]}和文章的总结：{previous_content["conclusion"]}'
    elif part_name == "reference":
        prompt += f'为以下的BibTeX条目生成一个标准引用格式: {bibtex_entries}'

    if word_limit:
        prompt += f'，请输出{word_limit}字'
    print(prompt)
    return generate_response_with_chat_model(prompt)

def main():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    st.set_page_config(page_title="交互式论文生成器", page_icon=":books:")
    st.write("### 交互式论文生成器 :books:")

    with st.sidebar:
        st.subheader("您的文档")
        bib_docs = st.file_uploader("在此上传您的BibTeX文件:", type=["bib"], accept_multiple_files=True)

    if bib_docs:
        bibtex_entries = get_bibtex_entries(bib_docs)
        paper_requirements = st.text_area(label="输入您的论文要求:", label_visibility='hidden')

        if "previous_content" not in st.session_state:
            st.session_state.previous_content = {}

        word_limit_intro = st.number_input("介绍部分的字数要求:", min_value=50, value=500)
        if st.button("生成介绍"):
            generated_intro = generate_paper_part("introduction", paper_requirements, bibtex_entries, word_limit=word_limit_intro)
            st.session_state.previous_content["introduction"] = generated_intro
        st.subheader("介绍")
        st.session_state.previous_content["introduction"] = st.text_area("", st.session_state.previous_content.get("introduction", ""), key="introduction")

        word_limit_creation = st.number_input("创新点部分的字数要求:", min_value=50, value=500)
        if st.button("生成创新点"):
            generated_creation = generate_paper_part("creation", paper_requirements, bibtex_entries, st.session_state.previous_content, word_limit=word_limit_creation)
            st.session_state.previous_content["creation"] = generated_creation
        st.subheader("创新点")
        st.session_state.previous_content["creation"] = st.text_area("", st.session_state.previous_content.get("creation", ""), key="creation")

        word_limit_related_work = st.number_input("相关工作部分的字数要求:", min_value=50, value=500)
        if st.button("生成相关工作"):
            generated_related_work = generate_paper_part("related_work", paper_requirements, bibtex_entries, st.session_state.previous_content, word_limit=word_limit_related_work)
            st.session_state.previous_content["related_work"] = generated_related_work
        st.subheader("相关工作")
        st.session_state.previous_content["related_work"] = st.text_area("", st.session_state.previous_content.get("related_work", ""), key="related_work")

        method_parts_count = st.number_input("您想要多少部分的方法?", min_value=1, max_value=10, value=3)
        word_limits_method = [st.number_input(f"方法 - 部分 {i+1} 的字数要求:", min_value=50, value=500) for i in range(method_parts_count)]
        for i in range(method_parts_count):
            if st.button(f"生成方法 - 部分 {i+1}"):
                generated_method = generate_paper_part("method", paper_requirements, bibtex_entries, st.session_state.previous_content, word_limit=word_limits_method[i])
                if "method" not in st.session_state.previous_content:
                    st.session_state.previous_content["method"] = []
                if len(st.session_state.previous_content["method"]) < i+1:
                    st.session_state.previous_content["method"].append(generated_method)
                else:
                    st.session_state.previous_content["method"][i] = generated_method
            st.subheader(f"方法 - 部分 {i+1}")
            st.session_state.previous_content.setdefault("method", [""] * method_parts_count)
            st.session_state.previous_content["method"][i] = st.text_area("", st.session_state.previous_content["method"][i], key=f"method_{i}")

        word_limit_conclusion = st.number_input("结论部分的字数要求:", min_value=50, value=500)
        if st.button("生成结论"):
            generated_conclusion = generate_paper_part("conclusion", paper_requirements, bibtex_entries, st.session_state.previous_content, word_limit=word_limit_conclusion)
            st.session_state.previous_content["conclusion"] = generated_conclusion
        st.subheader("结论")
        st.session_state.previous_content["conclusion"] = st.text_area("", st.session_state.previous_content.get("conclusion", ""), key="conclusion")

        word_limit_discussion = st.number_input("讨论部分的字数要求:", min_value=50, value=500)
        if st.button("生成讨论"):
            generated_discussion = generate_paper_part("discussion", paper_requirements, bibtex_entries, st.session_state.previous_content, word_limit=word_limit_discussion)
            st.session_state.previous_content["discussion"] = generated_discussion
        st.subheader("讨论")
        st.session_state.previous_content["discussion"] = st.text_area("", st.session_state.previous_content.get("discussion", ""), key="discussion")

        word_limit_abstract = st.number_input("摘要部分的字数要求:", min_value=50, value=300)
        if st.button("生成摘要"):
            generated_abstract = generate_paper_part("abstract", paper_requirements, bibtex_entries, st.session_state.previous_content, word_limit=word_limit_abstract)
            st.session_state.previous_content["abstract"] = generated_abstract
        st.subheader("摘要")
        st.session_state.previous_content["abstract"] = st.text_area("", st.session_state.previous_content.get("abstract", ""), key="abstract")

        if st.button("生成参考文献"):
            st.subheader("参考文献")
            for entry in bibtex_entries:
                formatted_reference = generate_paper_part("reference", paper_requirements, entry, st.session_state.previous_content)
                st.write(formatted_reference)


if __name__ == '__main__':
    main()

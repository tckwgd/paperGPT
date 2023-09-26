import streamlit as st
import bibtexparser
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryMemory
import openai

# 设置OpenAI API 密钥
openai.api_key = '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'

def parse_bib(bib_file_content):
    parser = bibtexparser.bparser.BibTexParser(common_strings=True)
    return bibtexparser.loads(bib_file_content, parser=parser).entries

llm = OpenAI(temperature=0, openai_api_key=openai.api_key)
memory = ConversationSummaryMemory(llm=OpenAI(openai_api_key=openai.api_key))


def generate_paper_conversation(entries, requirements):
    conversation_with_summary = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )

    # 为论文各部分生成内容
    sections = ["Introduction", "Method", "Results", "Discussion", "Conclusion", "Abstract", "References"]
    paper_content = {}

    for section in sections:
        conversation_with_summary.predict(input=f"Generate the {section} section of a paper based on the following references and requirements: {entries} {requirements}")
        paper_content[section] = conversation_with_summary.get_last_response()

    return paper_content

st.title("论文生成器")
uploaded_file = st.file_uploader("上传你的bib文件", type=["bib"])

# 在 Streamlit 应用中使用新的函数
if uploaded_file:
    requirements = st.text_area("请输入你的特定要求：")
    if st.button("生成论文"):
        bib_content = uploaded_file.read().decode()
        entries = parse_bib(bib_content)
        paper_content = generate_paper_conversation(entries, requirements)

        for section, content in paper_content.items():
            st.subheader(section)
            st.text_area(f"{section} 内容如下：", value=content, height=400)

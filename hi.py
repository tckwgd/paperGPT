import streamlit as st
import bibtexparser
import openai

# 设置OpenAI API 密钥
openai.api_key = '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'

def parse_bib(bib_file_content):
    parser = bibtexparser.bparser.BibTexParser(common_strings=True)
    return bibtexparser.loads(bib_file_content, parser=parser).entries

import openai

def generate_content_from_bib(entries, requirements):
    prompt = "Based on the following references: \n\n"
    for entry in entries:
        title = entry.get('title', '')
        author = entry.get('author', '')
        journal = entry.get('journaltitle', '')
        date = entry.get('date', '')
        abstract = entry.get('abstract', '')
        note = entry.get('note', '')

        prompt += f"Title: {title} \n"
        prompt += f"Author(s): {author} \n"
        prompt += f"Journal: {journal}, Date: {date} \n"
        prompt += f"Abstract: {abstract} \n"
        prompt += f"Note: {note} \n\n"

    prompt += f"Based on the above references, please generate a paper that includes the following requirements: {requirements}"
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k", messages=messages)
    return response.choices[0].message['content'].strip()


st.title("论文生成器")
uploaded_file = st.file_uploader("上传你的bib文件", type=["bib"])

if uploaded_file:
    requirements = st.text_area("请输入你的特定要求：")
    if st.button("生成论文"):
        bib_content = uploaded_file.read().decode()
        entries = parse_bib(bib_content)
        paper_content = generate_content_from_bib(entries, requirements)
        st.text_area("你的论文内容如下：", value=paper_content, height=400)

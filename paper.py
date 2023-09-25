import streamlit as st
import openai
from dotenv import load_dotenv
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from htmlTemplates import css, bot_template, user_template
import os

def get_bibtex_entries(bib_docs):
    entries = []
    for bib in bib_docs:
        bib_content = bib.read().decode()
        parser = bibtexparser.bparser.BibTexParser(common_strings=True)
        bib_database = bibtexparser.loads(bib_content, parser=parser)
        for entry in bib_database.entries:
            db = BibDatabase()
            db.entries = [entry]
            entries.append(bibtexparser.dumps(db))
    return entries

def generate_response_with_chat_model(prompt):
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-16k",
      messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

def generate_paper_parts(paper_requirements, bibtex_entries):
    paper_parts = ['引言', '研究方法', '实验与结果', '讨论', '结论', '摘要', '目录', '参考文献']
    generated_paper = {}
    for part in paper_parts:
        prompt = f'Generate {part} for a paper with requirements: {paper_requirements} and references: {bibtex_entries}'
        generated_paper[part] = generate_response_with_chat_model(prompt)
    return generated_paper

def main():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    st.set_page_config(page_title="Auto Paper Generator", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    st.header("Auto Paper Generator :books:")
    paper_requirements = st.text_input("Enter your paper requirements:")
    with st.sidebar:
        st.subheader("Your documents")
        bib_docs = st.file_uploader("Upload your BibTeX files here and click on 'Generate'", type=["bib"], accept_multiple_files=True)
        if st.button("Generate"):
            with st.spinner("Generating"):
                # get bibtex entries
                bibtex_entries = get_bibtex_entries(bib_docs)

                # generate paper
                generated_paper = generate_paper_parts(paper_requirements, bibtex_entries)
                for part, content in generated_paper.items():
                    st.subheader(part)
                    st.write(content)

if __name__ == '__main__':
    main()

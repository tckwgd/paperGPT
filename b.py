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
        for entry in bib_database.entries:
            db = BibDatabase()
            db.entries = [entry]
            entries.append(bibtexparser.dumps(db))
    return entries

def generate_response_with_chat_model(prompt):
    response = openai.ChatCompletion.create(
      model="gpt-4",
      messages=[
            {"role": "system", "content": "You are a professor."},
            {"role": "user", "content": prompt}
        ],
      n=1  # request 1 possible responses
    )
    return [choice.message['content'] for choice in response.choices][0]  # take the first response

def generate_paper_part(part_name, paper_requirements, bibtex_entries, previous_content="", extra_info=""):
    prompt = f'Generate {part_name} for a paper with requirements: {paper_requirements}'

    if part_name == "introduction":
        prompt += f', using the abstracts and authors from references: {bibtex_entries}'
    elif part_name == "creation":
        prompt += ', summarizing the main innovations and providing an outline of the paper'
    elif part_name == "related_work":
        prompt += f', based on the articles in the references: {bibtex_entries}'
    elif part_name == "method":
        prompt += f', expanding on the details mentioned in the creation section: {previous_content["creation"]}'
    elif part_name == "conclusion":
        prompt += f', summarizing the introduction: {previous_content["introduction"]} and the methods used'
    elif part_name == "discussion":
        prompt += f', providing insights and discussions based on all the content generated above'

    return generate_response_with_chat_model(prompt)

def main():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    st.set_page_config(page_title="Interactive Paper Generator", page_icon=":books:")
    st.write("### Interactive Paper Generator :books:")

    with st.sidebar:
        st.subheader("Your documents")
        bib_docs = st.file_uploader("Upload your BibTeX files here:", type=["bib"], accept_multiple_files=True)

    if bib_docs:
        bibtex_entries = get_bibtex_entries(bib_docs)
        paper_requirements = st.text_area("Enter your paper requirements:")

        if "previous_content" not in st.session_state:
            st.session_state.previous_content = {}

        # Generate Introduction
        if st.button("Generate Introduction"):
            generated_intro = generate_paper_part("introduction", paper_requirements, bibtex_entries)
            st.session_state.previous_content["introduction"] = generated_intro
        st.subheader("Introduction")
        st.session_state.previous_content["introduction"] = st.text_area("", st.session_state.previous_content.get("introduction", ""), key="introduction")

        # Generate Creation
        if st.button("Generate Creation"):
            generated_creation = generate_paper_part("creation", paper_requirements, bibtex_entries, st.session_state.previous_content)
            st.session_state.previous_content["creation"] = generated_creation
        st.subheader("Creation")
        st.session_state.previous_content["creation"] = st.text_area("", st.session_state.previous_content.get("creation", ""), key="creation")

        # Generate Related Work
        if st.button("Generate Related Work"):
            generated_related_work = generate_paper_part("related_work", paper_requirements, bibtex_entries, st.session_state.previous_content)
            st.session_state.previous_content["related_work"] = generated_related_work
        st.subheader("Related Work")
        st.session_state.previous_content["related_work"] = st.text_area("", st.session_state.previous_content.get("related_work", ""), key="related_work")

        # Generate method parts
        method_parts_count = st.number_input("How many method parts you want?", min_value=1, max_value=10, value=3)
        for i in range(method_parts_count):
            if st.button(f"Generate Method - Part {i+1}"):
                generated_method = generate_paper_part("method", paper_requirements, bibtex_entries, st.session_state.previous_content)
                if "method" not in st.session_state.previous_content:
                    st.session_state.previous_content["method"] = []
                if len(st.session_state.previous_content["method"]) < i+1:
                    st.session_state.previous_content["method"].append(generated_method)
                else:
                    st.session_state.previous_content["method"][i] = generated_method
            st.subheader(f"Method - Part {i+1}")
            st.session_state.previous_content.setdefault("method", [""] * method_parts_count)
            st.session_state.previous_content["method"][i] = st.text_area("", st.session_state.previous_content["method"][i], key=f"method_{i}")

        # Generate Conclusion
        if st.button("Generate Conclusion"):
            generated_conclusion = generate_paper_part("conclusion", paper_requirements, bibtex_entries, st.session_state.previous_content)
            st.session_state.previous_content["conclusion"] = generated_conclusion
        st.subheader("Conclusion")
        st.session_state.previous_content["conclusion"] = st.text_area("", st.session_state.previous_content.get("conclusion", ""), key="conclusion")

        # Generate Discussion
        if st.button("Generate Discussion"):
            generated_discussion = generate_paper_part("discussion", paper_requirements, bibtex_entries, st.session_state.previous_content)
            st.session_state.previous_content["discussion"] = generated_discussion
        st.subheader("Discussion")
        st.session_state.previous_content["discussion"] = st.text_area("", st.session_state.previous_content.get("discussion", ""), key="discussion")

        # Display References
        if st.button("Generate References"):
            st.subheader("References")
            for entry in bibtex_entries:
                st.write(entry)

if __name__ == '__main__':
    main()

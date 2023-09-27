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
      model="gpt-3.5-turbo-16k",
      messages=[
            {"role": "system", "content": "You are a professor."},
            {"role": "user", "content": prompt}
        ],
      n=1  # request 1 possible responses
    )
    return [choice.message['content'] for choice in response.choices][0]  # Return the first response as string

def generate_paper_part(part_name, paper_requirements, bibtex_entries, previous_content="", extra_info=""):
    prompt = f'Generate {part_name} for a paper with requirements: {paper_requirements}, references: {bibtex_entries}, previous content: {previous_content} and extra information: {extra_info}'
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
        total_word_count = st.number_input("Desired total word count:", min_value=1000)
        language_choice = st.radio("Choose a language:", ["English", "Chinese"])

        # Initialize session state for previous content
        if "previous_content" not in st.session_state:
            st.session_state.previous_content = {
                "introduction": "",
                "creation": "",
                "related_work": "",
                "method": [],
                "conclusion": "",
                "discussion": ""
            }

        if st.button("Generate Introduction"):
            generated_intro = generate_paper_part("introduction", paper_requirements, bibtex_entries)
            st.session_state.previous_content["introduction"] = generated_intro

        st.subheader("Introduction")
        st.session_state.previous_content["introduction"] = st.text_area("Introduction Text Area", st.session_state.previous_content["introduction"], key="introduction")

        if st.button("Generate Creation"):
            generated_creation = generate_paper_part("creation", paper_requirements, bibtex_entries, st.session_state.previous_content["introduction"])
            print(st.session_state.previous_content["introduction"])
            st.session_state.previous_content["creation"] = generated_creation

        st.subheader("Creation")
        st.session_state.previous_content["creation"] = st.text_area("Creation Text Area", st.session_state.previous_content["creation"], key="creation")

        if st.button("Generate Related Work"):
            generated_related_work = generate_paper_part("related_work", paper_requirements, bibtex_entries, st.session_state.previous_content["introduction"])
            st.session_state.previous_content["related_work"] = generated_related_work

        st.subheader("Related Work")
        st.session_state.previous_content["related_work"] = st.text_area("Related Work Text Area", st.session_state.previous_content["related_work"], key="related_work")

        # Display method parts
        method_parts_count = st.number_input("How many method parts you want?", min_value=1, max_value=10, value=3)
        for i in range(method_parts_count):
            if st.button(f"Generate Method - Part {i+1}"):
                generated_method = generate_paper_part("method", paper_requirements, bibtex_entries, st.session_state.previous_content["creation"])
                if len(st.session_state.previous_content["method"]) < i+1:
                    st.session_state.previous_content["method"].append(generated_method)
                else:
                    st.session_state.previous_content["method"][i] = generated_method
            st.subheader(f"Method - Part {i+1}")
            if len(st.session_state.previous_content["method"]) < i+1:
                st.session_state.previous_content["method"].append("")
            st.session_state.previous_content["method"][i] = st.text_area(f"Method Part {i+1} Text Area", st.session_state.previous_content["method"][i], key=f"method_{i}")

        if st.button("Generate Conclusion"):
            generated_conclusion = generate_paper_part("conclusion", paper_requirements, bibtex_entries, st.session_state.previous_content["introduction"] + "".join(st.session_state.previous_content["method"]))
            st.session_state.previous_content["conclusion"] = generated_conclusion

        st.subheader("Conclusion")
        st.session_state.previous_content["conclusion"] = st.text_area("Conclusion Text Area", st.session_state.previous_content["conclusion"], key="conclusion")

        if st.button("Generate Discussion"):
            content_summary = st.session_state.previous_content["introduction"] + st.session_state.previous_content["creation"] + "".join(st.session_state.previous_content["method"]) + st.session_state.previous_content["conclusion"]
            generated_discussion = generate_paper_part("discussion", paper_requirements, bibtex_entries, content_summary)
            st.session_state.previous_content["discussion"] = generated_discussion

        st.subheader("Discussion")
        st.session_state.previous_content["discussion"] = st.text_area("Discussion Text Area", st.session_state.previous_content["discussion"], key="discussion")

        if st.button("Generate References"):
            # Just display the references for now
            st.subheader("References")
            for entry in bibtex_entries:
                st.write(entry)

if __name__ == '__main__':
    main()

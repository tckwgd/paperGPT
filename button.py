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
    return [choice.message['content'] for choice in response.choices]

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

        # Placeholder for previous content
        previous_content = {
            "introduction": "",
            "creation": "",
            "related_work": "",
            "method": [],
            "conclusion": "",
            "discussion": ""
        }

        if st.button("Generate Introduction"):
            generated_intro = generate_paper_part("introduction", paper_requirements, bibtex_entries)
            previous_content["introduction"] = generated_intro
            st.subheader("Introduction")
            st.write(generated_intro)

        if st.button("Generate Creation"):
            generated_creation = generate_paper_part("creation", paper_requirements, bibtex_entries, previous_content["introduction"])
            previous_content["creation"] = generated_creation
            st.subheader("Creation")
            st.write(generated_creation)

        if st.button("Generate Related Work"):
            generated_related_work = generate_paper_part("related_work", paper_requirements, bibtex_entries, previous_content["introduction"])
            previous_content["related_work"] = generated_related_work
            st.subheader("Related Work")
            st.write(generated_related_work)

        for i in range(3):
            if st.button(f"Generate Method - Part {i+1}"):
                generated_method = generate_paper_part("method", paper_requirements, bibtex_entries, previous_content["creation"])
                previous_content["method"].append(generated_method)
                st.subheader(f"Method - Part {i+1}")
                st.write(generated_method)

        if st.button("Generate Conclusion"):
            generated_conclusion = generate_paper_part("conclusion", paper_requirements, bibtex_entries, previous_content["introduction"] + "".join(previous_content["method"]))
            print(previous_content["method"])
            previous_content["conclusion"] = generated_conclusion
            st.subheader("Conclusion")
            st.write(generated_conclusion)

        if st.button("Generate Discussion"):
            content_summary = previous_content["introduction"] + previous_content["creation"] + "".join(previous_content["method"]) + previous_content["conclusion"]
            generated_discussion = generate_paper_part("discussion", paper_requirements, bibtex_entries, content_summary)
            st.subheader("Discussion")
            st.write(generated_discussion)

        if st.button("Generate References"):
            # Just display the references for now
            st.subheader("References")
            for entry in bibtex_entries:
                st.write(entry)

if __name__ == '__main__':
    main()

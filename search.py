import streamlit as st
import requests

CROSSREF_API_URL = "https://api.crossref.org/works"
HEADERS = {
    "User-Agent": "BibRetriever/1.0 (your_email@example.com)"  # 替换为你的真实邮箱
}

def get_bib_from_crossref(doi):
    response = requests.get(f"{CROSSREF_API_URL}/{doi}/transform/application/x-bibtex", headers=HEADERS)
    return response.text if response.status_code == 200 else None

def search_papers(keyword, num_papers):
    response = requests.get(CROSSREF_API_URL, params={"query": keyword, "rows": num_papers}, headers=HEADERS)
    if response.status_code == 200:
        items = response.json()["message"]["items"]
        bibtex_entries = []
        for item in items:
            doi = item["DOI"]
            bib_data = get_bib_from_crossref(doi)
            abstract = item.get("abstract", "")
            # 添加摘要到 Bibtex 项
            modified_bib_data = bib_data.rstrip("}\n") + f",\n  abstract = {{{abstract}}}\n" + "}\n"
            bibtex_entries.append(modified_bib_data)
        return bibtex_entries
    else:
        return []


st.title("Bib Retriever")
keyword = st.text_input("Enter Keyword:")
num_papers = st.number_input("Number of Papers:", min_value=1, max_value=100, value=1)
if st.button("Search"):
    results = search_papers(keyword, num_papers)
    for result in results:
        if result:
            st.text(result)
        else:
            st.warning("Unable to retrieve the bib data for one of the papers.")


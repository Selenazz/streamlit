import streamlit as st
import json
import os
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Better Notion",
    layout="wide"
)

st.title("Notion for Literature")

# Load literature data
DATA_FILE = "example-bib.json"  # All available papers
BOOKMARKS_FILE = "bookmarks.json"  # Bookmarked papers

def load_literature():
    """Load literature from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            # Handle both array format and object with "references" key
            if isinstance(data, dict) and "references" in data:
                return data["references"]
            elif isinstance(data, list):
                return data
    return []

def load_bookmarks():
    """Load bookmarked papers"""
    if os.path.exists(BOOKMARKS_FILE):
        with open(BOOKMARKS_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, dict) and "references" in data:
                return data["references"]
            elif isinstance(data, list):
                return data
    return []

def save_bookmarks(bookmarks_list):
    """Save bookmarked papers to JSON file"""
    with open(BOOKMARKS_FILE, "w") as f:
        json.dump({"references": bookmarks_list}, f, indent=2)

def add_bookmark(paper):
    """Add a paper to bookmarks"""
    bookmarks = load_bookmarks()
    # Check if already bookmarked
    if not any(b.get('id') == paper.get('id') for b in bookmarks):
        bookmarks.append(paper)
        save_bookmarks(bookmarks)
        return True
    return False

def remove_bookmark(paper_id):
    """Remove a paper from bookmarks"""
    bookmarks = load_bookmarks()
    bookmarks = [b for b in bookmarks if b.get('id') != paper_id]
    save_bookmarks(bookmarks)

def is_bookmarked(paper_id):
    """Check if a paper is bookmarked"""
    bookmarks = load_bookmarks()
    return any(b.get('id') == paper_id for b in bookmarks)

# Load existing data
literature = load_literature()
bookmarks = load_bookmarks()

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search", "📖 Browse All", "⭐ Bookmarks", "➕ Add Literature"])

with tab1:
    st.header("Search Literature")
    col1, col2 = st.columns([12, 1])
    with col1:
        search_query = st.text_input("Search by title or author:", label_visibility="collapsed")
    with col2:
        search_button = st.button("🔍", help="Search", use_container_width=True)
    
    if search_query and search_button:
        results = []
        for item in literature:
            # Search in title
            if search_query.lower() in item['title'].lower():
                results.append(item)
            # Search in authors (handle list)
            else:
                authors = item.get('authors', [])
                if isinstance(authors, list):
                    authors_str = " ".join(authors)
                else:
                    authors_str = str(authors)
                if search_query.lower() in authors_str.lower():
                    results.append(item)
        
        if results:
            st.write(f"Found {len(results)} result(s)")
            for item in results:
                authors = item.get('authors', [])
                if isinstance(authors, list):
                    authors_str = ", ".join(authors)
                else:
                    authors_str = str(authors)
                
                col1, col2 = st.columns([11, 1])
                with col1:
                    st.write(f"**{item['title']}** ({item['year']})")
                    st.write(f"*{authors_str}*")
                    if item.get('journal'):
                        st.write(f"Journal: {item['journal']}")
                    if item.get('publication'):
                        st.write(f"Publication: {item['publication']}")
                    if item.get('doi'):
                        st.write(f"DOI: [{item['doi']}](https://doi.org/{item['doi']})")
                    if item.get('abstract'):
                        st.write(f"Abstract: {item['abstract']}")
                with col2:
                    if is_bookmarked(item.get('id')):
                        if st.button("⭐", key=f"unbookmark_search_{item.get('id')}", help="Remove bookmark"):
                            remove_bookmark(item.get('id'))
                            st.rerun()
                    else:
                        if st.button("☆", key=f"bookmark_search_{item.get('id')}", help="Bookmark"):
                            add_bookmark(item)
                            st.rerun()
                st.divider()
        else:
            st.warning("No results found")

with tab2:
    st.header("Browse All Literature")
    if literature:
        for i, item in enumerate(literature):
            with st.expander(f"📄 {item['title']} ({item['year']})"):
                col1, col2 = st.columns([4, 1])
                with col1:
                    # Format authors
                    authors = item.get('authors', [])
                    if isinstance(authors, list):
                        authors_str = ", ".join(authors)
                    else:
                        authors_str = str(authors)
                    st.write(f"**Authors:** {authors_str}")
                    
                    # Show journal info if available
                    if item.get('journal'):
                        st.write(f"**Journal:** {item['journal']}")
                    
                    # Show publication details
                    if item.get('publication'):
                        st.write(f"**Publication:** {item['publication']}")
                    
                    # Show volume/issue/pages if available
                    vol_info = []
                    if item.get('volume'):
                        vol_info.append(f"Vol. {item['volume']}")
                    if item.get('issue'):
                        vol_info.append(f"Issue {item['issue']}")
                    if item.get('pages'):
                        vol_info.append(f"pp. {item['pages']}")
                    if vol_info:
                        st.write(f"**Details:** {', '.join(vol_info)}")
                    
                    st.write(f"**Year:** {item['year']}")
                    
                    if item.get('doi'):
                        st.write(f"**DOI:** [{item['doi']}](https://doi.org/{item['doi']})")
                    if item.get('url'):
                        st.write(f"**URL:** [Link]({item['url']})")
                    if item.get('abstract'):
                        st.write(f"**Abstract:** {item['abstract']}")
                    if item.get('notes'):
                        st.write(f"**Notes:** {item['notes']}")
                with col2:
                    if is_bookmarked(item.get('id')):
                        if st.button("⭐", key=f"unbookmark_{item.get('id')}", help="Remove bookmark"):
                            remove_bookmark(item.get('id'))
                            st.rerun()
                    else:
                        if st.button("☆", key=f"bookmark_{item.get('id')}", help="Bookmark"):
                            add_bookmark(item)
                            st.rerun()
    else:
        st.info("No literature found. Try searching!")

with tab3:
    st.header("⭐ Bookmarked Papers")
    if bookmarks:
        for i, item in enumerate(bookmarks):
            with st.expander(f"📄 {item['title']} ({item['year']})"):
                col1, col2 = st.columns([4, 1])
                with col1:
                    # Format authors
                    authors = item.get('authors', [])
                    if isinstance(authors, list):
                        authors_str = ", ".join(authors)
                    else:
                        authors_str = str(authors)
                    st.write(f"**Authors:** {authors_str}")
                    
                    # Show journal info if available
                    if item.get('journal'):
                        st.write(f"**Journal:** {item['journal']}")
                    
                    # Show publication details
                    if item.get('publication'):
                        st.write(f"**Publication:** {item['publication']}")
                    
                    # Show volume/issue/pages if available
                    vol_info = []
                    if item.get('volume'):
                        vol_info.append(f"Vol. {item['volume']}")
                    if item.get('issue'):
                        vol_info.append(f"Issue {item['issue']}")
                    if item.get('pages'):
                        vol_info.append(f"pp. {item['pages']}")
                    if vol_info:
                        st.write(f"**Details:** {', '.join(vol_info)}")
                    
                    st.write(f"**Year:** {item['year']}")
                    
                    if item.get('doi'):
                        st.write(f"**DOI:** [{item['doi']}](https://doi.org/{item['doi']})")
                    if item.get('url'):
                        st.write(f"**URL:** [Link]({item['url']})")
                    if item.get('abstract'):
                        st.write(f"**Abstract:** {item['abstract']}")
                    if item.get('notes'):
                        st.write(f"**Notes:** {item['notes']}")
                with col2:
                    if st.button("❌", key=f"remove_bookmark_{item.get('id')}", help="Remove from bookmarks"):
                        remove_bookmark(item.get('id'))
                        st.rerun()
    else:
        st.info("No bookmarked papers yet. Click the ☆ icon to bookmark papers!")

with tab4:
    st.header("Add New Literature")
    with st.form("add_literature_form"):
        title = st.text_input("Title *", placeholder="Enter the title")
        authors = st.text_input("Authors *", placeholder="Comma-separated names")
        year = st.number_input("Year *", min_value=1900, max_value=datetime.now().year, value=datetime.now().year)
        publication = st.text_input("Publication/Journal/Conference", placeholder="Where was it published?")
        url = st.text_input("URL (optional)", placeholder="https://...")
        notes = st.text_area("Notes (optional)", placeholder="Your observations or summary")
        
        submitted = st.form_submit_button("Add Literature to Bookmarks")
        if submitted:
            if not title or not authors:
                st.error("Please fill in Title and Authors fields")
            else:
                # Generate a unique ID
                max_id = max([item.get('id', 0) for item in literature], default=0)
                new_item = {
                    "id": max_id + 1,
                    "title": title,
                    "authors": authors.split(",") if "," in authors else [authors],
                    "year": int(year),
                    "publication": publication,
                    "url": url,
                    "notes": notes,
                    "added_date": datetime.now().isoformat()
                }
                add_bookmark(new_item)
                st.success("Paper added to bookmarks!")
                st.rerun()
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

# Add version toggle
col1, col2 = st.columns([10, 2])
with col2:
    version = st.radio("Version:", ["no-AI", "AI"], horizontal=True)

st.divider()

# Load literature data
DATA_FILE = "example-bib.json"  # All available papers
BOOKMARKS_FILE = "bookmarks.json"  # Bookmarked papers
METADATA_FILE = "bookmarks_metadata.json"  # Tags and comments for bookmarks

def load_literature():
    """Load literature from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            # Handle both array format and object with "references" key
            if isinstance(data, dict) and "references" in data:
                items = data["references"]
            elif isinstance(data, list):
                items = data
            else:
                return []
            
            # Ensure all items have IDs
            for i, item in enumerate(items):
                if 'id' not in item:
                    item['id'] = i + 1
            return items
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

def load_metadata():
    """Load bookmark metadata (tags, comments, colors)"""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_metadata(metadata):
    """Save bookmark metadata"""
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)

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
    # Also remove metadata
    metadata = load_metadata()
    if str(paper_id) in metadata:
        del metadata[str(paper_id)]
        save_metadata(metadata)

def is_bookmarked(paper_id):
    """Check if a paper is bookmarked"""
    bookmarks = load_bookmarks()
    return any(b.get('id') == paper_id for b in bookmarks)

def get_bookmark_metadata(paper_id):
    """Get tags and comments for a bookmark"""
    metadata = load_metadata()
    return metadata.get(str(paper_id), {"tags": [], "comments": "", "tag_colors": {}})

def get_paper_title_by_id(paper_id):
    """Get paper title by ID"""
    for paper in literature:
        if paper.get('id') == paper_id:
            return paper.get('title', 'Unknown')
    return 'Unknown'

def display_citation_links(cites_list, cited_by_list, context=""):
    """Display citation links with copy-to-clipboard functionality
    
    Args:
        cites_list: List of paper IDs this paper cites
        cited_by_list: List of paper IDs that cite this paper
        context: Unique context string to avoid duplicate keys (e.g., "search_0", "browse_5", "bookmarks_3")
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Cites:**")
        if cites_list:
            # Create buttons for copying citation IDs
            cols = st.columns(len(cites_list))
            for idx, cite_id in enumerate(cites_list):
                with cols[idx]:
                    paper_title = get_paper_title_by_id(cite_id)
                    if st.button(f"#{cite_id}", key=f"cite_link_{context}_{cite_id}", help=f"{paper_title}"):
                        st.toast(f"{paper_title}\n(ID: {cite_id})\n\nPaste ID in search bar to view")
        else:
            st.caption("No cites found")
    
    with col2:
        st.write("**Cited by:**")
        if cited_by_list:
            # Create buttons for copying cited_by IDs
            cols = st.columns(len(cited_by_list))
            for idx, cited_by_id in enumerate(cited_by_list):
                with cols[idx]:
                    paper_title = get_paper_title_by_id(cited_by_id)
                    if st.button(f"#{cited_by_id}", key=f"cited_by_link_{context}_{cited_by_id}", help=f"{paper_title}"):
                        st.toast(f"{paper_title}\n(ID: {cited_by_id})\n\nPaste title or ID in search bar to view")
        else:
            st.caption("No citations found")
        
        # Add instructional text
        st.caption("Search ID in the search tab to view the paper")

# Load existing data
literature = load_literature()
bookmarks = load_bookmarks()

# Initialize tab state for citation navigation
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# ===== NO-AI VERSION =====
if version == "no-AI":

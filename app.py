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

# Create tabs
tab1, tab2, tab3 = st.tabs(["🔍 Search", "📖 Browse All", "⭐ Bookmarks"])

with tab1:
    st.header("Search Literature")
    
    # Initialize session state for search
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'show_search_results' not in st.session_state:
        st.session_state.show_search_results = False
    
    col1, col2 = st.columns([12, 1])
    with col1:
        # Update session state when text input changes
        def on_search_input_change():
            st.session_state.search_query = st.session_state.search_box_widget
            st.session_state.show_search_results = True
        
        search_query = st.text_input(
            "Search by title or author:", 
            value=st.session_state.search_query, 
            label_visibility="collapsed", 
            on_change=on_search_input_change, 
            key="search_box_widget"
        )
    with col2:
        search_button = st.button("🔍", help="Search", use_container_width=True)
    
    # Only update session state if user actually typed something or button was clicked
    # This prevents overwriting the citation button's session state update
    if search_button:
        st.session_state.search_query = st.session_state.search_box_widget
        st.session_state.show_search_results = True
    
    # Clear results if search box is emptied
    if not st.session_state.search_box_widget:
        st.session_state.show_search_results = False
    
    if search_query and st.session_state.show_search_results:
        results = []
        
        # Try to search by ID first
        try:
            search_id = int(search_query.strip())
            for item in literature:
                if item.get('id') == search_id:
                    results.append(item)
        except ValueError:
            # If not a number, search by title and authors
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
            for i, item in enumerate(results):
                with st.expander(f" {item['title']} ({item['year']})"):
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
                        
                        # Display citation links
                        cites = item.get('cites', [])
                        cited_by = item.get('cited_by', [])
                        if cites or cited_by:
                            st.divider()
                            display_citation_links(cites, cited_by, context=f"search_{i}_{item.get('id')}")
                    with col2:
                        if is_bookmarked(item.get('id')):
                            if st.button("⭐", key=f"search_unbookmark_{i}_{item.get('id')}", help="Remove bookmark"):
                                remove_bookmark(item.get('id'))
                                st.rerun()
                        else:
                            if st.button("☆", key=f"search_bookmark_{i}_{item.get('id')}", help="Bookmark"):
                                add_bookmark(item)
                                st.rerun()
        else:
            st.warning("No results found")

with tab2:
    st.header("Browse All Literature")
    if literature:
        for i, item in enumerate(literature):
            with st.expander(f" {item['title']} ({item['year']})"):
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
                    
                    # Display citation links
                    cites = item.get('cites', [])
                    cited_by = item.get('cited_by', [])
                    if cites or cited_by:
                        st.divider()
                        display_citation_links(cites, cited_by, context=f"browse_{i}_{item.get('id')}")
                with col2:
                    if is_bookmarked(item.get('id')):
                        if st.button("⭐", key=f"browse_unbookmark_{i}_{item.get('id')}", help="Remove bookmark"):
                            remove_bookmark(item.get('id'))
                            st.rerun()
                    else:
                        if st.button("☆", key=f"browse_bookmark_{i}_{item.get('id')}", help="Bookmark"):
                            add_bookmark(item)
                            st.rerun()
    else:
        st.info("No literature found. Try searching!")

with tab3:
    st.header("⭐ Bookmarked Papers")
    if bookmarks:
        for i, item in enumerate(bookmarks):
            # Get metadata for this bookmark
            metadata = get_bookmark_metadata(item.get('id'))
            tags = metadata.get('tags', [])
            comments = metadata.get('comments', '')
            tag_colors = metadata.get('tag_colors', {})
            
            # Create expander title with tags and comments preview
            tag_display = ""
            if tags:
                # Define emoji color options (must match the selectbox options)
                emoji_colors = {
                    '🔴 Red': '#FF0000',
                    '🟠 Orange': '#FFA500',
                    '🟡 Yellow': '#FFFF00',
                    '🟢 Green': '#00FF00',
                    '🔵 Blue': '#0000FF',
                    '🟣 Purple': '#800080',
                    '🟤 Brown': '#8B4513',
                    '⚫ Black': '#000000',
                    '⚪ White': '#FFFFFF',
                    '🩶 Gray': '#808080'
                }
                
                # Create reverse mapping from hex to emoji
                hex_to_emoji = {v.upper(): k.split()[0] for k, v in emoji_colors.items()}
                
                tag_parts = []
                for tag in tags:
                    hex_color = tag_colors.get(tag, '#0000FF').upper()
                    emoji = hex_to_emoji.get(hex_color, '🔵')  # Default to blue if not found
                    tag_parts.append(f"{emoji} {tag}")
                tag_display = " | " + ", ".join(tag_parts)
            
            comment_preview = ""
            if comments:
                # Show first 100 chars of comments
                preview_text = comments[:100].replace('\n', ' ')
                if len(comments) > 100:
                    comment_preview = f" | 💬 {preview_text}..."
                else:
                    comment_preview = f" | 💬 {preview_text}"
            
            expander_title = f" {item['title']} ({item['year']}){tag_display}{comment_preview}"
            
            with st.expander(expander_title):
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
                    
                    # Display citation links
                    cites = item.get('cites', [])
                    cited_by = item.get('cited_by', [])
                    if cites or cited_by:
                        st.divider()
                        display_citation_links(cites, cited_by, context=f"bookmarks_{i}_{item.get('id')}")
                    
                    # Tags and Comments Section
                    st.divider()
                    st.subheader("Tags & Comments")
                    
                    # Tags management
                    st.write("**Tags:**")
                    
                    # Get all available tags from all bookmarks for suggestions
                    all_metadata = load_metadata()
                    all_tags = set()
                    for meta in all_metadata.values():
                        all_tags.update(meta.get('tags', []))
                    available_tags = sorted(list(all_tags))
                    
                    # Display suggestion of existing tags
                    if available_tags:
                        st.caption(f"💡 Existing tags: {', '.join(available_tags)}")
                    
                    # Text input for tags (comma-separated)
                    tags_input = st.text_input(
                        "Enter tags (comma-separated):",
                        value=", ".join(tags),
                        key=f"tags_input_{i}_{item.get('id')}"
                    )
                    
                    # Parse the tags input
                    selected_tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                    
                    # Color picker for each tag
                    if selected_tags:
                        st.write("**Tag Colors:**")
                        
                        # Define emoji color options
                        emoji_colors = {
                            '🔴 Red': '#FF0000',
                            '🟠 Orange': '#FFA500',
                            '🟡 Yellow': '#FFFF00',
                            '🟢 Green': '#00FF00',
                            '🔵 Blue': '#0000FF',
                            '🟣 Purple': '#800080',
                            '🟤 Brown': '#8B4513',
                            '⚫ Black': '#000000',
                            '⚪ White': '#FFFFFF',
                            '🩶 Gray': '#808080'
                        }
                        
                        for tag in selected_tags:
                            col_tag, col_color = st.columns([3, 1])
                            with col_tag:
                                st.write(f" {tag}")
                            with col_color:
                                # Find current color label
                                current_hex = tag_colors.get(tag, '#0000FF')
                                current_label = '🔵 Blue'  # default
                                for label, hex_val in emoji_colors.items():
                                    if hex_val == current_hex:
                                        current_label = label
                                        break
                                
                                selected_color_label = st.selectbox(
                                    label=f"Color for {tag}",
                                    options=list(emoji_colors.keys()),
                                    index=list(emoji_colors.keys()).index(current_label) if current_label in emoji_colors.keys() else 0,
                                    key=f"color_{i}_{tag}",
                                    label_visibility="collapsed"
                                )
                                tag_colors[tag] = emoji_colors[selected_color_label]
                    
                    # Comments
                    st.write("**Comments:**")
                    new_comments = st.text_area(
                        "Add your notes or observations",
                        value=comments,
                        key=f"comments_{i}_{item.get('id')}",
                        height=100
                    )
                    
                    # Save button
                    if st.button("💾 Save Tags & Comments", key=f"save_metadata_{i}_{item.get('id')}"):
                        # Save metadata
                        metadata = load_metadata()
                        metadata[str(item.get('id'))] = {
                            "tags": selected_tags,
                            "comments": new_comments,
                            "tag_colors": tag_colors
                        }
                        save_metadata(metadata)
                        st.success("Tags and comments saved!")
                        st.rerun()
                
                with col2:
                    if st.button("❌", key=f"bookmarks_remove_{i}_{item.get('id')}", help="Remove from bookmarks"):
                        remove_bookmark(item.get('id'))
                        st.rerun()
    else:
        st.info("No bookmarked papers yet. Click the ☆ icon to bookmark papers!")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Read the file
with open('app.py', 'r') as f:
    lines = f.readlines()

# Find the line with "display_citation_links(cites, cited_by, context=f"bookmarks_" in the AI version
# We need to find the second occurrence (the first is in no-AI)
count = 0
insert_line = -1
for i, line in enumerate(lines):
    if 'display_citation_links(cites, cited_by, context=f"bookmarks_' in line:
        count += 1
        if count == 2:  # This is the AI version
            insert_line = i
            break

if insert_line != -1:
    # Find the "# Display citation links" comment before this line
    for j in range(insert_line - 1, -1, -1):
        if "# Display citation links" in lines[j]:
            ai_summary_code = [
                "                        # AI Summary - AI version specific\n",
                "                        st.divider()\n",
                "                        st.subheader('🤖 AI Summary')\n",
                "                        with st.spinner('Generating summary...'):\n",
                "                            summary = get_ai_summary(item['title'], item.get('id'))\n",
                "                        st.write(summary)\n",
                "                        \n",
            ]
            lines = lines[:j] + ai_summary_code + lines[j:]
            break
    
    # Write back
    with open('app.py', 'w') as f:
        f.writelines(lines)
    
    print("OK: AI summary code inserted in AI version's Bookmarks tab")
else:
    print("ERROR: Could not find the location to insert AI summary in Bookmarks tab")

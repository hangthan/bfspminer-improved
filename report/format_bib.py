import re
from pathlib import Path

bib_file = r"d:\2026\bfspminer-improved\report\references.bib"
with open(bib_file, "r", encoding="utf-8") as f:
    content = f.read()

# very basic parsing since bibtex parser might not be installed
entries = []
current_entry = ""
for line in content.split("\n"):
    if line.strip().startswith("@"):
        if current_entry:
            entries.append(current_entry)
        current_entry = line + "\n"
    elif current_entry:
        current_entry += line + "\n"
if current_entry:
    entries.append(current_entry)

parsed_entries = []
for entry in entries:
    type_match = re.search(r"@(\w+)\{([^,]+),", entry)
    if not type_match: continue
    e_type = type_match.group(1).lower()
    e_id = type_match.group(2)
    
    # parse fields
    fields = {}
    field_matches = re.finditer(r"(\w+)\s*=\s*(?:\{|\")?(.+?)(?:\}|\")?,?(?=\n)", entry)
    for m in field_matches:
        key = m.group(1).lower()
        val = m.group(2).strip()
        fields[key] = val
        
    author = fields.get("author", "").replace(" and ", ", ")
    title = fields.get("title", "").replace("{", "").replace("}", "")
    year = fields.get("year", "")
    journal = fields.get("journal", fields.get("booktitle", ""))
    volume = fields.get("volume", "")
    number = fields.get("number", "")
    pages = fields.get("pages", "").replace("--", "-")
    publisher = fields.get("publisher", "")
    howpublished = fields.get("howpublished", "")
    note = fields.get("note", "")
    
    parsed_entries.append({
        "id": e_id,
        "type": e_type,
        "author": author,
        "title": title,
        "year": year,
        "journal": journal,
        "volume": volume,
        "number": number,
        "pages": pages,
        "publisher": publisher,
        "howpublished": howpublished,
        "note": note
    })

# sort by author
parsed_entries.sort(key=lambda x: x["author"].lower())

out = []
out.append("\\begin{thebibliography}{99}")
out.append("\\setlength{\\itemindent}{-1cm}")
out.append("\\setlength{\\leftmargin}{1cm}")
out.append("\\vspace{0.5cm}")
out.append("\\noindent\\textbf{Tiếng Anh}")

for i, e in enumerate(parsed_entries):
    parts = []
    # Author
    author = e['author']
    parts.append(f"{author} ({e['year']})")
    
    # Title
    if e['type'] in ['article', 'inproceedings']:
        parts.append(f"``{e['title']}''")
        if e['journal']:
            parts.append(f"\\textit{{{e['journal']}}}")
    else:
        parts.append(f"\\textit{{{e['title']}}}")
    
    # Vol/No
    if e['volume']:
        vol_str = e['volume']
        if e['number']:
            vol_str += f"({e['number']})"
        parts.append(vol_str)
        
    # Pages
    if e['pages']:
        parts.append(e['pages'])
        
    # Publisher / Note
    if e['publisher'] and e['type'] not in ['article']:
        parts.append(e['publisher'])
    if e['howpublished']:
        parts.append(e['howpublished'])
    if e['note']:
        parts.append(e['note'].replace("\\url", "\\url"))
        
    item_text = "\\bibitem{" + e['id'] + "} " + ", ".join(parts) + "."
    out.append(item_text)

out.append("\\end{thebibliography}")

with open(r"d:\2026\bfspminer-improved\report\refs_manual.tex", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("Done")

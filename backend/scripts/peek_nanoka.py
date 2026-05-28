import re
from pathlib import Path

html = Path(
    r"C:\Users\iyous\.cursor\projects\c-Users-iyous-python-project\agent-tools\606ce7d4-4594-4e31-b519-30273edeec31.txt"
).read_text(encoding="utf-8", errors="replace")
print("len", len(html))
classes = set(re.findall(r'class="([^"]+)"', html[:3_000_000]))
keys = ("char", "splash", "hero", "material", "level", "talent", "asc", "card", "grid", "layout", "page", "panel", "sidebar", "backdrop", "gacha")
for c in sorted(classes):
    if any(k in c.lower() for k in keys):
        print("CLASS:", c[:180])
# find div structure hints in first 200k of body content after svelte
idx = html.find("Wriothesley")
print("idx name", idx)
if idx > 0:
    print(html[idx - 500 : idx + 1500])

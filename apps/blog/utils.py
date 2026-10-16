from bs4 import BeautifulSoup


def process_content_toc(html):
    """h2 های داخل محتوا رو id دار می‌کنه و لیست فهرست مطالب برمی‌گردونه."""
    soup = BeautifulSoup(html or "", "html.parser")
    toc = []
    for index, heading in enumerate(soup.find_all("h2"), start=1):
        heading_id = f"toc-{index}"
        heading["id"] = heading_id
        toc.append({
            "id": heading_id,
            "text": heading.get_text(strip=True),
            "number": index,
        })
    return str(soup), toc
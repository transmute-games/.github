"""Check the profile's local links, SVGs, and sharing-image exports."""

from html.parser import HTMLParser
from pathlib import Path
import re
import struct
import subprocess
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent


class ImageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if value and name in {"src", "srcset", "href"}:
                self.paths.append(value)


def validate():
    subprocess.run(["git", "diff", "--check", "origin/main...HEAD"], cwd=ROOT, check=True)
    subprocess.run(["git", "diff", "--check", "HEAD"], cwd=ROOT, check=True)
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts or ".flox" in path.parts:
            continue
        content = path.read_text()
        links = ImageLinks()
        links.feed(content)
        links.paths.extend(re.findall(r"\]\(([^)]+)\)", content))
        for link in links.paths:
            target = urlsplit(link)
            if target.scheme or target.netloc or not target.path:
                continue
            destination = (path.parent / unquote(target.path)).resolve()
            if not destination.is_relative_to(ROOT) or not destination.is_file():
                raise ValueError(f"{path.relative_to(ROOT)}: broken local link {link}")

    brand = ROOT / "assets/brand"
    for path in brand.rglob("*.svg"):
        document = ET.parse(path)
        if document.getroot().tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError(f"{path.name}: invalid SVG root")
        for node in document.iter():
            for key, value in node.attrib.items():
                if key.endswith("href") and not value.startswith(("data:", "#")):
                    raise ValueError(f"{path.name}: external SVG dependency")

    for name, expected in {"avatar.png": (1024, 1024), "social-preview.png": (1200, 630)}.items():
        data = (brand / name).read_bytes()
        if data[:8] != b"\x89PNG\r\n\x1a\n" or len(data) < 24:
            raise ValueError(f"{name}: invalid PNG header")
        dimensions = struct.unpack(">II", data[16:24])
        if dimensions != expected:
            raise ValueError(f"{name}: expected {expected}, found {dimensions}")
    if (brand / "social-preview.png").stat().st_size > 1_000_000:
        raise ValueError("Social preview exceeds the 1 MB asset budget")
    print("PASS: profile links, self-contained SVGs, PNG dimensions, and preview budget")


if __name__ == "__main__":
    validate()

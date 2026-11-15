import pytest
from pathlib import Path
from backend.app.services.rag.extraction import DocumentExtractor, ExtractedDocument

SAMPLE_TXT = """
CENTRAL CONSUMER PROTECTION AUTHORITY
NOTIFICATION
New Delhi, the 2nd June, 2022

xxxGIDHxxx
----------------------------------------
Section 18. Powers of Central Authority.
(1) The Central Authority shall protect, promote and enforce the rights of consumers as a class.
(2) Without prejudice to the generality of the provisions, the Central Authority may inquire or cause an inquiry to be made.
"""

def test_clean_text():
    dirty_text = "Hello\xa0world\r\n\r\n\r\n\r\nxxxGIDHxxx------Test    text"
    cleaned = DocumentExtractor.clean_text(dirty_text)
    assert "\xa0" not in cleaned
    assert "\r" not in cleaned
    assert "xxxGIDHxxx" not in cleaned
    assert "------" not in cleaned
    assert "Hello world" in cleaned
    assert "Test text" in cleaned

def test_extract_txt(tmp_path):
    txt_file = tmp_path / "sample_act.txt"
    txt_file.write_text(SAMPLE_TXT, encoding="utf-8")

    meta = {
        "title": "CCPA Powers",
        "category": "statutory",
        "source_url": "https://consumeraffairs.nic.in",
        "issuing_authority": "Ministry of Consumer Affairs",
        "verification_status": "verified_official",
        "is_authoritative_for_rag": True
    }

    doc = DocumentExtractor.extract(txt_file, meta)
    assert isinstance(doc, ExtractedDocument)
    assert doc.doc_id == "sample_act"
    assert doc.title == "CCPA Powers"
    assert doc.is_authoritative is True
    assert "Powers of Central Authority" in doc.text
    assert "xxxGIDHxxx" not in doc.text

def test_extract_html(tmp_path):
    html_content = """
    <html>
        <head><title>NCH FAQs</title><script>var x = 1;</script><style>body {color: red;}</style></head>
        <body>
            <h1>National Consumer Helpline</h1>
            <p>Call toll-free 1915 to lodge grievances.</p>
        </body>
    </html>
    """
    html_file = tmp_path / "nch_test.html"
    html_file.write_text(html_content, encoding="utf-8")

    meta = {
        "title": "NCH Guidelines",
        "category": "nch_procedures",
        "source_url": "https://consumerhelpline.gov.in",
        "issuing_authority": "NCH",
        "verification_status": "verified_official",
        "is_authoritative_for_rag": True
    }

    doc = DocumentExtractor.extract_html(html_file, meta)
    assert "National Consumer Helpline" in doc.text
    assert "1915" in doc.text
    assert "var x = 1" not in doc.text
    assert "color: red" not in doc.text

def test_unsupported_extension(tmp_path):
    invalid_file = tmp_path / "document.xyz"
    invalid_file.write_text("random content", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported file format"):
        DocumentExtractor.extract(invalid_file, {})

"""Shared test fixtures — mock HTML responses for scraper tests."""

import json

import pytest

# Sample __NEXT_DATA__ JSON matching the Isha Foundation page structure
SAMPLE_QUOTE_TEXT = "Meditation is not a conquest or achievement – it is a homecoming."

SAMPLE_NEXT_DATA = {
    "props": {
        "pageProps": {
            "pageDataDetail": {
                "contentType": "wisdom_content_child",
                "title": [{"value": "February 22, 2026"}],
                "urlAlias": [{"locale": "en_IN", "value": "february-22-2026"}],
                "summary": [{"value": SAMPLE_QUOTE_TEXT}],
                "heroImage": [
                    {"value": {"url": "https://static.sadhguru.org/d/46272/sample.jpg"}}
                ],
            }
        }
    }
}


@pytest.fixture
def mock_quote_html():
    """HTML response with __NEXT_DATA__ containing a valid quote."""
    next_data_json = json.dumps(SAMPLE_NEXT_DATA)
    return f"""<!DOCTYPE html>
<html>
<head><title>Sadhguru Quotes</title></head>
<body>
<script id="__NEXT_DATA__" type="application/json">{next_data_json}</script>
</body>
</html>"""


@pytest.fixture
def mock_404_html():
    """HTML response for a 404 page (no quote found)."""
    return """<!DOCTYPE html>
<html>
<head><title>Page Not Found</title></head>
<body><h1>404 - Page Not Found</h1></body>
</html>"""


@pytest.fixture
def mock_empty_quote_html():
    """HTML with __NEXT_DATA__ but empty summary (no quote text)."""
    data = {
        "props": {
            "pageProps": {
                "pageDataDetail": {
                    "summary": [{"value": ""}],
                }
            }
        }
    }
    next_data_json = json.dumps(data)
    return f"""<!DOCTYPE html>
<html>
<head><title>Sadhguru Quotes</title></head>
<body>
<script id="__NEXT_DATA__" type="application/json">{next_data_json}</script>
</body>
</html>"""


@pytest.fixture
def mock_no_next_data_html():
    """HTML without __NEXT_DATA__ script tag."""
    return """<!DOCTYPE html>
<html>
<head><title>Sadhguru Quotes</title></head>
<body><p>Some content</p></body>
</html>"""

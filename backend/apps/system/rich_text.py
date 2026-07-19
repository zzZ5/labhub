import bleach
from bleach.css_sanitizer import CSSSanitizer


RICH_TEXT_TAGS = {
    "p", "h2", "h3", "strong", "b", "em", "i", "u", "s", "strike",
    "ul", "ol", "li", "blockquote", "a", "img", "figure", "figcaption",
    "br", "hr",
}
RICH_TEXT_ATTRIBUTES = {
    "a": ["href", "target", "rel"],
    "img": ["src", "alt", "title", "loading"],
    "*": ["style"],
}
RICH_TEXT_CSS_SANITIZER = CSSSanitizer(allowed_css_properties=["text-align"])


def sanitize_rich_text_html(value):
    return bleach.clean(
        value or "",
        tags=RICH_TEXT_TAGS,
        attributes=RICH_TEXT_ATTRIBUTES,
        protocols={"http", "https", "mailto"},
        css_sanitizer=RICH_TEXT_CSS_SANITIZER,
        strip=True,
    )

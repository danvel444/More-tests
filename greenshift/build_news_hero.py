"""Build the News (blog) hero for a Blocksy Pro Content Block shown on the blog page.

Same style as the other page heroes (TFG black, thread lines, red bottom edge), sized to
Blocksy's container so the text lines up with the logo.
"""
from build_policy_blocks import ACCENT, GS_PREVIEW_CSS, SOFT_WHITE, THREAD_HERO_CSS, make_hero, write

PAGE = {"dir": "news-hero", "title": "News Hero", "preview_css": GS_PREVIEW_CSS}

if __name__ == "__main__":
    hero = make_hero(
        seed="news-hero", bg="#0d0e10", caption="Company updates", title="News",
        intro="Stay informed with the latest updates from The Fastener Group.",
        buttons=[], accent=ACCENT, pattern_css=THREAD_HERO_CSS, caption_color=SOFT_WHITE,
        align_to_theme=True,
    )
    write(PAGE, hero)

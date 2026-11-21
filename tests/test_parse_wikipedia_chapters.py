import pytest
import wikitextparser as wtp

from parse_wikipedia_chapters import (
    CHAPTER_PREFIX_DICTIONARY,
    Chapter,
    ChapterIndex,
    add_chapter_prefix_to_chapter_name,
    calculate_missing_chapter_index,
    character_in_unicode_range,
    convert_chapters_for_driverbrainz,
    generate_kana,
    generate_missing_chapter_indices,
    parse_chapter_from_item,
    parse_chapter_from_template,
    parse_wikipedia_page,
    prefix_chapter_titles,
    remove_extra_spaces_hiragana,
    replace_last,
    use_unicode_punctuation,
)


def test_use_unicode_punctuation() -> None:
    assert (
        use_unicode_punctuation('It\'s a "test" - "really"...')
        == "It’s a “test” ‐ “really”…"
    )


def test_character_in_unicode_range() -> None:
    assert character_in_unicode_range("。", 0x3000, 0x303F)
    assert not character_in_unicode_range("a", 0x3000, 0x303F)


@pytest.mark.parametrize(
    ("hiragana", "expected"),
    [
        ("えいが  に", "えいが に"),
        ("えいが 、 さそわ", "えいが、さそわ"),
        ("だい 1 わ", "だい1わ"),
        ("「 はじまり 」", "「はじまり」"),
        ("ａ ｖ ｓ ． ｂ", "ａｖｓ．ｂ"),
    ],
)
def test_remove_extra_spaces_hiragana(hiragana: str, expected: str) -> None:
    assert remove_extra_spaces_hiragana(hiragana) == expected


def test_remove_extra_spaces_hiragana_cjk_symbols() -> None:
    assert remove_extra_spaces_hiragana("はじまり 。 おわり") == "はじまり。おわり"


def test_replace_last() -> None:
    assert replace_last("第|index|話 ", " ", "】") == "第|index|話】"


@pytest.mark.parametrize(
    ("item", "expected_type", "expected_index", "expected_english"),
    [
        ('Chapter 1 "The Beginning"', "Chapter", 1, "The Beginning"),
        ('Chapter 1.5 "Interlude"', "Chapter", 1.5, "Interlude"),
        ('5 "The Fifth"', "Chapter", 5, "The Fifth"),
        ('Special Chapter: "Bonus"', "Special Chapter", None, "Bonus"),
        ('Extra "Bonus"', "Extra", None, "Bonus"),
        ("The Beginning", "Chapter", None, "The Beginning"),
    ],
)
def test_parse_chapter_from_item(
    item: str,
    expected_type: str,
    expected_index: ChapterIndex | None,
    expected_english: str,
) -> None:
    assert parse_chapter_from_item(item) == {
        "type": expected_type,
        "index": expected_index,
        "english": expected_english,
        "kanji": expected_english,
        "hepburn": expected_english,
    }


@pytest.mark.parametrize(
    "item", ['Chapter 1: "Title"', 'Chapter 1. "Title"', '1. "Title"', '1: "Title"']
)
def test_parse_chapter_from_item_with_separator(item: str) -> None:
    assert parse_chapter_from_item(item) == {
        "type": "Chapter",
        "index": 1,
        "english": "Title",
        "kanji": "Title",
        "hepburn": "Title",
    }


def test_parse_chapter_from_template() -> None:
    template = wtp.parse('{{Nihongo|"The Beginning"|始まり|Hajimari}}').templates[0]
    assert parse_chapter_from_template(template, 3) == {
        "type": "Chapter",
        "index": 3,
        "english": "The Beginning",
        "kanji": "始まり",
        "hepburn": "Hajimari",
    }


def test_parse_chapter_from_template_without_index_or_japanese() -> None:
    template = wtp.parse("{{Nihongo|The Beginning}}").templates[0]
    assert parse_chapter_from_template(template) == {
        "type": "Chapter",
        "index": None,
        "english": "The Beginning",
        "kanji": "The Beginning",
        "hepburn": "The Beginning",
    }


GRAPHIC_NOVEL_LIST = """
{{Graphic novel list
| VolumeNumber    = 1
| ChapterList     =
* {{Nihongo|"The Beginning"|始まり|Hajimari}}
* {{Nihongo|"The Middle"|真ん中|Mannaka}}
* Extra. {{Nihongo|"The Extra"|おまけ|Omake}}
}}
"""


def test_parse_wikipedia_page_graphic_novel_list() -> None:
    assert parse_wikipedia_page(GRAPHIC_NOVEL_LIST) == [
        {
            "type": "Chapter",
            "index": 1,
            "english": "The Beginning",
            "kanji": "始まり",
            "hepburn": "Hajimari",
        },
        {
            "type": "Chapter",
            "index": None,
            "english": "The Middle",
            "kanji": "真ん中",
            "hepburn": "Mannaka",
        },
        {
            "type": "Extra",
            "index": None,
            "english": "The Extra",
            "kanji": "おまけ",
            "hepburn": "Omake",
        },
    ]


def test_parse_wikipedia_page_without_lists() -> None:
    assert parse_wikipedia_page("Just some text.") == []


def chapter(chapter_type: str, index: ChapterIndex | None = None) -> Chapter:
    return {"type": chapter_type, "index": index}


@pytest.mark.parametrize(
    ("previous", "current", "subsequent", "expected"),
    [
        (None, chapter("Chapter", 7), None, 7),
        (None, chapter("Chapter"), None, 1),
        (chapter("Chapter", 3), chapter("Chapter"), None, 4),
        (chapter("Chapter", 3), chapter("Bonus"), chapter("Chapter"), 3.5),
        (chapter("Chapter", 3), chapter("Bonus"), chapter("Bonus"), 3.1),
        (chapter("Chapter", 3), chapter("Bonus"), None, 3.5),
        (chapter("Bonus", 3.5), chapter("Chapter"), None, 4),
        (chapter("Bonus", 3.5), chapter("Bonus"), None, 3.6),
        (None, chapter("Chapter"), chapter("Chapter", 5), 4),
        (None, chapter("Chapter"), chapter("Bonus", 2.5), 2),
        (None, chapter("Bonus"), chapter("Chapter", 2), 1.5),
        (None, chapter("Bonus"), chapter("Bonus", 2.5), 2.4),
    ],
)
def test_calculate_missing_chapter_index(
    previous: Chapter | None,
    current: Chapter,
    subsequent: Chapter | None,
    expected: ChapterIndex,
) -> None:
    assert calculate_missing_chapter_index(previous, current, subsequent) == expected


def test_generate_missing_chapter_indices() -> None:
    chapters = [
        chapter("Chapter", 1),
        chapter("Chapter"),
        chapter("Bonus"),
        chapter("Chapter"),
    ]
    assert [c["index"] for c in generate_missing_chapter_indices(chapters)] == [
        1,
        2,
        2.5,
        3,
    ]


def test_generate_missing_chapter_indices_single_chapter() -> None:
    assert generate_missing_chapter_indices([chapter("Chapter")]) == [
        chapter("Chapter", 1)
    ]


def test_generate_missing_chapter_indices_empty() -> None:
    assert generate_missing_chapter_indices([]) == []


def test_generate_kana() -> None:
    [converted] = generate_kana([{"kanji": "ひらがな"}])
    assert converted["kana"] == "ヒラガナ"
    assert converted["hiragana"] == "ひらがな"


TITLES: Chapter = {
    "english": "Title",
    "kanji": "題名",
    "kana": "ダイメイ",
    "hiragana": "だいめい",
    "hepburn": "Daimei",
}


def test_add_chapter_prefix_to_chapter_name() -> None:
    assert add_chapter_prefix_to_chapter_name(
        TITLES, CHAPTER_PREFIX_DICTIONARY["bonus"], False, None
    ) == {
        "english": "Bonus Chapter: Title",
        "kanji": "番外編 題名",
        "kana": "バンガイヘン ダイメイ",
        "hiragana": "ばんがいへん だいめい",
        "hepburn": "Bangai‐hen Daimei",
    }


def test_add_chapter_prefix_to_chapter_name_with_brackets() -> None:
    assert add_chapter_prefix_to_chapter_name(
        TITLES, CHAPTER_PREFIX_DICTIONARY["chapter"], True, "Ch. |index|: "
    ) == {
        "english": "Ch. |index|: Title",
        "kanji": "【第|index|話】題名",
        "kanji_sort": "第|index|話 題名",
        "kana": "【ダイ|index|ワ】ダイメイ",
        "kana_sort": "ダイ|index|ワ ダイメイ",
        "hiragana": "【だい|index|わ】だいめい",
        "hiragana_sort": "だい|index|わ だいめい",
        "hepburn": "[Dai |index|‐wa] Daimei",
        "hepburn_sort": "Dai |index|‐wa Daimei",
    }


def test_prefix_chapter_titles_regular_chapter() -> None:
    chapters: list[Chapter] = [{"type": "Chapter", "index": 1, **TITLES}]
    [prefixed] = prefix_chapter_titles(chapters, False, None)
    assert prefixed["english"] == "Chapter |index|: Title"
    assert prefixed["kanji"] == "第|index|話 題名"


@pytest.mark.parametrize(
    ("chapter_type", "expected_english"),
    [
        ("Bonus", "Bonus Chapter: Title"),
        ("Extra", "Bonus Chapter: Title"),
        ("Side Story", "Side Story: Title"),
    ],
)
def test_prefix_chapter_titles_special_chapter(
    chapter_type: str, expected_english: str
) -> None:
    chapters: list[Chapter] = [{"type": chapter_type, "index": 1.5, **TITLES}]
    prefixed = prefix_chapter_titles(chapters, False, None)
    assert len(prefixed) == 1
    assert prefixed[0]["english"] == expected_english


def test_prefix_chapter_titles_unknown_chapter_type() -> None:
    chapters: list[Chapter] = [{"type": "Prologue", "index": 0.5, **TITLES}]
    prefixed = prefix_chapter_titles(chapters, False, None)
    assert len(prefixed) == 1
    assert prefixed[0]["english"] == "Prologue Title"
    assert prefixed[0]["kanji"] == "Prologue 題名"


def test_convert_chapters_for_driverbrainz() -> None:
    chapters: list[Chapter] = [
        {
            "index": 1,
            "english": "I Will Make You Invite Me to a Movie",
            "english_sort": "Will Make You Invite Me to a Movie",
            "kanji": "映画に誘わせたい",
            "hiragana": "えいがにさそわせたい",
            "hiragana_sort": "えいが に さそわ せたい",
            "hepburn": "Eiga ni Sasowasetai",
        },
        {
            "index": 1.5,
            "english": "Extra",
            "kanji": "おまけ",
            "hiragana": "おまけ",
            "hepburn": "Omake",
            "hepburn_sort": "Omake",
        },
    ]
    assert convert_chapters_for_driverbrainz(chapters) == {
        "1": {
            "0": {"title": "映画に誘わせたい", "sort": "えいが に さそわ せたい"},
            "1": {
                "title": "I Will Make You Invite Me to a Movie",
                "sort": "Will Make You Invite Me to a Movie",
            },
            "2": {"title": "Eiga ni Sasowasetai"},
        },
        "1.5": {
            "0": {"title": "おまけ", "sort": "おまけ"},
            "1": {"title": "Extra"},
            "2": {"title": "Omake", "sort": "Omake"},
        },
    }

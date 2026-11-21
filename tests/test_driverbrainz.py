import pytest

from driverbrainz import (
    FormatMap,
    JSONObject,
    apply_subtitles,
    convert_to_japanese_numeral,
    find_edition_id,
    format_disambiguation,
    format_index,
    format_number,
    inherit_from_original_work,
    sanitize_sort,
    write_roman,
)


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (1, "I"),
        (4, "IV"),
        (9, "IX"),
        (14, "XIV"),
        (40, "XL"),
        (1994, "MCMXCIV"),
        (2026, "MMXXVI"),
    ],
)
def test_write_roman(number: int, expected: str) -> None:
    assert write_roman(number) == expected


@pytest.mark.parametrize(
    ("number", "requested_type", "expected"),
    [
        (0, "kanji", "零"),
        (1, "kanji", "一"),
        (10, "kanji", "十"),
        (11, "kanji", "十一"),
        (20, "kanji", "二十"),
        (100, "kanji", "百"),
        (111, "kanji", "百十一"),
        (1234, "kanji", "千二百三十四"),
        (10_000, "kanji", "万"),
        (99_999, "kanji", "九万九千九百九十九"),
        (21, "hiragana", "にじゅういち"),
        (12, "hepburn", "JūNi"),
        (3, "formal_kanji", "参"),
        (30, "formal_kanji", "参拾"),
    ],
)
def test_convert_to_japanese_numeral(
    number: int, requested_type: str, expected: str
) -> None:
    assert convert_to_japanese_numeral(number, requested_type) == expected


def test_convert_to_japanese_numeral_unknown_type() -> None:
    assert convert_to_japanese_numeral(1, "cyrillic") == ""


def test_convert_to_japanese_numeral_too_large() -> None:
    assert convert_to_japanese_numeral(100_000, "kanji") == ""


@pytest.mark.parametrize(
    ("number", "number_format", "expected"),
    [
        (12, "numeral", "12"),
        (12, "roman_numeral", "XII"),
        (12, "kanji", "十二"),
        (12, "hiragana", "じゅうに"),
        (12, "unknown", ""),
    ],
)
def test_format_number(number: int, number_format: str, expected: str) -> None:
    assert format_number(number, number_format) == expected


FORMAT_MAP: FormatMap = {
    "English": {"Latin": "roman_numeral"},
    "Japanese": {"Kanji": "kanji", "Latin": "numeral"},
}


@pytest.mark.parametrize(
    ("index", "title", "expected"),
    [
        ("12", {"language": "Japanese", "script": "Kanji"}, "十二"),
        ("12", {"language": "Japanese", "script": "Latin"}, "12"),
        ("12", {"language": "English", "script": "Latin"}, "XII"),
        # Non-integer indices are left alone.
        ("1.5", {"language": "Japanese", "script": "Kanji"}, "1.5"),
    ],
)
def test_format_index(index: str, title: JSONObject, expected: str) -> None:
    assert format_index(index, title, FORMAT_MAP) == expected


@pytest.mark.parametrize(
    ("sort", "expected"),
    [
        ("【第1話】タイトル", "第1話 タイトル"),
        ("【第1話】", "第1話"),
        ("[Chapter 1] Title", "Chapter 1 Title"),
        ("(Side Story) Title", "Side Story Title"),
        ('"Quoted" Title', "Quoted Title"),
        ("#1 Title", "1 Title"),
        ("Plain Title", "Plain Title"),
    ],
)
def test_sanitize_sort(sort: str, expected: str) -> None:
    assert sanitize_sort(sort) == expected


def test_format_disambiguation_with_publication_year() -> None:
    assert (
        format_disambiguation("manga, |publication_year|", {"1": "2020"}, "1")
        == "manga, 2020"
    )


@pytest.mark.parametrize("publication_years", [None, {}, {"2": "2021"}])
def test_format_disambiguation_without_publication_year(
    publication_years: dict[str, str] | None,
) -> None:
    assert (
        format_disambiguation("manga, |publication_year|", publication_years, "1")
        == "manga, |publication_year|"
    )


def test_apply_subtitles() -> None:
    titles: list[JSONObject] = [{"text": "原題"}, {"text": "Title"}, {"text": "Gendai"}]
    subtitles: JSONObject = {
        "1": {
            "0": {"title": "映画に誘わせたい", "sort": "えいが に さそわ せたい"},
            "1": {"title": "I Will Make You Invite Me to a Movie"},
        },
        "2": {"0": {"title": "Wrong index"}},
    }
    assert apply_subtitles(titles, subtitles, "1") == [
        {
            "text": "原題",
            "subtitle": "映画に誘わせたい",
            "sort_subtitle": "えいが に さそわ せたい",
        },
        {
            "text": "Title",
            "subtitle": "I Will Make You Invite Me to a Movie",
            "sort_subtitle": "",
        },
        {"text": "Gendai", "subtitle": "", "sort_subtitle": ""},
    ]


def test_apply_subtitles_resets_existing_subtitles() -> None:
    titles: list[JSONObject] = [
        {"text": "Title", "subtitle": "Old", "sort_subtitle": "Old"}
    ]
    assert apply_subtitles(titles, {}, "1") == [
        {"text": "Title", "subtitle": "", "sort_subtitle": ""}
    ]


EDITIONS = {"1": "first-edition", "10": "second-edition", "20.5": "third-edition"}


@pytest.mark.parametrize(
    ("index", "expected"),
    [
        ("0.5", None),
        ("1", "first-edition"),
        ("9.5", "first-edition"),
        ("10", "second-edition"),
        ("20", "second-edition"),
        ("21", "third-edition"),
    ],
)
def test_find_edition_id(index: str, expected: str | None) -> None:
    assert find_edition_id(EDITIONS, index) == expected


def test_find_edition_id_without_editions() -> None:
    assert find_edition_id({}, "1") is None


def test_inherit_from_original_work() -> None:
    original_work: JSONObject = {
        "type": "Novel",
        "relationships": [
            {"role": "writer", "id": "writer-id"},
            {"role": "illustrator", "id": "illustrator-id"},
            {"role": "translator", "id": "translator-id"},
            {"role": "contributor", "id": ""},
        ],
    }
    translation_work: JSONObject = {
        "type": "",
        "relationships": [{"role": "writer", "id": "writer-id"}],
    }
    inherit_from_original_work(original_work, translation_work)
    assert translation_work == {
        "type": "Novel",
        "relationships": [
            {"role": "writer", "id": "writer-id"},
            {"role": "illustrator", "id": "illustrator-id"},
        ],
    }


def test_inherit_from_original_work_keeps_translation_type() -> None:
    translation_work: JSONObject = {"type": "Short Story", "relationships": []}
    inherit_from_original_work({"type": "Novel", "relationships": []}, translation_work)
    assert translation_work["type"] == "Short Story"

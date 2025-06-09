#!/usr/bin/env python
import argparse
import json
import logging
import math
import pykakasi
import requests
import wikitextparser as wtp

logger = logging.getLogger(__name__)

APP_NAME = "parse_wikipedia_chapters"

CHAPTER_PREFIX_DICTIONARY = {
    "chapter": {
        "english": "Chapter |index|: ",
        "kanji": "第|index|話 ",  # 	【第|index|話】
        "kana": "ダイ|index|ワ ",
        "hiragana": "だい|index|わ ",
        "hepburn": "Dai |index| Wa ",
    },
    "bonus": {
        "english": "Bonus Chapter: ",
        "kanji": "番外編 ",
        "kana": "バンガイヘン ",
        "hiragana": "ばんがいへん ",
        "hepburn": "Bangai‐hen ",
    },
    "side": {
        "english": "Side Story: ",
        "kanji": "外伝 ",  # 【外伝】
        "kana": "ガイデン ",
        "hiragana": "がいでん ",
        "hepburn": "Gaiden ",
    },
}


def fetch_wikipedia_section(page_title: str, section_number: int) -> str:
    url = f"https://en.wikipedia.org/w/api.php?action=parse&page={page_title}&section={section_number}&contentmodel=wikitext&prop=wikitext&format=json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    if "parse" not in data:
        return None
    return data["parse"]["wikitext"]["*"]


def filter_templates_by_normal_name(templates: list, normal_name: str):
    for template in templates:
        if template.normal_name() == normal_name:
            yield template


def parse_wikipedia_page(wikitext: str) -> list:
    # parsed = wtp.parse(wikitext, "utf-8")
    parsed = wtp.parse(wikitext)
    graphic_novel_lists = filter_templates_by_normal_name(
        parsed.templates, "Graphic novel list"
    )
    chapters = []
    for graphic_novel_list in graphic_novel_lists:
        for row in graphic_novel_list.get_lists():
            for item, template in zip(row.items, row.templates):
                chapter = {}
                prefix_part = item.replace(template.string, "").strip().strip(".")
                chapter_type = None
                index = None
                if prefix_part.isdecimal():
                    index = float(prefix_part)
                    chapter_type = "Chapter"
                    if index.is_integer():
                        index = int(index)
                elif prefix_part:
                    chapter_type = prefix_part
                else:
                    # Assume it is a regular chapter
                    chapter_type = "Chapter"
                english = template.arguments[0].value
                if english.startswith('"') and english.endswith('"'):
                    english = english.strip('"')
                # todo Fix spaces in Japanese conversion
                # todo Replace double quotes with unicode counterparts
                english.replace("'", "’").replace("-", "‐").replace("...", "…")
                if len(template.arguments) == 1:
                    chapter["type"] = chapter_type
                    chapter["index"] = index
                    chapter["english"] = english
                    chapter["kanji"] = english
                    chapter["hepburn"] = english
                else:
                    chapter["type"] = chapter_type
                    chapter["index"] = index
                    chapter["english"] = english
                    chapter["kanji"] = (
                        template.arguments[1]
                        .value.replace("'", "’")
                        .replace("-", "‐")
                        .replace("...", "…")
                    )
                    chapter["hepburn"] = (
                        template.arguments[2]
                        .value.replace("'", "’")
                        .replace("-", "‐")
                        .replace("...", "…")
                    )
                chapters.append(chapter)
    return chapters


def calculate_missing_chapter_index(previous, current, subsequent):
    if "index" in current and current["index"] is not None:
        return current["index"]
    if previous is None and subsequent is None:
        return 1
    if previous:
        if previous["type"] == "Chapter":
            if current["type"] == "Chapter":
                # If the previous chapter and the current chapter are normal chapters, the type of the following chapter is inconsequential.
                # Just add one.
                return previous["index"] + 1
            else:
                # The current chapter is a special chapter.
                if subsequent:
                    # There is a chapter after this one.
                    if subsequent["type"] == "Chapter":
                        # The next chapter is a normal chapter.
                        return round(previous["index"] + 0.5, 1)
                    else:
                        # The next chapter is a special chapter.
                        return round(previous["index"] + 0.1, 1)
                else:
                    return round(previous["index"] + 0.5, 1)
        else:
            # The previous chapter is a special chapter.
            # The type of the previous chapter is inconsequential.
            if current["type"] == "Chapter":
                # If the current chapter is a regular chapter, just round up.
                return math.ciel(previous["index"])
            else:
                # If the current chapter is a special chapter, add 0.1 instead.
                return round(previous["index"] + 0.1, 1)
    else:
        # There is no previous chapter but there is a subsequent chapter.
        if current["type"] == "Chapter":
            if subsequent["type"] == "Chapter":
                # The next chapter is a normal chapter.
                return subsequent["index"] - 1
            else:
                # The next chapter is a special chapter.
                return math.floor(subsequent["index"])
        else:
            # This chapter is a special chapter
            if subsequent["type"] == "Chapter":
                # The next chapter is a normal chapter.
                return round(subsequent["index"] - 0.5, 1)
            else:
                # The next chapter is a special chapter.
                return round(subsequent["index"] - 0.1, 1)


def generate_missing_chapter_indices(chapters: list) -> list:
    if len(chapters) == 0:
        return []
    if len(chapters) == 1:
        chapters[0]["index"] = calculate_missing_chapter_index(None, chapters[0], None)
    # previous_index = None
    previous_chapter = None
    for current_index, current_chapter in enumerate(chapters):
        if "index" in current_chapter and current_chapter["index"] is not None:
            previous_chapter = current_chapter
            continue

        # Index is missing.
        if current_index == 0:
            # This is the first chapter.
            # There must be another chapter following this one.
            current_chapter["index"] = calculate_missing_chapter_index(
                None, current_chapter, chapters[current_index + 1]
            )
        elif current_index == len(chapters) - 1:
            # This is the last chapter.
            # There must be a chapter preceding this one.
            current_chapter["index"] = calculate_missing_chapter_index(
                previous_chapter, current_chapter, None
            )
        else:
            # This is neither the first chapter nor the last chapter.
            current_chapter["index"] = calculate_missing_chapter_index(
                previous_chapter, current_chapter, chapters[current_index + 1]
            )
        previous_chapter = current_chapter
    return chapters


def filter_kakasi_output(kakasi_output: list, key: str):
    for character_set in kakasi_output:
        yield character_set[key]


def generate_kana(chapters: list) -> list:
    kks = pykakasi.kakasi()
    for chapter in chapters:
        converted = kks.convert(chapter["kanji"])
        chapter["kana"] = " ".join(filter_kakasi_output(converted, "kana"))
        chapter["hiragana"] = " ".join(filter_kakasi_output(converted, "hira"))
    return chapters


def replace_last(source_string, replace_what, replace_with):
    head, _sep, tail = source_string.rpartition(replace_what)
    return head + replace_with + tail


def add_chapter_prefix_to_chapter_name(
    chapter, prefix, use_brackets_japanese: bool, english_chapter_prefix: str
):
    for language in prefix.keys():
        if language in chapter:
            if use_brackets_japanese and language in [
                "kanji",
                "kana",
                "hiragana",
                "hepburn",
            ]:
                if language in ["kanji", "kana", "hiragana"]:
                    # Remove the space at the end when using brackets with Japanese characters.
                    c = (
                        "【"
                        + replace_last(prefix[language], " ", "】")
                        + chapter[language]
                    )
                    c_sort = prefix[language] + chapter[language]
                    chapter[language] = c
                    chapter[language + "_sort"] = c_sort
                else:
                    # Use square brackets for the hepburn which uses latin characters
                    c = (
                        "["
                        + replace_last(prefix[language], " ", "] ")
                        + chapter[language]
                    )
                    c_sort = prefix[language] + chapter[language]
                    chapter[language] = c
                    chapter[language + "_sort"] = c_sort
            else:
                if (
                    language == "english"
                    and english_chapter_prefix is not None
                    and len(english_chapter_prefix) > 0
                ):
                    chapter[language] = english_chapter_prefix + chapter[language]
                else:
                    chapter[language] = prefix[language] + chapter[language]
    return chapter


def prefix_chapter_titles(
    chapters: list, use_brackets_japanese: bool, english_chapter_prefix: str
):
    for chapter in chapters:
        unknown_prefix = True
        for key, prefix in CHAPTER_PREFIX_DICTIONARY.items():
            if (
                (key == "chapter" and chapter["type"].lower() == "chapter")
                or (key != "chapter" and key in chapter["type"].lower())
                or (key == "bonus" and "extra" in chapter["type"].lower())
            ):
                if (
                    chapter["type"].lower() == "chapter"
                    and english_chapter_prefix is not None
                    and len(english_chapter_prefix) > 0
                ):
                    chapter = add_chapter_prefix_to_chapter_name(
                        chapter, prefix, use_brackets_japanese, english_chapter_prefix
                    )
                else:
                    chapter = add_chapter_prefix_to_chapter_name(
                        chapter,
                        prefix,
                        use_brackets_japanese,
                        english_chapter_prefix=None,
                    )
                unknown_prefix = False
                break
        if unknown_prefix:
            logger.warning(
                f"Unknown chapter type '{chapter['type']}' for chapter {chapter['index']}!"
            )
    return chapters


# Convert chapters for DriverBrainz
#
#   "1": {
#     "0": {"title": "映画に誘わせたい", "sort": "えいが に さそわ せたい"},
#     "1": {"title": "I Will Make You Invite Me to a Movie"},
#     "2": {"title": "Eiga ni Sasowasetai"}
#   },
#
def convert_chapters_for_driverbrainz(chapters: list) -> dict:
    converted = {}
    for chapter in chapters:
        converted[str(chapter["index"])] = {
            "0": {
                "title": chapter["kanji"],
                "sort": chapter["hiragana_sort"]
                if "hiragana_sort" in chapter
                else chapter["hiragana"],
            },
            "1": {"title": chapter["english"]},
            "2": {"title": chapter["hepburn"]},
        }
        if "hepburn_sort" in chapter:
            converted[str(chapter["index"])]["2"]["sort"] = chapter["hepburn_sort"]
    return converted


def main():
    parser = argparse.ArgumentParser(
        prog="parse_wikipedia_chapters.py",
        description="Parse chapters from Wikipedia",
    )
    parser.add_argument("page_title")
    parser.add_argument("section_number", type=int)
    parser.add_argument("--use-brackets-japanese", action="store_true")
    parser.add_argument("--english-chapter-prefix", type=str)
    args = parser.parse_args()
    wikitext = fetch_wikipedia_section(args.page_title, args.section_number)
    chapters = parse_wikipedia_page(wikitext)
    chapters = generate_missing_chapter_indices(chapters)
    chapters = generate_kana(chapters)
    chapters = prefix_chapter_titles(
        chapters, args.use_brackets_japanese, args.english_chapter_prefix
    )
    converted_chapters = convert_chapters_for_driverbrainz(chapters)
    chapters_json = json.dumps(
        {"subtitles": converted_chapters}, indent=2, ensure_ascii=False
    )
    print(chapters_json)
    the_range = [str(chapter["index"]) for chapter in chapters]
    # the_range = []
    # for chapter in [chapter['index'] for chapter in chapters]:
    #     if not chapter.is_integer():
    #         the_range.append(str(chapter))
    the_range_json = json.dumps({"range": the_range}, ensure_ascii=False)
    print(the_range_json)


if __name__ == "__main__":
    main()

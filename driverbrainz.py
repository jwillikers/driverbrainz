#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import argparse
from collections import OrderedDict
import copy
import json
import math
import platformdirs
import logging
import os
import shutil

logger = logging.getLogger(__name__)

APP_NAME = "DriverBrainz"
CACHE_DIR = platformdirs.user_cache_dir(
    appname="DriverBrainz", appauthor=False, ensure_exists=True
)
COOKIES_CACHE_FILE = os.path.join(CACHE_DIR, "cookies.json")

MUSICBRAINZ_CREATE_WORK_URL = "https://beta.musicbrainz.org/work/create"
MUSICBRAINZ_CREATE_RELEASE_GROUP_URL = (
    "https://beta.musicbrainz.org/release-group/create"
)
BOOKBRAINZ_CREATE_WORK_URL = "https://bookbrainz.org/work/create"

MUSICBRAINZ_WORK_TYPE = "Prose"

MUSICBRAINZ_WRITER = ""
MUSICBRAINZ_ORIGINAL_WRITER_CREDITED_AS = None
MUSICBRAINZ_TRANSLATED_WRITER_CREDITED_AS = ""
MUSICBRAINZ_ORIGINAL_WORK_SERIES = ""
MUSICBRAINZ_TRANSLATED_WORK_SERIES = ""
MUSICBRAINZ_TRANSLATOR = ""

ORIGINAL_BOOKBRAINZ_WORK_IDENTIFIERS = {}
TRANSLATED_BOOKBRAINZ_WORK_IDENTIFIERS = {}

# Use the following snippet to format the items in a MusicBrainz series so that they can be copied and pasted here.
# http get --headers [Accept "application/json"]  $"https://musicbrainz.org/ws/2/series/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx?inc=work-rels" | get relations | select attribute-values.number work.id | rename number id | each {|w| $"    \"($w.number)\": \"https://beta.musicbrainz.org/work/($w.id)\"," } | print --raw
ORIGINAL_MUSICBRAINZ_WORK_IDENTIFIERS = {}

# http get --headers [Accept "application/json"]  $"https://musicbrainz.org/ws/2/series/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx?inc=work-rels" | get relations | select attribute-values.number work.id | rename number id | each {|w| $"    \"($w.number)\": \"https://beta.musicbrainz.org/work/($w.id)\"," } | print --raw
TRANSLATED_MUSICBRAINZ_WORK_IDENTIFIERS = {}

# ORIGINAL_MUSICBRAINZ_WORK = {
#     "title": ORIGINAL_TITLE,
#     "type": MUSICBRAINZ_WORK_TYPE,
#     "language": ORIGINAL_LANGUAGE,
#     "disambiguation": ORIGINAL_WORK_DISAMBIGUATION_COMMENT,
#     "aliases": ORIGINAL_WORK_ALIASES,
#     "series": MUSICBRAINZ_ORIGINAL_WORK_SERIES,
#     "artists": [
#         {
#             "id": MUSICBRAINZ_WRITER,
#             "role": "Writer",
#             "credited_as": MUSICBRAINZ_ORIGINAL_WRITER_CREDITED_AS,
#         },
#     ],
#     "tags": TAGS,
# }

# TRANSLATED_MUSICBRAINZ_WORK = {
#     "title": ORIGINAL_WORK_ALIASES[0],
#     "type": MUSICBRAINZ_WORK_TYPE,
#     "language": TRANSLATED_LANGUAGE,
#     "disambiguation": TRANSLATED_WORK_DISAMBIGUATION_COMMENT,
#     "aliases": TRANSLATED_WORK_ALIASES,
#     "series": MUSICBRAINZ_TRANSLATED_WORK_SERIES,
#     "artists": [
#         {
#             "id": MUSICBRAINZ_WRITER,
#             "role": "Writer",
#             "credited_as": MUSICBRAINZ_TRANSLATED_WRITER_CREDITED_AS,
#         },
#         {
#             "id": MUSICBRAINZ_TRANSLATOR,
#             "role": "Translator",
#         },
#     ],
#     "tags": TAGS,
# }

# MUSICBRAINZ_RELEASE_GROUP = {
#     "name": ORIGINAL_WORK_ALIASES[0]["text"],
#     "disambiguation": "light novel, English, unabridged",
#     "primary_type": "Other",
#     "secondary_type": "Audiobook",
#     "series": "",
#     "credits": [
#         {
#             "id": MUSICBRAINZ_WRITER,
#             "credited_as": "Such and such",
#             "join_phrase": " read by ",
#         },
#         {
#             "id": "",
#         },
#     ],
#     "tags": ["light novel", "unabridged"],
# }

# MUSICBRAINZ_RELEASE_GROUP_LINKS = {
#     "1": [
#         {
#             "url": "",
#             "type": "discography entry",
#         },
#     ],
#     "2": [
#         {
#             "url": "",
#             "type": "discography entry",
#         },
#     ],
# }


# https://stackoverflow.com/a/28777781/9835303
def write_roman(num):
    if not num.is_integer():
        return num

    roman = OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, y = divmod(num, r)
            yield roman[r] * x
            num -= r * x
            if num <= 0:
                break

    return "".join([a for a in roman_num(num)])


# https://en.wikipedia.org/wiki/Japanese_numerals
# Note: The mapping to formal Kanji is currently only useful for Fire Force's specific choice of characters.
# Tweak as necessary.
STANDARD_JAPANESE_NUMERALS = {
    0: {
        "kanji": "零",  # 〇
        "hiragana": "れい",
        "hepburn": "Rei",  # or Zero
        "formal_kanji": "零",
    },
    1: {
        "kanji": "一",
        "hiragana": "いち",
        "hepburn": "Ichi",
        "formal_kanji": "壱",
    },
    2: {
        "kanji": "二",
        "hiragana": "に",
        "hepburn": "Ni",
        "formal_kanji": "弐",
    },
    3: {
        "kanji": "三",
        "hiragana": "さん",
        "hepburn": "San",
        "formal_kanji": "参",
    },
    4: {
        "kanji": "四",
        "hiragana": "し",
        "hepburn": "Shi",
        "formal_kanji": "四",
    },
    5: {
        "kanji": "五",
        "hiragana": "ご",
        "hepburn": "Go",
        "formal_kanji": "伍",
    },
    6: {
        "kanji": "六",
        "hiragana": "ろく",
        "hepburn": "Roku",
        "formal_kanji": "陸",
    },
    7: {
        "kanji": "七",
        "hiragana": "なな",
        "hepburn": "Nana",
        "formal_kanji": "七",
    },
    8: {
        "kanji": "八",
        "hiragana": "はち",
        "hepburn": "Hachi",
        "formal_kanji": "八",
    },
    9: {
        "kanji": "九",
        "hiragana": "きゅう",
        "hepburn": "Kyū",
        "formal_kanji": "九",
    },
    10: {
        "kanji": "十",
        "hiragana": "じゅう",
        "hepburn": "Jū",
        "formal_kanji": "拾",
    },
    100: {
        "kanji": "百",
        "hiragana": "ひゃく",
        "hepburn": "Hyaku",
        "formal_kanji": "佰",
    },
    1_000: {
        "kanji": "千",
        "hiragana": "せん",
        "hepburn": "Sen",
        "formal_kanji": "千",
    },
    10_000: {
        "kanji": "万",
        "hiragana": "まん",
        "hepburn": "Man",
        "formal_kanji": "万",
    },
    100_000_000: {
        "kanji": "億",
        "hiragana": "おく",
        "hepburn": "Oku",
    },
}


# Convert an integer to the requested type in Japanese.
#
# The requested type can be kanji, hiragana, hepburn, or formal_kanji.
def convert_to_japanese_numeral(num: int, requested_type: str) -> str:
    if not num.is_integer():
        return num

    if requested_type not in ["kanji", "hiragana", "hepburn", "formal_kanji"]:
        return None

    # I'm not worrying about numbers larger than 99,999 right now
    if (num // 10000) > 9:
        return None
    string = ""
    number = num
    for power in [4, 3, 2, 1, 0]:
        power_of_ten = math.pow(10, power)
        quotient = number // power_of_ten
        if quotient > 0:
            if power == 0:
                string += STANDARD_JAPANESE_NUMERALS[quotient][requested_type]
            elif quotient == 1:
                string += STANDARD_JAPANESE_NUMERALS[power_of_ten][requested_type]
            elif quotient > 1:
                string += (
                    STANDARD_JAPANESE_NUMERALS[quotient][requested_type]
                    + STANDARD_JAPANESE_NUMERALS[power_of_ten][requested_type]
                )
            number = number % power_of_ten
    if len(string) == 0:
        return STANDARD_JAPANESE_NUMERALS[0][requested_type]
    return string


# Format an integer according to the given format.
#
# The requested format can be kanji, hiragana, hepburn, formal_kanji, numeral, or roman_numeral.
def format_number(number: int, format: str) -> str:
    if not number.is_integer():
        return number

    if format not in [
        "kanji",
        "hiragana",
        "hepburn",
        "formal_kanji",
        "numeral",
        "roman_numeral",
    ]:
        return None

    if format == "numeral":
        return f"{number}"

    if format == "roman_numeral":
        return write_roman(number)

    return convert_to_japanese_numeral(number, format)


DEFAULT_INDEX_NUMBER_FORMAT_MAP = {
    "English": {
        "Latin": "numeral",
    },
    "Japanese": {
        "Kanji": "numeral",
        "Latin": "numeral",
    },
}

DEFAULT_SORT_INDEX_NUMBER_FORMAT_MAP = {
    "English": {
        "Latin": "numeral",
    },
    "Japanese": {
        "Kanji": "numeral",
        "Latin": "numeral",
    },
}


# Insert an index using the necessary format
def format_index(index: str, title: dict, format_map: dict) -> str:
    format = format_map[title["language"]][title["script"]]
    if format == "numeral":
        return index
    number = None
    if not index.isnumeric():
        return index
    number = float(index)
    if not number.is_integer():
        return number
    number = int(number)
    return format_number(number, format)


# Sanitize a sort field by removing leading pairs of brackets, parentheses, and similar punctuation
def sanitize_sort(sanitized_sort_title: str) -> str:
    if sanitized_sort_title.startswith("【"):
        sanitized_sort_title = sanitized_sort_title.replace("【", "", 1)
        if sanitized_sort_title.endswith("】"):
            sanitized_sort_title = sanitized_sort_title.replace("】", "", 1)
        else:
            sanitized_sort_title = sanitized_sort_title.replace("】", " ", 1)
    if sanitized_sort_title.startswith("["):
        sanitized_sort_title = sanitized_sort_title.replace("[", "", 1)
        sanitized_sort_title = sanitized_sort_title.replace("]", "", 1)
    if sanitized_sort_title.startswith("("):
        sanitized_sort_title = sanitized_sort_title.replace("(", "", 1)
        sanitized_sort_title = sanitized_sort_title.replace(")", "", 1)
    if sanitized_sort_title.startswith('"'):
        sanitized_sort_title = sanitized_sort_title.replace('"', "", 1)
        sanitized_sort_title = sanitized_sort_title.replace('"', "", 1)
    if sanitized_sort_title.startswith("#"):
        sanitized_sort_title = sanitized_sort_title.replace("#", "", 1)
    return sanitized_sort_title


def musicbrainz_log_in(driver, username):
    username_text_box = driver.find_element(by=By.ID, value="id-username")
    username_text_box.send_keys(username)
    password_text_box = driver.find_element(by=By.ID, value="id-password")
    password_text_box.send_keys(os.environ.get("MUSICBRAINZ_PASSWORD"))
    submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button:nth-child(1)")
    submit_button.click()


def bookbrainz_set_title(
    driver,
    index,
    title,
    index_number_format_map: dict = DEFAULT_INDEX_NUMBER_FORMAT_MAP,
    sort_index_number_format_map: dict = DEFAULT_SORT_INDEX_NUMBER_FORMAT_MAP,
):
    wait = WebDriverWait(driver, timeout=200)
    # todo Make more accurate by relative to label
    name_text_box = driver.find_element(
        by=By.XPATH,
        value="(//div[@class='form-group']/input[@class='form-control'])[1]",
    )
    subtitle = ""
    if "subtitle" in title and title["subtitle"]:
        subtitle = title["subtitle"]
    name = (
        title["text"]
        .replace("|subtitle|", subtitle)
        .replace("|index|", format_index(index, title, index_number_format_map))
    )
    name_text_box.send_keys(name)
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//label[@class='form-label']/span[@class='text-danger' and text()='Sort Name']",
            )
        )
    )
    sort_guess_button = driver.find_element(
        by=By.XPATH, value="//button[text()='Guess']"
    )
    sort_copy_button = driver.find_element(by=By.XPATH, value="//button[text()='Copy']")
    # todo Make more accurate by relative to label
    sort_name_text_box = driver.find_element(
        by=By.XPATH,
        value="(//div[@class='input-group']/input[@class='form-control'])[2]",
    )
    if title["sort"] == "COPY":
        sort_copy_button.click()
    elif title["sort"] == "GUESS":
        sort_guess_button.click()
    else:
        sort_subtitle = ""
        if "sort_subtitle" in title and title["sort_subtitle"]:
            sort_subtitle = title["sort_subtitle"]
        else:
            sort_subtitle = subtitle
        sort_name_text_box.send_keys(
            sanitize_sort(
                title["sort"]
                .replace("|subtitle|", sort_subtitle)
                .replace(
                    "|index|", format_index(index, title, sort_index_number_format_map)
                )
            )
        )
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//label[@class='form-label']/span[@class='text-success' and text()='Sort Name']",
            )
        )
    )
    language_text_box = driver.find_element(
        by=By.XPATH,
        value="(//div[@class='form-group']/div[starts-with(@class,'Select')]/div[starts-with(@class,'react-select__control')]/div[starts-with(@class,'react-select__value-container')]/div/div[@class='react-select__input']/input[@id='react-select-language-input'])[1]",
    )
    language_text_box.send_keys(title["language"])
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//div[starts-with(@class,'react-select__menu-list')]/div[@id='react-select-language-option-0' and text()='{title['language']}']",
            )
        )
    )
    first_language_option = driver.find_element(
        by=By.XPATH,
        value=f"//div[starts-with(@class,'react-select__menu-list')]/div[@id='react-select-language-option-0' and text()='{title['language']}']",
    )
    first_language_option.click()
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//span[@class='text-success' and text()='Language']")
        )
    )


def bookbrainz_add_aliases(driver, aliases):
    wait = WebDriverWait(driver, timeout=200)
    add_aliases_button = driver.find_element(
        by=By.XPATH, value="//button[text()='Add aliases…']"
    )
    add_aliases_button.click()
    wait.until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, ".modal-title"), "Alias Editor"
        )
    )
    add_alias_button = driver.find_element(
        by=By.CSS_SELECTOR, value=".offset-lg-9 > .btn"
    )
    close_button = driver.find_element(by=By.XPATH, value="//button[text()='Close']")
    for index, alias in enumerate(aliases):
        one_based_index = index + 1
        name_text_box = driver.find_element(
            by=By.XPATH,
            value=f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/input[@class='form-control'])[{one_based_index}]",
        )
        sort_name_text_box = driver.find_element(
            by=By.XPATH,
            value=f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/div[@class='input-group']/input[@class='form-control'])[{one_based_index}]",
        )
        guess_button = driver.find_element(
            by=By.XPATH,
            value=f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/div[@class='input-group']/div[@class='input-group-append']/button[text()='Guess'])[{one_based_index}]",
        )
        copy_button = driver.find_element(
            by=By.XPATH,
            value=f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/div[@class='input-group']/div[@class='input-group-append']/button[text()='Copy'])[{one_based_index}]",
        )
        language_text_box = driver.find_element(
            by=By.XPATH,
            value=f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/div[starts-with(@class,'Select')]/div[starts-with(@class,'react-select__control')]/div[starts-with(@class,'react-select__value-container')]/div/div[@class='react-select__input']/input[@id='react-select-language-input'])[{one_based_index}]",
        )
        primary_checkbox = driver.find_element(
            by=By.XPATH,
            value=f"(//div/div[@class='row']/div/div[@class='form-check']/input[@class='form-check-input'])[{one_based_index}]",
        )
        name_text_box.send_keys(alias["text"])
        wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/label[@class='form-label']/span[@class='text-success' and starts-with(text(),'Name')])[{one_based_index}]",
                )
            )
        )
        if alias["sort"] == "COPY":
            copy_button.click()
        elif alias["sort"] == "GUESS":
            guess_button.click()
        else:
            sort_name_text_box.send_keys(alias["sort"])
        wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/label[@class='form-label']/span[@class='text-success' and starts-with(text(),'Sort Name')])[{one_based_index}]",
                )
            )
        )
        language_text_box.send_keys(alias["language"])
        wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    f"//div[starts-with(@class,'react-select__menu-list')]/div[@id='react-select-language-option-0' and text()='{alias['language']}']",
                )
            )
        )
        first_language_option = driver.find_element(
            by=By.XPATH,
            value=f"//div[starts-with(@class,'react-select__menu-list')]/div[@id='react-select-language-option-0' and text()='{alias['language']}']",
        )
        first_language_option.click()
        wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/label[@class='form-label']/span[@class='text-success' and starts-with(text(),'Language')])[{one_based_index}]",
                )
            )
        )
        if alias["primary"]:
            primary_checkbox.click()
            wait.until(EC.element_to_be_selected(primary_checkbox))
        if index < len(aliases) - 1:
            add_alias_button.click()
            wait.until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/input[@class='form-control'])[{one_based_index + 1}]",
                    )
                )
            )
        else:
            close_button.click()
            wait.until(EC.visibility_of(add_aliases_button))


# todo This almost certainly doesn't work.
# Use XPATH.
def bookbrainz_add_identifiers(driver, identifiers):
    wait = WebDriverWait(driver, timeout=200)
    add_identifiers_button = driver.find_element(by=By.CSS_SELECTOR, value=".wrap")
    add_identifiers_button.click()
    wait.until(
        EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, ".modal-title"), "Identifier Editor"
        )
    )
    add_identifier_button = driver.find_element(
        by=By.CSS_SELECTOR, value=".offset-lg-9 > .btn"
    )
    close_button = driver.find_element(by=By.CSS_SELECTOR, value=".modal-footer > .btn")
    for index, identifier in enumerate(identifiers):
        one_based_index = index + 1
        row = f"div:nth-child({one_based_index}) > .row"
        if one_based_index == 1:
            row = ".col-lg-4"
        value_text_box = driver.find_element(
            by=By.CSS_SELECTOR, value=f"{row} .form-control"
        )
        value_text_box.send_keys(identifier)
        wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f"{row} .text-success"))
        )
        if index < len(identifiers) - 1:
            add_identifier_button.click()
            wait.until(
                EC.visibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        f"div:nth-child({one_based_index + 1}) > .row .form-control",
                    )
                )
            )
        else:
            close_button.click()
            wait.until(EC.visibility_of_element_located(add_identifiers_button))


def bookbrainz_set_work_type(driver, work_type):
    wait = WebDriverWait(driver, timeout=200)
    work_type_text_box = driver.find_element(By.ID, "react-select-workType-input")
    work_type_text_box.send_keys(work_type)
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//div[starts-with(@class,'react-select__menu-list')]/div[starts-with(@class,'react-select__option')]/div[text()='{work_type}']",
            )
        )
    )
    work_type_option = driver.find_element(
        by=By.XPATH,
        value=f"//div[starts-with(@class,'react-select__menu-list')]/div[starts-with(@class,'react-select__option')]/div[text()='{work_type}']",
    )
    work_type_option.click()
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//div[@class='form-group']/label[@class='form-label' and text()='Type']/../div/div[starts-with(@class,'react-select__control')]/div[starts-with(@class,'react-select__value-container')]/div[starts-with(@class,'react-select__single-value') and text()='{work_type}']",
            )
        )
    )


def bookbrainz_add_series(driver, series, index):
    wait = WebDriverWait(driver, timeout=200)
    add_relationships_button = driver.find_element(
        by=By.XPATH, value="//span[contains(.,' Add relationship')]"
    )
    add_relationships_button.click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-body")))
    other_entity_text_box = driver.find_element(
        By.ID, "react-select-relationshipEntitySearchField-input"
    )
    other_entity_text_box.send_keys(series)
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//div[@class='progress']/div[@aria-valuenow=50]")
        )
    )
    relationship_text_box_locator = locate_with(
        By.XPATH, "//div[@class='react-select__input']/input"
    ).below(other_entity_text_box)
    relationship_text_box = driver.find_element(relationship_text_box_locator)
    relationship_text_box.send_keys("is part of")
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//div[starts-with(@class,'react-select__menu-list')]/div/div[starts-with(@class,'margin-left-d')][1]",
            )
        )
    )
    react_select_option = driver.find_element(
        By.XPATH,
        "//div[starts-with(@class,'react-select__menu-list')]/div/div[starts-with(@class,'margin-left-d')][1]",
    )
    react_select_option.click()
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//small[contains(.,'Indicates a Work is part of a Series')]")
        )
    )
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//div[@class='progress']/div[@aria-valuenow=100]")
        )
    )
    number_text_box = driver.find_element(By.CSS_SELECTOR, ".form-control:nth-child(5)")
    number_text_box.send_keys(index)
    add_button = driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(3)")
    add_button.click()
    wait.until(EC.visibility_of(add_relationships_button))


BOOKBRAINZ_RELATIONSHIP_VERB = {
    "adaptation": "is an adaptation of",
    "adapter": "adapted",
    "contributor": "contributed to",
    "edition": "contains",
    "illustrator": "illustrated",
    "letterer": "lettered",
    "provided art for": "provided art for",
    "provided story for": "provided story for",
    "revisor": "revised",
    "translation": "is a translation of",
    "translator": "translated",
    "writer": "wrote",
}


def bookbrainz_add_relationship(driver, relationship):
    if (
        "id" not in relationship
        or not relationship["id"]
        or "role" not in relationship
        or not relationship["role"]
    ):
        return
    wait = WebDriverWait(driver, timeout=200)
    add_relationships_button = driver.find_element(
        by=By.XPATH, value="//span[contains(.,' Add relationship')]"
    )
    add_relationships_button.click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-body")))
    other_entity_text_box = driver.find_element(
        By.ID, "react-select-relationshipEntitySearchField-input"
    )
    other_entity_text_box.send_keys(relationship["id"])
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//div[@class='progress']/div[@aria-valuenow=50]")
        )
    )
    relation = BOOKBRAINZ_RELATIONSHIP_VERB[relationship["role"].lower()]
    relationship_text_box_locator = locate_with(
        By.XPATH, "//div[@class='react-select__input']/input"
    ).below(other_entity_text_box)
    relationship_text_box = driver.find_element(relationship_text_box_locator)
    relationship_text_box.send_keys(relation)
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//div[starts-with(@class,'react-select__menu-list')]/div/div[starts-with(@class,'margin-left-d')][1]",
            )
        )
    )
    react_select_option = driver.find_element(
        By.XPATH,
        "//div[starts-with(@class,'react-select__menu-list')]/div/div[starts-with(@class,'margin-left-d')][1]",
    )
    react_select_option.click()
    wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//div[@class='progress']/div[@aria-valuenow=100]")
        )
    )
    wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div:nth-child(2) > .form-group > .form-text")
        )
    )
    add_button = driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(3)")
    add_button.click()
    wait.until(EC.visibility_of(add_relationships_button))


def bookbrainz_create_work(
    driver,
    work,
    index,
    username=None,
    index_number_format_map: dict = DEFAULT_INDEX_NUMBER_FORMAT_MAP,
    sort_index_number_format_map: dict = DEFAULT_SORT_INDEX_NUMBER_FORMAT_MAP,
):
    wait = WebDriverWait(driver, timeout=200)

    driver.get(BOOKBRAINZ_CREATE_WORK_URL)

    wait.until(
        lambda x: (
            x.find_element(By.CSS_SELECTOR, ".logo img")
            or x.find_element(By.ID, ".logo > .logo")
        )
    )
    if "https://musicbrainz.org/oauth2/authorize" in driver.current_url:
        musicbrainz_log_in(driver, username)
        wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".card-header > div"))
        )
        cookies = []
        try:
            with open(COOKIES_CACHE_FILE) as f:
                cookies = json.load(f)
        except FileNotFoundError:
            pass
        cookies = [
            cookie
            for cookie in cookies
            if not (
                cookie["domain"] == "bookbrainz.org" and cookie["name"] == "connect.sid"
            )
        ]
        cookies.append(driver.get_cookie("connect.sid"))
        with open(COOKIES_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=4)
    bookbrainz_set_title(
        driver,
        index,
        work["titles"][0],
        index_number_format_map=index_number_format_map,
        sort_index_number_format_map=sort_index_number_format_map,
    )
    # todo Make more accurate by relative to label
    disambiguation_text_box = driver.find_element(
        by=By.XPATH,
        value="(//div[@class='form-group']/input[@class='form-control'])[2]",
    )
    if "disambiguation" in work and work["disambiguation"]:
        disambiguation_text_box.send_keys(work["disambiguation"])
        wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//span[@class='text-success' and text()='Disambiguation']")
            )
        )

    if "titles" in work and len(work["titles"]) > 1:
        titles = []
        for a in work["titles"][1:]:
            subtitle = ""
            if "subtitle" in a and a["subtitle"]:
                subtitle = a["subtitle"]
            sort_subtitle = ""
            if "sort_subtitle" in a and a["sort_subtitle"]:
                sort_subtitle = a["sort_subtitle"]
            else:
                sort_subtitle = subtitle
            titles.append(
                {
                    "text": a["text"]
                    .replace("|subtitle|", subtitle)
                    .replace(
                        "|index|", format_index(index, a, index_number_format_map)
                    ),
                    "sort": sanitize_sort(
                        a["sort"]
                        .replace("|subtitle|", sort_subtitle)
                        .replace(
                            "|index|",
                            format_index(index, a, sort_index_number_format_map),
                        )
                    ),
                    "language": a["language"],
                    "primary": a["primary"] if "primary" in a else False,
                }
            )
        bookbrainz_add_aliases(driver, titles)
    if "identifiers" in work and work["identifiers"]:
        bookbrainz_add_identifiers(driver, work["identifiers"])
    bookbrainz_set_work_type(driver, work["type"])

    work_language_text_box = driver.find_element(
        by=By.XPATH,
        value="(//div[@class='form-group']/div[starts-with(@class,'Select')]/div[starts-with(@class,'react-select__control')]/div[starts-with(@class,'react-select__value-container')]/div/div[@class='react-select__input']/input[@id='react-select-language-input'])[2]",
    )
    work_language_text_box.send_keys(work["language"])
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//div[starts-with(@class,'react-select__menu-list')]/div[@id='react-select-language-option-0' and text()='{work['language']}']",
            )
        )
    )
    first_work_language_option = driver.find_element(
        by=By.XPATH,
        value=f"//div[starts-with(@class,'react-select__menu-list')]/div[@id='react-select-language-option-0' and text()='{work['language']}']",
    )
    first_work_language_option.click()
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//div[contains(@class,'react-select__multi-value__label') and contains(text(),'{work['language']}')]",
            )
        )
    )
    if "series" in work and work["series"]:
        for series in work["series"]:
            if "id" in series and series["id"]:
                if "offset" in series and series["offset"]:
                    offset_index = float(index) + series["offset"]
                    if offset_index.is_integer():
                        offset_index = int(offset_index)
                    bookbrainz_add_series(
                        driver,
                        series["id"],
                        str(offset_index),
                    )
                else:
                    bookbrainz_add_series(driver, series["id"], index)
    if "relationships" in work:
        for relationship in work["relationships"]:
            if relationship:
                bookbrainz_add_relationship(driver, relationship)
    submit_button = driver.find_element(
        by=By.XPATH, value="(//button[@type='submit'])[2]"
    )
    submit_button.click()
    wait.until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//a[contains(@class,'btn-success') and contains(text(),'Add Edition')]",
            )
        )
    )


# def musicbrainz_add_series(macropad, series, index):
#     macropad.keyboard.send(macropad.Keycode.SPACE)
#     driver.implicitly_wait(0.2)
#     write(macropad, "Series")
#     macropad.keyboard.send(macropad.Keycode.TAB)
#     write(macropad, "has parts / part of")
#     driver.implicitly_wait(0.25)
#     tab(macropad, 2)
#     write(macropad, series)
#     driver.implicitly_wait(1)
#     macropad.keyboard.send(macropad.Keycode.TAB)
#     write(macropad, f"{index}")
#     macropad.keyboard.send(macropad.Keycode.ENTER)
#     driver.implicitly_wait(0.2)


# def musicbrainz_add_translation_of_relationship(macropad, original_work_id):
#     macropad.keyboard.send(macropad.Keycode.SPACE)
#     driver.implicitly_wait(0.2)
#     write(macropad, "Work")
#     driver.implicitly_wait(0.1)
#     macropad.keyboard.send(macropad.Keycode.TAB)
#     driver.implicitly_wait(0.1)
#     write(macropad, "later versions / version of")
#     driver.implicitly_wait(0.25)
#     tab(macropad, 2)
#     driver.implicitly_wait(0.1)
#     if original_work_id == "PASTE_FROM_CLIPBOARD":
#         paste(macropad)
#     else:
#         write(macropad, original_work_id)
#     driver.implicitly_wait(1)
#     tab(macropad, 2)
#     driver.implicitly_wait(0.1)
#     macropad.keyboard.send(macropad.Keycode.SPACE)
#     driver.implicitly_wait(0.2)
#     tab(macropad, 2)
#     driver.implicitly_wait(0.1)
#     macropad.keyboard.send(macropad.Keycode.SPACE)
#     driver.implicitly_wait(0.2)
#     tab(macropad, 2)
#     driver.implicitly_wait(0.1)
#     macropad.keyboard.send(macropad.Keycode.SPACE)
#     driver.implicitly_wait(0.2)


# def musicbrainz_add_artist(macropad, artist):
#     macropad.keyboard.send(macropad.Keycode.SPACE)
#     driver.implicitly_wait(0.75)
#     write(macropad, "Artist")
#     macropad.keyboard.send(macropad.Keycode.TAB)
#     driver.implicitly_wait(0.1)
#     write(macropad, artist["role"])
#     driver.implicitly_wait(0.1)
#     macropad.keyboard.send(macropad.Keycode.ENTER)
#     driver.implicitly_wait(0.1)
#     macropad.keyboard.send(macropad.Keycode.TAB)
#     write(macropad, artist["id"])
#     driver.implicitly_wait(1)
#     if "credited_as" in artist and artist["credited_as"]:
#         macropad.keyboard.send(macropad.Keycode.TAB)
#         driver.implicitly_wait(0.1)
#         write(macropad, artist["credited_as"])
#         driver.implicitly_wait(0.1)
#     macropad.keyboard.send(macropad.Keycode.ENTER)
#     driver.implicitly_wait(0.2)


# def musicbrainz_add_identifiers(macropad, identifiers):
#     for identifier in identifiers:
#         write(macropad, identifier)
#         driver.implicitly_wait(0.4)
#         macropad.keyboard.send(macropad.Keycode.ENTER)
#         driver.implicitly_wait(0.4)


# # This is done after the work is created
# def musicbrainz_add_aliases(macropad, aliases, index=None):
#     for alias_index, alias in enumerate(aliases):
#         macropad.keyboard.send(macropad.Keycode.CONTROL, macropad.Keycode.L)
#         driver.implicitly_wait(0.1)
#         macropad.keyboard.send(macropad.Keycode.CONTROL, macropad.Keycode.RIGHT_ARROW)
#         driver.implicitly_wait(0.2)
#         write(macropad, "/add-alias")
#         driver.implicitly_wait(0.2)
#         macropad.keyboard.send(macropad.Keycode.ESCAPE)
#         driver.implicitly_wait(0.1)
#         macropad.keyboard.send(macropad.Keycode.ENTER)
#         driver.implicitly_wait(12)

#         # Add the alias
#         macropad.keyboard.send(macropad.Keycode.CONTROL, macropad.Keycode.A)
#         macropad.keyboard.send(macropad.Keycode.BACKSPACE)
#         driver.implicitly_wait(0.1)

#         if alias["text"] == "PASTE_FROM_CLIPBOARD":
#             paste(macropad)
#             if index:
#                 write(macropad, f"{index}")
#         else:
#             write(macropad, alias["text"])

#         tab(macropad, 3)

#         if alias["sort"] == "PASTE_FROM_CLIPBOARD":
#             paste(macropad)
#             if index:
#                 write(macropad, f"{index}")
#             tab(macropad, 3)
#         elif alias["sort"] == "COPY":
#             tab(macropad, 2)
#             macropad.keyboard.send(macropad.Keycode.SPACE)
#             driver.implicitly_wait(0.1)
#             tab(macropad, 3)
#         elif alias["sort"] == "GUESS":
#             tab(macropad, 1)
#             driver.implicitly_wait(0.1)
#             macropad.keyboard.send(macropad.Keycode.SPACE)
#             driver.implicitly_wait(0.1)
#             tab(macropad, 1)
#             macropad.keyboard.send(macropad.Keycode.SPACE)
#             driver.implicitly_wait(0.1)
#             tab(macropad, 3)
#         else:
#             write(macropad, alias["sort"])
#             tab(macropad, 3)

#         # Reset the language list to the beginning as a precaution.
#         macropad.keyboard.send(macropad.Keycode.A)
#         macropad.keyboard.send(macropad.Keycode.TAB)
#         macropad.keyboard.send(macropad.Keycode.SHIFT, macropad.Keycode.TAB)
#         write(macropad, alias["language"])
#         driver.implicitly_wait(0.1)
#         macropad.keyboard.send(macropad.Keycode.TAB)
#         if alias["primary"]:
#             macropad.keyboard.send(macropad.Keycode.SPACE)
#         tab(macropad, 2)
#         write(macropad, "Work name")
#         macropad.keyboard.send(macropad.Keycode.TAB)
#         macropad.keyboard.send(macropad.Keycode.ENTER)
#         driver.implicitly_wait(12)

#         if alias_index < len(aliases) - 1:
#             # Remove the /aliases part at the end of the URL in the URL bar
#             macropad.keyboard.send(macropad.Keycode.CONTROL, macropad.Keycode.L)
#             driver.implicitly_wait(0.1)
#             macropad.keyboard.send(macropad.Keycode.CONTROL, macropad.Keycode.RIGHT_ARROW)
#             driver.implicitly_wait(0.1)
#             for _ in range(8):
#                 macropad.keyboard.send(macropad.Keycode.BACKSPACE)


# This is done after a work has been created
# def musicbrainz_add_tags(macropad, tags, index=None):
#     macropad.keyboard.send(macropad.Keycode.CONTROL, macropad.Keycode.L)
#     driver.implicitly_wait(0.1)
#     macropad.keyboard.send(macropad.Keycode.CONTROL, macropad.Keycode.RIGHT_ARROW)
#     driver.implicitly_wait(0.2)
#     write(macropad, "/tags")
#     driver.implicitly_wait(0.2)
#     macropad.keyboard.send(macropad.Keycode.ESCAPE)
#     driver.implicitly_wait(0.1)
#     macropad.keyboard.send(macropad.Keycode.ENTER)
#     driver.implicitly_wait(12)
#     for alias_index, alias in enumerate(aliases):
#         # Add the alias
#         macropad.keyboard.send(macropad.Keycode.CONTROL, macropad.Keycode.A)
#         macropad.keyboard.send(macropad.Keycode.BACKSPACE)
#         driver.implicitly_wait(0.1)

#         if alias["text"] == "PASTE_FROM_CLIPBOARD":
#             paste(macropad)
#             if index:
#                 write(macropad, f"{index}")
#         else:
#             write(macropad, alias["text"])

#         tab(macropad, 5)
#         macropad.keyboard.send(macropad.Keycode.SPACE)
#         driver.implicitly_wait(0.1)
#         tab(macropad, 3)
#         # Reset the language list to the beginning as a precaution.
#         macropad.keyboard.send(macropad.Keycode.A)
#         macropad.keyboard.send(macropad.Keycode.TAB)
#         macropad.keyboard.send(macropad.Keycode.SHIFT, macropad.Keycode.TAB)
#         write(macropad, alias["language"])
#         driver.implicitly_wait(0.1)
#         macropad.keyboard.send(macropad.Keycode.TAB)
#         if alias["primary"]:
#             macropad.keyboard.send(macropad.Keycode.SPACE)
#         tab(macropad, 2)
#         write(macropad, "Work name")
#         macropad.keyboard.send(macropad.Keycode.TAB)
#         macropad.keyboard.send(macropad.Keycode.ENTER)
#         driver.implicitly_wait(12)

#         if alias_index < len(aliases) - 1:
#             # Remove the /aliases part at the end of the URL in the URL bar
#             macropad.keyboard.send(macropad.Keycode.CONTROL, macropad.Keycode.L)
#             driver.implicitly_wait(0.1)
#             macropad.keyboard.send(macropad.Keycode.CONTROL, macropad.Keycode.RIGHT_ARROW)
#             driver.implicitly_wait(0.1)
#             for _ in range(8):
#                 macropad.keyboard.send(macropad.Keycode.BACKSPACE)


# def musicbrainz_create_work(macropad, work, index):
#     macropad.keyboard.send(macropad.Keycode.CONTROL, macropad.Keycode.T)
#     write(macropad, MUSICBRAINZ_CREATE_WORK_URL)
#     macropad.keyboard.send(macropad.Keycode.ENTER)
#     driver.implicitly_wait(15)
#     # I use the a user script which automatically focuses on the first input box in MusicBrainz.
#     subtitle = ""
#     if "subtitle" in work["title"] and work["title"]["subtitle"]:
#         subtitle = work["title"]["subtitle"]
#     if "text" in work["title"] and work["title"]["text"]:
#         write(macropad, work["title"]["text"].replace("|index|", f"{index}").replace("|subtitle|", subtitle))
#     else:
#         macropad.keyboard.send(macropad.Keycode.CONTROL, macropad.Keycode.V)
#         write(macropad, f"{index}")
#     driver.implicitly_wait(0.1)
#     tab(macropad, 3)
#     if "disambiguation" in work and work["disambiguation"]:
#         write(macropad, work["disambiguation"])
#     driver.implicitly_wait(0.1)
#     tab(macropad, 2)
#     write(macropad, work["type"])
#     driver.implicitly_wait(0.1)
#     macropad.keyboard.send(macropad.Keycode.TAB)
#     write(macropad, work["language"])
#     driver.implicitly_wait(0.1)
#     tab(macropad, 10)

#     if "artists" in work:
#         for artist in work["artists"]:
#             musicbrainz_add_artist(macropad, artist)

#     if "series" in work and work["series"]:
#         musicbrainz_add_series(macropad, work["series"], index)

#     if "translation_of" in work and work["translation_of"]:
#         musicbrainz_add_translation_of_relationship(macropad, work["translation_of"])

#     macropad.keyboard.send(macropad.Keycode.TAB)
#     if "identifiers" in work and work["identifiers"]:
#         musicbrainz_add_identifiers(macropad, work["identifiers"])

#     # Submit by just hitting enter here, thanks to the MusicBrainz user script
#     macropad.keyboard.send(macropad.Keycode.ENTER)
#     driver.implicitly_wait(18)

#     # After the work is created, add the aliases
#     if "aliases" in work and work["aliases"]:
#         aliases = []
#         for a in work["aliases"]:
#             subtitle = ""
#             if "subtitle" in a and a["subtitle"]:
#                 subtitle = a["subtitle"]
#             sort_subtitle = ""
#             if "sort_subtitle" in a and a["sort_subtitle"]:
#                 sort_subtitle = a["sort_subtitle"]
#             aliases.append(
#                 {
#                     "text": a["text"].replace("|index|", f"{index}").replace("|subtitle|", subtitle),
#                     "sort": a["sort"].replace("|index|", f"{index}").replace("|subtitle|", sort_subtitle),
#                     "language": a["language"],
#                     "primary": a["primary"],
#                 }
#             )
#         musicbrainz_add_aliases(macropad, aliases, index)


# # Set the Artist credit for a MusicBrainz Release Group
# def musicbrainz_set_artist_credit(macropad, credits):
#     macropad.keyboard.send(macropad.Keycode.SPACE)
#     driver.implicitly_wait(1)
#     for index, credit in enumerate(credits):
#         write(macropad, credit["id"])
#         driver.implicitly_wait(1)
#         macropad.keyboard.send(macropad.Keycode.TAB)
#         driver.implicitly_wait(0.1)
#         if "credited_as" in credit and credit["credited_as"]:
#             write(macropad, credit["credited_as"])
#             driver.implicitly_wait(0.1)
#         macropad.keyboard.send(macropad.Keycode.TAB)
#         driver.implicitly_wait(0.1)
#         if "join_phrase" in credit and credit["join_phrase"]:
#             write(macropad, credit["join_phrase"])
#             driver.implicitly_wait(0.1)
#             macropad.keyboard.send(macropad.Keycode.ESCAPE)
#             driver.implicitly_wait(0.1)
#             macropad.keyboard.send(macropad.Keycode.TAB)
#             driver.implicitly_wait(0.1)
#         if index < len(credits) - 1:
#             tab(macropad, 1 if index == 0 else 3)
#             driver.implicitly_wait(0.1)
#             macropad.keyboard.send(macropad.Keycode.SPACE)
#             driver.implicitly_wait(1)
#             for _ in range(5):
#                 macropad.keyboard.send(macropad.Keycode.SHIFT, macropad.Keycode.TAB)
#             driver.implicitly_wait(0.1)
#         else:
#             tab(macropad, 6)
#             driver.implicitly_wait(0.1)
#             macropad.keyboard.send(macropad.Keycode.SPACE)
#             driver.implicitly_wait(0.5)


# def musicbrainz_add_external_links(macropad, links):
#     for link in links:
#         if "url" not in link or not link["url"]:
#             continue
#         write(macropad, link["url"])
#         driver.implicitly_wait(0.75)
#         macropad.keyboard.send(macropad.Keycode.ENTER)
#         driver.implicitly_wait(0.25)
#         if "type" in link and link["type"]:
#             write(macropad, link["type"])
#             driver.implicitly_wait(0.1)
#             tab(macropad, 2)
#             driver.implicitly_wait(0.1)


# def musicbrainz_create_release_group(macropad, release_group, index):
#     driver.close()
#     driver.get(MUSICBRAINZ_CREATE_RELEASE_GROUP_URL)
#     write(macropad, release_group["name"].replace("|index|", f"{index}"))
#     driver.implicitly_wait(0.1)
#     tab(macropad, 5)
#     musicbrainz_set_artist_credit(macropad, release_group["credits"])
#     macropad.keyboard.send(macropad.Keycode.TAB)
#     if "disambiguation" in release_group and release_group["disambiguation"]:
#         write(macropad, release_group["disambiguation"])
#         driver.implicitly_wait(0.1)
#     tab(macropad, 2)
#     driver.implicitly_wait(0.1)
#     write(macropad, release_group["primary_type"])
#     driver.implicitly_wait(0.1)
#     macropad.keyboard.send(macropad.Keycode.TAB)
#     driver.implicitly_wait(0.1)
#     write(macropad, release_group["secondary_type"])
#     driver.implicitly_wait(0.1)
#     macropad.keyboard.send(macropad.Keycode.TAB)
#     driver.implicitly_wait(0.1)
#     if "series" in release_group and release_group["series"]:
#         musicbrainz_add_series(macropad, release_group["series"], i)
#     macropad.keyboard.send(macropad.Keycode.TAB)
#     driver.implicitly_wait(0.1)
#     musicbrainz_add_external_links(macropad, release_group["links"])
#     macropad.keyboard.send(macropad.Keycode.ENTER)
#     driver.implicitly_wait(15)


def main():
    parser = argparse.ArgumentParser(
        prog="driverbrainz.py",
        description="Automate time-consuming tasks contributing metadata to BookBrainz and MusicBrainz",
    )

    parser.add_argument("command", nargs="?", default="add_bookbrainz_work_series")
    parser.add_argument(
        "filename",
        nargs="?",
        default=os.path.join(os.path.dirname(os.path.realpath(__file__)), "data.json"),
    )
    parser.add_argument("--range-start", type=int)
    parser.add_argument("--range-end", type=int)
    parser.add_argument("--no-headless", action="store_true")
    parser.add_argument("--username")
    args = parser.parse_args()

    username = args.username
    if username is None:
        username = os.environ.get("MUSICBRAINZ_USERNAME")
    if username is None:
        logger.error(
            'Missing MusicBrainz username. Please supply it with the "--username" flag or the "MUSICBRAINZ_USERNAME" environment variable.'
        )
        exit(1)

    if os.environ.get("MUSICBRAINZ_PASSWORD") is None:
        logger.error(
            'Missing MusicBrainz password. Please supply it through the "MUSICBRAINZ_PASSWORD" environment variable.'
        )
        exit(1)

    if args.range_start and not args.range_end:
        logger.error(
            'Given option "--range-start" but missing option "--range-end". Pleas supply the "--range-end" option.'
        )
        exit(1)

    data = {}
    try:
        with open(args.filename) as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Failed to open the file {args.filename}")
        exit(1)

    range_start = args.range_start
    if not args.range_start and args.range_end:
        range_start = 1

    range_ = []
    if args.range_start and args.range_end:
        # Convert the indices to a string.
        range_ = [str(i) for i in range(range_start, args.range_end + 1)]
    elif "range" in data and data["range"]:
        range_ = [str(i) for i in data["range"]]

    if "bookbrainz_work" in data["original"]:
        if "bookbrainz_work" in data["translation"]:
            if (
                "type" not in data["translation"]["bookbrainz_work"]
                or not data["bookbrainz_work"]["translation"]["type"]
            ):
                data["translation"]["bookbrainz_work"]["type"] = data["original"][
                    "bookbrainz_work"
                ]["type"]
            for relationship in data["original"]["bookbrainz_work"]["relationships"]:
                if relationship["id"]:
                    if relationship["role"] in ["writer", "provided story for"]:
                        if {
                            "role": "provided story for",
                            "id": relationship["id"],
                        } not in data["translation"]["bookbrainz_work"][
                            "relationships"
                        ]:
                            data["translation"]["bookbrainz_work"][
                                "relationships"
                            ].append(
                                {"role": "provided story for", "id": relationship["id"]}
                            )
                    elif relationship["role"] in ["illustrator"]:
                        if {
                            "role": "illustrator",
                            "id": relationship["id"],
                        } not in data["translation"]["bookbrainz_work"][
                            "relationships"
                        ]:
                            data["translation"]["bookbrainz_work"][
                                "relationships"
                            ].append({"role": "illustrator", "id": relationship["id"]})
                    elif relationship["role"] in ["provided art for"]:
                        if {
                            "role": "provided art for",
                            "id": relationship["id"],
                        } not in data["translation"]["bookbrainz_work"][
                            "relationships"
                        ]:
                            data["translation"]["bookbrainz_work"][
                                "relationships"
                            ].append(
                                {"role": "provided art for", "id": relationship["id"]}
                            )
                    elif relationship["role"] in ["contributor"]:
                        if {
                            "role": "contributor",
                            "id": relationship["id"],
                        } not in data["translation"]["bookbrainz_work"][
                            "relationships"
                        ]:
                            data["translation"]["bookbrainz_work"][
                                "relationships"
                            ].append({"role": "contributor", "id": relationship["id"]})

    # To have a special title sort in MusicBrainz, it's necessary to add an alias.
    # aliases = []
    # if "aliases" in ORIGINAL_MUSICBRAINZ_WORK:
    #     aliases = ORIGINAL_MUSICBRAINZ_WORK["aliases"].copy()
    # if (
    #     ORIGINAL_MUSICBRAINZ_WORK["title"]["sort"] != "COPY"
    #     and ORIGINAL_MUSICBRAINZ_WORK["title"]["text"]
    #     != ORIGINAL_MUSICBRAINZ_WORK["title"]["sort"]
    # ):
    #     aliases.append(
    #         {
    #             "text": ORIGINAL_MUSICBRAINZ_WORK["title"]["text"],
    #             "sort": ORIGINAL_MUSICBRAINZ_WORK["title"]["sort"],
    #             "language": ORIGINAL_MUSICBRAINZ_WORK["title"]["language"],
    #             "primary": True,
    #         }
    #     )
    #     if original_work["subtitles"]:
    #         subtitles = {}
    #         for index, subtitle in original_work["subtitles"].items():
    #             if 0 in subtitle and subtitle[0]:
    #                 subtitle[len(aliases)] = subtitle[0]
    #             subtitles[index] = subtitle
    #         original_work["subtitles"] = subtitles
    # ORIGINAL_MUSICBRAINZ_WORK["aliases"] = aliases

    # TRANSLATED_SUBTITLES = {}
    # for index, subtitle in original_work["subtitles"].copy().items():
    #     if 1 in subtitle and subtitle[1]:
    #         TRANSLATED_SUBTITLES[index] = {0: subtitle[1].copy()}

    # aliases = []
    # if "aliases" in TRANSLATED_MUSICBRAINZ_WORK:
    #     aliases = TRANSLATED_MUSICBRAINZ_WORK["aliases"].copy()
    # if (
    #     TRANSLATED_MUSICBRAINZ_WORK["title"]["sort"] != "COPY"
    #     and TRANSLATED_MUSICBRAINZ_WORK["title"]["text"]
    #     != TRANSLATED_MUSICBRAINZ_WORK["title"]["sort"]
    # ):
    #     aliases.append(
    #         {
    #             "text": TRANSLATED_MUSICBRAINZ_WORK["title"]["text"],
    #             "sort": TRANSLATED_MUSICBRAINZ_WORK["title"]["sort"],
    #             "language": TRANSLATED_MUSICBRAINZ_WORK["title"]["language"],
    #             "primary": True,
    #         }
    #     )
    #     if TRANSLATED_SUBTITLES:
    #         for index, subtitle in TRANSLATED_SUBTITLES.items():
    #             if 0 in subtitle and subtitle[0]:
    #                 TRANSLATED_SUBTITLES[index][len(TRANSLATED_WORK_ALIASES)] = subtitle[
    #                     0
    #                 ].copy()
    # TRANSLATED_MUSICBRAINZ_WORK["aliases"] = aliases

    geckodriver = shutil.which("geckodriver")
    if geckodriver is None:
        logger.error("geckodriver not found in PATH!")
        exit(1)
    geckodriver = str(geckodriver)
    service = webdriver.FirefoxService(executable_path=geckodriver)
    options = FirefoxOptions()
    if not args.no_headless:
        options.add_argument("--headless")
    # Avoid using too much RAM over time.
    # 512,000 KiB is 500 MiB
    # 1,048,576 KiB is 1 GiB
    options.set_preference("browser.cache.memory.capacity", 1_048_576)

    driver = webdriver.Firefox(options=options, service=service)

    wait = WebDriverWait(driver, timeout=200)

    try:
        with open(COOKIES_CACHE_FILE) as f:
            cookies = json.load(f)
            bookbrainz_cookie = next(
                (
                    cookie
                    for cookie in cookies
                    if cookie["domain"] == "bookbrainz.org"
                    and cookie["name"] == "connect.sid"
                ),
                None,
            )
            if bookbrainz_cookie is not None:
                driver.get("https://bookbrainz.org")
                wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".logo img"))
                )
                driver.add_cookie(bookbrainz_cookie)
    except FileNotFoundError:
        pass

    # Add a bunch of MusicBrainz works
    # if command == "add_musicbrainz_work_series":
    #     for i in RANGE:
    #         print(f"{i}")

    #         original_work = ORIGINAL_MUSICBRAINZ_WORK.copy()

    #         original_identifiers = []
    #         if i in IDENTIFIERS:
    #             original_identifiers = IDENTIFIERS[i].copy()
    #         if i in ORIGINAL_MUSICBRAINZ_WORK_IDENTIFIERS:
    #             original_identifiers.append(ORIGINAL_MUSICBRAINZ_WORK_IDENTIFIERS[i])
    #         if i in ORIGINAL_BOOKBRAINZ_WORK_IDENTIFIERS:
    #             original_identifiers.append(ORIGINAL_BOOKBRAINZ_WORK_IDENTIFIERS[i])

    #         original_work["identifiers"] = original_identifiers

    #         subtitle = ""
    #         if i in SUBTITLES and SUBTITLES[i] and 0 in SUBTITLES[i] and SUBTITLES[i][0] and "title" in SUBTITLES[i][0] and SUBTITLES[i][0]["title"]:
    #             subtitle = SUBTITLES[i][0]["title"]
    #         sort_subtitle = ""
    #         if i in SUBTITLES and SUBTITLES[i] and 0 in SUBTITLES[i] and SUBTITLES[i][0] and "sort" in SUBTITLES[i][0] and SUBTITLES[i][0]["sort"]:
    #             sort_subtitle = SUBTITLES[i][0]["sort"]

    #         original_work["title"]["subtitle"] = subtitle
    #         original_work["title"]["sort_subtitle"] = sort_subtitle

    #         aliases = []
    #         for alias_index, alias in enumerate(original_work["aliases"].copy(), start=1):
    #             alias["subtitle"] = ""
    #             alias["sort_subtitle"] = ""
    #             if i in SUBTITLES and SUBTITLES[i] and alias_index in SUBTITLES[i] and SUBTITLES[i][alias_index]:
    #                 if "title" in SUBTITLES[i][alias_index] and SUBTITLES[i][alias_index]["title"]:
    #                     alias["subtitle"] = SUBTITLES[i][alias_index]["title"]
    #                 if "sort" in SUBTITLES[i][alias_index] and SUBTITLES[i][alias_index]["sort"]:
    #                     alias["sort_subtitle"] = SUBTITLES[i][alias_index]["sort"]
    #             aliases.append(alias)
    #         original_work["aliases"] = aliases

    #         musicbrainz_create_work(macropad, original_work, i)

    #         original_work_url = driver.current_url

    #         # Now create the translated work
    #         translated_work = TRANSLATED_MUSICBRAINZ_WORK.copy()
    #         translated_work["title"] = TRANSLATED_MUSICBRAINZ_WORK["title"].copy()
    #         translated_work["aliases"] = TRANSLATED_MUSICBRAINZ_WORK["aliases"].copy()

    #         translated_identifiers = []
    #         if i in IDENTIFIERS:
    #             translated_identifiers = IDENTIFIERS[i].copy()
    #         if i in TRANSLATED_MUSICBRAINZ_WORK_IDENTIFIERS:
    #             translated_identifiers.append(TRANSLATED_MUSICBRAINZ_WORK_IDENTIFIERS[i])
    #         if i in TRANSLATED_BOOKBRAINZ_WORK_IDENTIFIERS:
    #             translated_identifiers.append(TRANSLATED_BOOKBRAINZ_WORK_IDENTIFIERS[i])

    #         translated_work["identifiers"] = translated_identifiers
    #         translated_work["translation_of"] = "PASTE_FROM_CLIPBOARD"

    #         subtitle = ""
    #         if i in SUBTITLES and SUBTITLES[i] and 1 in SUBTITLES[i] and SUBTITLES[i][1] and "title" in SUBTITLES[i][1] and SUBTITLES[i][1]["title"]:
    #             subtitle = SUBTITLES[i][1]["title"]
    #         sort_subtitle = ""
    #         if i in SUBTITLES and SUBTITLES[i] and 1 in SUBTITLES[i] and SUBTITLES[i][1] and "sort" in SUBTITLES[i][1] and SUBTITLES[i][1]["sort"]:
    #             sort_subtitle = SUBTITLES[i][1]["sort"]

    #         translated_work["title"]["subtitle"] = subtitle
    #         translated_work["title"]["sort_subtitle"] = sort_subtitle

    #         aliases = []
    #         for alias_index, alias in enumerate(translated_work["aliases"].copy()):
    #             alias["subtitle"] = ""
    #             alias["sort_subtitle"] = ""
    #             if i in SUBTITLES and TRANSLATED_SUBTITLES[i] and alias_index in TRANSLATED_SUBTITLES[i] and TRANSLATED_SUBTITLES[i][alias_index]:
    #                 if "title" in TRANSLATED_SUBTITLES[i][alias_index] and TRANSLATED_SUBTITLES[i][alias_index]["title"]:
    #                     alias["subtitle"] = TRANSLATED_SUBTITLES[i][alias_index]["title"]
    #                 if "sort" in TRANSLATED_SUBTITLES[i][alias_index] and TRANSLATED_SUBTITLES[i][alias_index]["sort"]:
    #                     alias["sort_subtitle"] = TRANSLATED_SUBTITLES[i][alias_index]["sort"]
    #             aliases.append(alias)
    #         translated_work["aliases"] = aliases

    #         musicbrainz_create_work(macropad, translated_work, i)

    #         # Restore the clipboard contents before continuing
    #         clipboard_select(macropad, 1)
    #     print("Complete")
    # # Create multiple Release Groups as part of a Release Group series in MusicBrainz
    # if command == "add_musicbrainz_release_group_series":
    #     for i in RANGE:
    #         print(f"{i}")
    #         release_group = MUSICBRAINZ_RELEASE_GROUP
    #         if i in MUSICBRAINZ_RELEASE_GROUP_LINKS:
    #             release_group["links"] = MUSICBRAINZ_RELEASE_GROUP_LINKS[i]
    #         musicbrainz_create_release_group(macropad, MUSICBRAINZ_RELEASE_GROUP, index=i)
    #     print("Complete")
    # Create a series of BookBrainz works with their translated works
    if args.command == "add_bookbrainz_work_series":
        for i in range_:
            # Create the original work first.
            print(f"{i}")

            original = copy.deepcopy(data["original"])
            original_work = original["bookbrainz_work"]

            original_work["language"] = original["language"]
            original_work["disambiguation"] = original["disambiguation"]

            if "identifiers" not in original_work:
                original_work["identifiers"] = []
            if "identifiers" in original and i in original["identifiers"]:
                original_work["identifiers"].append(
                    copy.deepcopy(original["identifiers"][i])
                )
            if "identifiers" in data and i in data["identifiers"]:
                original_work["identifiers"].append(
                    copy.deepcopy(data["identifiers"][i])
                )

            titles = []
            for title_index, title in enumerate(original["titles"]):
                title_index = str(title_index)
                title["subtitle"] = ""
                title["sort_subtitle"] = ""
                if (
                    i in original["subtitles"]
                    and original["subtitles"][i]
                    and title_index in original["subtitles"][i]
                    and original["subtitles"][i][title_index]
                ):
                    if (
                        "title" in original["subtitles"][i][title_index]
                        and original["subtitles"][i][title_index]["title"]
                    ):
                        title["subtitle"] = original["subtitles"][i][title_index][
                            "title"
                        ]
                    if (
                        "sort" in original["subtitles"][i][title_index]
                        and original["subtitles"][i][title_index]["sort"]
                    ):
                        title["sort_subtitle"] = original["subtitles"][i][title_index][
                            "sort"
                        ]
                titles.append(title)
            original_work["titles"] = titles

            bookbrainz_create_work(
                driver,
                original_work,
                i,
                username=username,
                index_number_format_map=data["index_number_format_map"],
                sort_index_number_format_map=data["sort_index_number_format_map"],
            )
            original_work_url = driver.current_url

            # Now create the translated work

            translation = copy.deepcopy(data["translation"])
            translation_work = translation["bookbrainz_work"]

            translation_work["language"] = translation["language"]
            translation_work["disambiguation"] = translation["disambiguation"]

            if "identifiers" not in translation_work:
                translation_work["identifiers"] = []
            if "identifiers" in translation and i in translation["identifiers"]:
                translation_work["identifiers"].append(
                    copy.deepcopy(translation["identifiers"][i])
                )
            if "identifiers" in data and i in data["identifiers"]:
                translation_work["identifiers"].append(
                    copy.deepcopy(data["identifiers"][i])
                )

            translated_edition_id = next(
                (
                    id
                    for index, id in reversed(
                        sorted(
                            list(translation_work["editions"].items()),
                            key=lambda pair: float(pair[0]),
                        )
                    )
                    if float(i) >= float(index)
                ),
                None,
            )
            if translated_edition_id is not None:
                translation_work["relationships"].append(
                    {
                        "role": "edition",
                        "id": translated_edition_id,
                    }
                )

            translation_work["relationships"].append(
                {
                    "role": "translation",
                    "id": original_work_url,
                }
            )

            if "titles" not in translation or not translation["titles"]:
                translation["titles"] = []

            titles = []
            for title_index, title in enumerate(translation["titles"]):
                title_index = str(title_index)
                title["subtitle"] = ""
                title["sort_subtitle"] = ""
                if (
                    "subtitles" in translation
                    and i in translation["subtitles"]
                    and translation["subtitles"][i]
                    and title_index in translation["subtitles"][i]
                    and translation["subtitles"][i][title_index]
                ):
                    if (
                        "title" in translation["subtitles"][i][title_index]
                        and translation["subtitles"][i][title_index]["title"]
                    ):
                        title["subtitle"] = translation["subtitles"][i][title_index][
                            "title"
                        ]
                    if (
                        "sort" in translation["subtitles"][i][title_index]
                        and translation["subtitles"][i][title_index]["sort"]
                    ):
                        title["sort_subtitle"] = translation["subtitles"][i][
                            title_index
                        ]["sort"]
                titles.append(title)
            translation_work["titles"] = [original_work["titles"][1]] + titles

            bookbrainz_create_work(
                driver,
                translation_work,
                i,
                username=username,
                index_number_format_map=data["index_number_format_map"],
                sort_index_number_format_map=data["sort_index_number_format_map"],
            )

    driver.quit()
    print("Complete")


if __name__ == "__main__":
    main()

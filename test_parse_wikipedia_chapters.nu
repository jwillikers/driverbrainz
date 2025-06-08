#!/usr/bin/env nu
use std assert
use std log
use parse_wikipedia_chapters.nu *

def test_parse_nihongo_line_oshi_no_ko_chapter_one [] {
  let expected = {
    chapter_part: ""
    english: "Mother & Children"
    kanji: "母と子"
    hepburn: "Haha to Ko"
  }
  let input = '|{{nihongo|"Mother & Children"|母と子|Haha to Ko}}'
  assert equal ($input | parse_nihongo_line) $expected
}

def test_parse_nihongo_line_the_seven_deadly_sins_chapter_one [] {
  let expected = {
    chapter_part: "01"
    english: "The Seven Deadly Sins"
    kanji: "七つの大罪"
    hepburn: "Nanatsu no Taizai"
  }
  let input = '*01. {{nihongo|"The Seven Deadly Sins"|七つの大罪|Nanatsu no Taizai}}'
  assert equal ($input | parse_nihongo_line) $expected
}

# todo Set index as 22.5
def test_parse_nihongo_line_the_seven_deadly_sins_bonus_chapter_nothing_wasted [] {
  let expected = {
    chapter_part: "Bonus Chapter"
    english: "Nothing Wasted"
    kanji: "無駄なものなんて何一つ"
    hepburn: "Muda na Mono Nante Nani hitotsu"
  }
  let input = '*Bonus Chapter. {{nihongo|"Nothing Wasted"|無駄なものなんて何一つ|Muda na Mono Nante Nani hitotsu}}'
  assert equal ($input | parse_nihongo_line) $expected
}

def test_parse_nihongo_line_the_seven_deadly_sins_side_story_ban_the_bandit [] {
  let expected = {
    chapter_part: "Side Story"
    english: "Ban the Bandit"
    kanji: "バンデット・バン"
    hepburn: "Bandetto Ban"
  }
  let input = '*Side Story. {{nihongo|"Ban the Bandit"|バンデット・バン|Bandetto Ban}}'
  assert equal ($input | parse_nihongo_line) $expected
}

def test_parse_nihongo_line_the_seven_deadly_sins_four_knights_of_the_apocalypse_chapter_one [] {
  let expected = {
    chapter_part: ""
    english: "The Boy's Departure"
    kanji: "少年は旅立つ"
    hepburn: "Shōnen wa Tabidatsu"
  }
  let input = "|{{Nihongo|\"The Boy's Departure\"|少年は旅立つ|Shōnen wa Tabidatsu}}"
  assert equal ($input | parse_nihongo_line) $expected
}

def test_parse_nihongo_line_vinland_saga_chapter_one [] {
  let expected = {
    chapter_part: "001"
    english: "Normanni"
    kanji: "北人"
    hepburn: "Norumanni"
  }
  let input = '*001. {{Nihongo|"Normanni"|北人|Norumanni}}'
  assert equal ($input | parse_nihongo_line) $expected
}

def test_parse_nihongo_line [] {
  test_parse_nihongo_line_oshi_no_ko_chapter_one
  test_parse_nihongo_line_the_seven_deadly_sins_chapter_one
  test_parse_nihongo_line_the_seven_deadly_sins_bonus_chapter_nothing_wasted
  test_parse_nihongo_line_the_seven_deadly_sins_side_story_ban_the_bandit
  test_parse_nihongo_line_the_seven_deadly_sins_four_knights_of_the_apocalypse_chapter_one
  test_parse_nihongo_line_vinland_saga_chapter_one
}

def test_is_chapter_line [] {
}

def main [] {
  test_parse_nihongo_line
  echo $"(ansi green)All tests passed!(ansi reset)"
}

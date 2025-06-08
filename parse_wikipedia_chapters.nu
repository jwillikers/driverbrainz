#!/usr/bin/env nu
use std log

# todo Add unit tests.
# todo Handle bonus chapters.
# todo Output as JSON.

def convert_ascii_to_unicode []: string -> string {
  (
    $in
    | str replace --all "'" "’"
    | str replace --all "-" "‐"
    | str replace --all "..." "…"
    | str replace --all " x " " × "
    | str replace --all " X " " × "
    # todo Double quotes
  )
}

def kanji_into_kana []: any -> string {
  let kanji = $in
  let result = (
  if ($kanji | describe) == "binary" {
    do {$kanji | encode utf8 | ^kakasi -JH -s -iutf8 -outf8} | complete
  } else {
    do {$kanji | ^kakasi -JH -s -iutf8 -outf8} | complete
  }
  )
  if $result.exit_code != 0 {
    log info $"Error running '($kanji) | ^kakasi -JH -s -iutf8 -outf8'\nstderr: ($result.stderr)\nstdout: ($result.stdout)"
    return ""
  }
  if ($result.stdout | describe) == "binary" {
    $result.stdout | decode utf8
  } else {
    $result.stdout
  }
}

# Parse the line containing a chapter title and its translations
export def parse_nihongo_line []: string -> record<chapter_part: string, english: string, kanji: string, hepburn: string> {
  let line = $in
  let parsed = $line | parse --regex '(?:(?:\s*\*\s*(?P<chapter_part>[0-9a-zA-Z\s_-]+)\s*\.\s+)|(?:\|))\{\{[nN]ihongo\|"(?P<english>.+)"(?:\|(?P<kanji>.+)\|(?P<hepburn>.+)\}\}){0,1}'
  if ($parsed | is-empty) {
    return null
  }
  $parsed | first
}

export def is_chapter_line []: string -> bool {
  let line = $in
  $line =~ '^(?:\s*\*\s*[0-9a-zA-Z\s_-]+\s*\.\s+)|(?:\|)\{\{[nN]ihongo\|' or ($line | str starts-with '|"')
}

export def is_nihongo_line []: string -> bool {
  let line = $in
  $line | str downcase | str contains "{{nihongo"
}

# Example volume lines:
# VolumeNumber    = 1

# Example chapter lines
# ' *03. {{nihongo|"What One Must Do"|自分がやるべきこと|Jibun ga Yarubeki koto}}'
# '|{{nihongo|"Happy End"|ハッピーエンド|Happīendo}}'
# '|"MEMe"'

# Given a Wikipedia page, parse the chapters of a manga into a format suitable for use in the subtitle section of the macropad script.
def main [
  wikipedia_page: string
  skip: int = 0 # Skip this many chapters
  take: int = 100 # Only take this many chapters after skipping
] {
  let chapters = (
    http get $"https://en.wikipedia.org/w/api.php?action=parse&page=($wikipedia_page)&contentmodel=wikitext&prop=wikitext&format=json"
    | get parse.wikitext.*
    | lines --skip-empty
    # | filter {|line| ($line | str starts-with '|{{nihongo|') or ($line | str starts-with '|"')}
    | filter {|line| $line | is_chapter_line}
    | each {|line|
      log debug $"($line)"
      if ($line | is_nihongo_line) {
        $line | parse_nihongo_line
      } else {
        let title = ($line | str trim --left --char '|' | str trim --char '"')
        # todo Special chapter handling here like for parse_nihongo_line
        let title = $line | parse --regex '(?P<index>\s*\*[0-9]+\.\s+){0,1}"{0,1}(?P<english>.+)"{0,1}' | first
        let chapter = {
          english: ($title.english | str trim --char '"')
          kanji: ($title.english | str trim --char '"')
          hepburn: ($title.english | str trim --char '"')
        }
        if "index" in $title and ($title.index | is-not-empty) {
          $chapter | insert index $title.index
        } else {
          $chapter
        }
      }
    }
  )
  let chapters = (
    $chapters | each {|chapter|
    # todo Parse chapter part into title and index
      if "chapter_part" in $chapter and ($chapter.chapter_part | is-not-empty) {
        # determine if it looks like an int
        $chapter | update index ($chapter.chapter_part | str trim | into int)
      } else {
        $chapter
      }
    }
  )
  let chapters = (
    $chapters | each {|chapter|
      if "index" in $chapter and ($chapter.index | is-not-empty) {
        $chapter | update index ($chapter.index | str trim | str trim --left --char '*' | str trim --right --char '.' | into int)
      } else {
        $chapter
      }
    }
  )
  log debug $"($chapters)"
  let chapters = (
    $chapters | each {|chapter|
      if ($chapter.kanji | is-empty) {
        $chapter | insert kana ""
      } else {
        $chapter | insert kana ($chapter.kanji | kanji_into_kana | (
          let input = $in;
          let input = (
            if ($input | str starts-with '[') {
              $input | str replace '[' '' | str replace ']' ''
            } else {
              $input
            }
          );
          if ($input | str starts-with '【') {
            $input | str replace '【' '' | str replace '】' ''
          } else {
            $input
          }
        ))
      }
    }
    | each {|chapter|
      {
          english: ($chapter.english | convert_ascii_to_unicode)
          kanji: ($chapter.kanji | convert_ascii_to_unicode)
          hepburn: ($chapter.hepburn | convert_ascii_to_unicode)
          kana: ($chapter.kana | convert_ascii_to_unicode)
      }
    }
  )
  let offset = (
    let chapters_with_indices = (
      $chapters | filter {|chapter|
        "index" in $chapter and ($chapter.index | is-not-empty)
      }
    );
    if ($chapters_with_indices | is-empty) {
      1
    } else {
      $chapters_with_indices | first | get index
    }
  )
  let chapters = (
    $chapters
    | enumerate
    | update index {|i| $i.index + $offset}
    | each {|chapter|
      if "index" in $chapter.item and ($chapter.item.index | is-not-empty) {
        $chapter | update index $chapter.item.index
      } else {
        $chapter
      }
    }
    | rename index title
  )

  # SUBTITLES = {
  #   "1": {
  #       0: {"title": "凛太郎と薫子", "sort": "りんたろう と かおるこ"},
  #       1: {"title": "Rintaro and Kaoruko"},
  #       2: {"title": "Rintarō to Kaoruko"},
  #   },
  #   "2": {
  #       0: {"title": "千鳥と桔梗", "sort": "ちどり と ききょう"},
  #       1: {"title": "Chidori and Kikyo"},
  #       2: {"title": "Chidori to Kikyō"},
  #   },
  # }

  # $chapters | skip $skip | take $take | reduce --fold '' {|chapter, acc|
  $chapters | reduce --fold '' {|chapter, acc|
    $acc + $"  \"($chapter.index)\": {\n    \"0\": {\"title\": \"($chapter.title.kanji)\", \"sort\": \"($chapter.title.kana)\"},\n    \"1\": {\"title\": \"($chapter.title.english)\"},\n    \"2\": {\"title\": \"($chapter.title.hepburn)\"}\n  },\n"
  }
}

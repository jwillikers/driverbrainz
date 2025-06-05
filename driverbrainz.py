#!/usr/bin/env python
import platformdirs
import json
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

import os
import shutil

APP_NAME = "DriverBrainz"
CACHE_DIR = platformdirs.user_cache_dir(appname="DriverBrainz", appauthor=False, ensure_exists=True)
COOKIES_CACHE_FILE = os.path.join(CACHE_DIR, "cookies.json")

# Prerequisites
#
# Firefox
# Disable the browser.translations.automaticallyPopup option in about:config
# Install the https://www.greasespot.net/[GreaseMonkey] extension in Firefox
# Install the SUPER MIND CONTROL II X Turbo user script for MusicBrainz
# https://github.com/jesus2099/konami-command/raw/master/mb_SUPER-MIND-CONTROL-II-X-TURBO.user.js
# Install the Guess Unicode Punctuation user script for MusicBrainz
#
# The clipse clipboard manager in the Sway desktop is necessary since I use it to manage the contents of the clipboard.
# It's bound to the keyboard shortcut Super+I
#
# Requires fcitx5 for the input of Unicode characters.
# sudo rpm-ostree install fcitx5-autostart
# sudo systemctl reboot
#
# This script is used on an Adafruit MacroPad using CircuitPython.
# It requires the MacroPad library plus all of its dependencies to be copied over to the lib directory on the MacroPad.

# Usage
#
# Configure the constants below as necessary for the works of the series you want to add.
# Set the volume start and end values, which are inclusive, accordingly.
# Save the updated script to the MacroPad in the code.py file.
# Copy the name for the first volume in the original language.
# This copied text will be used as the title and immediately followed by the index value.
# Open a browser window and focus on it.
# Click the desired key to create the series.
# Always test with 1 or 2 works in the series before doing more.
#

# Key Legend
#
# Keys are numbered in the order of left to right, top to bottom.
# The first key, #0, is the one in the top left which resides below the OLED screen.
#
# 0 - Create a series of MusicBrainz works along with their associated translated works
# 1 - Create a series of MusicBrain release groups
# 2 -
# 3 - Create a series of BookBrainz works along with their associated translated works
# 4 -
# 5 -
# 6 -
# 7 -
# 8 -
# 9 - Test snippet
# 10 -
# 11 -
#
# Rotary Encoder -
#

VOLUME_START = 114
VOLUME_END = 346

# Convert the indices to a string.
RANGE = [str(i) for i in range(VOLUME_START, VOLUME_END + 1)]

# RANGE = [
#     "1",
#     "1.1",
#     "1.2",
#     "1.3",
#     "2",
#     "3",
#     "4",
#     "5",
#     "6",
#     "7",
#     "8",
#     "9",
#     "10",
#     "11",
#     "12",
#     "13",
# ]

SUBTITLES = {
  '1': {
    0: {'title': '七つの大罪', 'sort': 'ななつ の たいざい'},
    1: {'title': 'The Seven Deadly Sins'},
    2: {'title': 'Nanatsu no Taizai'},
  },
  '2': {
    0: {'title': '聖騎士の剣', 'sort': 'せいきし の つるぎ'},
    1: {'title': 'The Holy Knight’s Sword'},
    2: {'title': 'Seikishi no Ken'},
  },
  '3': {
    0: {'title': '自分がやるべきこと', 'sort': 'じぶん がやるべきこと'},
    1: {'title': 'What One Must Do'},
    2: {'title': 'Jibun ga Yarubeki koto'},
  },
  '4': {
    0: {'title': '眠れる森の罪', 'sort': 'ねむれ る もり の つみ'},
    1: {'title': 'The Sin in the Sleeping Forest'},
    2: {'title': 'Nemureru Mori no Tsumi'},
  },
  '5': {
    0: {'title': '暗闇の記憶', 'sort': 'くらやみ の きおく'},
    1: {'title': 'Dark Memories'},
    2: {'title': 'Kurayami no Kioku'},
  },
  '6': {
    0: {'title': '聖騎士ギルサンダー', 'sort': 'せいきし ギルサンダー'},
    1: {'title': 'The Holy Knight Gilthunder'},
    2: {'title': 'Seikishi Girusandā'},
  },
  '7': {
    0: {'title': '暗闇の虜囚', 'sort': 'くらやみ の とりこ しゅう'},
    1: {'title': 'Dark Prisoner'},
    2: {'title': 'Kurayami no Ryoshū'},
  },
  '8': {
    0: {'title': '少女の夢', 'sort': 'しょうじょ の ゆめ'},
    1: {'title': 'A Girl’s Dream'},
    2: {'title': 'Shoujo no Yume'},
  },
  '9': {
    0: {'title': '触れてはならない', 'sort': 'ふれて はならない'},
    1: {'title': 'No Touching'},
    2: {'title': 'Furete wa Naranai'},
  },
  '10': {
    0: {'title': '見えざる悪意', 'sort': 'みえ ざる あくい'},
    1: {'title': 'An Unseen Malice'},
    2: {'title': 'Miezaru Akui'},
  },
  '11': {
    0: {'title': 'たとえあなたが死んでも', 'sort': 'たとえあなたが しん でも'},
    1: {'title': 'Even If You Died'},
    2: {'title': 'Tatoe Anata ga Shindemo'},
  },
  '12': {
    0: {'title': '混沌の宴', 'sort': 'こんとん の うたげ'},
    1: {'title': 'A Chaotic Party'},
    2: {'title': 'Konton no Utage'},
  },
  '13': {
    0: {'title': '捧げる覚悟', 'sort': 'ささげ る かくご'},
    1: {'title': 'Ready To Sacrifice'},
    2: {'title': 'Sasageru Kakugo'},
  },
  '14': {
    0: {'title': 'エクスプロージョン', 'sort': 'エクスプロージョン'},
    1: {'title': 'Explosion'},
    2: {'title': 'Ekusupurōjon'},
  },
  '15': {
    0: {'title': '再会のとばっちり', 'sort': 'さいかい のとばっちり'},
    1: {'title': 'Caught In the Reunion'},
    2: {'title': 'Saikai no Tobacchiri'},
  },
  '16': {
    0: {'title': 'はじまりの詩', 'sort': 'はじまりの し'},
    1: {'title': 'The Poem of Beginnings'},
    2: {'title': 'Hajimari no Uta'},
  },
  '17': {
    0: {'title': '嵐の予感', 'sort': 'あらし の よかん'},
    1: {'title': 'Storm’s Brewing'},
    2: {'title': 'Arashi no Yokan'},
  },
  '18': {
    0: {'title': '感動の再会', 'sort': 'かんどう の さいかい'},
    1: {'title': 'A Touching Reunion'},
    2: {'title': 'Kandō no Saikai'},
  },
  '19': {
    0: {'title': '強欲の罪', 'sort': 'ごうよく の つみ'},
    1: {'title': 'The Sin of Greed'},
    2: {'title': 'Gōyoku no Tsumi'},
  },
  '20': {
    0: {'title': '二つの道', 'sort': 'ふたつ の みち'},
    1: {'title': 'Two Paths'},
    2: {'title': 'Futatsu no Michi'},
  },
  '21': {
    0: {'title': 'リベンジ • ナイト', 'sort': 'リベンジ ジ� ナイト'},
    1: {'title': 'Revenge Knight'},
    2: {'title': 'Ribenji • Naito'},
  },
  '22': {
    0: {'title': '恐るべき追跡者', 'sort': 'おそる べき ついせき もの'},
    1: {'title': 'A Pursuer to Fear'},
    2: {'title': 'Osorubeki Tsuiseki‐sha'},
  },
  '23': {
    0: {'title': 'いつか必ず', 'sort': 'いつか かならず'},
    1: {'title': 'Someday, I Swear'},
    2: {'title': 'Itsuka kanarazu'},
  },
  '24': {
    0: {'title': '追いつめられる伝説たち', 'sort': 'おい つめられる でんせつ たち'},
    1: {'title': 'The Pursued Legends'},
    2: {'title': 'Oitsumerareru Densetsu‐tachi'},
  },
  '25': {
    0: {'title': 'よろしければ四対一で', 'sort': 'よろしければ し たいいち で'},
    1: {'title': 'Four‐On‐One, If It’s All Right'},
    2: {'title': 'Yoroshikereba 4 Tai 1 de'},
  },
  '26': {
    0: {'title': '死者たちとの別れ', 'sort': 'ししゃ たちとの わかれ'},
    1: {'title': 'Farewell to the Deceased'},
    2: {'title': 'Shisha‐tachi to no Wakare'},
  },
  '27': {
    0: {'title': '無情の雨', 'sort': 'むじょう の あめ'},
    1: {'title': 'Cruel Rain'},
    2: {'title': 'Mujō no Ame'},
  },
  '28': {
    0: {'title': 'キケンなオトコ', 'sort': 'キケン な オトコ'},
    1: {'title': 'A Dangerous Man'},
    2: {'title': 'Kiken na Otoko'},
  },
  '29': {
    0: {'title': '暗黒の脈動', 'sort': 'あんこく の みゃくどう'},
    1: {'title': 'Dark Pulse'},
    2: {'title': 'Ankoku no Myakudō'},
  },
  '30': {
    0: {'title': '集まれ！お祭り野郎共 Atsumare!', 'sort': 'あつまれ ！ お まつり やろう とも Atsumare!'},
    1: {'title': 'Gather, You Festival Bastards!'},
    2: {'title': 'Omatsuri yarō‐domo'},
  },
  '31': {
    0: {'title': 'バイゼル喧嘩祭り', 'sort': 'バイゼル けんか まつり'},
    1: {'title': 'The Vaizel Fighting Festival'},
    2: {'title': 'Baizeru Kenka Matsuri'},
  },
  '32': {
    0: {'title': '強者そろいぶみ', 'sort': 'つわもの そろいぶみ'},
    1: {'title': 'The Lineup of Strong Men'},
    2: {'title': 'Tsuwamono Soroibumi'},
  },
  '33': {
    0: {'title': '大荒れ模様', 'sort': 'おおあれ もよう'},
    1: {'title': 'Signs of a Great Chaos'},
    2: {'title': 'Ōare Moyō'},
  },
  '34': {
    0: {'title': 'メリオダフ対バーン', 'sort': 'メリオダフ つい バーン'},
    1: {'title': 'Meliodaf vs. Bain'},
    2: {'title': 'Meriodafu tai Bān'},
  },
  '35': {
    0: {'title': '奪われたメリオダス', 'sort': 'うばわ れた メリオダス'},
    1: {'title': 'Robbed Meliodas'},
    2: {'title': 'Ubawareta Meriodasu'},
  },
  '36': {
    0: {'title': '瞬きするその刹那 Mabataki', 'sort': 'まばたき するその せつな Mabataki'},
    1: {'title': 'That Blinking Moment'},
    2: {'title': 'Suru Sono Setsuna'},
  },
  '37': {
    0: {'title': '近づく邂逅', 'sort': 'ちかづ く かいこう'},
    1: {'title': 'Approaching Chance Encounter'},
    2: {'title': 'Chikazuku Kaikō'},
  },
  '38': {
    0: {'title': '偶然と必然', 'sort': 'ぐうぜん と ひつぜん'},
    1: {'title': 'Chance & Necessity'},
    2: {'title': 'Gūzen to Hitsuzen'},
  },
  '39': {
    0: {'title': '積年の思い', 'sort': 'せきねん の おもい'},
    1: {'title': 'A Longstanding Grudge'},
    2: {'title': 'Sekinen no Omoi'},
  },
  '40': {
    0: {'title': 'バイゼル喧嘩祭り決勝戦', 'sort': 'バイゼル けんか まつり けっしょうせん'},
    1: {'title': 'Vaizel’s Fighting Festival Finals'},
    2: {'title': 'Baizeru Kenka Matsuri Kesshōsen'},
  },
  '41': {
    0: {'title': '戦慄のカノン', 'sort': 'せんりつ の カノン'},
    1: {'title': 'Hair‐Raising Canon'},
    2: {'title': 'Senritsu no Kanon'},
  },
  '42': {
    0: {'title': 'デーモン・リアクター', 'sort': 'デーモン ・ リアクター'},
    1: {'title': 'Demon Reactor'},
    2: {'title': 'Dēmon Riakutā'},
  },
  '43': {
    0: {'title': '危険な賭け', 'sort': 'きけん な かけ'},
    1: {'title': 'A Dangerous Bet'},
    2: {'title': 'Kiken na Kake'},
  },
  '44': {
    0: {'title': '絶望へのカウントダウン', 'sort': 'ぜつぼう への カウントダウン'},
    1: {'title': 'Countdown to Despair'},
    2: {'title': 'Zetsubō e no Kauntodaun'},
  },
  '45': {
    0: {'title': '暴虐のカーニバル', 'sort': 'ぼうぎゃく の カーニバル'},
    1: {'title': 'Carnival of Atrocity'},
    2: {'title': 'Bōgyaku no Kānibaru'},
  },
  '46': {
    0: {'title': '姉妹だもんね', 'sort': 'しまい だもんね'},
    1: {'title': 'Because We’re Sisters'},
    2: {'title': 'Shimai da mon ne'},
  },
  '47': {
    0: {'title': '破壊の使徒', 'sort': 'はかい の しと'},
    1: {'title': 'Apostle of Destruction'},
    2: {'title': 'Hakai no Shito'},
  },
  '48': {
    0: {'title': 'めでたく全滅', 'sort': 'めでたく ぜんめつ'},
    1: {'title': 'Happy Annihilation'},
    2: {'title': 'Medetaku Zenmetsu'},
  },
  '49': {
    0: {'title': '余儀なき敗走', 'sort': 'よぎな き はいそう'},
    1: {'title': 'Unavoidable Retreat'},
    2: {'title': 'Yoginaki Haisō'},
  },
  '50': {
    0: {'title': '祭りのあとの', 'sort': 'まつり のあとの'},
    1: {'title': 'After the Festival'},
    2: {'title': 'Matsuri no Ato no'},
  },
  '51': {
    0: {'title': '胸の奥', 'sort': 'むね の おく'},
    1: {'title': 'In the Depths of the Heart'},
    2: {'title': 'Mune no Oku'},
  },
  '52': {
    0: {'title': '噂の真相', 'sort': 'うわさ の しんそう'},
    1: {'title': 'The Truth Behind the Rumors'},
    2: {'title': 'Uwasa no Shinsō'},
  },
  '53': {
    0: {'title': '鎧巨人 対 暁闇の咆哮 Āmā', 'sort': 'よろい きょじん つい あかつき やみ の ほうこう  m '},
    1: {'title': 'The Armor Giant vs. The Roars of Dawn'},
    2: {'title': 'Jaianto tai Dōn Roā'},
  },
  '54': {
    0: {'title': '動かなかった男', 'sort': 'うごか なかった おとこ'},
    1: {'title': 'The Man Who Didn’t Move'},
    2: {'title': 'Ugokanakatta Otoko'},
  },
  '55': {
    0: {'title': 'その男、無情につき', 'sort': 'その おとこ 、 むじょう につき'},
    1: {'title': 'That Man, and His Heartlessness'},
    2: {'title': 'Sono Otoko, Mujō Ni Tsuki'},
  },
  '56': {
    0: {'title': 'アンホーリィ・ナイト', 'sort': 'アンホーリィ ・ ナイト'},
    1: {'title': 'Unholy Knight'},
    2: {'title': 'Anhōrii·Naito'},
  },
  '57': {
    0: {'title': '遠き日の風景', 'sort': 'とおき にち の ふうけい'},
    1: {'title': 'The Scene of a Far‐Off Day'},
    2: {'title': 'Tōki Hi No Fūkei'},
  },
  '58': {
    0: {'title': '背負う覚悟', 'sort': 'せおう かくご'},
    1: {'title': 'Assumed Readiness'},
    2: {'title': 'Seou Kakugo'},
  },
  '59': {
    0: {'title': '読めない男 参入', 'sort': 'よめ ない おとこ さんにゅう'},
    1: {'title': 'The Unreadable Man'},
    2: {'title': 'Yomenai Otoko Sannyū'},
  },
  '60': {
    0: {'title': 'にじみ出す混沌', 'sort': 'にじみ だす こんとん'},
    1: {'title': 'A Creeping Chaos'},
    2: {'title': 'Nijimidasu Konton'},
  },
  '61': {
    0: {'title': '駆りたてられる伝説たち', 'sort': 'かり たてられる でんせつ たち'},
    1: {'title': 'The Legends Get Stirred Up'},
    2: {'title': 'Karitaterareru Densetsu‐tachi'},
  },
  '62': {
    0: {'title': '悪党は止まらない', 'sort': 'あくとう は とま らない'},
    1: {'title': 'The Devil Won’t Stop'},
    2: {'title': 'Akutō Wa Tomaranai'},
  },
  '63': {
    0: {'title': 'アーサー・ペンドラゴン', 'sort': 'アーサー ・ ペンドラゴン'},
    1: {'title': 'Arthur Pendragon'},
    2: {'title': 'Āsā Pendoragon'},
  },
  '64': {
    0: {'title': '王国侵入作戦！！', 'sort': 'おうこく しんにゅう さくせん ！！'},
    1: {'title': 'Strategy To Invade The Kingdom'},
    2: {'title': 'Ōkoku Shin’nyū Sakusen!!'},
  },
  '65': {
    0: {'title': '回避しえぬ衝突', 'sort': 'かいひ しえぬ しょうとつ'},
    1: {'title': 'Inescapable Collision'},
    2: {'title': 'Kaihi Shienu Shōtotsu'},
  },
  '66': {
    0: {'title': '最初の犠牲', 'sort': 'さいしょ の ぎせい'},
    1: {'title': 'First Sacrifice'},
    2: {'title': 'Saisho no Gisei'},
  },
  '67': {
    0: {'title': '亀裂', 'sort': 'きれつ'},
    1: {'title': 'Crack'},
    2: {'title': 'Kiretsu'},
  },
  '68': {
    0: {'title': '圧倒的戦力差', 'sort': 'あっとうてき せんりょく さ'},
    1: {'title': 'Overwhelming Gap In Fighting Strength'},
    2: {'title': 'Attōteki Senryoku‐sa'},
  },
  '69': {
    0: {'title': '初体験は誰にでもある', 'sort': 'しょたいけん は だれ にでもある'},
    1: {'title': 'There’s A First Time For Everything'},
    2: {'title': 'Hatsu Taiken wa Dare ni demo aru'},
  },
  '70': {
    0: {'title': '業火の聖騎士長', 'sort': 'ぎょう ひ の せいきし ちょう'},
    1: {'title': 'The Hellfire Captain of the Holy Knights'},
    2: {'title': 'Gōka no Seikishi‐chō'},
  },
  '71': {
    0: {'title': '闇に在るもの', 'sort': 'やみ に ある もの'},
    1: {'title': 'What Lies In The Shadows'},
    2: {'title': 'Yami ni aru Mono'},
  },
  '72': {
    0: {'title': '遅すぎた男', 'sort': 'おそす ぎた おとこ'},
    1: {'title': 'The Man That Was Too Late'},
    2: {'title': 'Oso Sugita Otoko'},
  },
  '73': {
    0: {'title': 'この命にかえても', 'sort': 'この いのち にかえても'},
    1: {'title': 'If it Kills Me'},
    2: {'title': 'Kono Inochi ni Kaete mo'},
  },
  '74': {
    0: {'title': '果たされる約束', 'sort': 'はた される やくそく'},
    1: {'title': 'Fulfilled Promise'},
    2: {'title': 'Hatasareru Yakusoku'},
  },
  '75': {
    0: {'title': '王たる所似', 'sort': 'おう たる ところ じ'},
    1: {'title': 'The Reason to be King'},
    2: {'title': 'Ō taru Yuen'},
  },
  '76': {
    0: {'title': '王女たちの想い', 'sort': 'おうじょ たちの おもい'},
    1: {'title': 'The Princesses’ Feelings'},
    2: {'title': 'Ōjo‐tachi no Omoi'},
  },
  '77': {
    0: {'title': 'あのコへの想い', 'sort': 'あの コ への おもい'},
    1: {'title': 'Feelings Toward Her'},
    2: {'title': 'Ano Ko e no Omoi'},
  },
  '78': {
    0: {'title': '命と引きかえに', 'sort': 'いのち と びき かえに'},
    1: {'title': 'In Exchange For My Life'},
    2: {'title': 'Inochi To Hikikae Ni'},
  },
  '79': {
    0: {'title': '今一度', 'sort': 'いまいちど'},
    1: {'title': 'Once More'},
    2: {'title': 'Ima Ichido'},
  },
  '80': {
    0: {'title': '怒涛の逆転劇', 'sort': 'どとう の ぎゃくてんげき'},
    1: {'title': 'A Dramatic Surge of Reversal'},
    2: {'title': 'Dotō no Gyakuten Geki'},
  },
  '81': {
    0: {'title': 'メリオダスの一撃', 'sort': 'メリオダス の いちげき'},
    1: {'title': 'Meliodas’ Strike'},
    2: {'title': 'Meriodasu no Ichigeki'},
  },
  '82': {
    0: {'title': '勇気のまじない', 'sort': 'ゆうき のまじない'},
    1: {'title': 'The Incantation of Bravery'},
    2: {'title': 'Yūki no Majinai'},
  },
  '83': {
    0: {'title': '紅蓮の豚', 'sort': 'ぐれん の ぶた'},
    1: {'title': 'Blazing Boar'},
    2: {'title': 'Guren no Buta'},
  },
  '84': {
    0: {'title': '一件落着', 'sort': 'いっけんらくちゃく'},
    1: {'title': 'The Matter is Settled'},
    2: {'title': 'Ikken Rakuchaku'},
  },
  '85': {
    0: {'title': '宴の始まり', 'sort': 'うたげ の はじまり'},
    1: {'title': 'The Party Begins'},
    2: {'title': 'Utage no Hajimari'},
  },
  '86': {
    0: {'title': '今そこに迫る脅威', 'sort': 'いま そこに せまる きょうい'},
    1: {'title': 'The Threat Now Closing In'},
    2: {'title': 'Ima soko ni Semaru Kyōi'},
  },
  '87': {
    0: {'title': '<憤怒>と<強欲>', 'sort': '< ふんど > と < ごうよく >'},
    1: {'title': 'Wrath & Greed'},
    2: {'title': 'Funnu to Gōyoku'},
  },
  '88': {
    0: {'title': 'この世の地獄', 'sort': 'この よの じごく'},
    1: {'title': 'Hell on Earth'},
    2: {'title': 'Kono Yo no Jigoku'},
  },
  '89': {
    0: {'title': '切なる願い', 'sort': 'せつな る ねがい'},
    1: {'title': 'Earnest Hope'},
    2: {'title': 'Setsunaru Negai'},
  },
  '90': {
    0: {'title': '君のためにできること', 'sort': 'くん のためにできること'},
    1: {'title': 'What I Can Do For You'},
    2: {'title': 'Kimi no Tame ni Dekiru koto'},
  },
  '91': {
    0: {'title': '忌むべき存在', 'sort': 'いむ べき そんざい'},
    1: {'title': 'A Loathsome Existence'},
    2: {'title': 'Imubeki Sonzai'},
  },
  '92': {
    0: {'title': '最終決戦開始', 'sort': 'さいしゅうけっせん かいし'},
    1: {'title': 'The Final Decisive Battle Begins'},
    2: {'title': 'Saishū Kessen Kaishi'},
  },
  '93': {
    0: {'title': '赤と灰', 'sort': 'あか と はい'},
    1: {'title': 'Red & Ashes'},
    2: {'title': 'Aka to Hai'},
  },
  '94': {
    0: {'title': '絶望降臨', 'sort': 'ぜつぼう こうりん'},
    1: {'title': 'The Advent of Despair'},
    2: {'title': 'Zetsubō Kōrin'},
  },
  '95': {
    0: {'title': '潰える希望', 'sort': 'ついえ る きぼう'},
    1: {'title': 'Defeated Hope'},
    2: {'title': 'Tsuieru Kibō'},
  },
  '96': {
    0: {'title': 'ホーク', 'sort': 'ホーク'},
    1: {'title': 'Hawk'},
    2: {'title': 'Hōku'},
  },
  '97': {
    0: {'title': 'エリザベス', 'sort': 'エリザベス'},
    1: {'title': 'Elizabeth'},
    2: {'title': 'Erizabesu'},
  },
  '98': {
    0: {'title': '祈り', 'sort': 'いのり'},
    1: {'title': 'Prayer'},
    2: {'title': 'Inori'},
  },
  '99': {
    0: {'title': '決着', 'sort': 'けっちゃく'},
    1: {'title': 'Resolution'},
    2: {'title': 'Kecchaku'},
  },
  '100': {
    0: {'title': '英雄たち', 'sort': 'えいゆう たち'},
    1: {'title': 'The Heroes'},
    2: {'title': 'Eiyū‐tachi'},
  },
  '101': {
    0: {'title': '愛の力', 'sort': 'あい の ちから'},
    1: {'title': 'The Power of Love'},
    2: {'title': 'Ai no Chikara'},
  },
  '102': {
    0: {'title': '別れの予感', 'sort': 'わかれ の よかん'},
    1: {'title': 'Premonition of Parting'},
    2: {'title': 'Wakare no Yokan'},
  },
  '103': {
    0: {'title': '新たなる旅立ち', 'sort': 'あらた なる たびだち'},
    1: {'title': 'A New Journey'},
    2: {'title': 'Aratanaru Tabidachi'},
  },
  '104': {
    0: {'title': '妖精王の帰還', 'sort': 'ようせい おう の きかん'},
    1: {'title': 'The Fairy King’s Return'},
    2: {'title': 'Yōsei‐Ō no Kikan'},
  },
  '105': {
    0: {'title': '何者でもない', 'sort': 'なにもの でもない'},
    1: {'title': 'The Nobody'},
    2: {'title': 'Nanimono demo nai'},
  },
  '106': {
    0: {'title': 'バロールの魔眼', 'sort': 'バロール の ま め'},
    1: {'title': 'Barol’s Evil Eye'},
    2: {'title': 'Barōru no Magan'},
  },
  '107': {
    0: {'title': '真実を求めて', 'sort': 'しんじつ を もとめ て'},
    1: {'title': 'Seek the Truth'},
    2: {'title': 'Shinjitsu o Motomete'},
  },
  '108': {
    0: {'title': '優しい目覚め', 'sort': 'やさしい めざめ'},
    1: {'title': 'Gentle Awakening'},
    2: {'title': 'Yasashii Mezame'},
  },
  '109': {
    0: {'title': '激震', 'sort': 'げきしん'},
    1: {'title': 'Earthquake'},
    2: {'title': 'Gekishin'},
  },
  '110': {
    0: {'title': '告白', 'sort': 'こくはく'},
    1: {'title': 'Confession'},
    2: {'title': 'Kokuhaku'},
  },
  '111': {
    0: {'title': '男の言い分', 'sort': 'おとこ の いいぶん'},
    1: {'title': 'The Man Has His Say'},
    2: {'title': 'Otoko no Iibun'},
  },
  '112': {
    0: {'title': '存在と証明', 'sort': 'そんざい と しょうめい'},
    1: {'title': 'Existence & Proof'},
    2: {'title': 'Sonzai to Shōmei'},
  },
  '113': {
    0: {'title': '啓示', 'sort': 'けいじ'},
    1: {'title': 'Revelation'},
    2: {'title': 'Keiji'},
  },
  '114': {
    0: {'title': 'とまどう英雄たち', 'sort': 'とまどう えいゆう たち'},
    1: {'title': 'The Lost Heroes'},
    2: {'title': 'Tomadō Eiyū‐tachi'},
  },
  '115': {
    0: {'title': '悪夢ふたたび', 'sort': 'あくむ ふたたび'},
    1: {'title': 'Nightmare Take Two'},
    2: {'title': 'Akumu Futatabi'},
  },
  '116': {
    0: {'title': '神器ロストヴェイン', 'sort': 'しんき ロストヴェイン'},
    1: {'title': 'The Sacred Treasure Lostvayne'},
    2: {'title': 'Jingi Rosutovein'},
  },
  '117': {
    0: {'title': '二人の妖精王', 'sort': 'ふたり の ようせい おう'},
    1: {'title': 'The Two Fairy Kings'},
    2: {'title': 'Futari no Yōsei‐ō'},
  },
  '118': {
    0: {'title': '激突！！妖精王の森', 'sort': 'げきとつ ！！ ようせい おう の もり'},
    1: {'title': 'Clash!! The Fairy King’s Forest'},
    2: {'title': 'Gekitotsu!! Yōsei‐ō no Mori'},
  },
  '119': {
    0: {'title': '十戒始動', 'sort': 'じゅっかい しどう'},
    1: {'title': 'The Ten Commandments on the Move'},
    2: {'title': 'Jikkai Shidō'},
  },
  '120': {
    0: {'title': '圧倒的暴力', 'sort': 'あっとうてき ぼうりょく'},
    1: {'title': 'Overwhelming Violence'},
    2: {'title': 'Attō‐teki Bōryoku'},
  },
  '121': {
    0: {'title': '予測不能', 'sort': 'よそくふのう'},
    1: {'title': 'Unpredictable'},
    2: {'title': 'Yosoku Funō'},
  },
  '122': {
    0: {'title': '魔神族の進攻', 'sort': 'まじん ぞく の しんこう'},
    1: {'title': 'The Demon Clan Advances'},
    2: {'title': 'Majin‐zoku no Shinkō'},
  },
  '123': {
    0: {'title': '償いの聖騎士長', 'sort': 'つぐない の せいきし ちょう'},
    1: {'title': 'The Chief Holy Knight Atones For His Sins'},
    2: {'title': 'Tsugunai no Seikishi‐chō'},
  },
  '124': {
    0: {'title': '友情がもたらしたもの', 'sort': 'ゆうじょう がもたらしたもの'},
    1: {'title': 'What the Friends Brought About'},
    2: {'title': 'Yūjō ga Motarashita Mono'},
  },
  '125': {
    0: {'title': '', 'sort': ''},
    1: {'title': 'Down With The Ten Commandments!!"|打倒〈十戒〉|Datō "Jikkai'},
    2: {'title': ''},
  },
  '126': {
    0: {'title': '記憶が目指す場所', 'sort': 'きおく が めざす ばしょ'},
    1: {'title': 'Where the Memory Leads'},
    2: {'title': 'Kioku ga Mezasu Basho'},
  },
  '127': {
    0: {'title': '絶望との再会', 'sort': 'ぜつぼう との さいかい'},
    1: {'title': 'A Reunion With Despair'},
    2: {'title': 'Zetsubō to no Saikai'},
  },
  '128': {
    0: {'title': 'その存在　傍若無人', 'sort': 'その そんざい 　 ぼうじゃくぶじん'},
    1: {'title': 'Their Presence, Outrageous'},
    2: {'title': 'Sono Sonzai Bōjakubujin'},
  },
  '129': {
    0: {'title': 'ドルイドの聖地', 'sort': 'ドルイド の せいち'},
    1: {'title': 'The Druids’ Holy Land'},
    2: {'title': 'Doruido no Seichi'},
  },
  '130': {
    0: {'title': 'やさしく貫く　その痛み', 'sort': 'やさしく つらぬく 　 その いたみ'},
    1: {'title': 'The Pain of Being Softly Pierced'},
    2: {'title': 'Yasashiku Tsuranuku Sono Itami'},
  },
  '131': {
    0: {'title': '愛する者との約束', 'sort': 'あいす る もの との やくそく'},
    1: {'title': 'A Promise To A Loved One'},
    2: {'title': 'Ai suru Mono to no Yakusoku'},
  },
  '132': {
    0: {'title': '僕たちに欠けたもの', 'sort': 'ぼく たちに かけ たもの'},
    1: {'title': 'What We Lacked'},
    2: {'title': 'Bokutachi ni Kaketa Mono'},
  },
  '133': {
    0: {'title': '焦りと不安', 'sort': 'あせり と ふあん'},
    1: {'title': 'Impatience & Anxiety'},
    2: {'title': 'Aseri to Fuan'},
  },
  '134': {
    0: {'title': 'もう団長ではない君へ', 'sort': 'もう だんちょう ではない くん へ'},
    1: {'title': 'To You, Who is No Longer Captain'},
    2: {'title': 'Mō Danchō de wa nai Kimi e'},
  },
  '135': {
    0: {'title': 'ほんの挨拶', 'sort': 'ほんの あいさつ'},
    1: {'title': 'A Little Greeting'},
    2: {'title': 'Honno Aisatsu'},
  },
  '136': {
    0: {'title': '散開する恐怖', 'sort': 'さんかい する きょうふ'},
    1: {'title': 'Spreading Fear'},
    2: {'title': 'Sankai suru Kyōfu'},
  },
  '137': {
    0: {'title': '僕と君の間に', 'sort': 'ぼく と くん の まに'},
    1: {'title': 'Between You & Me'},
    2: {'title': 'Boku to Kimi no Aida ni'},
  },
  '138': {
    0: {'title': '闇との戦い', 'sort': 'やみ との たたかい'},
    1: {'title': 'A Fight with Darkness'},
    2: {'title': 'Yami to no Tatakai'},
  },
  '139': {
    0: {'title': '昔の話を聞かせて', 'sort': 'むかし の はなし を きか せて'},
    1: {'title': 'Tell me About the Past'},
    2: {'title': 'Mukashi no Hanashi wo Kikasete'},
  },
  '140': {
    0: {'title': '盗賊と少年', 'sort': 'とうぞく と しょうねん'},
    1: {'title': 'The Thief & The Boy'},
    2: {'title': 'Tōzoku to Shōnen'},
  },
  '141': {
    0: {'title': '父親と息子', 'sort': 'ちちおや と むすこ'},
    1: {'title': 'Father & Son'},
    2: {'title': 'Chichioya to Musuko'},
  },
  '142': {
    0: {'title': '愛の在り処', 'sort': 'あい の あり ところ'},
    1: {'title': 'Where Love is Found'},
    2: {'title': 'Ai no Arika'},
  },
  '143': {
    0: {'title': '聖女の叫び', 'sort': 'せいじょ の さけび'},
    1: {'title': 'The Saint’s Shriek'},
    2: {'title': 'Seijo no Sakebi'},
  },
  '144': {
    0: {'title': 'その男〈強欲〉につき', 'sort': 'その おとこ 〈 ごうよく 〉 につき'},
    1: {'title': 'That Man Walks the Way of Greed'},
    2: {'title': 'Sono Otoko 〈Gōyoku〉 ni Tsuki'},
  },
  '145': {
    0: {'title': '美しき魂', 'sort': 'うつくし き たましい'},
    1: {'title': 'Beautiful Soul'},
    2: {'title': 'Utsukushiki Tamashii'},
  },
  '146': {
    0: {'title': 'さらば愛しき盗賊', 'sort': 'さらば いとし き とうぞく'},
    1: {'title': 'Farewell, Beloved Thief'},
    2: {'title': 'Saraba Itoshiki Tōzoku'},
  },
  '147': {
    0: {'title': '死の猛追', 'sort': 'しの もうつい'},
    1: {'title': 'The Chase of Death'},
    2: {'title': 'Shi no Mōtsui'},
  },
  '148': {
    0: {'title': 'ガラン・ゲーム', 'sort': 'ガラン ・ ゲーム'},
    1: {'title': 'Galland’s Game'},
    2: {'title': 'Garan Gēmu'},
  },
  '149': {
    0: {'title': 'ガランの魔力', 'sort': 'ガラン の まりょく'},
    1: {'title': 'Galland’s Magic'},
    2: {'title': 'Garan no Maryoku'},
  },
  '150': {
    0: {'title': '太陽の主', 'sort': 'たいよう の しゅ'},
    1: {'title': 'Master of the Sun'},
    2: {'title': 'Taiyō no Aruji'},
  },
  '151': {
    0: {'title': '舞台がボクらを待っている', 'sort': 'ぶたい が ボク らを て いる'},
    1: {'title': 'The Stage Awaits Us'},
    2: {'title': 'Butai ga Bokura wo Matte Iru'},
  },
  '152': {
    0: {'title': '燭光にさそわれて', 'sort': 'しょく ひかり にさそわれて'},
    1: {'title': 'Attracted by the Candle’s Light'},
    2: {'title': 'Shokkō ni Sasowarete'},
  },
  '153': {
    0: {'title': '戦慄の告白', 'sort': 'せんりつ の こくはく'},
    1: {'title': 'A Bloodcurdling Confession'},
    2: {'title': 'Senritsu no Kokuhaku'},
  },
  '154': {
    0: {'title': '悪魔は微笑む', 'sort': 'あくま は ほほえむ'},
    1: {'title': 'The Demon Smiles'},
    2: {'title': 'Akuma wa Hohoemu'},
  },
  '155': {
    0: {'title': '死の罠の迷宮', 'sort': 'しの わな の めいきゅう'},
    1: {'title': 'Death‐Trap Maze'},
    2: {'title': 'Shi no Wana no Meikyū'},
  },
  '156': {
    0: {'title': '迷宮探索競技', 'sort': 'めいきゅう たんさく きょうぎ'},
    1: {'title': 'The Maze Exploration Contest'},
    2: {'title': 'Meikyū Tansaku Kyōgi'},
  },
  '157': {
    0: {'title': '乱れ舞い踊る挑戦者たち', 'sort': 'みだれ まい おどる ちょうせんしゃ たち'},
    1: {'title': 'The Contenders That Dance a Frenzied Jig'},
    2: {'title': 'Midare Maiodoru Chōsenshatachi'},
  },
  '158': {
    0: {'title': '狂宴の勇者たち', 'sort': 'きょうえん の ゆうしゃ たち'},
    1: {'title': 'The Brave Revelers'},
    2: {'title': 'Kyōen no Yūsha‐tachi'},
  },
  '159': {
    0: {'title': '言葉はいらない', 'sort': 'ことば はいらない'},
    1: {'title': 'No Words Necessary'},
    2: {'title': 'Kotoba wa Iranai'},
  },
  '160': {
    0: {'title': 'ゴー！！ブレイクスルー', 'sort': 'ゴー ！！ ブレイクスルー'},
    1: {'title': 'Go!! Break Through!'},
    2: {'title': 'Gō!! Bureikusurū'},
  },
  '161': {
    0: {'title': '伝承の者共', 'sort': 'でんしょう の もの とも'},
    1: {'title': 'Legendary Figures'},
    2: {'title': 'Denshō no Monodomo'},
  },
  '162': {
    0: {'title': '運命の共闘者は誰だ！？', 'sort': 'うんめい の きょうとう もの は だれ だ ！？'},
    1: {'title': 'Who Will Share Their Fate?!'},
    2: {'title': 'Unmei no Kyōtō‐sha wa Dare da!?'},
  },
  '163': {
    0: {'title': '王女と聖女', 'sort': 'おうじょ と せいじょ'},
    1: {'title': 'The Princess and the Holy Maiden'},
    2: {'title': 'Ōjo to Seijo'},
  },
  '164': {
    0: {'title': '譲らぬ者共', 'sort': 'ゆずら ぬ もの とも'},
    1: {'title': 'Those Who Will Never Surrender'},
    2: {'title': 'Yuzuranu Monodomo'},
  },
  '165': {
    0: {'title': 'ちぐはぐラバーズ', 'sort': 'ちぐはぐ ラバーズ'},
    1: {'title': 'Incongrous Lovers'},
    2: {'title': 'Chiguhagu Rabāzu'},
  },
  '166': {
    0: {'title': 'そこに芽吹くもの', 'sort': 'そこに め ふく もの'},
    1: {'title': 'What Buds There'},
    2: {'title': 'Soko ni Mebuku Mono'},
  },
  '167': {
    0: {'title': 'キミの中の大切な', 'sort': 'キミ の なかの たいせつ な'},
    1: {'title': 'What’s Precious Within You'},
    2: {'title': 'Kimi no Naka no Taisetsuna'},
  },
  '168': {
    0: {'title': '〈十戒〉殲滅作戦', 'sort': '〈 じゅっかい 〉 せんめつ さくせん'},
    1: {'title': 'The Ten Commandments Extermination Plan'},
    2: {'title': '<Jikkai> Senmetsu Sakusen'},
  },
  '169': {
    0: {'title': '伝説の最弱聖騎士', 'sort': 'でんせつ の さいじゃく せいきし'},
    1: {'title': 'The Legendary Weakest Holy Knight'},
    2: {'title': 'Densetsu no Saijaku Seikishi'},
  },
  '170': {
    0: {'title': 'その光は誰が為に', 'sort': 'その ひかり は だれが ために'},
    1: {'title': 'From Whom That Light Shines'},
    2: {'title': 'Sono Hikari wa Daregatame ni'},
  },
  '171': {
    0: {'title': '時は来たれり', 'sort': 'とき は きた れり'},
    1: {'title': 'The Time Has Come'},
    2: {'title': 'Toki wa Kitareri'},
  },
  '172': {
    0: {'title': 'かつて友だった お前たちへ', 'sort': 'かつて とも だった お まえ たちへ'},
    1: {'title': 'To You, Who Were Once My Friends'},
    2: {'title': 'Katsute Tomodatta Omaetachi e'},
  },
  '173': {
    0: {'title': '闇は降り立つ', 'sort': 'やみ は おり たつ'},
    1: {'title': 'The Darkness Comes Down'},
    2: {'title': 'Yami wa Oritatsu'},
  },
  '174': {
    0: {'title': 'メリオダス ｖｓ．〈十戒〉', 'sort': 'メリオダス ｖｓ．〈 じゅっかい 〉'},
    1: {'title': 'Meliodas vs. The Ten Commandments'},
    2: {'title': 'Meriodasu vs. <Jikkai>'},
  },
  '175': {
    0: {'title': '大好きなメリオダスへ', 'sort': 'だいすき な メリオダス へ'},
    1: {'title': 'To My Beloved Meliodas'},
    2: {'title': 'Daisukina Meriodasu e'},
  },
  '176': {
    0: {'title': '闇は語る', 'sort': 'やみ は かたる'},
    1: {'title': 'The Darkness Speaks'},
    2: {'title': 'Yami wa Kataru'},
  },
  '177': {
    0: {'title': '僕が君にしてあげられること', 'sort': 'ぼく が くん にしてあげられること'},
    1: {'title': 'What I Can Do For You'},
    2: {'title': 'Boku ga Kimi ni shite Agerareru Koto'},
  },
  '178': {
    0: {'title': '暗黒のブリタニア', 'sort': 'あんこく の ブリタニア'},
    1: {'title': 'Britannia in Darkness'},
    2: {'title': 'Ankoku no Buritania'},
  },
  '179': {
    0: {'title': '希望を求めて', 'sort': 'きぼう を もとめ て'},
    1: {'title': 'Have Hope'},
    2: {'title': 'Kibō wo Motomete'},
  },
  '180': {
    0: {'title': 'さまよえる騎士', 'sort': 'さまよえる きし'},
    1: {'title': 'The Wandering Knight'},
    2: {'title': 'Samayoeru Kishi'},
  },
  '181': {
    0: {'title': '聖騎士長ザラトラス', 'sort': 'せいきし ちょう ザラトラス'},
    1: {'title': 'Chief Holy Knight Zaratras'},
    2: {'title': 'Seikishi‐chō Zaratorasu'},
  },
  '182': {
    0: {'title': 'たしかなぬくもり', 'sort': 'たしかなぬくもり'},
    1: {'title': 'Certain Warmth'},
    2: {'title': 'Tashikana Nukumori'},
  },
  '183': {
    0: {'title': 'デンジャーゾーン', 'sort': 'デンジャーゾーン'},
    1: {'title': 'Danger Zone'},
    2: {'title': 'Denjā Zōn'},
  },
  '184': {
    0: {'title': '超激突！！', 'sort': 'ちょう げきとつ ！！'},
    1: {'title': 'Mega Clash!!'},
    2: {'title': 'Chō‐Gekitotsu!!'},
  },
  '185': {
    0: {'title': '〈傲慢〉 ｖｓ．〈慈愛〉', 'sort': '〈 ごうまん 〉 ｖｓ．〈 じあい 〉'},
    1: {'title': 'Pride vs. Love'},
    2: {'title': '<Gōman> vs. <Jiai>'},
  },
  '186': {
    0: {'title': 'リオネス防衛戦', 'sort': 'リオネス ぼうえいせん'},
    1: {'title': 'Defensive War in Liones'},
    2: {'title': 'Rionesu Bōei‐sen'},
  },
  '187': {
    0: {'title': '滅びよ邪悪な者共よ', 'sort': 'ほろび よ じゃあく な もの とも よ'},
    1: {'title': 'Die, All You Wicked'},
    2: {'title': 'Horobi yo Jaaku na Monodomo yo'},
  },
  '188': {
    0: {'title': '〈罪〉の帰還', 'sort': '〈 つみ 〉 の きかん'},
    1: {'title': 'Return Of The Sins'},
    2: {'title': '〈Tsumi〉 no kikan'},
  },
  '189': {
    0: {'title': '英雄 立つ！！', 'sort': 'えいゆう たつ ！！'},
    1: {'title': 'The Hero Rises!!'},
    2: {'title': 'Eiyū Tatsu!!'},
  },
  '190': {
    0: {'title': '魔宴', 'sort': 'ま うたげ'},
    1: {'title': 'Demon Party'},
    2: {'title': 'Maen'},
  },
  '191': {
    0: {'title': '満たされぬ女', 'sort': 'みた されぬ おんな'},
    1: {'title': 'Insatiable Woman'},
    2: {'title': 'Mitasarenu Onna'},
  },
  '192': {
    0: {'title': 'ヘンドリクセン vs．フラウドリン', 'sort': 'ヘンドリクセン vs ． フラウドリン'},
    1: {'title': 'Hendrickson vs. Fraudrin'},
    2: {'title': 'Hendorikusen vs. Furaudorin'},
  },
  '193': {
    0: {'title': '覚悟の聖騎士長', 'sort': 'かくご の せいきし ちょう'},
    1: {'title': 'The Determined Chief Holy Knight'},
    2: {'title': 'Kakugo no Seikishi‐chō'},
  },
  '194': {
    0: {'title': '残酷なる希望', 'sort': 'ざんこく なる きぼう'},
    1: {'title': 'A Cruel Hope'},
    2: {'title': 'Zankokunaru Kibō'},
  },
  '195': {
    0: {'title': 'リオネス防衛戦終結！', 'sort': 'リオネス ぼうえいせん しゅうけつ ！'},
    1: {'title': 'Liones’s Defensive Battle Come to an End!'},
    2: {'title': 'Rionesu Bōei‐sen Shūketsu!'},
  },
  '196': {
    0: {'title': '君がいるだけで', 'sort': 'くん がいるだけで'},
    1: {'title': 'So Long As You’re Here'},
    2: {'title': 'Kimi ga Iru Dake de'},
  },
  '197': {
    0: {'title': 'それぞれの答え', 'sort': 'それぞれの こたえ'},
    1: {'title': 'To Each His Own Answer'},
    2: {'title': 'Sorezore no Kotae'},
  },
  '198': {
    0: {'title': '巨人と妖精', 'sort': 'きょじん と ようせい'},
    1: {'title': 'The Giant & the Fairy'},
    2: {'title': 'Kyojin to Yōsei'},
  },
  '199': {
    0: {'title': '光なき者たち', 'sort': 'ひかり なき もの たち'},
    1: {'title': 'Those Without Light'},
    2: {'title': 'Hikari Nakisha‐tachi'},
  },
  '200': {
    0: {'title': '聖戦の記憶', 'sort': 'せいせん の きおく'},
    1: {'title': 'Memories of the Holy War'},
    2: {'title': 'Seisen no Kioku'},
  },
  '201': {
    0: {'title': '共闘する者たち', 'sort': 'きょうとう する もの たち'},
    1: {'title': 'Those Who Fight in Arms'},
    2: {'title': 'Kyōtō Suru Mono‐tachi'},
  },
  '202': {
    0: {'title': '聖戦の役者たち', 'sort': 'せいせん の やくしゃ たち'},
    1: {'title': 'Players in the Holy War'},
    2: {'title': 'Seisen no Yakusha‐tachi'},
  },
  '203': {
    0: {'title': 'リュドシェルの計画', 'sort': 'リュドシェル の けいかく'},
    1: {'title': 'Ludoshel’s Plan'},
    2: {'title': 'Ryudosheru no Keikaku'},
  },
  '204': {
    0: {'title': '光あれ', 'sort': 'ひかり あれ'},
    1: {'title': 'Let There Be Light'},
    2: {'title': 'Hikari are'},
  },
  '205': {
    0: {'title': '十戒 ｖｓ．四大天使', 'sort': 'じゅっかい ｖｓ． よんだい てんし'},
    1: {'title': 'The Ten Commandments vs. The Archangels'},
    2: {'title': 'Jikkai vs. Yon Daitenshi'},
  },
  '206': {
    0: {'title': '野獣 吼える', 'sort': 'やじゅう こう える'},
    1: {'title': 'Wild Beasts Howl'},
    2: {'title': 'Yajū Hoeru'},
  },
  '207': {
    0: {'title': '破壊獣インデュラ', 'sort': 'はかい けもの インデュラ'},
    1: {'title': 'Indura, Creature of Destruction'},
    2: {'title': 'Hakai‐jū Indeyura'},
  },
  '208': {
    0: {'title': 'エリザベス ｖｓ．インデュラ', 'sort': 'エリザベス ｖｓ． インデュラ'},
    1: {'title': 'Elizabeth vs. Indura'},
    2: {'title': 'Erizabesu vs. Indyura'},
  },
  '209': {
    0: {'title': '未来への前進', 'sort': 'みらい への ぜんしん'},
    1: {'title': 'Into the Future'},
    2: {'title': 'Mirai e no Zenshin'},
  },
  '210': {
    0: {'title': '感情メイルシュトローム', 'sort': 'かんじょう メイルシュトローム'},
    1: {'title': 'Emotional Maelstrom'},
    2: {'title': 'Kanjō Meirushutorōmu'},
  },
  '211': {
    0: {'title': 'さよならを告げる人', 'sort': 'さよならを つげ る にん'},
    1: {'title': 'He Who Says Goodbye'},
    2: {'title': 'Sayonara wo Tsugeru Hito'},
  },
  '212': {
    0: {'title': '贈り物', 'sort': 'おくりもの'},
    1: {'title': 'The Gift'},
    2: {'title': 'Okurimono'},
  },
  '213': {
    0: {'title': 'それをボクらは愛と呼ぶ', 'sort': 'それを ボク らは あい と よぶ'},
    1: {'title': 'We Call That Love'},
    2: {'title': 'Sore wo Boku‐ra wa Ai to Yobu'},
  },
  '214': {
    0: {'title': 'あの日の君にはもう届かない', 'sort': 'あの にち の くん にはもう とどか ない'},
    1: {'title': 'The Unreachable Past'},
    2: {'title': 'Ano Hi no Kimi ni Hamou Todokanai'},
  },
  '215': {
    0: {'title': '処刑人ゼルドリス', 'sort': 'しょけい にん ゼルドリス'},
    1: {'title': 'Zeldris The Executioner'},
    2: {'title': 'Shokei hito Zerudorisu'},
  },
  '216': {
    0: {'title': 'いざ、大罪集結へ！！', 'sort': 'いざ 、 たいざい しゅうけつ へ ！！'},
    1: {'title': 'Deadly Sins, Unite!!'},
    2: {'title': 'Iza, Taizai Shūketsu e'},
  },
  '217': {
    0: {'title': '心の在り処', 'sort': 'こころ の あり ところ'},
    1: {'title': 'Where the Heart is'},
    2: {'title': 'Kokoro no Arika'},
  },
  '218': {
    0: {'title': 'また会えたね', 'sort': 'また あえ たね'},
    1: {'title': 'We Meet Again'},
    2: {'title': 'Mata Aeta ne'},
  },
  '219': {
    0: {'title': '英雄たちの休息', 'sort': 'えいゆう たちの きゅうそく'},
    1: {'title': 'The Heroes Take a Break'},
    2: {'title': 'Eiyū‐tachi no Kyūsoku'},
  },
  '220': {
    0: {'title': '英雄たちの宴', 'sort': 'えいゆう たちの うたげ'},
    1: {'title': 'The Heroes’ Feast'},
    2: {'title': 'Eiyū‐tachi no Utage'},
  },
  '221': {
    0: {'title': 'はやる心', 'sort': 'はやる こころ'},
    1: {'title': 'It’s All I Can Do'},
    2: {'title': 'Hayaru Kokoro'},
  },
  '222': {
    0: {'title': '呪われし恋人たち', 'sort': 'のろわ れし こいびと たち'},
    1: {'title': 'The Cursed Lovers'},
    2: {'title': 'Norowareshi Koibito‐tachi'},
  },
  '223': {
    0: {'title': 'とまどう恋人たち', 'sort': 'とまどう こいびと たち'},
    1: {'title': 'Bewildered Lovers'},
    2: {'title': 'Tomadō Koibito‐tachi'},
  },
  '224': {
    0: {'title': 'それが僕らの生きる道', 'sort': 'それが ぼくら の いき る みち'},
    1: {'title': 'The Life We Live'},
    2: {'title': 'Sore ga Bokurano Ikiru Michi'},
  },
  '225': {
    0: {'title': 'それぞれの葛藤', 'sort': 'それぞれの かっとう'},
    1: {'title': 'Troubles Between Us'},
    2: {'title': 'Sorezore no Kattō'},
  },
  '226': {
    0: {'title': 'アラクレ', 'sort': 'アラクレ'},
    1: {'title': 'Untamed'},
    2: {'title': 'Arakure'},
  },
  '227': {
    0: {'title': '怨念たちは眠らない', 'sort': 'おんねん たちは ねむら ない'},
    1: {'title': 'The Hateful Cannot Rest'},
    2: {'title': 'Onnen‐tachi wa Nemuranai'},
  },
  '228': {
    0: {'title': '女神と聖女', 'sort': 'めがみ と せいじょ'},
    1: {'title': 'The Goddess and the Saint'},
    2: {'title': 'Megami to Seijo'},
  },
  '229': {
    0: {'title': '愛は乙女の力', 'sort': 'あい は おとめ の ちから'},
    1: {'title': 'Love is a Maiden’s Power'},
    2: {'title': 'Ai wa Otome no Chikara'},
  },
  '230': {
    0: {'title': 'メラスキュラの誤算', 'sort': 'メラスキュラ の ごさん'},
    1: {'title': 'Melascula’s Miscalculation'},
    2: {'title': 'Merasukyura no Gosan'},
  },
  '231': {
    0: {'title': '', 'sort': ''},
    1: {'title': 'Pride vs. Wrath"|〈傲慢〉vs.〈憤怒〉|"Gōman" vs."Fundo'},
    2: {'title': ''},
  },
  '232': {
    0: {'title': '最強 ｖｓ．最凶', 'sort': 'さいきょう ｖｓ． さい きょう'},
    1: {'title': 'The Strongest vs. The Most Wicked'},
    2: {'title': 'Saikyō vs. Saikyō'},
  },
  '233': {
    0: {'title': 'ダメージ', 'sort': 'ダメージ'},
    1: {'title': 'Damage'},
    2: {'title': 'Damēji'},
  },
  '234': {
    0: {'title': '未知への扉', 'sort': 'みち への とびら'},
    1: {'title': 'The Door to the Unknown'},
    2: {'title': 'Michi e no Tobira'},
  },
  '235': {
    0: {'title': '新たなる脅威', 'sort': 'あらた なる きょうい'},
    1: {'title': 'A New Threat'},
    2: {'title': 'Aratanaru Kyōi'},
  },
  '236': {
    0: {'title': '絶望ランデブー', 'sort': 'ぜつぼう ランデブー'},
    1: {'title': 'Hopeless Rendezvous'},
    2: {'title': 'Zetsubō Randebū'},
  },
  '237': {
    0: {'title': 'おしゃぶりの鬼', 'sort': 'おしゃぶりの おに'},
    1: {'title': 'The Pacifier Demon'},
    2: {'title': 'Oshaburi no Oni'},
  },
  '238': {
    0: {'title': '生まれた隙', 'sort': 'うまれ た げき'},
    1: {'title': 'An Opening Presents Itself'},
    2: {'title': 'Umareta Suki'},
  },
  '239': {
    0: {'title': '団長へ', 'sort': 'だんちょう へ'},
    1: {'title': 'To The Captain'},
    2: {'title': 'Danchō e'},
  },
  '240': {
    0: {'title': '未来への礎', 'sort': 'みらい への いしずえ'},
    1: {'title': 'Cornerstone to the Future'},
    2: {'title': 'Mirai e no Ishizue'},
  },
  '241': {
    0: {'title': '受け継がれる魂', 'sort': 'うけつが れる たましい'},
    1: {'title': 'Inheritable Spirit'},
    2: {'title': 'Uketsugareru Tamashii'},
  },
  '242': {
    0: {'title': '', 'sort': ''},
    1: {'title': 'The End of The Seven Deadly Sins"|<七つの大罪> 終結|"Nanatsu no Taizai'},
    2: {'title': ''},
  },
  '243': {
    0: {'title': 'そして彼は旅に出る', 'sort': 'そして かれは たび に でる'},
    1: {'title': 'And  Then He Leaves on a Trip'},
    2: {'title': 'Soshite Kare wa Tabi ni Deru'},
  },
  '244': {
    0: {'title': '選ばれし王女', 'sort': 'えらば れし おうじょ'},
    1: {'title': 'The Chosen Queen'},
    2: {'title': 'Erabareshi Ōjo'},
  },
  '245': {
    0: {'title': '聖者の行進', 'sort': 'せいじゃ の こうしん'},
    1: {'title': 'When The Saints Go Marching In'},
    2: {'title': 'Seija no Kōshin'},
  },
  '246': {
    0: {'title': '邂逅', 'sort': 'かいこう'},
    1: {'title': 'Chance Meeting'},
    2: {'title': 'Kaikō'},
  },
  '247': {
    0: {'title': '回収', 'sort': 'かいしゅう'},
    1: {'title': 'Collecting'},
    2: {'title': 'Kaishū'},
  },
  '248': {
    0: {'title': 'ボクたちの選択', 'sort': 'ボク たちの せんたく'},
    1: {'title': 'Our Choice'},
    2: {'title': 'Boku‐tachi no Sentaku'},
  },
  '249': {
    0: {'title': '取引', 'sort': 'とりひき'},
    1: {'title': 'Deal'},
    2: {'title': 'Torihiki'},
  },
  '250': {
    0: {'title': '王女の覚悟', 'sort': 'おうじょ の かくご'},
    1: {'title': 'Her Resolve'},
    2: {'title': 'Ōjo no Kakugo'},
  },
  '251': {
    0: {'title': '聖戦協定', 'sort': 'せいせん きょうてい'},
    1: {'title': 'The Holy War Accord'},
    2: {'title': 'Seisen Kyōtei'},
  },
  '252': {
    0: {'title': '宿怨', 'sort': 'やど えん'},
    1: {'title': 'An Old Grudge'},
    2: {'title': 'Shukuen'},
  },
  '253': {
    0: {'title': '失われし恩寵', 'sort': 'うしなわ れし おんちょう'},
    1: {'title': 'Lost Grace'},
    2: {'title': 'Ushinawareshi Onchō'},
  },
  '254': {
    0: {'title': '絶望のキャメロット', 'sort': 'ぜつぼう の キャメロット'},
    1: {'title': 'Camelot in Despair'},
    2: {'title': 'Zetsubō no Kyamerotto'},
  },
  '255': {
    0: {'title': '希望の子', 'sort': 'きぼう の こ'},
    1: {'title': 'Child of Hope'},
    2: {'title': 'Kibō no Ko'},
  },
  '256': {
    0: {'title': '貫く聖剣', 'sort': 'つらぬく せいけん'},
    1: {'title': 'The Piercing Sacred Sword'},
    2: {'title': 'Tsuranuku Seiken'},
  },
  '257': {
    0: {'title': '出撃の時', 'sort': 'しゅつげき の とき'},
    1: {'title': 'Sallying Forth'},
    2: {'title': 'Shutsugeki no Toki'},
  },
  '258': {
    0: {'title': '聖戦の幕開け', 'sort': 'せいせん の まくあけ'},
    1: {'title': 'Dawn of the Holy War'},
    2: {'title': 'Seisen no Makuake'},
  },
  '259': {
    0: {'title': '戦渦のブリタニア', 'sort': 'せん うず の ブリタニア'},
    1: {'title': 'War‐Ravaged Britannia'},
    2: {'title': 'Senka no Buritania'},
  },
  '260': {
    0: {'title': 'キミに伝えたいこと', 'sort': 'キミ に つたえ たいこと'},
    1: {'title': 'What I Want to Tell You'},
    2: {'title': 'Kimi ni Tsutaetai Koto'},
  },
  '261': {
    0: {'title': '迷子の猫', 'sort': 'まいご の ねこ'},
    1: {'title': 'Lost Cat'},
    2: {'title': 'Maigo no Neko'},
  },
  '262': {
    0: {'title': '闇に歪む者', 'sort': 'やみ に ひずむ もの'},
    1: {'title': 'The One Warped by Darkness'},
    2: {'title': 'Yami ni Yugamu Mono'},
  },
  '263': {
    0: {'title': '闇爆ぜる', 'sort': 'やみ はぜ る'},
    1: {'title': 'Splitting Darkness'},
    2: {'title': 'Yami Hazeru'},
  },
  '264': {
    0: {'title': '歪み捻じれ壊れる男', 'sort': 'ひずみ ねじ れ こわれ る おとこ'},
    1: {'title': 'A Warped, Twisted, and Broken Man'},
    2: {'title': 'Yugami Nejire Kowareru Otoko'},
  },
  '265': {
    0: {'title': '暴走する愛', 'sort': 'ぼうそう する あい'},
    1: {'title': 'Rampaging Love'},
    2: {'title': 'Bōsō suru Ai'},
  },
  '266': {
    0: {'title': '追う者 追われる者', 'sort': 'おう もの おわ れる もの'},
    1: {'title': 'The Pursuer and the Pursued'},
    2: {'title': 'Ō Mono Owareru Mono'},
  },
  '267': {
    0: {'title': '天空より', 'sort': 'てんくう より'},
    1: {'title': 'From the Skies'},
    2: {'title': 'Tenkū yori'},
  },
  '268': {
    0: {'title': '煉獄より', 'sort': 'れんごく より'},
    1: {'title': 'From Purgatory'},
    2: {'title': 'Rengoku yori'},
  },
  '269': {
    0: {'title': '煉獄ライフ', 'sort': 'れんごく ライフ'},
    1: {'title': 'Purgatory Life'},
    2: {'title': 'Rengoku Raifu'},
  },
  '270': {
    0: {'title': '未知との遭遇', 'sort': 'みち との そうぐう'},
    1: {'title': 'A Meeting with the Unknown'},
    2: {'title': 'Michi to no Sōgū'},
  },
  '271': {
    0: {'title': '一途なる想い', 'sort': 'いちず なる おもい'},
    1: {'title': 'A Single‐Minded Love'},
    2: {'title': 'Ichizu naru Omoi'},
  },
  '272': {
    0: {'title': '永劫する戦い', 'sort': 'えいごう する たたかい'},
    1: {'title': 'Eternal Battle'},
    2: {'title': 'Eigō suru Tatakai'},
  },
  '273': {
    0: {'title': '聖戦の犠牲者', 'sort': 'せいせん の ぎせいしゃ'},
    1: {'title': 'The Victims of the Holy War'},
    2: {'title': 'Seisen no Giseisha'},
  },
  '274': {
    0: {'title': '絶望の堕天使マエル', 'sort': 'ぜつぼう の だてんし マエル'},
    1: {'title': 'The Despairing Fallen Angel Mael'},
    2: {'title': 'Zetsubō no Datenshi Maeru'},
  },
  '275': {
    0: {'title': '心を一つに', 'sort': 'こころ を ひとつ に'},
    1: {'title': 'Together as One'},
    2: {'title': 'Kokoro wo Hitotsu ni'},
  },
  '276': {
    0: {'title': '悲しき一撃', 'sort': 'かなし き いちげき'},
    1: {'title': 'The Tragic Strike'},
    2: {'title': 'Kanashiki Ichigeki'},
  },
  '277': {
    0: {'title': '愛から自由になる術はない', 'sort': 'あい から じゆう になる じゅつ はない'},
    1: {'title': 'There’s No Way To Free Yourself From Love'},
    2: {'title': 'Ai kara Jiyū ni naru Sube wa nai'},
  },
  '278': {
    0: {'title': '絶望に立ち向かえ!!', 'sort': 'ぜつぼう に たち むか え !!'},
    1: {'title': 'Confront Despair!!'},
    2: {'title': 'Zetsubō ni Tachimukae!!'},
  },
  '279': {
    0: {'title': '勝利の鐘の音', 'sort': 'しょうり の かね の おと'},
    1: {'title': 'The Tolling of the Victory Bell'},
    2: {'title': 'Shōri no Kane no Ne'},
  },
  '280': {
    0: {'title': '崩壊', 'sort': 'ほうかい'},
    1: {'title': 'Collapse'},
    2: {'title': 'Hōkai'},
  },
  '281': {
    0: {'title': '妖精王vs.死の天使', 'sort': 'ようせい おう vs. しの てんし'},
    1: {'title': 'The Fairy Kings vs. The Angel of Death'},
    2: {'title': 'Yōsei‐ō vs. Shi no Tenshi'},
  },
  '282': {
    0: {'title': '', 'sort': ''},
    1: {'title': 'Gowther vs. Mael'},
    2: {'title': ''},
  },
  '283': {
    0: {'title': '生還への渇望', 'sort': 'せいかん への かつぼう'},
    1: {'title': 'A Drive to Survive'},
    2: {'title': 'Seikan e no Katsubō'},
  },
  '284': {
    0: {'title': '希望への扉', 'sort': 'きぼう への とびら'},
    1: {'title': 'The Doorway to Hope'},
    2: {'title': 'Kibō e no tobira'},
  },
  '285': {
    0: {'title': 'その先に在るもの', 'sort': 'その さきに ある もの'},
    1: {'title': 'What Lies Ahead'},
    2: {'title': 'Sono saki ni aru mono'},
  },
  '286': {
    0: {'title': '閃光', 'sort': 'せんこう'},
    1: {'title': 'Flash'},
    2: {'title': 'Senkō'},
  },
  '287': {
    0: {'title': '暗黒の王子', 'sort': 'あんこく の おうじ'},
    1: {'title': 'The Prince of Darkness'},
    2: {'title': 'Ankoku no Ōji'},
  },
  '288': {
    0: {'title': '', 'sort': ''},
    1: {'title': 'Ominous Nebula"|凶星雲(オミノス・ネビュラ)|Ominusu Nebyura'},
    2: {'title': ''},
  },
  '289': {
    0: {'title': '〈傲慢〉ｖｓ.〈敬神〉', 'sort': '〈 ごうまん 〉ｖｓ . 〈 たかし かみ 〉'},
    1: {'title': 'Pride vs. Piety'},
    2: {'title': '<Gōman> vs. <Keishin>'},
  },
  '290': {
    0: {'title': '小賢しき蛆虫たち', 'sort': 'こざかし き うじむし たち'},
    1: {'title': 'Clever Little Grubs'},
    2: {'title': 'Kozakashiki Ujimushi‐tachi'},
  },
  '291': {
    0: {'title': '魔女の晩餐', 'sort': 'まじょ の ばんさん'},
    1: {'title': 'The Witch’s Feast'},
    2: {'title': 'Majō no Bansan'},
  },
  '292': {
    0: {'title': '悪夢の顕現 希望の帰還', 'sort': 'あくむ の けんげん きぼう の きかん'},
    1: {'title': 'The Stuff of Nightmares, The Return of Hope'},
    2: {'title': 'Akumu no Kengen Kibō no Kikan'},
  },
  '293': {
    0: {'title': '', 'sort': ''},
    1: {'title': 'When "Someday" Comes True"|「いつか」が叶う時|"Itsuka'},
    2: {'title': ''},
  },
  '294': {
    0: {'title': '希望と葛藤と絶望', 'sort': 'きぼう と かっとう と ぜつぼう'},
    1: {'title': 'Hope, Conflict, and Despair'},
    2: {'title': 'Kibō to Kattō to Zetsubō'},
  },
  '295': {
    0: {'title': '集結するものたち', 'sort': 'しゅうけつ するものたち'},
    1: {'title': 'That Which Gathers'},
    2: {'title': 'Shūketsu suru Mono‐tachi'},
  },
  '296': {
    0: {'title': '友として 兄として', 'sort': 'とも として あに として'},
    1: {'title': 'As a Friend, As a Brother'},
    2: {'title': 'Tomo toshite Ani Toshite'},
  },
  '297': {
    0: {'title': '太陽の救済', 'sort': 'たいよう の きゅうさい'},
    1: {'title': 'The Salvation of the Sun'},
    2: {'title': 'Taiyō no Kyūsai'},
  },
  '298': {
    0: {'title': 'マエルvs.ゼルドリス', 'sort': 'マエル vs. ゼルドリス'},
    1: {'title': 'Mael vs. Zeldris'},
    2: {'title': 'Maeru vs. Zerudorisu'},
  },
  '299': {
    0: {'title': 'すべてが凍り付く', 'sort': 'すべてが こおり つく'},
    1: {'title': 'Everyone Freezes'},
    2: {'title': 'Subete ga Kooritsuku'},
  },
  '300': {
    0: {'title': '魔神王メリオダス', 'sort': 'まじん おう メリオダス'},
    1: {'title': 'The Demon Lord Meliodas'},
    2: {'title': 'Majin‐Ō Meriodasu'},
  },
  '301': {
    0: {'title': '神と対時する人', 'sort': 'かみ と つい とき する にん'},
    1: {'title': 'The One Who Stands Against A God'},
    2: {'title': 'Kami to taiji suru hito'},
  },
  '302': {
    0: {'title': 'みんながキミを待っている', 'sort': 'みんなが キミ を て いる'},
    1: {'title': 'Everyone’s Waiting for You'},
    2: {'title': 'Minna ga Kimi wo Matte iru'},
  },
  '303': {
    0: {'title': 'みんながキミの力になる', 'sort': 'みんなが キミ の ちから になる'},
    1: {'title': 'We’ll All Be Your Strength'},
    2: {'title': 'Minna ga Kimi no Chikara ni Naru'},
  },
  '304': {
    0: {'title': '処刑人は願う', 'sort': 'しょけい にん は ねがう'},
    1: {'title': 'The Executioner’s Wish'},
    2: {'title': 'Shokeinin wa Negau'},
  },
  '305': {
    0: {'title': '断末魔', 'sort': 'だんまつま'},
    1: {'title': 'Death Throes'},
    2: {'title': 'Danmatsuma'},
  },
  '306': {
    0: {'title': '永き旅の終着', 'sort': 'ながき たび の しゅうちゃく'},
    1: {'title': 'The End of a Long Journey'},
    2: {'title': 'Nagaki Tabi no Shūchaku'},
  },
  '307': {
    0: {'title': '幸せに包まれる時', 'sort': 'しあわせ に つつま れる とき'},
    1: {'title': 'Until We’re Shrouded in Happiness'},
    2: {'title': 'Shiawase ni tsutsuma reru toki'},
  },
  '308': {
    0: {'title': 'メリオダスが消える', 'sort': 'メリオダス が きえ る'},
    1: {'title': 'Meliodas Disappears'},
    2: {'title': 'Meriodasu ga Kieru'},
  },
  '309': {
    0: {'title': 'れが私の生きる道', 'sort': 'れが わたし の いき る みち'},
    1: {'title': 'This is the Path I Live'},
    2: {'title': 'Rega watashi no ikiru michi'},
  },
  '310': {
    0: {'title': 'さょなら セつの大罪', 'sort': 'さょなら セ つの たいざい'},
    1: {'title': 'Farewell, Seven Deadly Sins'},
    2: {'title': 'Sayonara Nanatsu no Taizai'},
  },
  '311': {
    0: {'title': 'まだ終わらない', 'sort': 'まだ おわ らない'},
    1: {'title': 'It’s Not Over Yet'},
    2: {'title': 'Mada Owaranai'},
  },
  '312': {
    0: {'title': '開戦', 'sort': 'かいせん'},
    1: {'title': 'Outbreak of War'},
    2: {'title': 'Kaisen'},
  },
  '313': {
    0: {'title': '宿命の兄弟', 'sort': 'しゅくめい の きょうだい'},
    1: {'title': 'Fated Brothers'},
    2: {'title': 'Shukumei no Kyōdai'},
  },
  '314': {
    0: {'title': '二人の魔神王', 'sort': 'ふたり の まじん おう'},
    1: {'title': 'Their Demon Lord'},
    2: {'title': 'Futari no Majin‐Ō'},
  },
  '315': {
    0: {'title': '最終戦争', 'sort': 'さいしゅうせんそう'},
    1: {'title': 'The Final Battle'},
    2: {'title': 'Saishū Sensō'},
  },
  '316': {
    0: {'title': '主恩のインデュラ', 'sort': 'しゅ おん の インデュラ'},
    1: {'title': 'The Lord’s Grace Indura'},
    2: {'title': 'Shuon no Indura'},
  },
  '317': {
    0: {'title': '傲慢なる決意', 'sort': 'ごうまん なる けつい'},
    1: {'title': 'Proud Determination'},
    2: {'title': 'Gōman naru Ketsui'},
  },
  '318': {
    0: {'title': '混迷の戦況', 'sort': 'こんめい の せんきょう'},
    1: {'title': 'Ambiguous Fight'},
    2: {'title': 'Konmei no Senkyō'},
  },
  '319': {
    0: {'title': '許されざる膠着', 'sort': 'ゆるさ れざる こうちゃく'},
    1: {'title': 'Unforgivable Deadlock'},
    2: {'title': 'Yurusarezaru Kōchaku'},
  },
  '320': {
    0: {'title': '絶望の兄弟', 'sort': 'ぜつぼう の きょうだい'},
    1: {'title': 'Brothers of Despair'},
    2: {'title': 'Zetsubō no Kyōdai'},
  },
  '321': {
    0: {'title': '光', 'sort': 'ひかり'},
    1: {'title': 'The Light'},
    2: {'title': 'Hikari'},
  },
  '322': {
    0: {'title': 'キミの名を呼ぶ声', 'sort': 'キミ の めい を よぶ こえ'},
    1: {'title': 'The Voice Calling Your Name'},
    2: {'title': 'Kimi no Na wo Yobu Koe'},
  },
  '323': {
    0: {'title': 'ボクはここにいる', 'sort': 'ボク はここにいる'},
    1: {'title': 'I’m Right Here'},
    2: {'title': 'Boku wa Koko ni Iru'},
  },
  '324': {
    0: {'title': '兄弟の約束', 'sort': 'きょうだい の やくそく'},
    1: {'title': 'A Promise Between Brothers'},
    2: {'title': 'Kyōdai no Yakusoku'},
  },
  '325': {
    0: {'title': '抗う者たち', 'sort': 'あらがう もの たち'},
    1: {'title': 'The Challengers'},
    2: {'title': 'Aragau Mono‐tachi'},
  },
  '326': {
    0: {'title': '', 'sort': ''},
    1: {'title': 'The Seven Deadly Sins vs. The Demon Lord"|＜七つの大罪＞vs.魔神王|"Nanatsu no Taizai'},
    2: {'title': ''},
  },
  '327': {
    0: {'title': 'エスカノールという男', 'sort': 'エスカノール という おとこ'},
    1: {'title': 'The Man Called Escanor'},
    2: {'title': 'Esukanōru to iu Otoko'},
  },
  '328': {
    0: {'title': '天上天下唯我独尊の極み', 'sort': 'てんじょうてんか ゆいがどくそん の きわみ'},
    1: {'title': 'The One: Ultimate'},
    2: {'title': 'Za Wan Arutimetto'},
  },
  '329': {
    0: {'title': 'ゼルドリスvs.魔神王', 'sort': 'ゼルドリス vs. まじん おう'},
    1: {'title': 'Zeldris vs. The Demon Lord'},
    2: {'title': 'Zerudorisu vs. Majin‐Ō'},
  },
  '330': {
    0: {'title': 'あがき', 'sort': 'あがき'},
    1: {'title': 'The Struggle'},
    2: {'title': 'Agaki'},
  },
  '331': {
    0: {'title': '倶に天を戴かず', 'sort': 'ぐ に てん を いただか ず'},
    1: {'title': 'Mortal Enemies'},
    2: {'title': 'Tomo ni Ten wo Itadakazu'},
  },
  '332': {
    0: {'title': '代償', 'sort': 'だいしょう'},
    1: {'title': 'The Price'},
    2: {'title': 'Daishō'},
  },
  '333': {
    0: {'title': '傲慢と暴食と傷跡', 'sort': 'ごうまん と ぼうしょく と きずあと'},
    1: {'title': 'Arrogance, Overeating, and Scars'},
    2: {'title': 'Gōman to Bōshoku to Kizuato'},
  },
  '334': {
    0: {'title': '一つの時代の終わり', 'sort': 'ひとつ の じだい の おわり'},
    1: {'title': 'The End of an Era'},
    2: {'title': 'Hitotsu no Jidai no Owari'},
  },
  '335': {
    0: {'title': '魔女が求めつづけたもの', 'sort': 'まじょ が もとめ つづけたもの'},
    1: {'title': 'What the Witch Had Always Wanted'},
    2: {'title': 'Majo ga Motometsuzuketa Mono'},
  },
  '336': {
    0: {'title': '混沌の王', 'sort': 'こんとん の おう'},
    1: {'title': 'The Lord of Chaos'},
    2: {'title': 'Konton no Ō'},
  },
  '337': {
    0: {'title': 'マーリン', 'sort': 'マーリン'},
    1: {'title': 'Merlin'},
    2: {'title': 'Mārin'},
  },
  '338': {
    0: {'title': '誕生', 'sort': 'たんじょう'},
    1: {'title': 'Birth'},
    2: {'title': 'Tanjō'},
  },
  '339': {
    0: {'title': '混沌の一端', 'sort': 'こんとん の いったん'},
    1: {'title': 'A Taste of Chaos'},
    2: {'title': 'Konton no Ittan'},
  },
  '340': {
    0: {'title': 'あなたに会いたくて', 'sort': 'あなたに あい たくて'},
    1: {'title': 'I Miss You'},
    2: {'title': 'Anata ni Aitakute'},
  },
  '341': {
    0: {'title': 'キャス・パリーグ', 'sort': 'キャス ・ パリーグ'},
    1: {'title': 'Cath Palug'},
    2: {'title': 'Kyasu Parīgu'},
  },
  '342': {
    0: {'title': '勝利の雄叫び', 'sort': 'しょうり の おす さけび'},
    1: {'title': 'Victory Cry'},
    2: {'title': 'Shōri no Otakebi'},
  },
  '343': {
    0: {'title': '永遠の王国', 'sort': 'えいえん の おうこく'},
    1: {'title': 'An Everlasting Kingdom'},
    2: {'title': 'Eien no Ōkoku'},
  },
  '344': {
    0: {'title': '未来へ', 'sort': 'みらい へ'},
    1: {'title': 'Towards the Future'},
    2: {'title': 'Mirai e'},
  },
  '345': {
    0: {'title': '継がれゆくもの', 'sort': 'つが れゆくもの'},
    1: {'title': 'Heirs'},
    2: {'title': 'Tsugareyuku Mono'},
  },
  '346': {
    0: {'title': 'あの空のように', 'sort': 'あの そら のように'},
    1: {'title': 'Like That Sky'},
    2: {'title': 'Ano Sora no Yō ni'},
  },
}

ORIGINAL_TITLE = {
    "text": "【第|index|話】|subtitle|",
    "sort": "だい|index|わ |subtitle|",  # Or GUESS
    "language": "Japanese",
}

ORIGINAL_WORK_DISAMBIGUATION_COMMENT = "The Seven Deadly Sins, manga"
TRANSLATED_WORK_DISAMBIGUATION_COMMENT = "The Seven Deadly Sins, manga, English"

ORIGINAL_LANGUAGE = "Japanese"
TRANSLATED_LANGUAGE = "English"

ORIGINAL_WORK_ALIASES = [
    # The first alias must always be the title for the translated works
    # Remember to use the appropriate Unicode characters!
    #
    # Apostrophe:: ’
    # Dash:: ‐
    # Ellipsis:: …
    # Multiplication Sign:: ×
    # Quotation Marks:: “”
    #
    {
        "text": "Chapter |index|: |subtitle|",
        "sort": "COPY",
        "language": "English",
        "primary": True,
    },
    # {
    #     "text": "The Fragrant Flower Blooms With Dignity, Chapter |index|: |subtitle|",
    #     "sort": "COPY",
    #     "language": "English",
    #     "primary": False,
    # },
    {
        "text": "[Dai |index| Wa] |subtitle|",
        "sort": "Dai |index| Wa |subtitle|",
        "language": "Japanese",
        "primary": False,
    },
]

TRANSLATED_WORK_ALIASES = [
    # {
    #     "text": "The Saga of Tanya the Evil, Vol. |index|",
    #     "sort": "GUESS",
    #     "language": "English",
    #     "primary": False,
    # },
]

MUSICBRAINZ_WORK_TYPE = "Prose"

MUSICBRAINZ_WRITER = ""
MUSICBRAINZ_ORIGINAL_WRITER_CREDITED_AS = None
MUSICBRAINZ_TRANSLATED_WRITER_CREDITED_AS = ""
MUSICBRAINZ_ORIGINAL_WORK_SERIES = ""
MUSICBRAINZ_TRANSLATED_WORK_SERIES = ""
MUSICBRAINZ_TRANSLATOR = ""

BOOKBRAINZ_WORK_TYPE = "manga" # Novel or manga

BOOKBRAINZ_ORIGINAL_WORK_SERIES = "ada8c121-1a2b-459b-add0-ee7f695a75b0"
BOOKBRAINZ_ORIGINAL_WORK_SECOND_SERIES = "2770aac1-2e00-4e87-b101-3a1223c0c0bc"
BOOKBRAINZ_WORK_SECOND_SERIES_OFFSET = 0
BOOKBRAINZ_TRANSLATED_WORK_SERIES = "ae93bf6b-4e83-4cac-8173-19c1d5d44648"
BOOKBRAINZ_TRANSLATED_WORK_SECOND_SERIES = "fcaca2f0-4702-4a84-b458-59235df33945"
BOOKBRAINZ_WRITER = "cfae7528-a044-43f3-966d-3c9165907e1a"
BOOKBRAINZ_ILLUSTRATOR = "cfae7528-a044-43f3-966d-3c9165907e1a"
BOOKBRAINZ_TRANSLATOR = "5647f4b8-65b8-442d-8e6d-cfab7fac734e"
BOOKBRAINZ_ADAPTER = None
BOOKBRAINZ_LETTERER = "1e3cfb9f-b7ec-499a-91d1-1a72e309b57c"

TRANSLATED_EDITIONS = {
    "113": "4c4baa70-6b36-4c6b-aaa8-8d597d6fff2b",
}

IDENTIFIERS = {
    # "1": ["", ""],
    # "2": ["", ""],
    # "3": ["", ""],
    # "4": ["", ""],
    # "5": ["", ""],
    # "6": ["", ""],
    # "7": ["", ""],
    # "8": ["", ""],
    # "9": ["", ""],
    # "10": ["", ""],
    # "11": ["", ""],
    # "12": ["", ""],
    # "13": ["", ""],
    # "14": ["", ""],
    # "15": ["", ""],
    # "16": ["", ""],
    # "17": ["", ""],
}

ORIGINAL_BOOKBRAINZ_WORK_IDENTIFIERS = {
}
TRANSLATED_BOOKBRAINZ_WORK_IDENTIFIERS = {
}

# Use the following snippet to format the items in a MusicBrainz series so that they can be copied and pasted here.
# http get --headers [Accept "application/json"]  $"https://musicbrainz.org/ws/2/series/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx?inc=work-rels" | get relations | select attribute-values.number work.id | rename number id | each {|w| $"    \"($w.number)\": \"https://beta.musicbrainz.org/work/($w.id)\"," } | print --raw
ORIGINAL_MUSICBRAINZ_WORK_IDENTIFIERS = {
}

# http get --headers [Accept "application/json"]  $"https://musicbrainz.org/ws/2/series/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx?inc=work-rels" | get relations | select attribute-values.number work.id | rename number id | each {|w| $"    \"($w.number)\": \"https://beta.musicbrainz.org/work/($w.id)\"," } | print --raw
TRANSLATED_MUSICBRAINZ_WORK_IDENTIFIERS = {
}

ORIGINAL_BOOKBRAINZ_WORK = {
    "title": ORIGINAL_TITLE,
    "type": BOOKBRAINZ_WORK_TYPE,
    "language": ORIGINAL_LANGUAGE,
    "disambiguation": ORIGINAL_WORK_DISAMBIGUATION_COMMENT,
    "aliases": ORIGINAL_WORK_ALIASES,
    "series": BOOKBRAINZ_ORIGINAL_WORK_SERIES,
    "second_series": BOOKBRAINZ_ORIGINAL_WORK_SECOND_SERIES,
    "second_series_offset": BOOKBRAINZ_WORK_SECOND_SERIES_OFFSET,
    "relationships": [
        {
            "role": "writer",
            "id": BOOKBRAINZ_WRITER,
        },
        {
            "role": "illustrator",
            "id": BOOKBRAINZ_ILLUSTRATOR,
        },
    ],
}

TRANSLATED_BOOKBRAINZ_WORK = {
    "title": ORIGINAL_WORK_ALIASES[0],
    "type": BOOKBRAINZ_WORK_TYPE,
    "language": TRANSLATED_LANGUAGE,
    "disambiguation": TRANSLATED_WORK_DISAMBIGUATION_COMMENT,
    "aliases": TRANSLATED_WORK_ALIASES,
    "series": BOOKBRAINZ_TRANSLATED_WORK_SERIES,
    "second_series": BOOKBRAINZ_TRANSLATED_WORK_SECOND_SERIES,
    "second_series_offset": BOOKBRAINZ_WORK_SECOND_SERIES_OFFSET,
    "relationships": [
        {
            "role": "provided story for",
            "id": BOOKBRAINZ_WRITER,
        },
        {
            "role": "illustrator",
            "id": BOOKBRAINZ_ILLUSTRATOR,
        },
        {
            "role": "translator",
            "id": BOOKBRAINZ_TRANSLATOR,
        },
        {
            "role": "adapter",
            "id": BOOKBRAINZ_ADAPTER,
        },
        {
            "role": "letterer",
            "id": BOOKBRAINZ_LETTERER,
        },
        # {
        #     "role": "letterer",
        #     "id": "d52c8c63-9e03-47b5-b6fa-10b2abec6131", # Madeleine Jose
        # },
    ],
}

TAGS = ["fiction", "light novel"]

ORIGINAL_MUSICBRAINZ_WORK = {
    "title": ORIGINAL_TITLE,
    "type": MUSICBRAINZ_WORK_TYPE,
    "language": ORIGINAL_LANGUAGE,
    "disambiguation": ORIGINAL_WORK_DISAMBIGUATION_COMMENT,
    "aliases": ORIGINAL_WORK_ALIASES,
    "series": MUSICBRAINZ_ORIGINAL_WORK_SERIES,
    "artists": [
        {
            "id": MUSICBRAINZ_WRITER,
            "role": "Writer",
            "credited_as": MUSICBRAINZ_ORIGINAL_WRITER_CREDITED_AS,
        },
    ],
    "tags": TAGS,
}

TRANSLATED_MUSICBRAINZ_WORK = {
    "title": ORIGINAL_WORK_ALIASES[0],
    "type": MUSICBRAINZ_WORK_TYPE,
    "language": TRANSLATED_LANGUAGE,
    "disambiguation": TRANSLATED_WORK_DISAMBIGUATION_COMMENT,
    "aliases": TRANSLATED_WORK_ALIASES,
    "series": MUSICBRAINZ_TRANSLATED_WORK_SERIES,
    "artists": [
        {
            "id": MUSICBRAINZ_WRITER,
            "role": "Writer",
            "credited_as": MUSICBRAINZ_TRANSLATED_WRITER_CREDITED_AS,
        },
        {
            "id": MUSICBRAINZ_TRANSLATOR,
            "role": "Translator",
        },
    ],
    "tags": TAGS,
}

MUSICBRAINZ_RELEASE_GROUP = {
    "name": ORIGINAL_WORK_ALIASES[0]["text"],
    "disambiguation": "light novel, English, unabridged",
    "primary_type": "Other",
    "secondary_type": "Audiobook",
    "series": "",
    "credits": [
        {
            "id": MUSICBRAINZ_WRITER,
            "credited_as": "Such and such",
            "join_phrase": " read by ",
        },
        {
            "id": "",
        },
    ],
    "tags": ["light novel", "unabridged"]
}

MUSICBRAINZ_RELEASE_GROUP_LINKS = {
    "1": [
        {
            "url": "",
            "type": "discography entry",
        },
    ],
    "2": [
        {
            "url": "",
            "type": "discography entry",
        },
    ],
    "3": [
        {
            "url": "",
            "type": "discography entry",
        },
    ],
    "4": [
        {
            "url": "",
            "type": "discography entry",
        },
    ],
    "5": [
        {
            "url": "",
            "type": "discography entry",
        },
    ],
    "6": [
        {
            "url": "",
            "type": "discography entry",
        },
    ],
    "7": [
        {
            "url": "",
            "type": "discography entry",
        },
    ],
    "8": [
        {
            "url": "",
            "type": "discography entry",
        },
    ],
    "9": [
        {
            "url": "",
            "type": "discography entry",
        },
    ],
    "10": [
        {
            "url": "",
            "type": "discography entry",
        },
    ],
}

# Constants which don't usually need to be changed
MUSICBRAINZ_CREATE_WORK_URL = "https://beta.musicbrainz.org/work/create"
MUSICBRAINZ_CREATE_RELEASE_GROUP_URL = "https://beta.musicbrainz.org/release-group/create"
BOOKBRAINZ_CREATE_WORK_URL = "https://bookbrainz.org/work/create"

def musicbrainz_log_in(driver, username):
    username_text_box = driver.find_element(by=By.ID, value="id-username")
    username_text_box.send_keys(username)
    password_text_box = driver.find_element(by=By.ID, value="id-password")
    password_text_box.send_keys(os.environ.get("MUSICBRAINZ_PASSWORD"))
    submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button:nth-child(1)")
    submit_button.click()


def bookbrainz_set_title(driver, index, title):
    wait = WebDriverWait(driver, timeout=100)
    # todo Make more accurate by relative to label
    name_text_box = driver.find_element(by=By.XPATH, value="(//div[@class='form-group']/input[@class='form-control'])[1]")
    subtitle = ""
    if "subtitle" in title and title["subtitle"]:
        subtitle = title["subtitle"]
    name = title["text"].replace("|index|", f"{index}").replace("|subtitle|", subtitle)
    name_text_box.send_keys(name)
    wait.until(EC.visibility_of_element_located((By.XPATH, "//label[@class='form-label']/span[@class='text-danger' and text()='Sort Name']")))
    sort_guess_button = driver.find_element(by=By.XPATH, value="//button[text()='Guess']")
    sort_copy_button = driver.find_element(by=By.XPATH, value="//button[text()='Copy']")
    # sort_name_text_box = driver.find_element(by=By.XPATH, value=".input-group:nth-child(2) > .form-control")
    # todo Make more accurate by relative to label
    sort_name_text_box = driver.find_element(by=By.XPATH, value="(//div[@class='input-group']/input[@class='form-control'])[2]")
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
        sort_name_text_box.send_keys(title["sort"].replace("|index|", f"{index}").replace("|subtitle|", sort_subtitle))
    wait.until(EC.visibility_of_element_located((By.XPATH, "//label[@class='form-label']/span[@class='text-success' and text()='Sort Name']")))
    language_text_box = driver.find_element(by=By.XPATH, value="(//div[@class='form-group']/div[starts-with(@class,'Select')]/div[starts-with(@class,'react-select__control')]/div[starts-with(@class,'react-select__value-container')]/div/div[@class='react-select__input']/input[@id='react-select-language-input'])[1]")
    language_text_box.send_keys(title["language"])
    wait.until(EC.visibility_of_element_located((By.XPATH, f"//div[starts-with(@class,'react-select__menu-list')]/div[@id='react-select-language-option-0' and text()='{title['language']}']")))
    first_language_option = driver.find_element(by=By.XPATH, value=f"//div[starts-with(@class,'react-select__menu-list')]/div[@id='react-select-language-option-0' and text()='{title['language']}']")
    first_language_option.click()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//span[@class='text-success' and text()='Language']")))

    # language_text_box.send_keys(title["language"])
    # wait.until(EC.visibility_of_element_located((By.ID, "react-select-language-option-0")))
    # first_language_option = driver.find_element(by=By.ID, value="react-select-language-option-0")
    # first_language_option.click()
    # wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".row:nth-child(4) .text-success")))


def bookbrainz_add_aliases(driver, aliases):
    wait = WebDriverWait(driver, timeout=100)
    add_aliases_button = driver.find_element(by=By.XPATH, value="//button[text()='Add aliases…']")
    add_aliases_button.click()
    wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".modal-title"), "Alias Editor"))
    add_alias_button = driver.find_element(by=By.CSS_SELECTOR, value=".offset-lg-9 > .btn")
    close_button = driver.find_element(by=By.XPATH, value="//button[text()='Close']")
    for index, alias in enumerate(aliases):
        one_based_index = index + 1
        name_text_box = driver.find_element(by=By.XPATH, value=f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/input[@class='form-control'])[{one_based_index}]")
        sort_name_text_box = driver.find_element(by=By.XPATH, value=f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/div[@class='input-group']/input[@class='form-control'])[{one_based_index}]")
        guess_button = driver.find_element(by=By.XPATH, value=f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/div[@class='input-group']/div[@class='input-group-append']/button[text()='Guess'])[{one_based_index}]")
        copy_button = driver.find_element(by=By.XPATH, value=f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/div[@class='input-group']/div[@class='input-group-append']/button[text()='Copy'])[{one_based_index}]")
        # language_text_box_locator = locate_with(By.XPATH, "react-select-language-input").to_right_of({By.CSS_SELECTOR: f"{row} .input-group > .form-control"})
        # language_text_box = driver.find_element(language_text_box_locator)
        language_text_box = driver.find_element(by=By.XPATH, value=f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/div[starts-with(@class,'Select')]/div[starts-with(@class,'react-select__control')]/div[starts-with(@class,'react-select__value-container')]/div/div[@class='react-select__input']/input[@id='react-select-language-input'])[{one_based_index}]")
        primary_checkbox = driver.find_element(by=By.XPATH, value=f"(//div/div[@class='row']/div/div[@class='form-check']/input[@class='form-check-input'])[{one_based_index}]")
        name_text_box.send_keys(alias["text"])
        wait.until(EC.visibility_of_element_located((By.XPATH, f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/label[@class='form-label']/span[@class='text-success' and starts-with(text(),'Name')])[{one_based_index}]")))
        if alias["sort"] == "COPY":
            copy_button.click()
        elif alias["sort"] == "GUESS":
            guess_button.click()
        else:
            sort_name_text_box.send_keys(alias["sort"])
        wait.until(EC.visibility_of_element_located((By.XPATH, f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/label[@class='form-label']/span[@class='text-success' and starts-with(text(),'Sort Name')])[{one_based_index}]")))
        # "css=.react-select__control--is-focused > .react-select__value-container"
        language_text_box.send_keys(alias["language"])
        wait.until(EC.visibility_of_element_located((By.XPATH, f"//div[starts-with(@class,'react-select__menu-list')]/div[@id='react-select-language-option-0' and text()='{alias['language']}']")))
        first_language_option = driver.find_element(by=By.XPATH, value=f"//div[starts-with(@class,'react-select__menu-list')]/div[@id='react-select-language-option-0' and text()='{alias['language']}']")
        first_language_option.click()
        wait.until(EC.visibility_of_element_located((By.XPATH, f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/label[@class='form-label']/span[@class='text-success' and starts-with(text(),'Language')])[{one_based_index}]")))
        if alias["primary"]:
            primary_checkbox.click()
            wait.until(EC.element_to_be_selected(primary_checkbox))
        if index < len(aliases) - 1:
            add_alias_button.click()
            wait.until(EC.visibility_of_element_located((By.XPATH, f"(//div/div[@class='row']/div[@class='col-lg-4']/div[@class='form-group']/input[@class='form-control'])[{one_based_index + 1}]")))
        else:
            close_button.click()
            # todo Or check title? Waiting for the modal dialog to disappear
            wait.until(EC.visibility_of(add_aliases_button))


def bookbrainz_add_identifiers(driver, identifiers):
    wait = WebDriverWait(driver, timeout=100)
    add_identifiers_button = driver.find_element(by=By.CSS_SELECTOR, value=".wrap")
    add_identifiers_button.click()
    wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".modal-title"), "Identifier Editor"))
    add_identifier_button = driver.find_element(by=By.CSS_SELECTOR, value=".offset-lg-9 > .btn")
    close_button = driver.find_element(by=By.CSS_SELECTOR, value=".modal-footer > .btn")
    for index, identifier in enumerate(identifiers):
        one_based_index = index + 1
        row = f"div:nth-child({one_based_index}) > .row"
        if one_based_index == 1:
            row = ".col-lg-4"
        value_text_box = driver.find_element(by=By.CSS_SELECTOR, value=f"{row} .form-control")
        value_text_box.send_keys(identifier)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"{row} .text-success")))
        if index < len(identifiers) - 1:
            add_identifier_button.click()
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"div:nth-child({one_based_index + 1}) > .row .form-control")))
        else:
            close_button.click()
            # todo Or check title? Waiting for the modal dialog to disappear
            wait.until(EC.visibility_of_element_located(add_identifiers_button))


def bookbrainz_set_work_type(driver, work_type):
    wait = WebDriverWait(driver, timeout=100)
    work_type_text_box = driver.find_element(By.ID, "react-select-workType-input")
    work_type_text_box.send_keys(work_type)
    # work_type_index = 0
    # if work_type == "Novel":
    #     work_type_index = 1
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".margin-left-d10")))
    if work_type == "Novel":
        work_type_text_box.send_keys(Keys.ARROW_DOWN)
        # todo Wait
        # work_type_index = 1
    work_type_text_box.send_keys(Keys.ENTER)
    # work_type_option = driver.find_element(by=By.CSS_SELECTOR, value=f"#react-select-workType-option-{work_type_index} > .margin-left-d10")
    # work_type_option.click()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@id='content']/form/div/div/div[3]/div/div/div/small")))
    # wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".row:nth-child(4) .text-success")))



def bookbrainz_add_series(driver, series, index):
    wait = WebDriverWait(driver, timeout=100)
    add_relationships_button = driver.find_element(by=By.XPATH, value="//span[contains(.,' Add relationship')]")
    add_relationships_button.click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-body")))
    other_entity_text_box = driver.find_element(By.ID, "react-select-relationshipEntitySearchField-input")
    other_entity_text_box.send_keys(series)
    # wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".progress-bar")))
    wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='progress']/div[@aria-valuenow=50]")))
    # relationship_text_box = None
    # if is_first_relationship:
    #wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "react-select__input")))
    # react_select_input_span = driver.find_element(By.XPATH, "//div[@class='react-select__input']/input")
    # relationship_text_box = react_select_input_span.find_element(By.TAG_NAME, "input")
    relationship_text_box_locator = locate_with(By.XPATH, "//div[@class='react-select__input']/input").below(other_entity_text_box)
    relationship_text_box = driver.find_element(relationship_text_box_locator)
    # else:
    #     wait.until(EC.visibility_of_element_located((By.ID, "react-select-4-input")))
    #     relationship_text_box = driver.find_element(By.ID, "react-select-4-input")
    # relationship_text_box.click()
    relationship_text_box.send_keys("is part of")
    # relationship_selection = None
    # if select_input_index == 2:
        # "react-select__option react-select__option--is-focused react-select__option--is-selected"
        # react-select__option--is-selected
        #react-select__option--is-focused
        # "react-select__menu-list"
    # wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='react-select__menu-list']/div/div[@class='react-select__option']")))
    # wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "react-select__menu")))
    # react_select_menu = driver.find_element(By.CLASS_NAME, "react-select__menu")
    # react_select_option = react_select_menu.find_element(By.CLASS_NAME, "margin-left-d0")
    # wait.until(EC.visibility_of_element_located((By.XPATH, "//div[starts-with(@class,'react-select__menu-list')]/div/div[@class='margin-left-d0'][1]")))
    # react_select_option = driver.find_element(By.XPATH, "//div[starts-with(@class,'react-select__menu-list')]/div/div[@class='margin-left-d0'][1]")
    wait.until(EC.visibility_of_element_located((By.XPATH, "//div[starts-with(@class,'react-select__menu-list')]/div/div[starts-with(@class,'margin-left-d')][1]")))
    react_select_option = driver.find_element(By.XPATH, "//div[starts-with(@class,'react-select__menu-list')]/div/div[starts-with(@class,'margin-left-d')][1]")
    # else:
        # wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"#react-select-{select_input_index + 1}-option-0 > .margin-left-d0")))
        # relationship_selection = driver.find_element(By.CSS_SELECTOR, f"#react-select-{select_input_index + 1}-option-0 > .margin-left-d0")
    react_select_option.click()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//small[contains(.,'Indicates a Work is part of a Series')]")))
    wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='progress']/div[@aria-valuenow=100]")))
    number_text_box = driver.find_element(By.CSS_SELECTOR, ".form-control:nth-child(5)")
    number_text_box.send_keys(index)
    add_button = driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(3)")
    add_button.click()
    wait.until(EC.visibility_of(add_relationships_button))


BOOKBRAINZ_RELATIONSHIP_VERB = {
    "adapter": "adapted",
    "edition": "contains",
    "illustrator": "illustrated",
    "letterer": "lettered",
    "provided story for": "provided story for",
    "revisor": "revised",
    "translation": "is a translation of",
    "translator": "translated",
    "writer": "wrote",
}


def bookbrainz_add_relationship(driver, relationship):
    if "id" not in relationship or not relationship["id"] or "role" not in relationship or not relationship["role"]:
        return
    wait = WebDriverWait(driver, timeout=100)
    add_relationships_button = driver.find_element(by=By.XPATH, value="//span[contains(.,' Add relationship')]")
    add_relationships_button.click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-body")))
    other_entity_text_box = driver.find_element(By.ID, "react-select-relationshipEntitySearchField-input")
    # if relationship["id"] == "PASTE_FROM_CLIPBOARD":
    #     paste(macropad)
    other_entity_text_box.send_keys(relationship["id"])
    wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='progress']/div[@aria-valuenow=50]")))
    relation = BOOKBRAINZ_RELATIONSHIP_VERB[relationship["role"].lower()]
    relationship_text_box_locator = locate_with(By.XPATH, "//div[@class='react-select__input']/input").below(other_entity_text_box)
    relationship_text_box = driver.find_element(relationship_text_box_locator)
    # relationship_text_box = driver.find_element(By.XPATH, "//div[@class='react-select__input']/input")
    # relationship_text_box = driver.find_element(By.XPATH, f"//div[@class='react-select__input']/input[contains(@value,'{relation}')]")
    # if is_first_relationship:
    # wait.until(EC.visibility_of_element_located((By.ID, f"react-select-{select_input_index}-input")))
    # relationship_text_box = driver.find_element(By.ID, f"react-select-{select_input_index}-input")
    # else:
    #     wait.until(EC.visibility_of_element_located((By.ID, "react-select-4-input")))
    #     relationship_text_box = driver.find_element(By.ID, "react-select-4-input")
        # relationship_text_box = driver.find_element(By.CSS_SELECTOR, ".react-select__control--is-focused > .react-select__value-container")
    relationship_text_box.send_keys(relation)
    wait.until(EC.visibility_of_element_located((By.XPATH, "//div[starts-with(@class,'react-select__menu-list')]/div/div[starts-with(@class,'margin-left-d')][1]")))
    react_select_option = driver.find_element(By.XPATH, "//div[starts-with(@class,'react-select__menu-list')]/div/div[starts-with(@class,'margin-left-d')][1]")
    # relationship_selection = None
    # if select_input_index == 2:
    #     wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".margin-left-d0")))
    #     relationship_selection = driver.find_element(By.CSS_SELECTOR, ".margin-left-d0")
    # else:
    #     wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"#react-select-{select_input_index + 1}-option-0 > .margin-left-d0")))
    #     relationship_selection = driver.find_element(By.CSS_SELECTOR, f"#react-select-{select_input_index + 1}-option-0 > .margin-left-d0")
    react_select_option.click()
    # //small XPATH?
    wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='progress']/div[@aria-valuenow=100]")))
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div:nth-child(2) > .form-group > .form-text")))
    add_button = driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(3)")
    add_button.click()
    wait.until(EC.visibility_of(add_relationships_button))


# original_work = {
#     "title": {
#         # "text": "",
#         "sort": ORIGINAL_WORK_TITLE_SORT,
#         "language": ORIGINAL_LANGUAGE,
#     },
#     "type": "",
#     "language": "",
#     "disambiguation": ORIGINAL_WORK_DISAMBIGUATION_COMMENT,
#     "aliases": original_aliases,
#     "identifiers": original_identifiers,
#     "series": BOOKBRAINZ_ORIGINAL_WORK_SERIES,
#     "relationships": [
#         {
#             "writer": BOOKBRAINZ_WRITER,
#             "illustrator": BOOKBRAINZ_ILLUSTRATOR,
#         }
#     ],
# }
def bookbrainz_create_work(driver, work, index):
    wait = WebDriverWait(driver, timeout=200)

    # driver.close()
    driver.get(BOOKBRAINZ_CREATE_WORK_URL)

    wait.until(lambda x: (x.find_element(By.CSS_SELECTOR, ".logo img") or x.find_element(By.ID, ".logo > .logo")))
    if "https://musicbrainz.org/oauth2/authorize" in driver.current_url:
        musicbrainz_log_in(driver, "jwillikers")
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".card-header > div")))
        cookies = []
        try:
            with open(COOKIES_CACHE_FILE) as f:
                cookies = json.load(f)
        except FileNotFoundError:
            pass
        cookies = [cookie for cookie in cookies if not (cookie["domain"] == "bookbrainz.org" and cookie["name"] == "connect.sid")]
        cookies.append(driver.get_cookie("connect.sid"))
        with open(COOKIES_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=4)
    bookbrainz_set_title(driver, index, work["title"])
    # disambiguation_label = driver.find_element(by=By.XPATH, value="//label[@class='form-label' and span/starts-with(text(),'Disambiguation')]")
    # disambiguation_text_box_locator = driver.find_element(by=By.XPATH, value=".row:nth-child(5) .form-control")
    # disambiguation_text_box_locator = locate_with(By.ID, "react-select-language-input").below({By.XPATH: "//div[@class='form-group']/input[@class='form-control']"})
    # todo Make more accurate by relative to label
    disambiguation_text_box = driver.find_element(by=By.XPATH, value="(//div[@class='form-group']/input[@class='form-control'])[2]")
    # disambiguation_text_box = driver.find_element(disambiguation_text_box_locator)
    if "disambiguation" in work and work["disambiguation"]:
        disambiguation_text_box.send_keys(work["disambiguation"])
        wait.until(EC.visibility_of_element_located((By.XPATH, "//span[@class='text-success' and text()='Disambiguation']")))

    if "aliases" in work and work["aliases"]:
        aliases = []
        for a in work["aliases"]:
            subtitle = ""
            if "subtitle" in a and a["subtitle"]:
                subtitle = a["subtitle"]
            sort_subtitle = ""
            if "sort_subtitle" in a and a["sort_subtitle"]:
                sort_subtitle = a["sort_subtitle"]
            else:
                sort_subtitle = subtitle
            aliases.append(
                {
                    "text": a["text"].replace("|index|", f"{index}").replace("|subtitle|", subtitle),
                    "sort": a["sort"].replace("|index|", f"{index}").replace("|subtitle|", sort_subtitle),
                    "language": a["language"],
                    "primary": a["primary"],
                }
            )
        bookbrainz_add_aliases(driver, aliases)
    if "identifiers" in work and work["identifiers"]:
        bookbrainz_add_identifiers(driver, work["identifiers"])
    bookbrainz_set_work_type(driver, work["type"])

    # work_language_text_box_locator = locate_with(By.ID, "react-select-language-input").below({By.ID: "react-select-workType-input"})
    # work_language_text_box = driver.find_element(work_language_text_box_locator)
    work_language_text_box = driver.find_element(by=By.XPATH, value="(//div[@class='form-group']/div[starts-with(@class,'Select')]/div[starts-with(@class,'react-select__control')]/div[starts-with(@class,'react-select__value-container')]/div/div[@class='react-select__input']/input[@id='react-select-language-input'])[2]")
    work_language_text_box.send_keys(work["language"])
    wait.until(EC.visibility_of_element_located((By.XPATH, f"//div[starts-with(@class,'react-select__menu-list')]/div[@id='react-select-language-option-0' and text()='{work['language']}']")))
    first_work_language_option = driver.find_element(by=By.XPATH, value=f"//div[starts-with(@class,'react-select__menu-list')]/div[@id='react-select-language-option-0' and text()='{work['language']}']")
    first_work_language_option.click()
    # wait.until(EC.visibility_of_element_located((By.XPATH, "//span[@class='text-success' and text()='Language']")))
    wait.until(EC.visibility_of_element_located((By.XPATH, f"//div[contains(@class,'react-select__multi-value__label') and contains(text(),'{work['language']}')]")))
    # select_work_language_element = driver.find_element(By.XPATH, "//div[2]/div/div/div/div/div")
    if "series" in work and work["series"]:
        bookbrainz_add_series(driver, work["series"], index)
    if "second_series" in work and work["second_series"]:
        if "second_series_offset" in work and work["second_series_offset"]:
            bookbrainz_add_series(driver, work["second_series"], str(int(index) + work["second_series_offset"]))
        else:
            bookbrainz_add_series(driver, work["second_series"], index)
    if "relationships" in work:
        for relationship in work["relationships"]:
            if relationship:
                bookbrainz_add_relationship(driver, relationship)
    submit_button = driver.find_element(by=By.XPATH, value="(//button[@type='submit'])[2]")
    submit_button.click()
    wait.until(EC.visibility_of_element_located((By.XPATH, "//a[contains(@class,'btn-success') and contains(text(),'Add Edition')]")))


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


# # To have a special title sort in MusicBrainz, it's necessary to add an alias.
aliases = []
if "aliases" in ORIGINAL_MUSICBRAINZ_WORK:
    aliases = ORIGINAL_MUSICBRAINZ_WORK["aliases"].copy()
if ORIGINAL_MUSICBRAINZ_WORK["title"]["sort"] != "COPY" and ORIGINAL_MUSICBRAINZ_WORK["title"]["text"] != ORIGINAL_MUSICBRAINZ_WORK["title"]["sort"]:
    aliases.append({
        "text": ORIGINAL_MUSICBRAINZ_WORK["title"]["text"],
        "sort": ORIGINAL_MUSICBRAINZ_WORK["title"]["sort"],
        "language": ORIGINAL_MUSICBRAINZ_WORK["title"]["language"],
        "primary": True,
    })
    if SUBTITLES:
        subtitles = {}
        for index, subtitle in SUBTITLES.items():
            if 0 in subtitle and subtitle[0]:
                subtitle[len(aliases)] = subtitle[0]
            subtitles[index] = subtitle
        SUBTITLES = subtitles
ORIGINAL_MUSICBRAINZ_WORK["aliases"] = aliases

TRANSLATED_SUBTITLES = {}
for index, subtitle in SUBTITLES.copy().items():
    if 1 in subtitle and subtitle[1]:
        TRANSLATED_SUBTITLES[index] = {
            0: subtitle[1].copy()
        }

aliases = []
if "aliases" in TRANSLATED_MUSICBRAINZ_WORK:
    aliases = TRANSLATED_MUSICBRAINZ_WORK["aliases"].copy()
if TRANSLATED_MUSICBRAINZ_WORK["title"]["sort"] != "COPY" and TRANSLATED_MUSICBRAINZ_WORK["title"]["text"] != TRANSLATED_MUSICBRAINZ_WORK["title"]["sort"]:
    aliases.append({
        "text": TRANSLATED_MUSICBRAINZ_WORK["title"]["text"],
        "sort": TRANSLATED_MUSICBRAINZ_WORK["title"]["sort"],
        "language": TRANSLATED_MUSICBRAINZ_WORK["title"]["language"],
        "primary": True,
    })
    if TRANSLATED_SUBTITLES:
        for index, subtitle in TRANSLATED_SUBTITLES.items():
            if 0 in subtitle and subtitle[0]:
                TRANSLATED_SUBTITLES[index][len(TRANSLATED_WORK_ALIASES)] = subtitle[0].copy()
TRANSLATED_MUSICBRAINZ_WORK["aliases"] = aliases

geckodriver = shutil.which("geckodriver")
service = webdriver.FirefoxService(executable_path=geckodriver)
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options, service=service)
wait = WebDriverWait(driver, timeout=100)

try:
    with open(COOKIES_CACHE_FILE) as f:
        cookies = json.load(f)
        bookbrainz_cookie = next((cookie for cookie in cookies if cookie["domain"] == "bookbrainz.org" and cookie["name"] == "connect.sid"), None)
        if bookbrainz_cookie is not None:
            driver.get("https://bookbrainz.org")
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".logo img")))
            driver.add_cookie(bookbrainz_cookie)
except FileNotFoundError:
    pass

last_position = 0

command = "add_bookbrainz_work_series"

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
if command == "add_bookbrainz_work_series":
    for i in RANGE:
        # Create the original work first.
        print(f"{i}")

        original_identifiers = []
        if i in IDENTIFIERS:
            original_identifiers = IDENTIFIERS[i].copy()
        if i in ORIGINAL_MUSICBRAINZ_WORK_IDENTIFIERS:
            original_identifiers.append(ORIGINAL_MUSICBRAINZ_WORK_IDENTIFIERS[i])

        original_work = ORIGINAL_BOOKBRAINZ_WORK.copy()

        original_work["identifiers"] = original_identifiers

        subtitle = ""
        if i in SUBTITLES and SUBTITLES[i] and 0 in SUBTITLES[i] and SUBTITLES[i][0] and "title" in SUBTITLES[i][0] and SUBTITLES[i][0]["title"]:
            subtitle = SUBTITLES[i][0]["title"]
        sort_subtitle = ""
        if i in SUBTITLES and SUBTITLES[i] and 0 in SUBTITLES[i] and SUBTITLES[i][0] and "sort" in SUBTITLES[i][0] and SUBTITLES[i][0]["sort"]:
            sort_subtitle = SUBTITLES[i][0]["sort"]

        original_work["title"]["subtitle"] = subtitle
        original_work["title"]["sort_subtitle"] = sort_subtitle

        aliases = []
        for alias_index, alias in enumerate(original_work["aliases"].copy(), start=1):
            alias["subtitle"] = ""
            alias["sort_subtitle"] = ""
            if i in SUBTITLES and SUBTITLES[i] and alias_index in SUBTITLES[i] and SUBTITLES[i][alias_index]:
                if "title" in SUBTITLES[i][alias_index] and SUBTITLES[i][alias_index]["title"]:
                    alias["subtitle"] = SUBTITLES[i][alias_index]["title"]
                if "sort" in SUBTITLES[i][alias_index] and SUBTITLES[i][alias_index]["sort"]:
                    alias["sort_subtitle"] = SUBTITLES[i][alias_index]["sort"]
            aliases.append(alias)
        original_work["aliases"] = aliases

        bookbrainz_create_work(driver, original_work, i)

        original_work_url = driver.current_url

        # Now create the translated work

        translated_identifiers = []
        if i in IDENTIFIERS:
            translated_identifiers = IDENTIFIERS[i].copy()
        if i in TRANSLATED_MUSICBRAINZ_WORK_IDENTIFIERS:
            translated_identifiers.append(TRANSLATED_MUSICBRAINZ_WORK_IDENTIFIERS[i])

        translated_work = TRANSLATED_BOOKBRAINZ_WORK.copy()

        translated_work["identifiers"] = translated_identifiers

        subtitle = ""
        if i in SUBTITLES and SUBTITLES[i] and 1 in SUBTITLES[i] and SUBTITLES[i][1] and "title" in SUBTITLES[i][1] and SUBTITLES[i][1]["title"]:
            subtitle = SUBTITLES[i][1]["title"]
        sort_subtitle = ""
        if i in SUBTITLES and SUBTITLES[i] and 1 in SUBTITLES[i] and SUBTITLES[i][1] and "sort" in SUBTITLES[i][1] and SUBTITLES[i][1]["sort"]:
            sort_subtitle = SUBTITLES[i][1]["sort"]

        translated_work["relationships"] = translated_work["relationships"].copy()
        translated_edition_id = next((id for index, id in reversed(sorted(list(TRANSLATED_EDITIONS.items()), key=lambda pair: float(pair[0]))) if float(i) > float(index)), None)
        if translated_edition_id is not None:
            translated_work["relationships"].append({
                "role": "edition",
                "id": translated_edition_id,
            })

        translated_work["relationships"].append({
            "role": "translation",
            "id": original_work_url,
        })

        translated_work["title"]["subtitle"] = subtitle
        translated_work["title"]["sort_subtitle"] = sort_subtitle

        aliases = []
        for alias_index, alias in enumerate(translated_work["aliases"].copy()):
            alias["subtitle"] = ""
            alias["sort_subtitle"] = ""
            if i in SUBTITLES and TRANSLATED_SUBTITLES[i] and alias_index in TRANSLATED_SUBTITLES[i] and TRANSLATED_SUBTITLES[i][alias_index]:
                if "title" in TRANSLATED_SUBTITLES[i][alias_index] and TRANSLATED_SUBTITLES[i][alias_index]["title"]:
                    alias["subtitle"] = TRANSLATED_SUBTITLES[i][alias_index]["title"]
                if "sort" in TRANSLATED_SUBTITLES[i][alias_index] and TRANSLATED_SUBTITLES[i][alias_index]["sort"]:
                    alias["sort_subtitle"] = TRANSLATED_SUBTITLES[i][alias_index]["sort"]
            aliases.append(alias)
        translated_work["aliases"] = aliases

        bookbrainz_create_work(driver, translated_work, i)

driver.quit()
print("Complete")

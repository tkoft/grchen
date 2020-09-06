#!/usr/bin/env python

"""Takes a file in a silly format and generates a html page for follow-along song lyrics.

Silly format: first line is page title.  "TITLE:" starts a new song, immediately to be followed by "ARTIST:" which gives artist name. Verses separated by empty lines. "CHORUS:" before choruses.  "BRIDGE:" before bridges.
"""

from __future__ import print_function

import argparse
import os
import re
import sys

import pystache


def readRealLine(infile):
    next_line = infile.readline()
    while next_line == "\n":
        next_line = infile.readline()
    return next_line


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("infile", help="Input file", type=argparse.FileType("r"))
    parser.add_argument(
        "-o",
        "--outfile",
        help="Output file",
        default="worship.html",
        type=argparse.FileType("w"),
    )

    args = parser.parse_args(arguments)

    infile = args.infile

    page_title = readRealLine(infile)  # first line should always be title

    next_line = readRealLine(infile)

    # sections loop
    sections = []
    while next_line != "":
        # not at EOF, next_line should be a TITLE or SECTION line
        section_title_match = re.match("TITLE:\s*(.+)", next_line)
        if section_title_match is None:
            section_title_match = re.match("SECTION:\s*(.+)", next_line)
            assert section_title_match is not None

            section_title = section_title_match.group(1)
            next_line = readRealLine(infile)

            section_text = ""
            while (
                not (next_line.startswith("TITLE:") or next_line.startswith("SECTION:"))
                and next_line != ""
            ):
                section_text += next_line
                next_line = readRealLine(infile)

            sections.append(
                {
                    "isLiturgy": True,
                    "isSong": False,
                    "sectionTitle": section_title,
                    "sectionText": section_text,
                }
            )

        else:
            song_title = section_title_match.group(1)
            next_line = readRealLine(infile)

            song_artist_match = re.match("ARTIST:\s*(.+)", next_line)
            assert song_artist_match is not None
            song_artist = song_artist_match.group(1)
            next_line = readRealLine(infile)

            # verses loop
            verses = []
            while (
                not (next_line.startswith("TITLE:") or next_line.startswith("SECTION:"))
                and next_line != ""
            ):
                is_bridge = False
                is_chorus = False
                verse = ""
                if next_line.startswith("CHORUS:"):
                    is_chorus = True
                    next_line = infile.readline()
                elif next_line.startswith("BRIDGE:"):
                    is_bridge = True
                    next_line = infile.readline()
                while next_line != "\n" and next_line != "":
                    verse += next_line
                    next_line = infile.readline()
                verses.append(
                    {"isChorus": is_chorus, "isBridge": is_bridge, "verse": verse}
                )
                next_line = readRealLine(
                    infile
                )  # get first line of next paragraph, or EOF

            sections.append(
                {
                    "isLiturgy": False,
                    "isSong": True,
                    "songTitle": song_title,
                    "songArtist": song_artist,
                    "verses": verses,
                }
            )
        # starting new section or EOF

    templateFile = open("liturgy_page_template.mustache", "r")
    hashInfo = {"title": page_title, "sections": sections}
    output = pystache.render(templateFile.read(), hashInfo)

    args.outfile.write(output)
    args.outfile.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

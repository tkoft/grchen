#!/usr/bin/env python

"""Takes a file in a silly format and generates a html page for follow-along song lyrics.

Silly format: first line is page title.  "TITLE:" starts a new song, immediately to be followed by "ARTIST:" which gives artist name. Verses separated by empty lines. "CHORUS:" before choruses.  "BRIDGE:" before bridges.
"""

from __future__ import print_function

import argparse
import os
import sys
import re

import pystache

def readRealLine(infile):
    nextLine = infile.readline()
    while (nextLine == "\n"):
        nextLine = infile.readline()
    return nextLine

def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("infile", help="Input file", type=argparse.FileType("r"))
    parser.add_argument(
        "-o",
        "--outfile",
        help="Output file",
        default=sys.stdout,
        type=argparse.FileType("w"),
    )

    args = parser.parse_args(arguments)

    infile = args.infile

    pageTitle = readRealLine(infile) # first line should always be title

    nextLine = readRealLine(infile)

    # songs loop
    songs = []
    while (nextLine != ""):
        # not at EOF, nextLine should be a TITLE line
        song_title_match = re.match('TITLE:\s*(.+)', nextLine)
        assert song_title_match is not None
        song_title = song_title_match.group(1)
        nextLine = readRealLine(infile)

        song_artist_match = re.match('ARTIST:\s*(.+)', nextLine)
        assert song_artist_match is not None
        song_artist = song_artist_match.group(1)
        nextLine = readRealLine(infile)

        # verses loop
        verses = []
        while (not nextLine.startswith("TITLE:") and nextLine != ""):
            isBridge = False
            isChorus = False
            verse = ""
            if nextLine.startswith("CHORUS:"):
                isChorus = True
                nextLine = infile.readline()
            elif nextLine.startswith("BRIDGE:"):
                isBridge = True
                nextLine = infile.readline()
            while nextLine != "\n" and nextLine != "":
                verse += nextLine
                nextLine = infile.readline()
            verses.append({"isChorus": isChorus, "isBridge": isBridge, "verse": verse})
            nextLine = readRealLine(infile) # get first line of next paragraph, or EOF

        songs.append({"songTitle": song_title, "songArtist": song_artist, "verses": verses})
        # starting new song or EOF

    templateFile = open("lyrics_page_template.mustache", "r")
    hashInfo = {"title": pageTitle, "songs": songs}
    output = pystache.render(templateFile.read(), hashInfo)

    args.outfile.write(output)
    args.outfile.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

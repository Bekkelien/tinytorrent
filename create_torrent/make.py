#!/usr/bin/python3
import os
import argparse
                     
if __name__ == "__main__":

    # Initialize parser
    parser = argparse.ArgumentParser(description='Create a torrent with py3createtorrent')
    parser.add_argument('-f', '--folder', help='Folder to files to create a torrent from', required=True)

    # Read arguments from command line
    args = parser.parse_args()

    if args.folder:
        print(args.folder)
        os.system(f"py3createtorrent -t udp://tracker.opentrackr.org:1337/announce ./create_torrent/files/{args.folder}")
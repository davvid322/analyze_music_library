# analyze_music_library
These programs extract metadata from a folder(s) of music files and reports any
which are not music files (ignoriing album art etc), have bitrate below 80 kbps,
or which don't have essential tags for song title and artist.

### Usage Notes
- There are two versions of the program.  One accesses a local folder / directory,
and the other accesses a network folder connected via a Samba share.
- The Samba version doesn't like network server names.  You need to instead use the 
IP address of the server followed by the share name (e.g., 192.168.0.50/Music Library).
- The programs generate an exceptions report text file, as well as a .csv file
containing all of the song / artist tags found for each file analyzed.  The report
also shows the total number of songs and hours of music.
- This is a plain text program that runs in a terminal.
- Developed with Python 3.10.6 on Ubuntu Linux 22.04, March 2022.
- Requires installation of 2 packages: mutagen and smbprotocol.
- Note that this has only been tested on on Linux, not Windows or Mac.
- The Samba version can fail if another program is accessing a file on the share.

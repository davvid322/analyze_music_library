# --------------------------------------------------------------------------
# analyze_music_local.py
# Developed with Python 3.10.6 on Ubuntu Linux 22.04
#
# This extracts metadata from a folder(s) of music files and reports any which are not
# music files (ignoriing album art etc), have a low bitrate, or don't have essential
# tages for song title and artist.
# This requires the mutagen package (e.g., Python3 -m pip install mutagen').
# This program also generates a .csv file of all files' metadata including tags.
#
# David Young - March, 2022
# --------------------------------------------------------------------------
import os
from mutagen.mp3 import MP3
from mutagen.asf import ASF
from mutagen.flac import FLAC
from datetime import datetime
import csv

# Start an empty exceptions report file and CSV file
music_root = input('Enter top level folder path for music library to analyze: ')
ex_filename = input('Enter exceptions report file path and name: ')
csv_filename = input('Enter CSV file path and name: ')
exrpt_file = open(ex_filename, 'w')
print('Music file metadata exceptions for all files starting at root : ',
      music_root, file=exrpt_file)
print('Lists non-music, low bitrate, or where title and artist are missing',
      file=exrpt_file)
print('=' * 80, '\n', file=exrpt_file)
print('Started: ', datetime.now().isoformat(' ', 'seconds'),
      '\n', file=exrpt_file)
csv_file = open(csv_filename, 'w', newline='')
csv_writer = csv.writer(csv_file, quotechar='"', delimiter=',',
                        quoting=csv.QUOTE_NONNUMERIC)
csv_header_row = ["File_Path", "File_Name", "Album", "Album Artist", "Song Title",
                  "Song Artist", "Track", "Genre", "Year", "Bitrate", "Minutes", "Type"]
csv_writer.writerow(csv_header_row)
dir_count = 0
file_count = 0
excp_count = 0
song_count = 0
minutes_count = 0.0
      
def analyze_file(pathname: str, filename: str):
    """Read and analyze one item from a directory list in the CWD"""
    global excp_count, song_count, minutes_count
    fullname = os.path.join(pathname, filename)
    csv_data_row = []
       
    # Determine media type as MP3, FLAC, or other (non-music / don't care)
    if ('.mp3' in fullname.lower()):
        media_type = 'MP3'
    elif ('.flac' in fullname.lower()):
        media_type = 'FLAC'
    elif ('.wma' in fullname.lower()):
        media_type = 'ASF'
    elif (('.jpg' in fullname.lower())
        or ('.jpeg' in fullname.lower())
        or ('.m3u' in fullname.lower())
        or ('.m4a' in fullname.lower())  # MP4 but tags are non-standardized rubbish
        or ('.txt' in fullname.lower())
        or ('.log' in fullname.lower())
        or ('.url' in fullname.lower())
        or ('.nfo' in fullname.lower())
        or ('.ini' in fullname.lower())
        or ('.db' in fullname.lower())):
        return  # ignore expected album art etc.
    else:
        media_type = 'WEIRD'
        print(fullname, ' - Not an MP3, FLAC, or ASF/WMA music file', file=exrpt_file)
        excp_count += 1
        return

    # Process MP3's
    if media_type == 'MP3':
        audio = MP3(fullname)
        try:
            songartist = audio['TPE1'].text[0]
        except:
            songartist = ''
        try:
            albumartist = audio['TPE2'].text[0]
        except:
            albumartist = ''
        try:
            album = audio['TALB'].text[0]
        except:
            album = ''
        try:
            songtitle = audio['TIT2'].text[0]
        except:
            songtitle = ''
        try:
            track = audio['TRCK'].text[0]
        except:
            track = ''
        try:
            genre = audio['TCON'].text[0]
        except:
            genre = ''
        try:
            year = audio['TDRC'].text[0]
        except:
            year = ''
        bitrate = audio.info.bitrate
        minutes = "{:.2f}".format(audio.info.length / 60.0)
    # End MP3
    elif media_type == 'FLAC':
        audio = FLAC(fullname)
        try:
            songartist = audio['artist'][0]
        except:
            songartist = ''
        try:
            album = audio['album'][0]
        except:
            album = ''
        try:
            genre = audio['genre'][0]
        except:
            genre = ''
        try:
            songtitle = audio['title'][0]
        except:
            songtitle = ''
        try:
            year = audio['date'][0]
        except:
            year = ''
        albumartist = songartist # FLAC's only have one artist field        
        track = ''
        bitrate = audio.info.bitrate
        minutes = "{:.2f}".format(audio.info.length / 60.0)
    # End FLAC
    elif media_type == 'ASF':
        audio = ASF(fullname)
        try:
            albumartist = audio['WM/AlbumArtist'][0].value
        except:
            albumartist = ''
        try:
            album = audio['WM/AlbumTitle'][0].value
        except:
            album = ''
        try:
            genre = audio['WM/Genre'][0].value
        except:
            genre = ''
        try:
            track = audio['WM/TrackNumber'][0].value
        except:
            track = ''
        try:
            year = audio['WM/Year'][0].value
        except:
            year = ''
        try:
            songartist = audio['Author'][0].value
        except:
            songartist = ''
        try:
            songtitle = audio['Title'][0].value
        except:
            songtitle = ''
        bitrate = audio.info.bitrate
        minutes = "{:.2f}".format(audio.info.length / 60.0)
    # End ASF
    else:
        return
        
    csv_data_row = [pathname, filename, album, albumartist, songtitle, songartist,
                    track, genre, year, bitrate, minutes, media_type]
    csv_writer.writerow(csv_data_row)
    song_count += 1
    minutes_count += (audio.info.length / 60.0)

    if bitrate < 80000:
        print(fullname, ' - has a low bitrate of ', bitrate, file=exrpt_file)
        excp_count += 1

    if (songtitle == '') or (songartist == ''):
        print(fullname, ' - missing metadata - Artist: ', songartist, '  Song: ',
              songtitle, file=exrpt_file)
        excp_count += 1


    return
# End analyzefile Function        
        
# Main program
# Recusively walk through all subfolders, and files therein in sorted order
for dirName, subdirList, fileList in os.walk(music_root):
    dir_count += 1
    print('Processing directory: %s' % dirName)
    for fname in sorted(fileList):
        file_count += 1
        analyze_file(dirName, fname)

# Print the report's summary statistics and show on-screen as well
hours = "{:.2f}".format(minutes_count / 60.0)
print('\nDirectories : ', dir_count, '\t Files : ', file_count,
      '\t Songs : ', song_count, '\t Exceptions : ', excp_count,
      '\t Hours of Music : ', hours, file=exrpt_file)
print('\nEnded: ', datetime.now().isoformat(' ', 'seconds'), file=exrpt_file)
print('\nProcessing complete', file=exrpt_file)
exrpt_file.close()
csv_file.close()
print('\nDirectories : ', dir_count, '\t Files : ', file_count,
      '\t Songs : ', song_count, '\t Exceptions : ', excp_count,
      '\t Hours of Music : ', hours)
print('\nProcessing complete')

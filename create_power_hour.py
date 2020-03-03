import os
import sys

import youtube_dl

# Provide the path to a directory
# Directory should contain a file list.txt
# list.txt should contain a list of URLs, Timestamps, and Track Names

LIST_FILE_NAME = "list.txt"
VIDEO_EXTENSION = "mp4"
MUSIC_EXTENSION = "mp3"
INTERMEDIATE_FILE_EXTENSION = "ts"
SECONDS_PER_SONG = 60

TRIM_SONG_COMMAND = "ffmpeg -y -loglevel panic -i \"{}\" -ss {} -t {} \"{}\""
CREATE_INTERMEDIATE_FILE_COMMAND = "ffmpeg -y -loglevel panic -i \"{}\" -c copy -bsf:v h264_mp4toannexb -f mpegts \"{}\""
CONCATENATE_FILES_COMMAND = "ffmpeg -y -loglevel panic -i \"concat:{}\" -c copy -bsf:a aac_adtstoasc \"{}\""
CREATE_SONG_FILE_COMMAND = "ffmpeg -y -loglevel panic -i \"{}\" \"{}\""


def get_arguments(argv):
    try:
        directory = str(argv[1])
        return directory
    except Exception as e:
        print("ERROR: List file location not specified")
        print(e)
        sys.exit(1)


def get_best_format_for_song(url, file_name):
    try:
        print("\t\tGetting format for", file_name)
        ydl_metadata = youtube_dl.YoutubeDL({"quiet": True})
        meta = ydl_metadata.extract_info(url, download=False)
        formats = meta.get('formats', [meta])

        max_width = -1
        download_format = -1
        for f in formats:
            extension = f['ext']
            format_id = f['format_id']
            audio_codec = f['acodec']

            if extension == VIDEO_EXTENSION and audio_codec != "none":
                width = f['width']
                if width > max_width:
                    max_width = width
                    download_format = format_id

        print("\t\tDone!")
        return download_format
    except Exception as e:
        print("ERROR: Could not get download format for", file_name)
        print(e)
        sys.exit(1)


def timestamp_to_seconds(timestamp, file_name):
    try:
        print("\t\tConverting timestamp for", file_name)
        minutes = int(song_timestamp[0:timestamp.index(":")])
        seconds = int(song_timestamp[timestamp.index(":") + 1:])
        start_time = (minutes * 60) + seconds

        print("\t\tDone!")
        return start_time
    except Exception as e:
        print("ERROR: Could not convert timestamp for", file_name)
        print(e)
        sys.exit(1)


def download_song(download_url, download_file_name, download_format):
    try:
        print("\t\tDownloading", download_file_name)
        ydl_downloader = youtube_dl.YoutubeDL({
            "quiet": True,
            "format": download_format,
            "outtmpl": download_file_name
        })
        ydl_downloader.download([download_url])
        print("\t\tDone!")

    except Exception as e:
        print("ERROR: Could not download song for", download_file_name)
        print(e)
        sys.exit(1)


def trim_song(untrimmed_file_name, start_time, song_num):
    try:
        print("\t\tTrimming", untrimmed_file_name)
        trimmed_file_name = str(song_num) + "_" + untrimmed_file_name
        trim_command = TRIM_SONG_COMMAND.format(
            untrimmed_file_name,
            start_time,
            SECONDS_PER_SONG,
            trimmed_file_name
        )
        os.system(trim_command)
        os.remove(untrimmed_file_name)
        print("\t\tDone!")
        return trimmed_file_name
    except Exception as e:
        print("ERROR: Could not trim song length for", untrimmed_file_name)
        print(e)
        sys.exit(1)


def create_intermediate_file(original_file_name):
    try:
        print("\t\tCreating intermediate file for", original_file_name)
        intermediate_file_name = (original_file_name[0:original_file_name.index(".")] + "." + INTERMEDIATE_FILE_EXTENSION).replace("\n", "")
        intermediate_file_command = CREATE_INTERMEDIATE_FILE_COMMAND.format(
            original_file_name,
            intermediate_file_name
        )
        os.system(intermediate_file_command)
        os.remove(original_file_name)
        print("\t\tDone!")
        return intermediate_file_name
    except Exception as e:
        print("ERROR: Could not create intermediate file for", original_file_name)
        print(e)
        sys.exit(1)


def concatenate_files(file_list, output_file):
    try:
        print("Merging files...")
        input_files = "|".join(file_list)
        concat_command = CONCATENATE_FILES_COMMAND.format(
            input_files,
            output_file
        )
        os.system(concat_command)

        for file in file_list:
            os.remove(file)
        print("Done!")
    except Exception as e:
        print("ERROR: Could not merge video files")
        print(e)
        sys.exit(1)


def create_music_file(video_file, output_music_file):
    try:
        print("Extracting audio file...")
        create_music_file_command = CREATE_SONG_FILE_COMMAND.format(
            video_file,
            output_music_file
        )
        os.system(create_music_file_command)
        print("Done!")
    except Exception as e:
        print("ERROR: Could not extract audio from video")
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    power_hour_directory = get_arguments(sys.argv)
    power_hour_video_output_file = (power_hour_directory + "/powerhour." + VIDEO_EXTENSION).replace("\n", "")
    power_hour_music_output_file = (power_hour_directory + "/powerhour." + MUSIC_EXTENSION).replace("\n", "")

    print("Creating power hour from", power_hour_directory, "...")
    list_file_path = power_hour_directory + "/" + LIST_FILE_NAME
    list_file = open(list_file_path, "r")
    list_file_all_lines = []

    for line in list_file:
        list_file_all_lines.append(line)

    intermediate_file_list = []

    song_num = 1
    for index in range(0, len(list_file_all_lines), 3):
        song_url_index = index
        song_timestamp_index = index + 1
        song_name_index = index + 2

        song_url = list_file_all_lines[song_url_index]
        song_timestamp = list_file_all_lines[song_timestamp_index]
        song_name = list_file_all_lines[song_name_index]

        song_file_name = (song_name + "." + VIDEO_EXTENSION).replace("\n", "")

        print("\tProcessing", song_file_name)
        song_format = get_best_format_for_song(song_url, song_file_name)
        song_start = timestamp_to_seconds(song_timestamp, song_file_name)
        download_song(song_url, song_file_name, song_format)
        trimmed_song_file_name = trim_song(song_file_name, song_start, song_num)
        intermediate_song_file_name = create_intermediate_file(trimmed_song_file_name)

        intermediate_file_list.append(intermediate_song_file_name)
        song_num += 1

    concatenate_files(intermediate_file_list, power_hour_video_output_file)
    print("Created", power_hour_video_output_file)
    create_music_file(power_hour_video_output_file, power_hour_music_output_file)
    print("Created", power_hour_music_output_file)
    print("Done!")

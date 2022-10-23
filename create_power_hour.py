import threading
import sys
import os
import timeit
import argparse

import youtube_dl

LIST_FILE_NAME = "list.txt"
BEEP_FILE_NAME = "beep.txt"
VIDEO_EXTENSION = "mp4"
MUSIC_EXTENSION = "mp3"
INTERMEDIATE_FILE_EXTENSION = "ts"

TRIM_SONG_COMMAND = "ffmpeg -y -loglevel panic -i \"{}\" -ss {} -t {} \"{}\""
CREATE_INTERMEDIATE_FILE_COMMAND = "ffmpeg -y -loglevel panic -i \"{}\" -c copy -bsf:v h264_mp4toannexb -f mpegts \"{}\""
CONCATENATE_FILES_COMMAND = "ffmpeg -y -loglevel panic -i \"concat:{}\" -c copy -bsf:a aac_adtstoasc \"{}\""
CREATE_SONG_FILE_COMMAND = "ffmpeg -y -loglevel panic -i \"{}\" \"{}\""


class video_downloader(threading.Thread):
    def __init__(self, download_url, download_file_name):
        threading.Thread.__init__(self)
        self.download_url = download_url
        self.download_file_name = download_file_name

    def run(self):
        download_format = get_best_format_for_song(self.download_url, self.download_file_name)
        download_song(self.download_url, self.download_file_name, download_format)


class video_trimmer(threading.Thread):
    def __init__(self, untrimmed_file_name, start_timestamp, song_num, seconds_per_song):
        threading.Thread.__init__(self)
        self.untrimmed_file_name = untrimmed_file_name
        self.start_time = timestamp_to_seconds(start_timestamp, untrimmed_file_name)
        self.song_num = song_num
        self.seconds_per_song = seconds_per_song

    def run(self):
        trim_song(self.untrimmed_file_name, self.start_time, self.song_num, self.seconds_per_song)


class intermediate_file_creator(threading.Thread):
    def __init__(self, file_name):
        threading.Thread.__init__(self)
        self.original_file_name = file_name

    def run(self):
        try:
            print("\t\t", self.name, "Creating intermediate file for", self.original_file_name)
            intermediate_file_name = (self.original_file_name[0:self.original_file_name.index(".")] + "." + INTERMEDIATE_FILE_EXTENSION).replace("\n", "")
            intermediate_file_command = CREATE_INTERMEDIATE_FILE_COMMAND.format(
                self.original_file_name,
                intermediate_file_name
            )
            os.system(intermediate_file_command)
            os.remove(self.original_file_name)
            print("\t\t", "Done creating intermediate file, created", intermediate_file_name, "!")
            return intermediate_file_name
        except Exception as e:
            print("ERROR: Could not create intermediate file for", self.original_file_name)
            print(e)
            sys.exit(1)


def get_arguments(argv):
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--directory",
            "-d",
            help="path to the directory with list.txt",
            type=str,
            required=True
        )
        parser.add_argument(
            "--beep",
            "-b",
            help="True or False; does this include a beep between songs?",
            type=bool,
            default=False,
            required=False
        )

        parsed_arguments = parser.parse_args()
        return parsed_arguments
    except Exception as e:
        print("ERROR: Could not parse arguments")
        print(e)
        sys.exit(1)


def get_best_format_for_song(url, file_name):
    try:
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

        return download_format
    except Exception as e:
        print("ERROR: Could not get download format for", file_name)
        print(e)
        sys.exit(1)


def timestamp_to_seconds(timestamp, file_name):
    try:
        minutes = int(timestamp[0:timestamp.index(":")])
        seconds = int(timestamp[timestamp.index(":") + 1:])
        total_seconds = (minutes * 60) + seconds
        return total_seconds
    except Exception as e:
        print("ERROR: Could not convert timestamp for", file_name)
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


def get_beep_file_and_length():
    try:
        beep_file_path = power_hour_directory + "/" + BEEP_FILE_NAME
        beep_file = open(beep_file_path, "r")
        beep_file_all_lines = []

        for line in beep_file:
            beep_file_all_lines.append(line)

        beep_url = beep_file_all_lines[0]
        beep_start = timestamp_to_seconds(beep_file_all_lines[1], "beep")
        beep_end = timestamp_to_seconds(beep_file_all_lines[2], "beep")
        beep_trimmed_length = beep_end - beep_start
        beep_file_name = ("beep." + VIDEO_EXTENSION).replace("\n", "")
        beep_format = get_best_format_for_song(beep_url, beep_file_name)

        download_song(beep_url, beep_file_name, beep_format)
        trimmed_beep_file_name = trim_song(beep_file_name, beep_start, 0, beep_trimmed_length)
        intermediate_beep_file_name = create_intermediate_file(trimmed_beep_file_name)

        return intermediate_beep_file_name, beep_trimmed_length
    except Exception as e:
        print("ERROR: Could not download beep")
        print(e)
        sys.exit(1)


def download_song(download_url, download_file_name, download_format):
    print("\t\tDownloading", download_file_name)
    try:
        download_format = get_best_format_for_song(download_url, download_file_name)
        ydl_downloader = youtube_dl.YoutubeDL({
            "quiet": True,
            "format": download_format,
            "outtmpl": download_file_name
        })
        ydl_downloader.download([download_url])
        print("\t\tDone downloading", download_file_name, "!")

    except Exception as e:
        print("ERROR: Could not download song for", download_file_name, download_url)
        print(e)
        sys.exit(1)


def trim_song(untrimmed_file_name, start_time, song_num, seconds_per_song):
    try:
        print("\t\tTrimming", untrimmed_file_name)
        trimmed_file_name = str(song_num) + "_" + untrimmed_file_name
        trim_command = TRIM_SONG_COMMAND.format(
            untrimmed_file_name,
            start_time,
            seconds_per_song,
            trimmed_file_name
        )
        os.system(trim_command)
        os.remove(untrimmed_file_name)
        print("\t\tDone trimming, created", trimmed_file_name, "!")
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
        print("\t\tDone creating intermediate file, created", intermediate_file_name, "!")
        return intermediate_file_name
    except Exception as e:
        print("ERROR: Could not create intermediate file for", original_file_name)
        print(e)
        sys.exit(1)


def remove_intermediate_files(file_list):
    deleted_beep = False
    for file in file_list:
        try:
            if file == "0_beep.ts":
                if not deleted_beep:
                    os.remove(file)
                    deleted_beep = True
            else:
                os.remove(file)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    start = timeit.default_timer()
    args = get_arguments(sys.argv)
    power_hour_directory = args.directory
    include_beep = args.beep

    print("Creating power hour from", power_hour_directory, "...")

    seconds_per_song = 60
    if include_beep:
        intermediate_beep_file_name, beep_length = get_beep_file_and_length()
        seconds_per_song = seconds_per_song - beep_length

    list_file_path = power_hour_directory + "/" + LIST_FILE_NAME
    list_file = open(list_file_path, "r")
    list_file_all_lines = []

    for line in list_file:
        list_file_all_lines.append(line)

    print("Starting", len(list_file_all_lines)/3, "downloads")
    download_threads = []
    download_start_time = timeit.default_timer()
    for index in range(0, len(list_file_all_lines), 3):
        song_url_index = index
        song_timestamp_index = index + 1
        song_name_index = index + 2

        song_url = list_file_all_lines[song_url_index]
        song_timestamp = list_file_all_lines[song_timestamp_index]
        song_name = list_file_all_lines[song_name_index]

        song_file_name = (song_name + "." + VIDEO_EXTENSION).replace("\n", "")

        download_thread = video_downloader(song_url, song_file_name)
        download_thread.start()
        download_threads.append(download_thread)

    # Wait for all threads to complete
    for t in download_threads:
        t.join()
    download_end_time = timeit.default_timer()
    print("Download Results:", len(list_file_all_lines)/3, "songs in", download_end_time-download_start_time, "seconds")

    song_num = 1

    print("Starting trimming")
    trim_threads = []
    trim_start_time = timeit.default_timer()
    for index in range(0, len(list_file_all_lines), 3):
        song_url_index = index
        song_timestamp_index = index + 1
        song_name_index = index + 2

        song_url = list_file_all_lines[song_url_index]
        song_timestamp = list_file_all_lines[song_timestamp_index]
        song_name = list_file_all_lines[song_name_index]

        song_file_name = (song_name + "." + VIDEO_EXTENSION).replace("\n", "")

        end_timestamp = 0
        start_timestamp = 0
        if "-" in song_timestamp:
            start_timestamp = timestamp_to_seconds(song_timestamp.split('-')[0], song_name)
            end_timestamp = timestamp_to_seconds(song_timestamp.split('-')[1], song_name)
            specified_song_seconds = end_timestamp - start_timestamp
            
            trim_thread = video_trimmer(song_file_name, song_timestamp.split('-')[0], song_num, specified_song_seconds)
            trim_thread.start()
            trim_threads.append(trim_thread)
        else:
            trim_thread = video_trimmer(song_file_name, song_timestamp, song_num, seconds_per_song)
            trim_thread.start()
            trim_threads.append(trim_thread)

        song_num += 1

    for t in trim_threads:
        t.join()
    trim_end_time = timeit.default_timer()
    print("Trim Results:", len(list_file_all_lines)/3, "songs in", trim_end_time-trim_start_time, "seconds")

    song_num = 1

    print("Starting creation of intermediate files")
    intermediate_file_threads = []
    intermediate_file_list = []
    intermediate_file_start_time = timeit.default_timer()
    for index in range(0, len(list_file_all_lines), 3):
        song_name_index = index + 2
        song_name = list_file_all_lines[song_name_index]
        song_file_name = (str(song_num) + "_" + song_name + "." + VIDEO_EXTENSION).replace("\n", "")
        intermediate_song_file_name = (str(song_num) + "_" + song_name + "." + INTERMEDIATE_FILE_EXTENSION).replace("\n", "")

        intermediate_file_thread = intermediate_file_creator(song_file_name)
        intermediate_file_thread.start()
        intermediate_file_threads.append(intermediate_file_thread)

        intermediate_file_list.append(intermediate_song_file_name)
        if include_beep:
            intermediate_file_list.append(intermediate_beep_file_name)

        song_num += 1

    for t in intermediate_file_threads:
        t.join()
    intermediate_file_end_time = timeit.default_timer()
    print("Intermediate File Results:", len(list_file_all_lines)/3, "songs in", intermediate_file_end_time-intermediate_file_start_time, "seconds")

    power_hour_video_output_file = (power_hour_directory + "/powerhour." + VIDEO_EXTENSION).replace("\n", "")
    power_hour_music_output_file = (power_hour_directory + "/powerhour." + MUSIC_EXTENSION).replace("\n", "")

    concatenate_files(intermediate_file_list, power_hour_video_output_file)
    print("Created", power_hour_video_output_file)
    create_music_file(power_hour_video_output_file, power_hour_music_output_file)
    print("Created", power_hour_music_output_file)
    print("Removing intermediate files...")
    remove_intermediate_files(intermediate_file_list)

    end = timeit.default_timer()

    print("Total Runtime:", end-start, "seconds")

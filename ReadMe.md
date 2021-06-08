# Power Hour Creator - Python
## System Requirements
* Windows (probably works on Linux but never tested maybe needs tweaking?)
* Python 3.x
* Pip
* Latest version of [ffmpeg](https://www.ffmpeg.org/download.html)
* FFMPEG added to Path
* Latest version of [youtube-dl](https://youtube-dl.org/)
* Latest version of [youtube_dl](https://pypi.org/project/youtube_dl/)
* youtube-dl added to Path

## Input
The program input is a directory that includes a `list.txt` file.
This should be provided with `-d` or `--directory`.

If you want to include a sound that plays between songs, the directory must
also include a `beep.txt` file, and the optional argument `-b` or `--beep`
must be provided and be `True` (defaults to `False`).

The length of any given video must not exceed 59:59

The `list.txt` file should be structured with each value on a new line as follows:
> video_url_1
>
> timestamp_1 (what time should the video start, i.e. 1:20)
> 
>name_1
>
>video_url_2
>
>timestamp_2
>
>name_2

and so on

The `beep.txt` file should have a single link, starting timestamp, and ending timestamp;
each value on a separate line
> beep_video_url
>
>starting_timestamp
>
>ending_timestamp

### Example list input
>https://www.youtube.com/watch?v=tGsKzZtRwxw
>
>0:00
>
>Star Wars
>
>https://www.youtube.com/watch?v=Pbg8T9r1DiQ
>
>0:00
>
>A Hard Day's Night
>
>https://www.youtube.com/watch?v=JNlnQwHWSYw
>
>
>2:10
>
>Come And Get Your Love
>
>https://www.youtube.com/watch?v=em9lziI07M4&t=94s
>
>0:00
>
>All Star

### Example beep input
>https://www.youtube.com/watch?v=EqH5vmh6oJk
>
>0:00
>
>0:04

## How to run
Execute `create_power_hour.py` with an argument to the directory with list.txt.

`python create_power_hour.py -d [directory_with_text_files]`

`python create_power_hour.py -d [directory_with_text_files.txt] -b [include_beep?]`

## Output
Two files will be created in the list.txt directory powerhour.mp4 and powerhour.mp3

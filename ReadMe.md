# Power Hour Creator - Python
## System Requirements
* Windows
* Python 3.x
* Pip
* Latest version of [ffmpeg](https://www.ffmpeg.org/download.html)
* FFMPEG added to Path
* Latest version of Python [youtube_dl](https://pypi.org/project/youtube_dl/)

## Input
The program input is a directory that includes a `list.txt` file.

The file should be structured with each value on a new line as follows:
> video_url_1
>
> timestamp_1 (what time should the video start, i.e. 1:20, 0:45)
> 
>name_1
>
>video_url_2
>
>timestamp_2
>
>name_2

and so on

## How to run
Execute `create_power_hour.py` with an argument to the directory with list.txt.

`python create_power_hour.py C:\[directory_with_list.txt]`

## Output
Two files will be created in the list.txt directory powerhour.mp4 and powerhour.mp3
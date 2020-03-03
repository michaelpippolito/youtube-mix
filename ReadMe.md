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
### Example input
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

## How to run
Execute `create_power_hour.py` with an argument to the directory with list.txt.

`python create_power_hour.py C:\[directory_with_list.txt]`

## Output
Two files will be created in the list.txt directory powerhour.mp4 and powerhour.mp3
This Python file can be used to create unique power hour mp3 files from your own playlists.

The song will change once every minute and give some indication when it changes. <br />
At each song change, participants are meant to take one shot of beer. <br />
For more information on power hours, check out: https://en.wikipedia.org/wiki/Power_hour <br />

In order for this code to run properly, a few installations are required.
  1. Python 2.7+
  2. The pydub library, available at: https://github.com/jiaaro/pydub#installation
  3. youtube-dl is used to download the songs, available at: https://rg3.github.io/youtube-dl/download.html
  4. ffmpeg is used to convert the songs to mp3 and cut them to the proper length, available at: https://ffmpeg.zeranoe.com/builds/
Note: this was built and run only on Ubuntu 14.04 - though it should run on another OS with mild changes.

How to run:
  - Create a text file called "powerhour.txt" which much be organized in the following manner:
    * [link to the sound between songs]
    * [timestamp to start the sound between songs]
    * [timestamp to end the sound between songs]
    * [link to song 1]
    * [timestamp to start song 1]
    * [link to song 2]
    * [timestamp to start song 2]
    * ...
    * [link to song 60]
    * [timestamp to start song 60]
    
      Example: <br />
        https://www.youtube.com/watch?v=DAGqTRbuExk <br />
        1:01 <br />
        1:04 <br />
        https://www.youtube.com/watch?v=4JW9zHZI3VA <br />
        1:30 <br />
        https://www.youtube.com/watch?v=OcPLPy5WKt0 <br />
        0:00 <br />
        etc. <br />
      
Notes on the code and using it:
  - The audio cannot be extracted by youtube-dl. This creates music files without proper headers which cannot be read or edited by ffmpeg.
    - In order to circumvent this, each video is first downloaded as an mp4, converted to an mp3, and then cut to the proper time.
  - Your text file should have a total of 123 lines.
  - Timestamps should be provided in mm:ss format. I have not implemented a function to convert from hh:mm:ss, but feel free to edit the timeStampConvert function!

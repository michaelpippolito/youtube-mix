from pydub import AudioSegment
import os
import subprocess

def timeStampConvert(timeStamp) :
    minutes = int(timeStamp[0:timeStamp.rfind(":")])
    seconds = int(timeStamp[timeStamp.rfind(":")+1:])
    return (minutes*60000) + (seconds*1000)

#open power hour text file
file = open("powerhour.txt", "r")

#download beep
print "Downloading beep..."
subprocess.call("youtube-dl --quiet -f mp4 -o beep.mp4 " + file.readline(), shell=True)
subprocess.call("ffmpeg -v quiet -i beep.mp4 -ab 160k -ac 2 -ar 44100 -vn beep.mp3", shell=True)
beep = AudioSegment.from_mp3("beep.mp3")
beepStart = timeStampConvert(file.readline())
beepEnd = timeStampConvert(file.readline())
beep = beep[beepStart:beepEnd]

#save beep
beep.export("real.mp3", format="mp3")

#remove extra files, and rename real file
os.remove("beep.mp4")
os.remove("beep.mp3")
os.rename("real.mp3", "beep.mp3")

#calculate length of each song based on beep
songLength = 60000 - (beepEnd - beepStart)

for i in range(1,61) :
    #read link
    link = file.readline()

    #do not attempt to download blank lines
    if link:
        curSong = str(i)

        print "Downloading song " + curSong + " of 60..."

        #calculate start and ending times
        start = timeStampConvert(file.readline())
        end = start + songLength

        subprocess.call("youtube-dl --quiet -f mp4 -o " + curSong + ".mp4 " + link, shell=True)
        subprocess.call("ffmpeg -v quiet -i " + curSong + ".mp4 -ab 160k -ac 2 -ar 44100 -vn " + curSong + ".mp3", shell=True)

        song = AudioSegment.from_mp3(curSong + ".mp3")
        song = song[start:end]
        song.export("real.mp3", format="mp3")

        os.remove(curSong + ".mp4")
        os.remove(curSong + ".mp3")
        os.rename("real.mp3", curSong + ".mp3")

#merge files into power hour, delete temporary files
if os.path.exists("1.mp3") :
    beep = AudioSegment.from_mp3("beep.mp3")
    powerhour = AudioSegment.from_mp3("1.mp3") + beep

    for i in range(2,61) :
        curSong = str(i) + ".mp3"
        if os.path.exists(curSong) :
            song = AudioSegment.from_mp3(curSong)
            powerhour += song + beep

            os.remove(curSong)

    os.remove("1.mp3")
    os.remove("beep.mp3")

    print "Exporting power hour..."
    powerhour.export("powerhour.mp3", format="mp3")
    print "Power hour saved as powerhour.mp3"
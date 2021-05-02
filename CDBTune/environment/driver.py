import os
import subprocess

filelist = []

for dirpath, dirs, files in os.walk('/scratch/bell/alexa157/googledata/'): 
  for filename in files:
    fname = os.path.join(dirpath,filename)
    if fname.endswith('.mkv') and "720P" in fname:
      filelist.append(fname)


for f in filelist:
  print("python test.py --video "+str(f)+" --width 1280 --height 720 --fps 30")
  subprocess.call("python /home/alexa157/CodecTune/CDBTune/environment/build/test.py --video "+str(f)+" --width 1280 --height 720 --fps 30", shell=True)
  

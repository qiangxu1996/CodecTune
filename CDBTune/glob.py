import os

outfile = open('globfile','w')

for dirpath, dirs, files in os.walk('/scratch/bell/alexa157/googledata/'): 
  for filename in files:
    fname = os.path.join(dirpath,filename)
    if fname.endswith('.mkv') and "720P" in fname:
      outfile.write(fname+'\n')

outfile.close()

import os
import datetime

def mkdir(path):
    path = os.path.normpath(path)
    path1 = path.split(os.sep) 
    
    for i, _ in enumerate(path1):
        ptmp = os.path.join('c:\\', *(path1[1:i+1]))
        print (ptmp)
        try: 
            os.mkdir(ptmp)
        except: 
            pass
    
    return

def getdate():
    date = datetime.datetime.today().isoformat()[:10]
    return date
import multiprocessing
import subprocess
import os


def run_other_scripts():
    while range(1):
        try:
            try:
                subprocess.run(['python3', 'crawl/batdongsan.py'])#, timeout=60)
            except:
                os.system('killall chrome')
            #subprocess.run(['python3', 'src/nhatot.py'], timeout=120)
            #subprocess.run(['python3', 'src/muaban.py'], timeout=120)
            #subprocess.run(['python3', 'src/guland.py'], timeout=120)
            #subprocess.run(['python3', 'src/homedy.py'], timeout=120)
            #subprocess.run(['python3', 'src/meeyland.py'], timeout=120)
            #subprocess.run(['python3', 'src/mogi.py'], timeout=120)
            #subprocess.run(['python3', 'src/cafeland.py'], timeout=120)
            #subprocess.run(['python3', 'src/sosanhnha.py'], timeout=120)
            #subprocess.run(['python3', 'src/alonhadat.py'], timeout=120)
        except:
            pass

if __name__ == "__main__":
  
    process = multiprocessing.Process(target=run_other_scripts)
    process.start()
    process.join()

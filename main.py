import multiprocessing
import subprocess
import os


def run_other_scripts():
    while range(1):
        try:
            try:
                subprocess.run(['python3', 'crawl/batdongsan.py'], timeout=360)
            except:
                os.system('killall chrome')
            subprocess.run(['python3', 'crawl/nhatot.py'], timeout=120)
            subprocess.run(['python3', 'crawl/muaban.py'], timeout=120)
            subprocess.run(['python3', 'crawl/guland.py'], timeout=120)
            subprocess.run(['python3', 'crawl/homedy.py'], timeout=120)
            subprocess.run(['python3', 'crawl/meeyland.py'], timeout=120)
            subprocess.run(['python3', 'crawl/mogi.py'], timeout=120)
            subprocess.run(['python3', 'crawl/cafeland.py'], timeout=120)
            subprocess.run(['python3', 'crawl/sosanhnha.py'], timeout=120)
            subprocess.run(['python3', 'crawl/alonhadat.py'], timeout=120)
        except:
            pass

if __name__ == "__main__":
  
    process = multiprocessing.Process(target=run_other_scripts)
    process.start()
    process.join()

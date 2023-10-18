import multiprocessing
import subprocess
import os


def run_other_scripts():
    while True:
        try:
            try:
                subprocess.run(['python3', 'src/batdongsan.py'], timeout=360)
            except:
                os.system('killall chrome')
            subprocess.run(['python3', 'src/nhatot.py'], timeout=300)
            subprocess.run(['python3', 'src/muaban.py'], timeout=300)
            subprocess.run(['python3', 'src/guland.py'], timeout=300)
            subprocess.run(['python3', 'src/homedy.py'], timeout=300)
            subprocess.run(['python3', 'src/meeyland.py'], timeout=300)
            subprocess.run(['python3', 'src/mogi.py'], timeout=300)
            subprocess.run(['python3', 'src/cafeland.py'], timeout=300)
            subprocess.run(['python3', 'src/sosanhnha.py'], timeout=300)
            subprocess.run(['python3', 'src/alonhadat.py'], timeout=300)
        except:
            pass

if __name__ == "__main__":

    process = multiprocessing.Process(target=run_other_scripts)
    process.start()
    

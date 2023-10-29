import multiprocessing
import subprocess
import os


def run_scripts():
    while True:
        try:
            subprocess.run(['python3', 'crawl/batdongsan.py'], timeout=60)
        except:
            os.system('killall chrome')
        subprocess.run(['python3', 'transfer.py'])
        subprocess.run(['python3', 'post_neststock.py'])

if __name__ == "__main__":
    process = multiprocessing.Process(target=run_scripts)
    process.start()
    process.join()

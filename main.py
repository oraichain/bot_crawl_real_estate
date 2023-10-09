import multiprocessing
import subprocess
import os

def run_batdongsan():
    while True:
        try:
            subprocess.run(['python3', 'src/batdongsan.py'], timeout=600)
        except:
            os.system('killall chrome')

def run_other_scripts():
    while True:
        try:
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
    # Tạo hai tiến trình riêng biệt cho hai vòng lặp
    process1 = multiprocessing.Process(target=run_batdongsan)
    process2 = multiprocessing.Process(target=run_other_scripts)

    # Bắt đầu hai tiến trình
    process1.start()
    process2.start()

    # Chờ cả hai tiến trình hoàn thành
    process1.join()
    process2.join()

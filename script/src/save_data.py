import os
from datetime import datetime



def save(hashmd5,data,website):
   xpath = f'./raw/{website}/{datetime.now().strftime("%Y-%m-%d")}'
   if not os.path.exists(xpath):
      os.mkdir(xpath)
   if not os.path.exists(f'{xpath}/{hashmd5}'):
      with open(f'{xpath}/{hashmd5}','w',encoding='utf-8') as f:
         f.write(data)
         f.close()
# tạo hàm loggin để lưu lại các thông tin cần thiết và lưu vào file log đồng thời in ra màn hình
import os
from datetime import datetime

def logging(message, level='info'):
      # lưu vào file log
      # lấy thời gian hiện tại
      now = datetime.now()
      # lấy tên file hiện tại
      filename = os.path.basename(__file__)
      # tạo đường dẫn đến file log theo ngày
      log_file = f'logs/{now.strftime("%Y-%m-%d")}.log'
      # tạo đường dẫn đến thư mục logs
      log_dir = os.path.dirname(log_file)
      # kiểm tra nếu thư mục logs chưa tồn tại thì tạo mới
      if not os.path.exists(log_dir):
         os.makedirs(log_dir)
      # tạo nội dung log
      content = f'{now.strftime("%d/%m/%Y %H:%M:%S")} - {level.upper()} - {message}'
      # lưu vào file log
      with open(log_file, 'a') as f:
         f.write(content + '\n')
      # in ra màn hình
      print(content)
      

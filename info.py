
from collections import Counter

day = '2023-10-20'
with open(f'./logs/{day}.log','r') as f:
   data_logs = f.read()
data_logs = data_logs.split('\n')
# remove empty string
data_logs = [data for data in data_logs if data != '']

print(f'Total: {len(data_logs)}')
# get number of domains   
number_domains = [data.split(' ')[7] for data in data_logs]
# count number of domains
number_domains = Counter(number_domains)
# convert to json
number_domains = dict(number_domains)
# sort by value
number_domains = dict(sorted(number_domains.items(), key=lambda item: item[1], reverse=True))

import matplotlib.pyplot as plt
import numpy as np


plt.bar(range(len(number_domains)), list(number_domains.values()), align='center')
plt.xticks(range(len(number_domains)), list(number_domains.keys()))
plt.xticks(rotation=90)
plt.xlabel('Domain')
plt.ylabel('Number of domains')
plt.title('Number of domains crawled in a day')
# in số lượng domain lên trên mỗi cột
for index, value in enumerate(list(number_domains.values())):
    plt.text(index, value, str(value), ha='center', va='bottom', fontsize=7)

# kéo dài bottom
plt.subplots_adjust(bottom=0.35)
    
plt.savefig(f'./logs/{day}.png')

plt.close()

   

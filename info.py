
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
print(number_domains)

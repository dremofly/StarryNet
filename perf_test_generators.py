"""
帮我补充一个csv文件，示例如下

type,src,des,time
ping,1,2,3
ping,1,3,5
ping,1,4,7
ping,1,5,9

其中第一列都是ping，
第二列的范围从1到60，
第三列的范围也是从1到60。

第三列从1开始递增，同时不能与第二列的数相同，
等到第三列递增完以后，第二列加1，第三列重复递增的过程。
最后一列不断+2
"""
import pandas as pd

data = {'type':[], 'src':[], 'des':[], 'time':[]}
time = 3

sat_numbers = 25
output_file = 'perf_data.csv'
ops = 'perf'

for src in range(1, sat_numbers+1):
    for des in range(1, sat_numbers+1):
        if src != des:
            data['type'].append(ops)
            data['src'].append(src)
            data['des'].append(des)
            data['time'].append(time)
            time += 15

df = pd.DataFrame(data)
df.to_csv(output_file, index=False)

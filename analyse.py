"""
Python使用typer实现一个数据分析函数。数据保存在一个文件夹中，这个文件夹的名称作为typer的输入。
文件夹中，一个测试结果保存在一个文件中。文件名例如。`ping-21-18_1035.txt`。
对于每一个文件的处理步骤：
1. 识别文件名中的第一个数字保存为变量src。
2. 识别文件名中的第二个数字保存为变量dec。
3. 识别文件名中的第三个数字保存为变量time_index。
4. 打开文件，找到文件中的倒数第二行，读取出该行开头packets的数量，该行结尾多少ms。
5. 将以上变量放到一个list中。
对于所有满足要求的文件，执行以上步骤，保存到一个list中。
"""

import os
import re
import typer
import matplotlib.pyplot as plt
import csv
from typing import List
import json

def get_config_from_json(json_file):
    # 从.json文件中读取配置
    with open(json_file, 'r') as file:
        config = json.load(file)

    # 提取需要的参数
    bandwidth = config['satellite link bandwidth ("X" Gbps)']
    loss = config['satellite link loss ("X"% )']
    return bandwidth, loss

def process_file(file_name: str) -> List:
    """Process a single file and return a list of results."""
    results = []

    # Parse numbers from file_name
    numbers = re.findall('\d+', file_name)
    if len(numbers) >= 3:
        src = int(numbers[-3])
        dec = int(numbers[-2])
        time_index = int(numbers[-1])
    else:
        print(f"Filename {file_name} doesn't have enough numbers.")
        return []
    

    # Read the file
    with open(file_name, 'r') as file:
        lines = file.readlines()
        if len(lines) >= 2:
            last_second_line = lines[-2]
            packets = re.search('(\d+) packets', last_second_line)
            if packets:
                packets = int(packets.group(1))
            ms = re.search('(\d+)ms', last_second_line)
            if ms:
                ms = int(ms.group(1))

        else:
            print(f"File {file_name} doesn't have enough lines.")
            return []

        results.append([src, dec, time_index, packets, ms])

    return results


def perf_file(line: str) -> list:
    """process single line of perf result file"""
    data = line.split()
    # print(data)
    duration = float(data[1].split('-')[-1])
    # print(f'duration: {duration}')
    if data[4] == 'MBytes':
        data_size = float(data[3])
    elif data[4] == 'GBytes':
        data_size = float(data[3])*1000
    else: # GBytes
        print(f"data size error {line}")
        exit(0)
    if data[6] == 'Mbits/sec':
        rate = float(data[5])
    elif data[6] == 'Gbits/sec':
        rate = float(data[5])*1000
    else: 
        print(f"rate error: {line}")
        exit(0)

    return [duration, data_size, rate]
    
    

def process_perf(file_name: str) -> list:
    """Process a single file and return a list of results."""
    results = []

    # Parse numbers from file_name
    numbers = re.findall('\d+', file_name)
    if len(numbers) >= 3:
        src = int(numbers[-3])
        dec = int(numbers[-2])
        time_index = int(numbers[-1])
    else:
        print(f"Filename {file_name} doesn't have enough numbers.")
        return []
    

    # Read the file
    with open(file_name, 'r') as file:
        lines = file.readlines()
        if len(lines) >= 2:
            last_second_line = lines[-4]
            last_line = lines[-3]
            s_time, s_data, s_rate = perf_file(last_second_line)
            r_time, r_data, r_rate = perf_file(last_line)

        else:
            print(f"File {file_name} doesn't have enough lines.")
            return []

        results.append([src, dec, time_index, s_time, s_data, s_rate, r_time, r_data, r_rate])

    return results

def process_led(file_name: str) -> list:
    pass
    """
    Python使用typer实现一个数据分析函数。数据保存在一个文件夹中，这个文件夹的名称作为typer的输入。
    文件夹中，一个测试结果保存在一个文件中。文件名例如。`perf-21-18_1035.txt`。
    对于每一个文件的处理步骤：
        1. 识别文件名中的第一个数字保存为变量src。
        2. 识别文件名中的第二个数字保存为变量dec。
        3. 识别文件名中的第三个数字保存为变量time_index。
        4. 打开文件，读取第二行和第一行，保存为line2, line1
        5. 将以上变量放到一个list中。
    对于所有满足要求的文件，执行以上步骤，保存到一个list中。
    """
    results = []
    numbers = re.findall('\d+', file_name)
    if len(numbers) >= 3:
        src = int(numbers[-3])
        dec = int(numbers[-2])
        time_index = int(numbers[-1])
    else:
        print(f"Filename {file_name} doesn't have enough numbers.")
        return []
    print(f"file_name {file_name}, {src}, {dec}, {time_index}")

    # 打开文件并读取倒数第二行
    with open(file_name, 'r') as file:
        lines = file.readlines()
        last_second_line = lines[-3]
        print(last_second_line)
        

        # 从倒数第二行获取TxR后的数值
        match = re.search(r"TxR: (\d+\.?\d*)", last_second_line)
        if match:
            rate = float(match.group(1))

            # 将所有变量添加到列表中
            results.append([src, dec, time_index, rate])
        
    # print(results)
    return results


def plot_results(results: List, bandwidth, loss, operation):
    """Sort the results by ms and plot."""
    # Sort results by ms
    results.sort(key=lambda x: x[4])

    # Prepare data for plotting
    src = [x[0] for x in results]
    dec = [x[1] for x in results]
    time_index = [x[2] for x in results]
    packets = [x[3] for x in results]
    ms = [x[4] for x in results]

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(ms, 'o-')
    plt.title(f'{operation} result with bandwidth={bandwidth} and loss={loss}')
    plt.xlabel('Index')
    if 'perf' in operation:
        plt.ylabel('MBytes/sec')
    else:
        plt.ylabel('ms')
    plt.grid(True)

    # Save figure
    plt.savefig(os.path.join('plots', f'b{bandwidth}-l{loss}-{operation}.png'))
    plt.close()

def plot_perf(results: List, bandwidth, loss, operation):
    """Sort the results by ms and plot."""
    print("plot perf res")
    # Sort results by ms
    results.sort(key=lambda x: x[4])

    # Prepare data for plotting
    src = [x[0] for x in results]
    dec = [x[1] for x in results]
    time_index = [x[2] for x in results]
    # packets = [x[3] for x in results]
    s_rate = [x[5] for x in results]

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(s_rate, 'o-')
    plt.title(f'{operation} result with bandwidth={bandwidth} and loss={loss}')
    plt.xlabel('Index')
    plt.ylabel('Mbits/sec')
    plt.grid(True)
    # plt.show()

    # Save figure
    plt.savefig(os.path.join('plots', f'b{bandwidth}-l{loss}-{operation}.png'))
    plt.close()

def plot_led(results: List):
    results.sort(key=lambda x: x[3])

    # Prepare data for plotting
    src = [x[0] for x in results]
    dec = [x[1] for x in results]
    time_index = [x[2] for x in results]
    # packets = [x[3] for x in results]
    rate = [x[3] for x in results]

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(rate, 'o-')
    plt.title('Results sorted by ms')
    plt.xlabel('Index')
    plt.ylabel('Mbits/sec')
    plt.grid(True)

    # Save figure
    plt.savefig('led.png')
    plt.close()

def write_to_csv(results: List):
    """Write results to a csv file."""
    with open('results.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["src", "dec", "time_index", "packets", "ms"])
        writer.writerows(results)

def write_perf_to_csv(results: List):
    """Write results to a csv file."""
    with open('perf.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["src", "dec", "time_index", "s_time", "s_data", "s_rate", "r_time", "r_data", "r_rate"])
        writer.writerows(results)

def help():
    print("example: python analyse.py '/Volumes/z370.local./NetBackup/nuc9/log/starrynet_perf/log_dir_20231016-16_42_30/starlink-5-5-550-53-grid-LeastDelay-dir1' perfcubic")
    print("example2: python analyse.py '/Volumes/z370.local./NetBackup/nuc9/log/starrynet_perf2/log_dir_20231017-20_17_51/starlink-5-5-550-53-grid-LeastDelay-dir1' perfbbr")

# def main(folder_name: str, operation: str):
def process_one_case(root_path, operation):
    """Process all files in a given folder."""
    all_results = []

    configFile = os.path.join(root_path, 'config.json.nuc2')
    bandwidth, loss = get_config_from_json(configFile)
    print(f"operations: {operation}; bandwidth: {bandwidth}; loss: {loss}")

    folder_name = os.path.join(root_path, 'starlink-5-5-550-53-grid-LeastDelay-dir1')

    for file_name in os.listdir(folder_name):
        if file_name.startswith(operation) and file_name.endswith('.txt'):
            file_path = os.path.join(folder_name, file_name)
            if operation == 'ping':
                results = process_file(file_path)
            elif operation == 'perfcubic':
                results = process_perf(file_path)
            elif operation == 'perfbbr':
                results = process_perf(file_path)
            elif operation == 'led':
                results = process_led(file_path)
            all_results.extend(results)


    # print("show res: ")
    # for res in all_results:
        # print(res)

    # Plot results
    if operation == 'ping':
        if all_results:
            plot_results(all_results, bandwidth, loss, operation)
            write_to_csv(all_results)
    elif operation == 'perfcubic':
        if all_results:
            plot_perf(all_results, bandwidth, loss, operation)
            write_perf_to_csv(all_results)
    elif operation == 'perfbbr':
        if all_results:
            plot_perf(all_results, bandwidth, loss, operation)
            write_perf_to_csv(all_results)
    elif operation == 'led':
        if all_results:
            plot_led(all_results)

def get_test_files(log_path):
    files = []
    for f in os.listdir(log_path):
        files.append(os.path.join(log_path, f))
    return files
        
def process_one_operation(files, operation):
    for f in files:
        print(f'==== process {f} ====')
        # logf = os.path.join(f, 'starlink-5-5-550-53-grid-LeastDelay-dir1')
        process_one_case(f, operation)
    

def main(logpath: str):
    typer.echo(f"logPath {logpath}")
    perf_path = os.path.join(logpath, 'starrynet_perf') 
    perf2_path = os.path.join(logpath, 'starrynet_perf2')
    ping_path = os.path.join(logpath, 'starrynet_ping')
    
    perf_files = get_test_files(perf_path)
    perf2_files = get_test_files(perf2_path)
    ping2_files = get_test_files(ping_path)

    process_one_operation(perf2_files, 'perfbbr')

if __name__ == "__main__":
    typer.run(main)

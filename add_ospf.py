import sys

if len(sys.argv) != 3:
    print("Usage: python script.py <interface-name> <config-file-path>")
    sys.exit(1)

interface_name = sys.argv[1]  # 从命令行参数获取接口名称
config_file_path = sys.argv[2]  # 从命令行参数获取配置文件路径

new_interface_config = f'    interface "{interface_name}" {{\n' \
                       '        type broadcast;     # Detected by default\n' \
                       '        cost 256;\n' \
                       '        hello 1;            # Default hello period 10 is too long\n' \
                       '    };\n'  # 新接口配置

# 读取现有的配置文件
with open(config_file_path, 'r') as file:
    lines = file.readlines()

# 添加新的接口配置到OSPF配置部分
with open(config_file_path, 'w') as file:
    ospf_area_found = False
    interface_block_started = False
    write_new_config = False
    readyToWrite = False
    for line in lines:
        if readyToWrite:
            file.write(new_interface_config)
            interface_block_started = False  # 重置interface块标志
            write_new_config = True
            readyToWrite = False

        if 'area 0 {' in line:
            ospf_area_found = True
        
        # 当我们在area 0块内部时，检测interface块的结束
        if ospf_area_found and 'interface' in line:
            interface_block_started = True
        
        if ospf_area_found and interface_block_started and '};' in line and 'interface' not in line and not write_new_config:
            # 在最后一个接口配置后添加新的接口
            readyToWrite = True
        
        file.write(line)  # 写入原始行或者是新的接口配置

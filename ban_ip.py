import subprocess
import random
import time

sep = '     '

def get_iftop_output():
    try:
        output = subprocess.check_output(['iftop', '-t', '-n', '-s 1', '-L 3'], universal_newlines=True)
        return output
    except subprocess.CalledProcessError as e:
        return ''

def parse_iftop_output(output):
    content_list = []
    up_content = None
    for t in output.split('\n'):
        if '<=' in t:
            content_list.append((
                up_content, t
            ))
        up_content = t
    
    ip_list = []
    for process_content, ip_content in content_list:
        res_process_content = list(filter(None, process_content.split(sep)))
        res_ip_content = list(filter(None, ip_content.split(sep)))

        for res in res_process_content:
            if 'Gb' in res:
                ip_list.append(res_ip_content[0])
                break
            elif 'MB' in res:
                if len(res.split('MB')[0]) > 2:
                    ip_list.append(res_ip_content[0])
                break
    return list(set(ip_list))

def block_ips(ips):
    for ip in ips:
        try:
            subprocess.run(['iptables', '-A', 'OUTPUT', '-d', ip, '-j', 'DROP'], check=True)
            print(f"Blocked IP: {ip}")
        except subprocess.CalledProcessError as e:
            print(f"Error blocking IP {ip}: {e}")

def main():
    while True:
        output = get_iftop_output()
        if not output:
            return
        ip_list = parse_iftop_output(output)
        print(ip_list)
        if ip_list:
            block_ips(ip_list)
        time.sleep(1 + random.random())
        print("\033[H\033[J")

if __name__ == "__main__":
    main()
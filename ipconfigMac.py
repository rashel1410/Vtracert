#!/usr/bin/python

import addresses
import subprocess

def ipconfig_all():

    args = ["ipconfig", "/all"]
    proc = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE)
    data = proc.stdout.read()
    lines = data.split('\r\n')
    return lines
    
def src_mac():

    lines = ipconfig_all()
    macs = []
    cnt=0
    for line in lines:
        if line != '':
            if line[0] == ' ':
                if ': ' in line:
                    key, value = line.split(': ')
                    if key.strip(' .') == 'Physical Address':
                        macs.append(value.strip())

    src_mac = macs[3].split('-')
    out_src = ''
    for part in src_mac:
        out_src += part
    print src_mac
    return out_src
 
def dst_mac():

    ips = []
    lines = ipconfig_all()
    for line in lines:
        if line != '':
            if line[0] == ' ':
                if ': ' in line:
                    if "Default Gateway" in line:
                        key,value = line.split(': ')
                        ips.append(value.strip())
    ip = ips[0]
    args = ["arp", "-a"]
    proc = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE)
    data = proc.stdout.read()
    rows = data.split('\r\n')
    mac = ''
    start = 24
    end = 41
    for row in rows:
        if row != '':
            if ip in row:
                mac = row[start:end]
    src_mac = mac.split('-')
    out_src = ''
    for part in src_mac:
        out_src += part
    return out_src
    
if __name__ == '__main__':
    main()
    
    
# #!/usr/bin/python

# import subprocess

# def main():

    # args = ["ipconfig", "/all"]
    # proc = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE)
    # data = proc.stdout.read()
    # lines = data.split('\r\n')
    # result = {}
    # cnt=0
    # #print data
    # #print lines
    # for line in lines:
        # if line != '':
            # if line[0] == ' ':
                # if ': ' in line:
                    # key, value = line.split(': ')
                    # #print key.strip(' .'),value.strip()
                    # print key.strip(' .')
                    # if key.strip(' .') in result.keys():
                        # result[key.strip(' .')+str(cnt)] = value.strip()
                        # cnt += 1
                    # else:
                        # result[key.strip(' .')] = value.strip()
                        
                    # #print key.strip(' .'),result[key.strip(' .')]
                    
            # #result[result_key] = temp
            
    # # for line in lines:
        # # temp = {}
        # # if line != '':
            # # if line[0] != ' ':
                # # result_key = line.strip()
            # # if line[0] == ' ':
                # # if ': ' in line:
                    # # key, value = line.split(': ')
                    # # #print key.strip(' .'),value.strip()
                    # # temp[key.strip(' .')] = value.strip()
                    # # #print key.strip(' .'),result[key.strip(' .')]
                    # # cnt += 1
            # # result[result_key] = temp
    # #print result
    # #for key,val in result:
    # print len(result.keys())
    # print cnt
    # print '\n'
    # print result
    # print result['Physical Address0']
    # print result['Physical Address1']

# if __name__ == '__main__':
    # main()
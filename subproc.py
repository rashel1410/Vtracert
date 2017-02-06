import subprocess

ip_or_dns = '10.0.0.138'
args = ["tracert", "-d", ip_or_dns]
proc = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE)
data = proc.communicate()[0]
lines = data.split('\r\n')
ip_list = []
for line in lines:
    if line != "":
        if line[0]==' ':    
            ip = line[32:]
            ip = ip.strip(' ')
            ip_list.append(ip)
print ip_list
# ip_list=['172.16.255.254']
# import xml.etree.ElementTree as et
# root = et.Element('list')
# i=0
# for ip in ip_list:
    # title = et.SubElement(root, ('ip'+str(i)))
    # i+=1
    # title.text = ip
    # print ip

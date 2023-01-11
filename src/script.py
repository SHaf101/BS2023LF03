
import sys


def get_number_hosts(eingabe_snm):
    ones = 0b11111111111111111111111111111111
    snm = int(get_formatted_ip(eingabe_snm),2)
    return (ones ^ snm) - 2
    pass


def get_formatted_ip(eingabe_ip:str):
    eingabe_ip = eingabe_ip.split(".")
    ip_formated = ""
    for i in range(len(eingabe_ip)):
        eingabe_ip[i] = format(int(eingabe_ip[i]), '#010b')[2:]
        ip_formated = ip_formated + eingabe_ip[i]
        pass
    return ip_formated
    pass


def get_netid(eingabe_ip, eingabe_snm, binary=0):
    ip_formated = get_formatted_ip(eingabe_ip)
    snm_formated = get_formatted_ip(eingabe_snm)

    netid = int(snm_formated, 2) & int(ip_formated, 2)

    if(binary<=1):
        #print(netid)
        netid = format(netid, '#010b')[2:]
        netid = f"{netid[:8]}.{netid[8:16]}.{netid[16:24]}.{netid[24:]}"

    if(binary == 0):
        netid = netid.split(".")

        for i in range(len(netid)):
            netid[i] = int(netid[i],2)
            pass
        
    return netid
    pass


def get_bcaddress(eingabe_ip, eingabe_snm, binary=0):
    bcaddr = format(get_netid(eingabe_ip, eingabe_snm, binary=2) | get_number_hosts(eingabe_snm)+1, '#010b') [2:]

    if(binary<=1):
        bcaddr = f"{bcaddr[:8]}.{bcaddr[8:16]}.{bcaddr[16:24]}.{bcaddr[24:]}"

    if(binary == 0):
        bcaddr = bcaddr.split(".")
        for i in range(len(bcaddr)):
            bcaddr[i] = int(bcaddr[i],2)
            pass

    return bcaddr
    pass


def print_error(error_code):

    pass


if __name__=="__main__":
    eingabe_ip = sys.argv[1]
    eingabe_snm = sys.argv[2]

    print(f"netid: {get_netid(eingabe_ip, eingabe_snm, binary=1)}")
    print(f"bcaddr: {get_bcaddress(eingabe_ip, eingabe_snm, binary=1)}")
    print(f"hosts: {get_number_hosts(eingabe_snm)}")
    pass

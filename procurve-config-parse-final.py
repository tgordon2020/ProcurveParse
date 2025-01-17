import csv
from netmiko import ConnectHandler
from ttp import ttp
import re
import threading


ttp_template = """
<group name = "interface_cfg">
interface {{ interface}}
   name {{ name | ORPHRASE }}
   dhcp-snooping trust {{ dhcp-snooping | set("True") | default("False") }}
   tagged vlan {{ tagged-vlan }}
   untagged vlan {{ untagged-vlan }}
   trunk {{ trunk-name }} lacp
</group>
"""

def switch_parse(**row):
    try:
        try: # Try SSH first
            
            connect = ConnectHandler(host=row['IP'],
            device_type = "hp_procurve", 
            username = "###",
            password = "###")
            print(f'connected to {row["IP"]}')


        except: # Try Different user
            connect = ConnectHandler(host=row['IP'],
            device_type = "hp_procurve", 
            username = "###",
            password = "###")
            print(f'connected to {row["IP"]}')

        #hostname = row['Switch Location']
        hostname = connect.find_prompt().strip("#")
        device_config = connect.send_command("show run structured")
        lldp_neighbors = connect.send_command("show lldp info remote", use_textfsm=True)
        int_status = connect.send_command("show interfaces brief", use_textfsm=True)
        int_transceivers = connect.send_command("show int transceiver")
        module = connect.send_command("show module")
        poe = connect.send_command("show power-over-ethernet brief")
        connect.disconnect()

                
        ### generate int transceiver dictionary object ###
        trans_regex = r"([A-L0-9]+)\s+([0-1,D,A,3,S,F,P,X,L,R,M,T+]+)\s+(J[0-9]+[A-Z]+)\s+([A-Z0-9]+)\s+([0-9,-]+)"
        trans_after_reg = re.finditer(trans_regex,int_transceivers)
        trans_dict = {}
        for trans in trans_after_reg:
            trans_dict[trans[1]]={"type": trans[2],
                                  "product": trans[3],
                                  "serial": trans[4],
                                  "part": trans[5]}
            

        ### generate interface status dictionary object
        status_dict = {}
        for interface in int_status:
            if "-" in interface['port']:
                int_stat = interface['port'].split("-")[0]
            else:
                int_stat = interface['port']
            status_dict[int_stat]={'type': interface['type'],
                                 'status': interface['status'],
                                 'mode': interface['mode']}


        ### generate POE dictionary object
        poe_regex = r"([A-L0-9]+)\s+[|]\s+(Yes|No)\s+(low|high)\s+(usage|lldp)\s+([0-9\sW]+)\s+([0-9]+.[0-9]+\sW)\s+(Searching|Delivering)\s+([0-4])\s+(off|on)"
        poe_after_reg = re.finditer(poe_regex,poe)
        poe_dict = {}
        for po in poe_after_reg:
            poe_dict[po[1]]={'pwr_enabled':po[2],
                             'pwr_priority':po[3],
                             'pre_detect':po[4],
                             'poe_pwr_rsrvd':po[5],
                             'poe_pwr_draw':po[6],
                             'pwr_status':po[7],
                             'plc_class':po[8]}
            

        ### generate LLDP dictionary object
        lldp_neighbor_dict = {}
        for neighbor in lldp_neighbors:
            lldp_neighbor_dict[neighbor['local_port']]={'neighbor_sysname': neighbor['neighbor_sysname']}
                

        ## Write out config, show module, and show power to text file ##
        with open(f"{hostname}.txt", 'w') as hostconfig:
            hostconfig.write(device_config)
        with open(f"{hostname}-module.txt", 'w') as module_txt:
            module_txt.write(module)
        with open(f"{hostname}-poe.txt", 'w') as poe_txt:
            poe_txt.write(poe)

 

        ## parse interface config to list of dicts ##
        parser = ttp(data=device_config, template=ttp_template)
        parser.parse()
        results = parser.result()[0][0]['interface_cfg']

        ### merge transceiver status into results
        for result in results:
            try:
                result['trans_type']=trans_dict[result['interface']]['type']
            except Exception as e:
                pass


        ### merge inteface status into results
        for result in results:
            try:
                result['int_type']=status_dict[result['interface']]['type']
                result['int_status']=status_dict[result['interface']]['status']
                result['int_mode']=status_dict[result['interface']]['mode']
            except Exception as e:
                pass


        ### merge lldp data into results  ###
        for result in results:
            try:
                result['lldp_neighbor_sysname']=lldp_neighbor_dict[result['interface']]['neighbor_sysname']
            except Exception as e:
                pass

        ### merge POE data into results ###
        for result in results:
            try:
                result['poe_status']=poe_dict[result['interface']]['pwr_status']
                result['poe_pwr_rsrvd']=poe_dict[result['interface']]['pse_pwr_rsrvd']
                result['poe_pwr_draw']=poe_dict[result['interface']]['pd_pwr_draw']
                result['poe_class']=poe_dict[result['interface']]['plc_class']
            except Exception as e:
                pass


        fieldnames = ["interface","name","int_type","int_status","int_mode","tx_kbps","tx_util","rx_kbps","rx_util","untagged-vlan","tagged-vlan","dhcp-snooping","poe_status","poe_alloc","poe_pwr_rsrvd","poe_pwr_draw","poe_class","lldp_neighbor_sysname","lldp_capabilties","trunk-name","trans_type"]
        with open(f"{hostname}-{row['IP']}.csv", "w", newline='') as config_csv:
            print(f"writing out {hostname}.csv ")
            writer = csv.DictWriter(config_csv, fieldnames=fieldnames)
            writer.writeheader()
            for interface in results:
                writer.writerow(interface)

    except Exception as e:
        print(e,row['IP'])
        failures.append(row['IP'])




failures = []

def threadstart():
    threads = []
    with open("switches.csv") as switch_csv:
        rows = csv.DictReader(switch_csv)
        for row in rows:
            node = threading.Thread(target=switch_parse,kwargs=(row))
            node.start()
            threads.append(node)
        for thread in threads:
            thread.join()


if __name__ == "__main__":
    threadstart()
    for failure in failures:
        print(failure)

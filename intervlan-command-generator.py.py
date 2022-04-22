def get_VLANS_info():
    '''Ask user for VLAN information and store it in a dictionary where the key is the VLAN's number and its value is a dictionary containing name, isnative, network, subnet, and gateway. It returns the "vlans" dictionary'''

    vlans = {}

    print('Enter Required VLAN Informations')
    while True:
        v_num = input('VLAN Number: ')

        if v_num == '':
            break

        v_num = int(v_num)

        v_name = input(f'VLAN {v_num} Name: ')

        v_is_native = input(f'VLAN {v_num} is Native (y/n): ')
        # converts the y/n answer to boolean True or False
        v_is_native = str(v_is_native).lower() == 'y'

        v_network = input(f'VLAN {v_num} Network: ')
        v_subnet = input(f'VLAN {v_num} Subnet: ')
        v_def_gateway = input(f'VLAN {v_num} Default Gateway: ')

        print('')

        # appends/stores the new information
        vlans[v_num] = {'name': v_name, 'isnative': v_is_native,
                        'network': v_network, 'subnet': v_subnet, 'def_gateway': v_def_gateway}

    print('\n')
    return vlans


def get_switches_info():
    '''Ask user for Switches information and store it in a dictionary where the key is the switch's name and its value is a dictionary containing  vlans with corresponding access_ports, and trunk port. It returns the "switches" dictionary'''

    switches = {}

    print('========================================')
    print('Enter Required Switch Informations')
    while True:
        s_name = input('Switch Name: ')

        if s_name == '':
            break

        # loop that ask for access ports and corresponding VLAN
        print(f'{s_name} Access Ports:')
        access_ports = {}
        while True:
            # Input can only be one input "f0/0" or in range format such us "f0/0-1" or "f0/0, f0/5-9"
            ports = input('Port/s: ')

            if ports == '':
                break

            v_num = input('  VLAN: ')

            access_ports[int(v_num)] = ports

        trunk_ports = input(f'{s_name} Trunk Ports: ')

        print('')

        switches[s_name] = {
            'access_ports': access_ports, 'trunk_ports': trunk_ports}

    print('========================================')
    print('\n')
    return switches


def get_routers_info():
    '''Ask user for Routers information and store it in a dictionary where the key is the router's name and its value is the trunk port/s. It returns the "switches" dictionary'''

    routers = {}

    print('========================================')
    print('Enter Required Switch Informations')
    while True:
        r_name = input('Router Name: ')

        if r_name == '':
            break

        trunking_port = input('Gigabit Trunking Port: ')

        print('')

        routers[r_name] = trunking_port

    print('========================================')
    print('\n')
    return routers


def gen_com_create_vlans(vlans):
    '''Takes the dictonary of vlans. It then prints out the command for creating the vlans'''

    for v_num in vlans:
        print('vlan', v_num)
        print('name', vlans[v_num]['name'])
        print('exit')


def gen_com_access_ports(access_ports):
    '''Takes the dictionary of access_ports. It then print out the command for enabling the interfaces and sets the interface switchport mode to access with corresponding vlan number'''

    for v_num in access_ports:
        ports = access_ports[v_num]

        # check whether to use the command "interface " or "interface range "
        if '-' not in ports:
            print(f'interface {ports}')
        else:
            print(f'interface range {ports}')

        print('no shutdown')
        print('switchport mode access')
        print(f'switchport access vlan {v_num}')
        print('exit')


def gen_com_trunk_ports(vlans, trunk_ports):
    '''Takes the dictonary of vlans and string of trunk_ports. It then print out the command for enabling the interfaces and sets the interface switchport mode to trunk with corresponding native vlan number'''

    # check whether to use the command "interface " or "interface range "
    if '-' not in trunk_ports:
        print(f'interface {trunk_ports}')
    else:
        print(f'interface range {trunk_ports}')

    print('no shutdown')
    print('switchport mode trunk')

    native_vlan = 1
    for v_num in vlans:
        if vlans[v_num]['isnative']:
            native_vlan = v_num

    if native_vlan != 1:
        print(f'switchport trunk native vlan {native_vlan}')
    print('exit')


def gen_com_router_subint(vlans, ports):
    '''Takes the dictionary of vlan and string of ports. Prints outs the command to enable the port for inter-vlan routing, and create the subinterfaces together with the appropriate vlan information'''

    # check whether to use the command "interface " or "interface range "
    if '-' not in ports:
        print(f'interface {ports}')
    else:
        print(f'interface range {ports}')

    print('no shutdown')
    print('exit')

    # generating command for the subinterfaces
    for v_num in vlans:
        vlan_info = vlans[v_num]
        v_is_native = vlan_info['isnative']
        v_def_gateway = vlan_info['def_gateway']
        v_subnet = vlan_info['subnet']

        print('interface', f'{ports}.{v_num}')
        print('no shutdown')

        command_encaps = f'encapsulation dot1Q {v_num}'
        if v_is_native:
            command_encaps += ' native'
        print(command_encaps)

        print(f'ip address {v_def_gateway} {v_subnet}')
        print('exit')


def gen_complete_command(vlans, switches, routers):
    '''Takes the dictionary of vlans, switches, and routers. It 
    then calls all the gen_com or generate command functions to   
    print out the complete command for setting up Router-on-Stick 
    InterVlan Routing'''

    # prints out the command for the switches
    for sw_name in switches:
        switch_info = switches[sw_name]

        print(f'{sw_name} VLAN set-up command:')
        print('========================================')
        gen_com_create_vlans(vlans)
        gen_com_access_ports(switch_info['access_ports'])

        trunk_ports = switch_info['trunk_ports']
        if trunk_ports != '':
            gen_com_trunk_ports(vlans, trunk_ports)
        print('========================================')
        print('\n')

    # prints out the command for the routers
    for r_name in routers:
        print(f'{r_name} Inter-VLAN set-up command:')
        print('========================================')
        gen_com_router_subint(vlans, routers[r_name])
        print('========================================')
        print('\n')


if __name__ == "__main__":
    print('Leave Blank values to procced next step \n')

    # get the needed informations
    vlans = get_VLANS_info()
    switches = get_switches_info()
    routers = get_routers_info()

    # generates the command
    gen_complete_command(vlans, switches, routers)

# vlans = {10: {'name': 'ADMIN', 'isnative': False, 'network': '192.168.10.0', 'subnet': '255.255.255.0', 'def_gateway': '192.168.10.1'}, 20: {'name': 'STAFF', 'isnative': False, 'network': '192.168.20.0',
#                                                                                                                                                  'subnet': '255.255.255.0', 'def_gateway': '192.168.20.1'}, 30: {'name': 'NATIVE', 'isnative': True, 'network': '192.168.30.0', 'subnet': '255.255.255.0', 'def_gateway': '192.168.30.1'}}
# switches = {'SW1': {'access_ports': {}, 'trunk_ports': 'F0/1-2, G0/1'}, 'SW2': {'access_ports': {10: 'F0/1',
#                                                                                                      20: 'F0/2'}, 'trunk_ports': 'G0/1'}, 'SW3': {'access_ports': {10: 'F0/1', 20: 'F0/2'}, 'trunk_ports': 'G0/2'}}
# routers = {'R1': 'G0/0/0'}
   
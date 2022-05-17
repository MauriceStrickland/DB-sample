#!/usr/bin/env python3
# File name: perforce_user_management.py
# Description: Drive the application by utilizing various classes and methods
# Author: Maurice Strickland
# Date: 2022-05-16

"""
Driver module for the script.

"""

import time
import sys
import argparse
from perforce_ldap import PerforceLdap
from perforce import Perforce
from email_alerts import P4Email

#servers to search
SERVER_LIST = ['serverA', 'serverB']


def is_modify_mode(conf):
    """
    Determine the mode of the script.

    This method takes the command line argument to determine
    if the script will run in read-only or modify mode. The
    default mode is read-only.

    :param conf: The arg passed from the command line
    :returns: Returns True for modify mode or False for read-only
    :rtype: bool

    .. literalinclude:: ../perforce_user_management/perforce_user_management.py
            :linenos:
            :language: python
            :lines: 42, 62-73

    .. warning:: Running the script in modify mode will remove departed users
        along with their clients from Perforce.
    """
    if conf.mode == 'r':
        print ("Read-Only")
        return False
    elif conf.mode == 'm':
        print ("Modify")
        return True
    else:
        print (f"{conf.mode} is not a valid argument")
        print ("USAGE:")
        print ("--mode r (read-only)")
        print ("--mode m (modify)")
        exit(3)

def create_csv(user_list, server):
    """
    Creates a CSV file of all the departed users along with
    details.

	The CSV created will be saved to the current directory
	with the file name of "PerforceDepartedeparted_users[CurrentDate].csv"


    :param userList: (list): A list of departed perforce_users
    :param server: Name of the current Perforce server

    .. literalinclude:: ../perforce_user_management/perforce_user_management.py
            :linenos:
            :language: python
            :lines: 75, 92-106
    """
    header = 'Name,Username,Email,Manager\'s email,LDAP Name'
    try:
        file_name = ('PerforceDeparteDepartedUsers-'+server+time.strftime("%d.%m.%Y")+'.csv')
        save_file = open(file_name, 'a')
        save_file.write(header + '\n')

        for user in user_list:
            new_line = user.to_csv_string()
            save_file.write(new_line + '\n')
        save_file.close()
        print (f'Saved to {file_name}')

    except IOError as excep:
        print ("Error creating csv")
        print (excep)

def generate_departed_user_list(user_list, ldap_con):
    """
    Creates and returns a list of departed perforce users

    :param user_list: All perforce users
    :param ldap_con: PerforceLdap instance

    :returns: List of all departed user in perforce

    .. literalinclude:: ../perforce_user_management/perforce_user_management.py
            :linenos:
            :language: python
            :lines: 108, 122-130
    """
    departed_users = []
    for user in user_list:
        user_info = ldap_con.search_ldap_for_user(user)

		#If the user is in the "de-provisoned group"
        if user_info:
            departed_users.append(user_info)

    return departed_users

def run_removals(d_users, perf, server):
    """
    This method starts the process of removing users.

    First it will email the users manager if the manager's
    email is valid. Then it will call the
    :func:`~perforce.Perforce.remove_perforce_user` method.

    :param d_users: List of all departed users in Perforce
    :param perf: perforce instance
    :param server: the current perforce server

    .. literalinclude:: ../perforce_user_management/perforce_user_management.py
            :linenos:
            :language: python
            :lines: 132, 149-155
    """

    for user in d_users:
        if '@' in user.manager_email:
            user.email_users_manager(server)

        #Removes user from Perforce
        perf.remove_perforce_user(user)

def get_args():
    """
        Retrieves the command line argument (if there is one).

        :returns: The script's running mode (r (read-only) or m (modify))

        .. literalinclude:: ../perforce_user_management/perforce_user_management.py
                :linenos:
                :language: python
                :lines: 157, 168-175
    """
    parser = argparse.ArgumentParser(description='Set the mode of the script')
    parser.add_argument('--mode',\
            metavar='FLAG',\
            help='read-only (r) or modify (m)',\
            default='r')

    conf = parser.parse_args()
    return conf

def main():
    """
    The main function of the script.

    Makes all the calls to connect to perforce and the ldap server.
    Creates the list of departed perforce_users.

    .. literalinclude:: ../perforce_user_management/perforce_user_management.py
            :linenos:
            :language: python
            :lines: 177, 190-216
    """
  
    log_file_name = 'PUM_Log_'+time.strftime("%d.%m.%Y")+'.txt'
    sys.stdout = open(log_file_name,'w') # Saves console output to a file
    
    perforce_users = []    # List of all perforce users
    departed_users = []     # List of all departed perforce users

    print (time.strftime("%d/%m/%Y") +' '+ time.strftime("%H:%M:%S"))  # For log purposes

    p4_ldap = PerforceLdap()
    perf = Perforce()
    p4_email = P4Email()

    p4_ldap.bind_to_ldap()
    for server in SERVER_LIST:

        perf.perforce_login(server)
        perforce_users = perf.get_perforce_users()

        departed_users = generate_departed_user_list(perforce_users, p4_ldap)

        if is_modify_mode(get_args()):
            run_removals(departed_users, perf, server)

        create_csv(departed_users, server)
        p4_email.email_admins(perf.get_perforce_server_name(), departed_users)
        perf.disconnect_from_perforce()


        departed_users *= 0    # Clears lists before running on next server
        perforce_users *= 0

    p4_ldap.unbind_from_ldap()

if __name__ == "__main__":
    main()

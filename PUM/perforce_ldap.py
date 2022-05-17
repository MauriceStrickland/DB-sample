#!/usr/bin/env python3
# File name: perforce_ldap.py
# Description: Supports all ldap interactions for the application
# Author: Maurice Strickland
# Date: 2022-05-16

"""Module for ldap server interactions"""

import sys
import os
import ldap
import ldap_helper
from perforce_user import PerforceUser

class PerforceLdap(object):
    """
    Connects to Ldap server to query the deprovisioned users.

    Methods:
        bind_to_ldap: Makes connection with ldap server.

        search_ldap_for_user: Searches for users in the deprovisioned
        user group.

        search_ldap_for_manager: Searches for manager.

        unbind_from_ldap: Stops connection from ldap server.
    """
    def __init__(self):
        """Sets the ldap server name and login credentials"""

        self.server = 'ldap://1.1.1.1'
        self.username = ('service_acct')
        self.password = os.environ.get('SVC_PWD')
        self.ldap = ''

    def bind_to_ldap(self):
        """
        Connects to the LDAP server

        .. literalinclude:: ../perforce_user_management/perforce_ldap.py
            :linenos:
            :language: python
            :lines: 55, 65-76
        """

        self.ldap = ldap.initialize(self.server)
        self.ldap.protocol_version = ldap.VERSION3
        self.ldap.set_option(ldap.OPT_REFERRALS, 0)

        try:
            self.ldap.simple_bind_s(self.username, self.password)
       
        except ldap.INVALID_CREDENTIALS:
            print ('Incorrect credentials!')
            sys.exit()
        except ldap.LDAPError as exception:
            print (exception)

    def search_ldap_for_user(self, user):
        """
        Searches the LDAP server for users in the "deprovisioned" group.

        .. literalinclude:: ../perforce_user_management/perforce_ldap.py
            :linenos:
            :language: python
            :lines: 78, 88-106
        """
		#Prepare the ldap search. Only Searches the Deprovisioned group
        basedn = "OU=Accounts,OU=Disabled"
        ldap_filter = "AccountName=%s" % user['User']
        attrs = ['mail', 'manager', 'AccountName', 'name']

        # Convert results into something easily usable.
        raw_res = self.ldap.search_s(basedn, ldap.SCOPE_SUBTREE, ldap_filter, attrs)
        res = ldap_helper.get_search_results(raw_res)

        if not res:
            return False
        for record in res:
            attr = record.get_attributes()

            if len(attr.keys()) == 4:
                return self.set_reg_user(attr, user)

            else:
                return self.set_other_user(attr, user)


    def set_reg_user(self, attr, user):
        """
        Creates a PerforceUser given all the user information
        has been found

        :param attr: the users attributes from the ldap query
        :param user: the users information from perforce

        .. literalinclude:: ../perforce_user_management/perforce_ldap.py
            :linenos:
            :language: python
            :lines: 109, 122-130
        """
        p4_user = PerforceUser()
        p4_user.name = user['FullName']
        p4_user.username = user['User']
        p4_user.last_access = user['Access']
        p4_user.email = ''.join(attr['mail'])
        p4_user.ldap_name = ''.join(attr['name']).replace(',', '.')
        p4_user.manager_email, p4_user.manager = \
                (self.search_ldap_for_manager(attr))
        return p4_user

    def set_other_user(self, attr, user):
        """
        Creates a PerforceUser given not all the user information
        has been found

        :param attr: the users attributes from the ldap query
        :param user: the users information from perforce

        .. literalinclude:: ../perforce_user_management/perforce_ldap.py
            :linenos:
            :language: python
            :lines: 132, 145-164
        """
        p4user = PerforceUser()
        p4user.name = user['FullName']
        p4user.username = user['User']

        if 'mail' in attr.keys():
            p4user.email = ''.join(attr['mail'])
        else:
            p4user.email = 'No email in LDAP. Perforce email: %s' % \
                    (user['Email'].replace(',', ' '))

        p4user.ldap_name = ''.join(attr['name']).replace(',', '.')

        if 'manager' in attr.keys():
            p4user.manager_email, p4user.manager = \
                        (self.search_ldap_for_manager(attr))
        else:
            p4user.manager_email, p4user.manager = \
                        ('No manager email', 'No manager in ldap')

        return p4user

    def search_ldap_for_manager(self, user_attr):
        """
        Searches LDAP for a user's managers details

        .. literalinclude:: ../perforce_user_management/perforce_ldap.py
            :linenos:
            :language: python
            :lines: 166, 176-189
        """

        # Manager Search Criteria
        basedn = ''.join(user_attr['manager'])
        ldap_filter = "cn=*"
        attrs = ['mail', 'displayname']

        raw_res = self.ldap.search_s(basedn, ldap.SCOPE_SUBTREE, ldap_filter, attrs)
        res = ldap_helper.get_search_results(raw_res)

        for record in res:
            attr = record.get_attributes()
            if len(attr.keys()) != 2:
                return 'No managers email', ''.join(attr['displayname'])
            else:
                return ''.join(attr['mail']), ''.join(attr['displayname'])

    def unbind_from_ldap(self):
        """
        Disconnects from the LDAP server

        .. literalinclude:: ../perforce_user_management/perforce_ldap.py
            :linenos:
            :language: python
            :lines: 191, 201-202
        """

        self.ldap.unbind()
        print ("Unbound")
		
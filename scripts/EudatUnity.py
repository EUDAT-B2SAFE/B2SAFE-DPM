#!/usr/bin/env python

import sys
import argparse
import json
import logging
import logging.handlers
import urllib2
import ConfigParser
import base64
import pprint
from pprint import pformat

logger = logging.getLogger('EUDATUnity')

class EudatUnity:

    def __init__(self, conf, parent_logger=None):
        """initialize the object"""

        if (parent_logger): self.logger = parent_logger
        else: self.logger = logging.getLogger('eudat')

        confkeys = ['host', 'username', 'password', 'carootdn']
        missingp = []
        for key in confkeys:
            if not key in conf: missingp.append(key)
        if len(missingp) > 0:
            self.logger.warning('missing parameters: ' + pformat(missingp))
        self.conf = conf


    def queryUnity(self, sublink):
        """
        :param argument: url to unitydb with entity (entityID) or group (groupName)
        :return:
        """
        auth = base64.encodestring('%s:%s' % (self.conf['username'], self.conf['password']))[:-1]
        header = "Basic %s" % auth
        url = self.conf['host'] + sublink
        request = urllib2.Request(url)
        request.add_header("Authorization",header)
        try:
            response = urllib2.urlopen(request)
        except IOError:
            self.logger.error("Wrong username or password", "", exc_info=1)
            sys.exit(1)

        assert response.code == 200
        json_data = response.read()
        response_dict = json.loads(json_data)

        return response_dict


    def getRemoteUsers(self):
        """
        Get the remote users' list
        """

        self.logger.info("Getting list of users from eudat db...")
        # get list of all groups in Unity
        group_list = self.queryUnity("group/%2F")

        final_list = {}
        list_member = []
        users_map = {}
        attribs_map = {}
        for member_id in group_list['members']:
            user_record = self.queryUnity("entity/"+str(member_id))
            attr_list = {}
            self.logger.debug("Query: entity/" + str(member_id) +
                              ", user record: " + pformat(user_record))
            identity_types = {}
            for identity in user_record['identities']:
                self.logger.debug("identity['typeId'] = " + identity['typeId'])
                self.logger.debug("identity['value'] = " + identity['value'])
                identity_types[identity['typeId']] = identity['value']

            if "userName" in identity_types.keys():
                list_member.append(identity_types['userName'])
                users_map[member_id] = identity_types['userName']
            elif "identifier" in identity_types.keys():
                list_member.append(identity_types['identifier'])
                users_map[member_id] = identity_types['identifier']
            else:
                list_member.append(str(member_id))
                users_map[member_id] = str(member_id)

            if "persistent" in identity_types.keys():
                # Here we build the DN: the way to build it could change
                # in the future.
                userDN = (self.conf['carootdn'] + '/CN=' + identity['value'] 
                          + '/CN=' + users_map[member_id])
                attr_list['DN'] = [userDN]

            attribs_map[users_map[member_id]] = attr_list

        self.eudatMembersAttrlist = attribs_map
        final_list['members'] = list_member
        final_list['attributes'] = attribs_map

        # Query and get list of all user from Groups in Unity
        list_group = {}
        for group_name in group_list['subGroups']:
            member_list = self.queryUnity("group"+group_name)
            user_list = []
            for member_id in member_list['members']:
                user_list.append(users_map[member_id])
            list_group[group_name[1:]] = user_list

        final_list['groups'] = list_group

        return final_list
        
        
    def getUser(self, persistentId):
        """
        get the user's attributes given the persistenId
        """
        self.logger.debug("Getting attribute DN for user " + persistentId)
        for user, attrs in self.eudatMembersAttrlist.iteritems():
            self.logger.debug("Checking user " + user)
            if 'DN' in attrs.keys():
                self.logger.debug("Checking DN " + attrs['DN'][0])
                if persistentId in attrs['DN'][0]:
                    return attrs['DN'][0]
                    
        return None
        


def _getConfOption(config, section, option):
    """
    get the options from the configuration file
    """

    if (config.has_option(section, option)):
        return config.get(section, option)
    else:
        sys.exit(1)


if __name__ == '__main__':
    
        parser = argparse.ArgumentParser(description='EUDATUnity')
        parser.add_argument('conf', default='eudatunity.conf',
                            help='path to the configuration file')
        parser.add_argument('--getdn', nargs=1,
                            help = 'get the DN of a user, given' 
                                 + ' the persitent identifier')

        _args = parser.parse_args()

        config = ConfigParser.RawConfigParser()
        config.readfp(open(_args.conf))
        logfilepath = _getConfOption(config, 'Common', 'logfile')
        loglevel = _getConfOption(config, 'Common', 'loglevel')

        ll = {'INFO': logging.INFO, 'DEBUG': logging.DEBUG, \
              'ERROR': logging.ERROR, 'WARNING': logging.WARNING}
        logger.setLevel(ll[loglevel])

        rfh = logging.handlers.RotatingFileHandler(logfilepath,
                                                   maxBytes=4194304,
                                                   backupCount=1)
        formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
        rfh.setFormatter(formatter)
        logger.addHandler(rfh)

        b2accessParam = {k:v for k,v in config.items('B2ACCESS')}
        eudatUnity = EudatUnity(b2accessParam, logger)      
        remote_users_list = eudatUnity.getRemoteUsers()
        if (_args.getdn):
            print eudatUnity.getUser(_args.getdn[0])
        else:
            print json.dumps(remote_users_list, sort_keys = True, indent = 4)

        sys.exit(0)

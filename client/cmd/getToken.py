#!/usr/bin/env python

import urllib2
import argparse
import ConfigLoader
import os
import json

def get_token(args, config):
    '''Get an authentication token from the DPM'''
    username = args.username.strip()
    password = args.password.strip()

    url = '%s://%s:%s%s' % (config.SectionMap('DpmServer')['scheme'],
                            config.SectionMap('DpmServer')['hostname'],
                            config.SectionMap('DpmServer')['port'],
                            config.SectionMap('DpmServer')['tokenpath'])

    authinfo = urllib2.HTTPPasswordMgrWithDefaultRealm()
    authinfo.add_password(None, url, username, password)
    handler = urllib2.HTTPBasicAuthHandler(authinfo)
    myopener = urllib2.build_opener(handler)
    urllib2.install_opener(myopener)

    print 'Getting token from URI: %s' % url

    try:
        response = urllib2.urlopen(url)
    except IOError, e:
        print "Problem contacting the server"
        print "Exception: ", e
        print "Headers: ", e.headers
        raise

    json_data = json.loads(response.read())

    if os.path.isfile(config.SectionMap('DpmServer')['tokenfile']):
        print 'Updating token in %s' % config.SectionMap('DpmServer')['tokenfile']
    else:
        print 'Creating token in %s' % config.SectionMap('DpmServer')['tokenfile']

    with open(config.SectionMap('DpmServer')['tokenfile'], 'w') as fout:
        json_output = {}
        json_output['token'] = json_data['token']
        json_output['created'] = json_data['created']
        json_output['expiry'] = json_data['expiry']
        fout.write(json.dumps(json_output))
        fout.write("\n")
        fout.close()
    print 'Finished'


def main():
    parser = argparse.ArgumentParser(description="Generate and store an authentication token")
    parser.add_argument("email", help="email address")
    parser.add_argument("password", help="DPM password")
    parser.add_argument("config", help="Path to configuration file")
    args = parser.parse_args()
    config = ConfigLoader.ConfigLoader(args.config)
    get_token(args, config)


if __name__ == '__main__':
    main()

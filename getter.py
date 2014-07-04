#!/usr/bin/env python

VERSION = '0.1'
ESL_FILE = '_esl.list'
##########################
def parse_esl_file(esl_fh):
    esl_fh.seek(0) # just in case
    #
    yaml_str = ''
    yaml_done = False
    #
    markdown_str = ''
    #
    while True:
        line = esl_fh.readline()
        if not line:
            break
        #
        if "~~##~~" in line:
            yaml_done = True
            continue
        #
        if not yaml_done:
            yaml_str += line
        else:
            markdown_str += line
    #
    return yaml_str, markdown_str

##########################
if __name__ == "__main__":
    import sys
#    import re
    import datetime
    import time
    import yaml
    import httplib
    import urllib2
    #
    print "Welcome to getter.py v. %s !\n" % VERSION
    #
    try:
        urls_fh = open(ESL_FILE, 'r')
    except IOError:
        sys.exit("Couldn't open URLs file: %s, exiting...\n" % ESL_FILE)
    #
    while True:
        line = urls_fh.readline()
        if not line:
            break
        #
        tmp = line.strip().split() # title alternative_url real_url
        if len(tmp) < 3:
            sys.exit("Found incomplete line, exiting...\n")
        #
        print "Found entry: %s: %s and %s" % (tmp[0], tmp[1], tmp[2])
        #
        print "Getting URL %s " % tmp[1]
        request = urllib2.Request(tmp[1])
        #
        try: 
            esl_fh = urllib2.urlopen(request)
        except urllib2.HTTPError, e:
            print 'HTTPError = %s, next entry!' % str(e.code)
            continue
        except urllib2.URLError, e:
            print 'URLError = %s, next entry!' % str(e.reason)
            continue
        except httplib.HTTPException, e:
            print 'HTTPException, next entry!'
            continue
        except Exception:
            import traceback
            print 'generic exception: %s, next entry!' % traceback.format_exc()
            continue
        #
        print "Parsing..."
        yaml_str, markdown_str = parse_esl_file(esl_fh)
        yaml_obj = yaml.load(yaml_str)





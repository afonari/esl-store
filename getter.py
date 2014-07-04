#!/usr/bin/env python

VERSION = '0.1'
ESL_FILE = '_esl.list'
##########################
def parse_esl_file(esl_fh):
    import markdown
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
    md = markdown.markdown(markdown_str, safe_mode='remove')
    return yaml_str, md

##########################
if __name__ == "__main__":
    import sys
#    import re
    import datetime
    import time
    import yaml
    import httplib
    import urllib2
    import sqlite3
    #
    print "Welcome to getter.py v. %s !\n" % VERSION
    #
    con = sqlite3.connect('esl-store.sqlite')
    cur = con.cursor()
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
        if len(tmp) < 2:
            sys.exit("Found incomplete line: '%s', exiting...\n" % line)
        #
        print "Found entry: %s: %s" % (tmp[0], tmp[1])
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
        yaml_str, md_str = parse_esl_file(esl_fh)
        #
        try:
            yaml_obj = yaml.load(yaml_str)
        except yaml.YAMLError, exc:
            print 'YAML.load error %s, next entry!' % str(exc)
            continue
        #
        print yaml_obj
        if not 'title' in yaml_obj.keys() or len(yaml_obj['title']) == 0:
            print "title empty, next entry!"
            continue
        #
        cur.execute( 'SELECT * FROM products WHERE title=?', (yaml_obj['title'],) )
        rows = cur.fetchall()
        #
        if len(rows) == 0:
            print 'No product with such entry: %s, next entry!' % yaml_obj['title']
            continue
        #
        #   Checking other entries
        #
        if not 'home_url' in yaml_obj.keys() or len(yaml_obj['home_url']) == 0:
            print "home_url empty, next entry!"
            continue
        #
        if not 'latest_download' in yaml_obj.keys() or len(yaml_obj['latest_download']) < 2:
            print "latest_download empty or incomplete, next entry!"
            continue
        #
        if not 'logo_url' in yaml_obj.keys() or len(yaml_obj['logo_url']) == 0:
            print "logo_url empty or incomplete, next entry!"
            continue
        #
        if not 'version' in yaml_obj.keys() or len(yaml_obj['version']) == 0:
            print "version empty, next entry!"
            continue
        #
        if not 'release_date' in yaml_obj.keys() or len(yaml_obj['release_date']) == 0:
            print "release_date empty, next entry!"
            continue
        #
        if not 'license' in yaml_obj.keys() or len(yaml_obj['license']) == 0:
            print "license empty, next entry!"
            continue
        #
        print md
        print rows





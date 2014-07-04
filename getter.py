#!/usr/bin/env python

VERSION = '0.1'
ESL_FILE = '_esl.list'
DATE_FORMATTER_STRING = "%d-%m-%Y"

##########################
def parse_esl_file(esl_fh):
    import markdown
    import yaml
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
    #
    try:
        yaml_obj = yaml.load(yaml_str)
    except yaml.YAMLError, exc:
        print 'WARNING: YAML.load error %s!' % str(exc)
        return 1, 0, 0
    #
    return 0, yaml_obj, md
#
def check_release_date(yaml_obj, release_date_key, date_formatter_str):
    import datetime
    #
    if not release_date_key in yaml_obj.keys():
        print "WARNING: %s is non-existent!" % release_date_key
        return 1, 0
    #
    date_str = yaml_obj[release_date_key]
    try:
        ret = datetime.datetime.strptime(date_str, date_formatter_str).date()
    except ValueError:
        print "WARNING: Couldn't parse the date in date_str: %s!" % date_str
        return 1, 0
    #
    return 0, ret
#
def check_url(url_str):
    import httplib
    import urllib2
    #
    if url_str is None:
        print 'WARNING: url_str is None!'
        return 1, 0
    #
    request = urllib2.Request(url_str)
    #
    try:
        url_fh = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
        print 'WARNING: HTTPError = %s!' % str(e.code)
        return 1, 0
    except urllib2.URLError, e:
        print 'WARNING: URLError = %s!' % str(e.reason)
        return 1, 0
    except httplib.HTTPException, e:
        print 'WARNING: HTTPException!'
        return 1, 0
    except ValueError:
        print "WARNING: Couldn't parse the URL!"
        return 1, 0
    except Exception:
        import traceback
        print 'generic exception: %s, next entry!' % traceback.format_exc()
        return
    #
    return 0, url_fh
#
def check_homepage(yaml_obj, homepage_key):
    #
    if not homepage_key in yaml_obj.keys():
        print "WARNING: %s is non-existent!" % homepage_key
        return 1, 0
    #
    homepage_url = yaml_obj[homepage_key]
    ierr, homepage_fh = check_url(homepage_url)
    if ierr == 1:
        return 1, 0
    #
    return 0, homepage_url
#
def check_latest_download(yaml_obj, latest_download_key):
    #
    if not latest_download_key in yaml_obj.keys():
        print "WARNING: %s is non-existent!" % latest_download_key
        return 1, 0
    #
    latest_download = yaml_obj[latest_download_key]
    if not isinstance(latest_download, list):
        print "WARNING: %s is non a list of 2 entries!" % latest_download
        return 1, 0
    #
    if len(latest_download[0]) == 0:
        print "WARNING: latest_download title (1st index) is empty!"
        return 1, 0
    #
    ierr, download_fh = check_url(latest_download[1])
    if ierr == 1:
        return 1, 0
    #
    return 0, latest_download
#
##########################
if __name__ == "__main__":
    import sys
#    import re
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
        if len(tmp[0]) == 0:
            print "WARNING: title empty, next entry!"
            continue
        #
        if len(tmp[1]) == 0:
            print "WARNING: URL empty, next entry!"
            continue
        #
        title = tmp[0]
        cur.execute( 'SELECT * FROM products WHERE title=?', (title,) )
        rows = cur.fetchall()
        #
        if len(rows) == 0:
            print 'WARNING: No product with the title: %s found in the DB, next entry!' % title
            continue
        #
        print "Getting URL %s " % tmp[1]
        #
        ierr, esl_fh = check_url(tmp[1])
        if ierr == 1:
            print "Next entry!"
        #
        print "Parsing..."
        ierr, yaml_obj, md_str = parse_esl_file(esl_fh)
        #
        print yaml_obj
        if not 'title' in yaml_obj.keys() or yaml_obj['title'] != title:
            print "WARNING: title nonexistent or not the same as in ESLs file, next entry!"
            continue
        #
        #   Checking other entries
        #
        ierr, homepage_url = check_homepage(yaml_obj, 'homepage')
        if ierr == 1:
            print "Next entry!"
            continue
        #
        ierr, latest_download = check_latest_download(yaml_obj, 'latest_download')
        if ierr == 1:
            print "Next entry!"
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
        ierr, release_date = check_release_date(yaml_obj, 'release_date', DATE_FORMATTER_STRING)
        if ierr == 1:
            print "Next entry!"
            continue
        #
        if not 'license' in yaml_obj.keys() or len(yaml_obj['license']) == 0:
            print "license empty, next entry!"
            continue
        #
        #
        # Ready to update!
        #
        cur.execute('UPDATE products SET homepage = ?, version = ?, release_date = ?, license = ?, description = ? WHERE title = ?', (homepage_url, yaml_obj['version'], release_date, yaml_obj['license'], md_str, yaml_obj['title']))
        con.commit()
        print md_str
        print rows





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
def check_url(url, download=False, local_name='', keep_fh=False):
    from urllib2 import urlopen, URLError, HTTPError
    import os
    #
    try:
        f = urlopen(url)
        #
        # Open our local file for writing
        if download == True:
            with open(local_name, "wb") as local_file:
                local_file.write(f.read())
    #
    #handle errors
    except HTTPError, e:
        print "WARNING: HTTP Error:", e.code, url
        if keep_fh: return 1, 0
        else: return 1
    except URLError, e:
        print "WARNING: URL Error:", e.reason, url
        if keep_fh: return 1, 0
        else: return 1
    #
    if keep_fh: return 0, f
    else: return 0
#

def check_homepage(yaml_obj, homepage_key):
    #
    if not homepage_key in yaml_obj.keys():
        print "WARNING: %s is non-existent!" % homepage_key
        return 1, 0
    #
    homepage_url = yaml_obj[homepage_key]
    ierr = check_url(homepage_url)
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
        print "WARNING: %s is not a list!" % latest_download
        return 1, 0
    #
    if len(latest_download[0]) == 0:
        print "WARNING: latest_download title (1st index) is empty!"
        return 1, 0
    #
    ierr = check_url(latest_download[1])
    if ierr == 1:
        return 1, 0
    #
    return 0, latest_download
#
def check_interfaced(yaml_obj, interfaced_with_key, cur, title):
    #
    if not interfaced_with_key in yaml_obj.keys():
        print "WARNING: %s is non-existent!" % interfaced_with_key
        return 1
    #
    interfaced_with = yaml_obj[interfaced_with_key]
    if not isinstance(interfaced_with, list):
        print "WARNING: %s is non a list!" % interfaced_with_key
        return 1
    #
    for val in interfaced_with:
        if val is None or len(val) == 0:
            continue
        #
        if val == title:
            print 'WARNING: Cannot interface product with itself!'
            continue
        #
        cur.execute( 'SELECT * FROM products WHERE title=?', (val,) )
        rows = cur.fetchall()
        #
        if len(rows) == 0:
            print 'WARNING: No product with the title: %s found in the DB for interfacing!' % val
            continue
        #
        cur.execute('INSERT INTO interface VALUES(?,?)', (title, val))
    #
    return 0
#
def check_version(yaml_obj, version_key):
    #
    if (version_key not in yaml_obj.keys()) or (yaml_obj[version_key] is None) or (len(yaml_obj[version_key])==0):
        print "WARNING: %s is non-existent!" % version_key
        return 1
    else:
        return 0, yaml_obj[version_key]
#
def check_license(yaml_obj, license_key):
    #
    if (license_key not in yaml_obj.keys()) or (yaml_obj[license_key] is None) or (len(yaml_obj[license_key])==0):
        print "WARNING: %s is non-existent!" % license_key
        return 1
    else:
        return 0, yaml_obj[license_key]
#
def check_logo(yaml_obj, logo_key, path_to_save):
    import imghdr
    #
    if (logo_key not in yaml_obj.keys()) or (yaml_obj[logo_key] is None) or (len(yaml_obj[logo_key])==0):
        print "WARNING: %s is non-existent!" % logo_key
        return 1, 0
    #
    logo_url = yaml_obj[logo_key]
    ierr, logo_fh = check_url(logo_url, keep_fh=True)
    if ierr == 1:
        return 1
    #
    logo_type = imghdr.what('', h=logo_fh.read())
    if (logo_type is not 'png') or (logo_type is not 'gif'):
        print "WARNING: Logo should be png or jpg!"
        return 1
    #
    return 0
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
        print "Getting data for %s product from URL %s " % (title, tmp[1])
        #
        ierr, esl_fh = check_url(tmp[1], keep_fh=True)
        if ierr == 1:
            print "Next entry!"
        #
        print "Parsing YAML and Markdown..."
        ierr, yaml_obj, md_str = parse_esl_file(esl_fh)
        #
        print yaml_obj
        #
        if ('title' not in yaml_obj.keys()) or (yaml_obj['title'] != title):
            print "WARNING: title nonexistent or not the same as in ESLs file, next entry!"
            continue
        #
        #   Checking other product attributes
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
        ierr = check_logo(yaml_obj, 'logo_url', 'ESLs/'+title)
        if ierr == 1:
            print "Next entry!"
            continue
        #
        ierr, version = check_version(yaml_obj, 'version')
        if ierr == 1:
            print "Next entry!"
            continue
        #
        ierr, release_date = check_release_date(yaml_obj, 'release_date', DATE_FORMATTER_STRING)
        if ierr == 1:
            print "Next entry!"
            continue
        #
        ierr, license = check_license(yaml_obj, 'license')
        if ierr == 1:
            print "Next entry!"
            continue
        #
        check_interfaced(yaml_obj, 'interfaced_with', cur, title)
        #
        #
        # Ready to update!
        #
        cur.execute('UPDATE products SET homepage = ?, latest_download = ?, version = ?, release_date = ?, license = ?, description = ? WHERE title = ?', (homepage_url, yaml_obj['version'], release_date, yaml_obj['license'], md_str, yaml_obj['title']))
        con.commit()
        print md_str
        print rows





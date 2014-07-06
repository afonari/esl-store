#!/usr/bin/env python

VERSION = '0.1'
ESL_FILE = '_esl.list'
DATE_FORMATTER_STRING = "%d-%m-%Y"
BLEACH_ALLOWED_TAGS = ['p','em','strong','ol','ul','li']

##########################
def parse_esl_file(esl_fh):
    import markdown
    import yaml
    import re
    import bleach
    #
    yaml_str = ''
    yaml_done = False
    #
    markdown_str = ''
    #
    p = re.compile("^\s*~~##~~\s*$")
    #
    while True:
        line = esl_fh.readline()
        if not line:
            break
        #
        # print line
        if p.match(line):
            yaml_done = True
            continue
        #
        if not yaml_done:
            yaml_str += line
        else:
            markdown_str += line
    #
    md = bleach.clean( markdown.markdown(markdown_str, safe_mode='remove'), tags=BLEACH_ALLOWED_TAGS, strip=True )
    #
    # print md
    # print yaml_str
    try:
        yaml_obj = yaml.load(yaml_str)
    except yaml.YAMLError, exc:
        print 'WARNING: YAML.load error %s!' % str(exc)
        return 1, 0, 0
    #
    if yaml_obj is None:
        print 'WARNING: yaml_obj is None!'
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
        ret = datetime.datetime.strptime(date_str, date_formatter_str)
    except ValueError:
        print "WARNING: Couldn't parse the date in date_str: %s!" % date_str
        return 1, 0
    #
    return 0, ret
#
def check_url(url, read=False):
    from urllib2 import urlopen, URLError, HTTPError
    import os
    #from io import BytesIO
    from StringIO import StringIO
    #
    file_io = None
    #
    try:
        f = urlopen(url)
        #
        # Open our local file for writing
        if read == True:
            file_io = StringIO(f.read())
    #
    #handle errors
    except HTTPError, e:
        print "WARNING: HTTP Error:", e.code, url
        return 1, 0
    except URLError, e:
        print "WARNING: URL Error:", e.reason, url
        return 1, 0
    #
    return 0, file_io
#
def check_homepage(yaml_obj, homepage_key):
    #
    if not homepage_key in yaml_obj.keys():
        print "WARNING: %s is non-existent!" % homepage_key
        return 1, 0
    #
    homepage_url = yaml_obj[homepage_key]
    ierr, dummy = check_url(homepage_url)
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
    ierr, dummy = check_url(latest_download[1])
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
        print "WARNING: %s is not a list!" % interfaced_with_key
        return 1
    #
    cur.execute('DELETE FROM interface WHERE product_title = ?', (title,))
    #
    for val in interfaced_with:
        if val is None or len(val) == 0:
            continue
        #
        if val == title:
            print 'WARNING: Cannot interface product with itself!'
            continue
        #
        cur.execute( 'SELECT title FROM products WHERE title=? COLLATE NOCASE', (val,) )
        rows = cur.fetchall()
        #
        if len(rows) == 0:
            print 'WARNING: No product with the title: %s found in the DB for interfacing!' % val
            continue
        #
        val = rows[0][0] # fix the case for letters in the title
        cur.execute('INSERT INTO interface VALUES(?,?)', (title, val))
    #
    return 0
#
def check_tags(yaml_obj, tags_key, cur, title):
    #
    if not tags_key in yaml_obj.keys():
        print "WARNING: %s is non-existent!" % tags_key
        return 1
    #
    tags = yaml_obj[tags_key]
    if not isinstance(tags, list):
        print "WARNING: %s is not a list!" % tags_key
        return 1
    #
    cur.execute('DELETE FROM products_tags WHERE product_title = ?', (title,))
    #
    for val in tags:
        if val is None or len(val) == 0:
            continue
        #
        cur.execute( 'SELECT * FROM tags WHERE title=? COLLATE NOCASE', (val,) )
        rows = cur.fetchall()
        #
        if len(rows) == 0:
            print 'WARNING: No tag (%s) found in the "tags" table!' % val
            continue
        #
        cur.execute( 'SELECT * FROM products WHERE title=? COLLATE NOCASE', (val,) )
        rows = cur.fetchall()
        #
        cur.execute('INSERT INTO products_tags VALUES(?,?)', (title, val))
    #
    return 0
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
def get_image_size(fhandle):
    import struct
    import imghdr
    #
    #fhandle = open(fname, 'rb')
    head = fhandle.read(24)
    if len(head) != 24:
        return 1, 0, 0, ''
    #
    img_type = imghdr.what(None, fhandle.getvalue())
    if img_type == 'png':
        check = struct.unpack('>i', head[4:8])[0]
        if check != 0x0d0a1a0a:
            return 1, 0, 0, ''
        width, height = struct.unpack('>ii', head[16:24])
    elif img_type == 'jpeg':
        try:
            fhandle.seek(0) # Read 0xff next
            size = 2
            ftype = 0
            while not 0xc0 <= ftype <= 0xcf:
                fhandle.seek(size, 1)
                byte = fhandle.read(1)
                while ord(byte) == 0xff:
                    byte = fhandle.read(1)
                ftype = ord(byte)
                size = struct.unpack('>H', fhandle.read(2))[0] - 2
            # We are at a SOFn block
            fhandle.seek(1, 1)  # Skip `precision' byte.
            height, width = struct.unpack('>HH', fhandle.read(4))
        except Exception: #IGNORE:W0703
            return 1, 0, 0, ''
    else:
        return 1, 0, 0, ''
    #
    return 0, width, height, img_type
#
def check_logo(yaml_obj, logo_key, path_to_save):
    import os
    #
    if (logo_key not in yaml_obj.keys()) or (yaml_obj[logo_key] is None) or (len(yaml_obj[logo_key])==0):
        print "WARNING: %s is non-existent!" % logo_key
        return 1, 0
    #
    logo_url = yaml_obj[logo_key]
    ierr, logo_fh = check_url(logo_url, read=True)
    if ierr == 1:
        return 1
    #
    logo_fh.seek(0)
    #with open(path_to_save, "wb") as local_file:
    #    local_file.write(logo_fh.read())
    #
    ierr, w, h, file_type = get_image_size(logo_fh)
    #
    if ierr == 1:
        print "WARNING: Logo (%s) was not recognized to be of 'png' or 'jpeg' type" % logo_url
        return 1
    #
    if not file_type in ['png', 'jpeg']:
        print "WARNING: Logo is of type: %s; should be png or jpeg!" % file_type
        return 1
    #
    if w > 200 or h > 100:
        print "WARNING: Logo is too large (%f x %f) should be 200px X 100px max!" % (w, h)
        return 1
    #
    logo_fh.seek(0)
    with open(path_to_save, "wb") as local_file:
        local_file.write(logo_fh.read())
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
        cur.execute( 'SELECT rowid, title FROM products WHERE title=?', (title,) )
        rows = cur.fetchall()
        #
        if len(rows) == 0:
            print 'WARNING: No product with the title: %s found in the DB, next entry!' % title
            continue
        #
        title_id = rows[0][0]
        #
        print "Getting data for %s product from URL %s " % (title, tmp[1])
        #
        ierr, esl_fh = check_url(tmp[1], read=True)
        if ierr == 1:
            print "Next entry!"
            continue
        #
        # print esl_fh
        print "Parsing YAML and Markdown..."
        esl_fh.seek(0)
        ierr, yaml_obj, md_str = parse_esl_file(esl_fh)
        #
        # print yaml_obj
        #
        # TODO check better for the empty keys and stuff!
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

        check_tags(yaml_obj, 'tags', cur, title)
        #
        ierr = check_logo(yaml_obj, 'logo_url', 'ESLs-logos/'+str(title_id))
        if ierr == 1:
            print "Next entry!"
            continue
        #
        # Ready to update!
        #
        cur.execute('UPDATE products SET homepage = ?, latest_download = ?, latest_download_url = ?, version = ?, release_date = ?, license = ?, description = ? WHERE title = ?', (homepage_url, latest_download[0], latest_download[1], version, release_date, license, md_str, title))
        con.commit()
        print "Committed !!"
        print "Next entry!\n"
        #
        #print md_str
        #print rows
        #




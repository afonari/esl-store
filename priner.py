#!/usr/bin/env python

VERSION = '0.1'
TAG_DIV = '<a class="__CLASS__" href="__TAG_NAME__.html">__TAG_NAME_SPACE__</a>'
INTERMEDIATE_DIV = '</div><hr />'
PRODUCT_LOGO_DIV = '<a class="product_icon" href="__PRODUCT_NAME__.html"><div style="width: 200px;height: 100px;"><img src="__PRODUCT_LOGO__" /></div>__PRODUCT_NAME_SPACE__</a>'
LOGOS_FOLDER = 'ESLs-logos/'
PRODUCT_DATA_DIV = '<h3>__PRODUCT_NAME__</h3><div style="width: 200px;height: 100px;display: inline;"><img src="__PRODUCT_LOGO__" /></div>__PRODUCT_DESC__<br />'

def generate_tags(tags_fetch_all, tag_current=''):
    ret_str = '<div class="tags">'
    #
    for row in tags_fetch_all:
        tag = row[0]
        #
        tag_ = re.sub(' ', '_', tag)
        div_tag = re.sub('__TAG_NAME__', tag_, TAG_DIV)
        div_tag = re.sub('__TAG_NAME_SPACE__', tag, div_tag)
        #
        if tag == tag_current:
            div_tag = re.sub('__CLASS__', 'tag_current', div_tag)
        else:
            div_tag = re.sub('__CLASS__', 'tag', div_tag)
        #
        ret_str += div_tag
    #
    ret_str += '</div>'
    return ret_str
#
def generate_product_data(product):
    import re
    #
    print product
    ret_str = '<div class="product_data">'
    #
    title, url, latest_download, latest_download_url, version, release_date, license, description, cecam_wiki = product
    ret_str += re.sub('__PRODUCT_NAME__', title, PRODUCT_DATA_DIV)
    #ret_str += re.sub('__PRODUCT_NAME__', title, PRODUCT_DATA_DIV)
    #
    return

if __name__ == "__main__":
    import sys
    import re
    import sqlite3
    #
    print "Welcome to printer.py v. %s !\n" % VERSION
    #
    with open ("header.tpl", "r") as myfile:
        header=myfile.read()
    #
    with open ("bottom.tpl", "r") as myfile:
        bottom=myfile.read()
    #
    con = sqlite3.connect('esl-store.sqlite')
    cur = con.cursor()
    #
    # TAGS
    #
    cur.execute( 'SELECT * FROM tags')
    rows = cur.fetchall()
    #
    # tag page generations
    rows.insert(0, (u'All',))
    print rows
    for row in rows:
        tag = row[0]
        tag_ = re.sub(' ', '_', tag)
        #
        f = open(tag_+'.html', 'w')
        f.write(header)
        #
        f.write(generate_tags(rows, tag_current=tag))
        #
        f.write("\n")
        f.write(INTERMEDIATE_DIV)
        #
        # PRODUCTS on the TAGS pages
        #
        f.write('<div class="product_holder">')
        if row[0] == 'All':
            cur.execute( 'SELECT DISTINCT product_title FROM products_tags' )
        else:
            cur.execute( 'SELECT product_title FROM products_tags WHERE tag = ?', (row[0],) )
        #
        products = cur.fetchall()
        #
        for product in products:
            cur.execute( 'SELECT rowid FROM products WHERE title = ?', (product[0],) )
            tmp = cur.fetchall()
            rowid = tmp[0][0]
            # print rowid
            #
            product_ = re.sub(' ', '_', product[0])
            div_product = re.sub('__PRODUCT_NAME__', product_, PRODUCT_LOGO_DIV)
            div_product = re.sub('__PRODUCT_NAME_SPACE__', product, div_product)
            div_product = re.sub('__PRODUCT_LOGO__', LOGOS_FOLDER+str(rowid), div_product)
            f.write(div_product)
            #f.write("\n")
        #
        #f.write('<br style="clear:both"/>')
        f.write('</div>')
        f.write(bottom)
        #print products
        #sys.exit(0)
        f.close()
#####################################
    print "Done with the 'TAGS' pages, continuing with 'PRODUCTS' pages..."
    print ""
    #
    # First generate links with tags
    cur.execute( 'SELECT * FROM tags')
    rows = cur.fetchall()
    #
    # product page generations
    rows.insert(0, (u'All',))
    tags_str = generate_tags(rows)
    #
    # print tags_str
    #
    cur.execute( 'SELECT * FROM products')
    rows = cur.fetchall()
    #
    for row in rows:
        generate_product_data(row)
        #product = row[0]
        #product_ = re.sub(' ', '_', tag)
        #
        f = open(product_+'.html', 'w')
        f.write(header)
        f.write("\n")
        #f.write()










    #
#!/usr/bin/env python

VERSION = '0.1'
TAG_DIV = '<a class="__CLASS__" href="__TAG_NAME__.html">__TAG_NAME_SPACE__</a>'
# INTERMEDIATE_DIV = '</div><hr />'
PRODUCT_LOGO_DIV = '<a class="product_icon" href="__PRODUCT_NAME__.html"><div style="width: 200px;height: 100px;"><img src="__PRODUCT_LOGO__" /></div>__PRODUCT_NAME_SPACE__</a>'
LOGOS_FOLDER = 'ESLs-logos/'
#
PRODUCT_DATA_DIV =  '<h3>__PRODUCT_NAME__</h3><div style="width: 200px;height: 100px;display: inline;"><img src="__PRODUCT_LOGO__" /></div>__PRODUCT_DESC__'
PRODUCT_DATA_DIV += '<div class="product_misc_data"><strong>Interfaced with:</strong> __PRODUCT_INTERFACED__<br />'
PRODUCT_DATA_DIV += '<strong>Homepage:</strong> <a href="__PRODUCT_HOMEPAGE__">__PRODUCT_HOMEPAGE__</a><br />'
PRODUCT_DATA_DIV += '__CECAM_WIKI_HOLDER__'
PRODUCT_DATA_DIV += '<strong>License:</strong> __PRODUCT_LICENSE__<br />'
PRODUCT_DATA_DIV += '<strong>Version:</strong> __PRODUCT_VERSION__<br />'
PRODUCT_DATA_DIV += '<strong>Release date:</strong> __PRODUCT_DATE__<br />'
PRODUCT_DATA_DIV += '<strong>Download the latest version:</strong> <a href="__PRODUCT_DOWNLOAD_URL__">__PRODUCT_DOWNLOAD__</a></div>'
#
PRODUCT_INTERFACE = '<a href="__PRODUCT__.html">__PRODUCT_SPACE__</a>'

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
        elif tag == 'ESL-Supported':
            div_tag = re.sub('__CLASS__', 'tag_esl_supported', div_tag)
        else:
            div_tag = re.sub('__CLASS__', 'tag', div_tag)
        #
        ret_str += div_tag
    #
    ret_str += '</div>'
    return ret_str
#
def generate_product_data(product, cur):
    import re
    import datetime
    #
    # print product
    ret_str = '<div class="product_data">'
    #
    rowid, title, url, latest_download, latest_download_url, version, release_date, license, desc, cecam_wiki_url, last_update = product
    title_ = re.sub(' ', '_', title)
    #
    # 'Interfaced with' goes 1st
    cur.execute( 'SELECT product1 FROM interface WHERE product = ?', (title,) )
    rows = cur.fetchall()
    #
    if len(rows) != 0:
        interface_str = ''
    else:
        interface_str = 'Nothing'
    #
    for i in range(len(rows)):
        row_ = re.sub(' ', '_', rows[i][0])
        tmp_ = re.sub('__PRODUCT__', row_, PRODUCT_INTERFACE)
        tmp_ = re.sub('__PRODUCT_SPACE__', rows[i][0], tmp_)
        interface_str += tmp_
        #
        if i+1 is not len(rows): # if the element is last, we dont need comma
            interface_str += ", "
    #
    release_date = datetime.datetime.fromtimestamp(release_date).strftime('%d-%b-%Y')

    product_div = re.sub('__PRODUCT_NAME__', str(title), PRODUCT_DATA_DIV)
    product_div = re.sub('__PRODUCT_LOGO__', LOGOS_FOLDER+str(rowid), product_div)
    product_div = re.sub('__PRODUCT_INTERFACED__', interface_str, product_div)
    product_div = re.sub('__PRODUCT_HOMEPAGE__', str(url), product_div)
    #
    if cecam_wiki_url is not None:
        product_div = re.sub('__CECAM_WIKI_HOLDER__', '<strong>ESL wiki-page:</strong> <a href="%s">%s</a><br />' % (cecam_wiki_url, cecam_wiki_url), product_div)
    else:
        product_div = re.sub('__CECAM_WIKI_HOLDER__', '', product_div)
    #
    product_div = re.sub('__PRODUCT_LICENSE__', str(license), product_div)
    product_div = re.sub('__PRODUCT_VERSION__', str(version), product_div)
    product_div = re.sub('__PRODUCT_DATE__', release_date, product_div)
    product_div = re.sub('__PRODUCT_DOWNLOAD_URL__', str(latest_download_url), product_div)
    product_div = re.sub('__PRODUCT_DOWNLOAD__', str(latest_download), product_div)
    product_div = re.sub('__PRODUCT_DESC__', str(desc), product_div)
    ret_str += product_div
    #
    ret_str += '</div>'
    return ret_str, title_

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
    rows.insert(len(rows), (u'ESL-Supported',))
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
        f.write("<hr />")
        f.write("\n")
        #
        # PRODUCTS on the TAGS pages
        #
        f.write('<div class="product_holder">')
        if row[0] == 'All':
            cur.execute( 'SELECT title FROM products' )
        elif row[0] == 'ESL-Supported':
            cur.execute( 'SELECT title FROM products WHERE cecam_wiki_url != ?', ('',)  )
        else:
            cur.execute( 'SELECT product_title FROM products_tags WHERE tag = ?', (row[0],) )
        #
        products = cur.fetchall()
        # print products
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
        #
        f.write('</div>')
        f.write("\n")
        f.write(bottom)
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
    rows.insert(len(rows), (u'ESL-Supported',))
    tags_str = generate_tags(rows)
    #
    # print tags_str
    #
    cur.execute( 'SELECT rowid, * FROM products')
    rows = cur.fetchall()
    #
    for row in rows:
        product_div, title_ = generate_product_data(row, cur)
        #
        f = open(title_+'.html', 'w')
        f.write(header)
        f.write(tags_str)
        f.write("\n")
        f.write("<hr />")
        f.write("\n")
        f.write(product_div)
        f.write("\n")
        f.write(bottom)
        f.close()










    #
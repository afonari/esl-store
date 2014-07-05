#!/usr/bin/env python

VERSION = '0.1'
TAG_DIV = '<a class="__CLASS__" href="__TAG_NAME__.html" __HOVER__>__TAG_NAME_SPACE__</a>'
INTERMEDIATE_DIV = '<br class="clearBoth" /><hr />'
PRODUCT_DIV = '<div class="product"><a href="__PRODUCT_NAME__.html">__PRODUCT_NAME_SPACE__</a></div>'

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
    cur.execute( 'SELECT * FROM tags')
    rows = cur.fetchall()
    #
    # tag page generations
    for row in rows:
        row_ = re.sub(' ', '_', row[0])
        f = open(row_+'.html', 'w')
        f.write(header)
        #
        for row1 in rows:
            row1_ = re.sub(' ', '_', row1[0])
            div_row1 = re.sub('__TAG_NAME__', row1_, TAG_DIV)
            div_row1 = re.sub('__TAG_NAME_SPACE__', row1, div_row1)
            #
            if row1_ == row_:
                div_row1 = re.sub('__CLASS__', 'tag_current', div_row1)
                div_row1 = re.sub('__HOVER__', '', div_row1)
            else:
                div_row1 = re.sub('__CLASS__', 'tag', div_row1)
                div_row1 = re.sub('__HOVER__', 'onMouseOver="this.style.background-color=\'#0F0\'" onMouseOut="this.style.background-color=\'#00F\'"', div_row1)
            #
            f.write(div_row1)
        #
        f.write(INTERMEDIATE_DIV)
        cur.execute( 'SELECT product_title FROM products_tags WHERE tag = ?', (row[0],) )
        products = cur.fetchall()
        #
        for product in products:
            product_ = re.sub(' ', '_', product[0])
            div_product = re.sub('__PRODUCT_NAME__', product_, PRODUCT_DIV)
            div_product = re.sub('__PRODUCT_NAME_SPACE__', product, div_product)
            f.write(div_product)
        #
        f.write(bottom)
        #print products
        #sys.exit(0)
        f.close()

    #
    #
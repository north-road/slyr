#!/usr/bin/env python

"""
Dumps the contents of an ESRI .style file to a set of binary blobs
"""

import pyodbc
import os

driver = [d for d in pyodbc.drivers() if 'Microsoft Access' in d][0]


def clean_symbol_name_for_file(symbol_name):
    """nasty little funtion to remove some characters which will choke"""
    file_name = symbol_name
    file_name = file_name.replace('/', '_')
    file_name = file_name.replace('>', '_')
    file_name = file_name.replace('\\', '_')
    file_name = file_name.replace('?', '_')
    file_name = file_name.replace('*', '_')
    return file_name

styles=[('fill','fill'),('line','line'),('marker','marker'),('fill105','fill')]
for (s,type) in styles:
    fill_style_db = os.path.join('styles',s + '.style')

    con = pyodbc.connect('DRIVER={};DBQ={}'.format(driver,fill_style_db))

    # grab fill symbols
    cur = con.cursor()
    SQL = 'SELECT name, object FROM [{} Symbols];'.format(type)
    rows = cur.execute(SQL).fetchall()
    cur.close()
    con.close()

    for r in rows:
        symbol_name=r[0]
        blob=r[1]

        out_filename=clean_symbol_name_for_file(symbol_name) + '.bin'
        file = os.path.join('styles',s+'_bin',out_filename)

        print(file)
        with open(file, 'wb') as e:
            e.write(blob)

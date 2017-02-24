#!/usr/bin/env python

"""
Dumps the contents of an ESRI .style file to a set of binary blobs
"""

import pyodbc
import os

def clean_symbol_name_for_file(symbol_name):
    """nasty little funtion to remove some characters which will choke"""
    file_name = symbol_name
    file_name = file_name.replace('/', '_')
    file_name = file_name.replace('>', '_')
    file_name = file_name.replace('\\', '_')
    file_name = file_name.replace('?', '_')
    file_name = file_name.replace('*', '_')
    return file_name

fill_style_db = 'styles/fill.style'
driver = '{Microsoft Access Driver (*.mdb, *.accdb)}' # may need to be tweaked

con = pyodbc.connect('DRIVER={};DBQ={}'.format(driver,fill_style_db))

# grab fill symbols
cur = con.cursor()
SQL = 'SELECT name, object FROM [Fill Symbols];'
rows = cur.execute(SQL).fetchall()
cur.close()
con.close()

for r in rows:
    symbol_name=r[0]
    blob=r[1]

    out_filename=clean_symbol_name_for_file(symbol_name) + '.bin'
    file = os.path.join('styles','fill_bin',out_filename)

    print(file)
    with open(file, 'wb') as e:
        e.write(blob)

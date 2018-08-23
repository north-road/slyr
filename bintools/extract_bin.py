#!/usr/bin/env python

"""
Dumps the contents of an ESRI .style file to a set of binary blobs
"""

import pyodbc
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file", help="style file to extract",nargs='?')
args = parser.parse_args()
print(args.file)

try:
    driver = [d for d in pyodbc.drivers() if 'Microsoft Access' in d][0]
except AttributeError:
    driver = None


def clean_symbol_name_for_file(symbol_name):
    """nasty little function to remove some characters which will choke"""
    file_name = symbol_name
    file_name = file_name.replace('/', '_')
    file_name = file_name.replace('>', '_')
    file_name = file_name.replace('\\', '_')
    file_name = file_name.replace('?', '_')
    file_name = file_name.replace('*', '_')
    return file_name

if not args.file:
    styles=[('fill','fill'),('line','line'),('marker','marker'),('fill105','fill')]
    styles=[(os.path.join('styles',s[0] + '.style'),s[1]) for s in styles]
    output_path = os.path.join('styles', 'bin')
else:
    styles=[(args.file, 'fill'),(args.file, 'line'),(args.file, 'marker')]
    output_path, _ = os.path.split(args.file)

for (fill_style_db,type) in styles:
    if driver is not None:
        # windows
        con = pyodbc.connect('DRIVER={};DBQ={}'.format(driver,fill_style_db))
    else:
        # linux
        con = pyodbc.connect('DRIVER=/usr/lib64/libmdbodbc.so;DBQ={}'.format(fill_style_db))

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
        file = os.path.join(output_path,out_filename)

        print(file)
        with open(file, 'wb') as e:
            e.write(blob)


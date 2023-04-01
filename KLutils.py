import os
import re
import glob
import shutil

import datetime
import numpy as np

import PyPDF2
from num2words import num2words



def str_to_date(s):
    return datetime.datetime.strptime(s, "%d.%m.%Y").date()

def line_to_no(line):
    inv_no = None
    try:
        inv_no = int(line.split(' ')[2])
    except(ValueError):
        inv_no = int(line.split(' ')[4])
    return inv_no

def invoice_to_data(invoicestr):
    inv_no = None
    date   = None
    mass   = None
    cost   = None
    client = None
    benef  = None
    for it,line in enumerate(invoicestr.splitlines()):
        if ('INVOICE No' in line):
            if inv_no is None:
                inv_no = line_to_no(line)
            if date is None:
                date   = str_to_date(line.split(' ')[-1])
        if ('TOTAL:' in line):
            if ('GRAND' in line):
                continue
            line = line.replace('.','')
            line = line.replace(',','.')
            ints = re.findall(r'\d+',line)
            if mass is None:
                mass = int(ints[0])
            if cost is None:
                cost = float(ints[1]+'.'+ints[2])
        if ('Messrs' in line):
            if client is None:
                client = invoicestr.splitlines()[it+1]+invoicestr.splitlines()[it+2]
        #
    if   ('ELVALHALCOR' in invoicestr):
        benef = 'Elval'
    elif ('SYMETAL' in invoicestr):
        benef = 'Symetal'
    elif ('International Trade S.A.' in invoicestr):
        if ('Quickpack' in client):
            benef = 'Symetal'
        else:
            benef = 'Elval'
    
    return inv_no, date, mass, cost, client, benef


def pdf_to_txt(pdfFileObj):
    pdfReader = PyPDF2.PdfReader(pdfFileObj)
    
    txt = ''
    for pageObj in pdfReader.pages:
        txt += pageObj.extract_text()
    
    return txt

def pdf_to_data(pdfFileObj):
    return invoice_to_data( pdf_to_txt(pdfFileObj) )

def valuesay(value):
    valuesayen = num2words(value, lang='en')
    valuesaypl = num2words(value, lang='pl')
    
    # change polish sign to latex code
    # only small letters are required
    valuesaypl = valuesaypl.replace('ą',r'\k{a}')
    valuesaypl = valuesaypl.replace('ę',r'\k{e}')
    valuesaypl = valuesaypl.replace('ł', r'{\l}')
    valuesaypl = valuesaypl.replace('ć',r'{\'c}')
    valuesaypl = valuesaypl.replace('ń',r'{\'n}')
    valuesaypl = valuesaypl.replace('ó',r'{\'o}')
    valuesaypl = valuesaypl.replace('ś',r'{\'s}')
    valuesaypl = valuesaypl.replace('ź',r'{\'z}')
    valuesaypl = valuesaypl.replace('ż',r'{\.z}')
    
    return valuesayen,valuesaypl

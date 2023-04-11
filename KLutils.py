import os
import re
import glob
import shutil

import datetime
import numpy as np

import PyPDF2
from num2words import num2words

import jinja2
from jinja2 import Template



def str_to_date(s):
    return datetime.datetime.strptime(s, "%d.%m.%Y").date()


def line_to_no(line):
    inv_no = None
    try:
        inv_no = int(line.split(' ')[2])
    except(ValueError):
        inv_no = int(line.split(' ')[4])
    return inv_no


def valuesay(value):
    value_rounded = round( value )
    value_decimal = round( 10.0*(value-value_rounded) )
    
    valuesayen = num2words(value_rounded, lang='en')
    valuesayen = valuesayen + '& {:2d}/100'
    valuesaypl = num2words(value_rounded, lang='pl')
    valuesayen = valuesayen + 'i {:2d}/100'
    
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


def invoice_to_data(invoicestr,eur_per_t=None):
    # variable initialization
    inv_no = None
    date   = None
    mass   = None
    cost   = None
    client = None
    benef  = None
    
    # read data from invoice (converted to string)
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
    
    # calculate provision value
    if eur_per_t is None:
        eur_per_t = { 'Elval'   : 40.0,
                      'Symetal' : 60.0 }
        eur_per_t = eur_per_t[benef]
    value = mass * eur_per_t / 1000
    
    # convert value to string
    valuesayen, valuesaypl = valuesay(value)
    value = '{:10.2f}'

    # save data to excel
    data = {'klno'       : klno,
            'invno'      : inv_no,
            'date'       : date,
            'bname'      : benef_name[benef],
            'vatno'      : benef_vatno[benef],
            'mass'       : mass/1000,
            'value'      : value,
            'valuesaypl' : valuesaypl,
            'valuesayen' : valuesayen,
            'eurpert'    : eur_per_t }
    
    return data


def pdf_to_txt(pdfFileObj):
    pdfReader = PyPDF2.PdfReader(pdfFileObj)
    
    txt = ''
    for pageObj in pdfReader.pages:
        txt += pageObj.extract_text()
    
    return txt


def pdf_to_data(pdfFileObj,eur_per_t=None):
    return invoice_to_data( pdf_to_txt(pdfFileObj), eur_per_t=eur_per_t )


def data_to_tex(data,template_file='/content/KL-Nord/KL_invoice_template.tex'):
    template = ''
    with open(template_file, 'r') as f:
        template = f.read()

    j2_template = Template(template)

    with open('{}.tex'.format(data['klno']), "w") as tex_file:
        tex_file.write(j2_template.render(data))

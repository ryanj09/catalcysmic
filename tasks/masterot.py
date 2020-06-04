"""Tasks related to the MASTER survey."""
import json
import os
import re
from decimal import Decimal

from astrocats.catalog.photometry import PHOTOMETRY
from astrocats.catalog.utils import jd_to_mjd, pbar
from astropy.io.ascii import read
from bs4 import BeautifulSoup

from astrocats.cataclysmic.cataclysmic import CATACLYSMIC

#DO NOT RUN! This code is currently not functional.#
def do_masterot(catalog):
    """Import list of MASTER events."""
    task_str = catalog.get_current_task_str()
    mast_url = 'http://observ.pereplet.ru/MASTER_OT.html'
    html = catalog.load_url(mast_url, os.path.join(
        catalog.get_current_task_repo(), 'MASTEROT/transients.html'))
    if not html:
        return
    bs = BeautifulSoup(html, 'html5lib')
    print(bs)#Beautifulsoup does not work the wepage is not neatly divided by columns like everywhere else
#the web page has no dividers in bs so basically bs cann't work for this webpage.
#code idea: use the following:
#	variable = 0
#	for line in f:
#        s = re.search(r'(?<=Y=\s)\d+',line)#need to figure out how to seacrch for ----
#		 if s:
#			 variable = variable + 1
#	 if variable = 1: read contents and add to list
#	 if variable = 2: end function
# alternative
#with open ('lorem.txt', 'rt') as myfile:  # Open file lorem.txt for reading text
#    for myline in myfile:                 # For each line, read it to a string 
#        if myline == ---:
#			 variable = variable + 1
    trs = bs.find('table').findAll('td')
    for tri, tr in enumerate(pbar(trs, task_str)):
        name = ''
#        ra = ''
#        dec = ''
        discdate = ''
        type = ''
        mag = ''
#        atellink = '' talk to professor about adding this and what to say if there is a gcn rather than atel
#        sdsslink = ''
        comment = '' #store to check if entry is a CV later
        if tri == 1:
            continue
        tds = tr.findAll('td')
#        atex = 0
        for tdi, td in enumerate(tds):
            if tdi == 1:

                name = catalog.add_entry(td.text.strip().replace("?","_"))
#                    atellink = td.find('a')
#                    atex = 1
#                    if atellink:
#                        atellink = atellink['href']
#                    else:
#                        atellink = ''
#            if tdi == 3:
#                ra = td.text
#            if tdi == 4:
#                dec = td.text
            if tdi == 2:
                discdate = td.text.replace('', '/')
            if tdi == 3:
                type = td.text
            if tdi == 4:
                mag = td.text
#            if tdi == 7:
#                sdsslink = td.find('a')
#                if sdsslink:
#                    sdsslink = sdsslink['href']
#                else:
#                    sdsslink = ''
            if tdi == 9:
                comment = td.text
        if 'CV' in type or 'CV?' in type:
            sources = [catalog.entries[name].add_source(
                url=mast_url, name='MAST-CV Transients')]
            typesources = sources[:]
            if atellink:
                sources.append(
                    (catalog.entries[name]
                     .add_source(name='ATel ' +
                                 atellink.split('=')[-1], url=atellink)))
#            if typelink:
#                typesources.append(
#                    (catalog.entries[name]
#                     .add_source(name='ATel ' +
#                                 typelink.split('=')[-1], url=typelink)))
            sources = ','.join(sources)
            typesources = ','.join(typesources)
            catalog.entries[name].add_quantity(CATACLYSMIC.ALIAS, name, sources)
            catalog.entries[name].add_quantity(
                CATACLYSMIC.DISCOVER_DATE, discdate, sources)
#            catalog.entries[name].add_quantity(CATACLYSMIC.RA, ra, sources,
#                                               u_value='floatdegrees')
#            catalog.entries[name].add_quantity(CATACLYSMIC.DEC, dec, sources,
#                                               u_value='floatdegrees')
            catalog.entries[name].add_quantity(
                CATACLYSMIC.VISUAL_MAG, mag, sources)
#            for ct in claimedtype.split('/'):
#                if ct != 'Unk':
#                    catalog.entries[name].add_quantity(CATACLYSMIC.CLAIMED_TYPE, ct,
#                                                       typesources)

        else:
            pass

    catalog.journal_entries()
    return

#talk to professor about light curves data
#def do_asas_atels(catalog):
#    """Import LCs exposed in ASASSN Atels."""
#    with open('/root/better-atel/atels.json') as f:
#        ateljson = json.load(f)
#    for entry in ateljson:
#        if ('asas-sn.osu.edu/light_curve' in entry['body'] and
#                'Cataclysmic' in entry['subjects']):
#            matches = re.findall(r'<a\s+[^>]*?href="([^"]*)".*?>(.*?)<\/a>',
#                                 entry['body'], re.DOTALL)
#            lcurl = ''
#            objname = ''
#            for match in matches:
#                if 'asas-sn.osu.edu/light_curve' in match[0]:
#                    lcurl = match[0]
#                    objname = re.findall(
#                        r'\bASASSN-[0-9][0-9].*?\b', match[1])
#                    if len(objname):
#                        objname = objname[0]
#            if objname and lcurl:
#                name, source = catalog.new_entry(
#                    objname, srcname='ASAS-SN Sky Patrol',
#                    bibcode='2017arXiv170607060K',
#                    url='https://asas-sn.osu.edu')
#                csv = catalog.load_url(lcurl + '.csv', os.path.join(
#                    catalog.get_current_task_repo(), os.path.join(
#                        'ASASSN', objname + '.csv')))
#                data = read(csv, format='csv')
#                for row in data:
#                    mag = str(row['mag'])
#                    if float(mag.strip('>')) > 50.0:
#                        continue
#                    photodict = {
#                        PHOTOMETRY.TIME: str(jd_to_mjd(
#                            Decimal(str(row['HJD'])))),
#                        PHOTOMETRY.MAGNITUDE: mag.strip('>'),
#                        PHOTOMETRY.SURVEY: 'ASASSN',
#                        PHOTOMETRY.SOURCE: source
#                    }
#                    if '>' in mag:
#                        photodict[PHOTOMETRY.UPPER_LIMIT] = True
#                    else:
#                        photodict[PHOTOMETRY.E_MAGNITUDE] = str(row['mag_err'])
#                    catalog.entries[name].add_photometry(**photodict)
#    catalog.journal_entries()
#    return

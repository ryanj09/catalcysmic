"""Tasks related to the ASASSN survey."""
import json
import os
import re
from decimal import Decimal

from astrocats.catalog.photometry import PHOTOMETRY
from astrocats.catalog.utils import jd_to_mjd, pbar
from astropy.io.ascii import read
from bs4 import BeautifulSoup

from astrocats.cataclysmic.cataclysmic import CATACLYSMIC


def do_asassn(catalog):
    """Import list of ASASSN events."""
    task_str = catalog.get_current_task_str()
    asn_url = 'http://www.astronomy.ohio-state.edu/~assassin/transients.html'
    html = catalog.load_url(asn_url, os.path.join(
        catalog.get_current_task_repo(), 'ASASSN/transients.html'))
    if not html:
        return
    bs = BeautifulSoup(html, 'html5lib')
    trs = bs.find('table').findAll('tr')
    for tri, tr in enumerate(pbar(trs, task_str)):
        name = ''
        ra = ''
        dec = ''
        discdate = ''
        mag = ''
        atellink = ''
        sdsslink = ''
        comment = '' #store to check if entry is a CV later
        if tri == 1:
            continue
        tds = tr.findAll('td')
        atex = 0
        for tdi, td in enumerate(tds):
            if tdi == 0 and td.text.strip() != '---':
                try:
                    name = catalog.add_entry(td.text.strip().replace("?","_"))
#                    atellink = td.find('a')
                    atex = 1
#                    if atellink:
#                        atellink = atellink['href']
#                    else:
#                        atellink = ''
                except ValueError:
                    pass
            if tdi == 1 and td.text.strip() != '---':
                if atex == 0:
                    name = catalog.add_entry(td.text.strip().replace("?","_").replace(':','_'))
#                    atellink = td.find('a')
#                    if atellink:
#                        atellink = atellink['href']
#                    else:
#                        atellink = ''
                else:
                    pass
            if tdi == 3:
                ra = td.text
            if tdi == 4:
                dec = td.text
            if tdi == 5:
                discdate = td.text.replace('-', '/')
                if discdate == 'bc094//0':
                    discdate = '' #ASASSN-15co was having bc094--0 as a date
            if tdi == 6:
                mag = td.text
            if tdi == 7:
                sdsslink = td.find('a')
                if sdsslink:
                    sdsslink = sdsslink['href']
                else:
                    sdsslink = ''
            if tdi == 11:
                comment = td.text
        if 'CV' in comment:
            sources = [catalog.entries[name].add_source(
                url=asn_url, name='ASAS-SN Transients')]
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
            catalog.entries[name].add_quantity(CATACLYSMIC.RA, ra, sources,
                                               u_value='floatdegrees')
            catalog.entries[name].add_quantity(CATACLYSMIC.DEC, dec, sources,
                                               u_value='floatdegrees')
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

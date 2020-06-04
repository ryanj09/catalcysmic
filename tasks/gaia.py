"""Import tasks for GAIA.
"""
import csv
import os
import re

from astrocats.catalog.utils import jd_to_mjd, pbar

from decimal import Decimal

from astrocats.cataclysmic.cataclysmic import CATACLYSMIC


def do_gaia(catalog):
    task_str = catalog.get_current_task_str()
    fname = os.path.join(catalog.get_current_task_repo(), 'GAIA/alerts.csv')
    csvtxt = catalog.load_url('http://gsaweb.ast.cam.ac.uk/alerts/alerts.csv',
                              fname)
    if not csvtxt:
        return
    tsvin = list(
        csv.reader(
            csvtxt.splitlines(), delimiter=',', skipinitialspace=True))
    reference = 'Gaia Photometric Science Alerts'
    refurl = 'http://gsaweb.ast.cam.ac.uk/alerts/alertsindex'
    loopcnt = 0
    for ri, row in enumerate(pbar(tsvin, task_str)):
        if ri == 0 or not row:
            continue
        name = catalog.add_entry(row[0])
        source = catalog.entries[name].add_source(name=reference, url=refurl)
        catalog.entries[name].add_quantity(CATACLYSMIC.ALIAS, name, source)
        year = '20' + re.findall(r'\d+', row[0])[0]
        catalog.entries[name].add_quantity(CATACLYSMIC.DISCOVER_DATE, year,
                                           source)
        catalog.entries[name].add_quantity(
            CATACLYSMIC.RA, row[2], source, u_value='floatdegrees')
        catalog.entries[name].add_quantity(
            CATACLYSMIC.DEC, row[3], source, u_value='floatdegrees')
        if name == 'Gaia16adj':
            continue
        #TODO: ? for cv's
        if row[7] and row[7] != 'unknown':
            type = row[7].replace('CV', '').strip()
            catalog.entries[name].add_quantity(CATACLYSMIC.CLAIMED_TYPE, type,
                                               source)
        elif any([
                xx in row[9].upper()
                for xx in ['CV CANDIATE', 'CANDIDATE CV', 'HOSTLESS BLUE TRANSIENT']
        ]):
            catalog.entries[name].add_quantity(CATACLYSMIC.CLAIMED_TYPE,
                                               'Candidate', source)

        if ('aka' in row[9].replace('gakaxy', 'galaxy').lower() and
                'AKARI' not in row[9]):
            commentsplit = (row[9].replace('_', ' ').replace('MLS ', 'MLS')
                            .replace('CSS ', 'CSS').replace('CV iPTF', 'iPTF')
                            .replace('CV ', 'CV').replace('AT ', 'AT'))
            commentsplit = commentsplit.split()
            for csi, cs in enumerate(commentsplit):
                if 'aka' in cs.lower() and csi < len(commentsplit) - 1:
                    alias = commentsplit[csi + 1].strip('(),:.ï»¿').replace(
                        'PSNJ', 'PSN J')
                    if alias[:6] == 'ASASSN' and alias[6] != '-':
                        alias = 'ASASSN-' + alias[6:]
                    if alias.lower() != 'master':
                        catalog.entries[name].add_quantity(CATACLYSMIC.ALIAS,
                                                           alias, source)
                    break

        fname = os.path.join(catalog.get_current_task_repo(),
                             'GAIA/') + row[0] + '.csv'

        csvtxt = catalog.load_url('http://gsaweb.ast.cam.ac.uk/alerts/alert/' +
                                  row[0] + '/lightcurve.csv', fname)

        tsvin2 = csv.reader(csvtxt.splitlines())
        for ri2, row2 in enumerate(tsvin2):
            if ri2 <= 1 or not row2:
                continue
            mjd = str(jd_to_mjd(Decimal(row2[1].strip())))
            magnitude = row2[2].strip()
            if magnitude == 'null':
                continue
            e_mag = 0.
            telescope = 'GAIA'
            band = 'G'
            catalog.entries[name].add_photometry(
                time=mjd,
                u_time='MJD',
                telescope=telescope,
                band=band,
                magnitude=magnitude,
                e_magnitude=e_mag,
                source=source)
        if catalog.args.update:
            catalog.journal_entries()
        loopcnt = loopcnt + 1
        if catalog.args.travis and loopcnt % catalog.TRAVIS_QUERY_LIMIT == 0:
            break
    catalog.journal_entries()
    return

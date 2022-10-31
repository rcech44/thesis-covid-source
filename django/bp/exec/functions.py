import math
import pprint
from time import sleep
import json
from urllib.request import urlopen
import urllib.parse
import mysql.connector
from datetime import datetime, timedelta
import random
import os
import sqlite3
import numpy as np

pocet_obyvatel = {"CZ0100": 1275406, "CZ0201": 99323, "CZ0202": 96624,"CZ0203": 164493,"CZ0204": 103894,"CZ0205": 75683,"CZ0206": 109354,"CZ0207": 127592,"CZ0208": 101120,"CZ0209": 188384,"CZ020A": 151093,"CZ020B": 114366,"CZ020C": 54898,"CZ0311": 195533,"CZ0312": 60096,"CZ0313": 89283,"CZ0314": 70769,"CZ0315": 50230,"CZ0316": 69773,"CZ0317": 101363,"CZ0321": 54391,"CZ0322": 84614,"CZ0323": 188407,"CZ0324": 68918,"CZ0325": 80666,"CZ0326": 48770,"CZ0327": 52941,"CZ0411": 87958,"CZ0412": 110052,"CZ0413": 85200,"CZ0421": 126294,"CZ0422": 121480,"CZ0423": 117582,"CZ0424": 85381,"CZ0425": 106773,"CZ0426": 124472,"CZ0427": 116916,"CZ0511": 101962,"CZ0512": 90171,"CZ0513": 173890,"CZ0514": 71547,"CZ0521": 162400,"CZ0522": 78713,"CZ0523": 107973,"CZ0524": 78424,"CZ0525": 115073,"CZ0531": 103746,"CZ0532": 172224,"CZ0533": 102866,"CZ0534": 135682,"CZ0631": 93692,"CZ0632": 112415,"CZ0633": 71571,"CZ0634": 109183,"CZ0635": 117164,"CZ0641": 107912,"CZ0642": 379466,"CZ0643": 225514,"CZ0644": 114801,"CZ0645": 151096,"CZ0646": 92317,"CZ0647": 113462,"CZ0711": 36752,"CZ0712": 233588,"CZ0713": 107580,"CZ0714": 126613,"CZ0715": 118397,"CZ0721": 103445,"CZ0722": 139829,"CZ0723": 140171,"CZ0724": 188987,"CZ0801": 89547,"CZ0802": 212347,"CZ0803": 240319,"CZ0804": 149919,"CZ0805": 173753,"CZ0806": 312104}

def format_number(num):
    if num >= 0:
        return "+ " + str(f"{abs(num):,}")
    else:
        return "- " + str(f"{abs(num):,}")

def get_today_summary():
    result = {}
    datum_string_now = datetime.now().strftime("%Y-%m-%d")
    datum_string_yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    datum_string_two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

    url_summary = 'https://onemocneni-aktualne.mzcr.cz/api/v3/zakladni-prehled?page=1&itemsPerPage=100&apiToken=c54d8c7d54a31d016d8f3c156b98682a'
    url_ockovani = 'https://onemocneni-aktualne.mzcr.cz/api/v3/testy-pcr-antigenni?page=1&itemsPerPage=100&datum%5Bbefore%5D=XYZ&datum%5Bafter%5D=ABC&apiToken=c54d8c7d54a31d016d8f3c156b98682a'
    url_umrti_now = 'https://onemocneni-aktualne.mzcr.cz/api/v3/umrti?page=1&itemsPerPage=10000&datum%5Bbefore%5D=XYZ&datum%5Bafter%5D=ABC&apiToken=c54d8c7d54a31d016d8f3c156b98682a'
    url_vyleceni_now = 'https://onemocneni-aktualne.mzcr.cz/api/v3/vyleceni?page=1&itemsPerPage=3&datum%5Bbefore%5D=XYZ&datum%5Bafter%5D=ABC&apiToken=c54d8c7d54a31d016d8f3c156b98682a'
    url_ockovani = url_ockovani.replace('XYZ', datum_string_now)
    url_ockovani = url_ockovani.replace('ABC', datum_string_yesterday)
    url_umrti_now = url_umrti_now.replace('XYZ', datum_string_now)
    url_umrti_now = url_umrti_now.replace('ABC', datum_string_yesterday)
    url_vyleceni_now = url_vyleceni_now.replace('XYZ', datum_string_now)
    url_vyleceni_now = url_vyleceni_now.replace('ABC', datum_string_yesterday)

    # Basic summary
    req = urllib.request.Request(url_summary)
    req.add_header('accept', 'application/json')
    response = urllib.request.urlopen(req)
    d = json.load(response)[0]

    result['nakazeni'] = f"{d['aktivni_pripady']:,}"
    result['vyleceni'] = f"{d['vyleceni']:,}"
    result['umrti'] = f"{d['umrti']:,}"
    result['rozdil_nakazeni'] = f"{format_number(d['potvrzene_pripady_vcerejsi_den'])}"

    # Collection of PCR tests
    req = urllib.request.Request(url_ockovani)
    req.add_header('accept', 'application/json')
    response = urllib.request.urlopen(req)
    d = json.load(response)[0]

    result['pocet_pcr_testu'] = f"{d['pocet_PCR_testy']:,}"
    result['pocet_pcr_testu_pozitivni'] = f"{(d['PCR_pozit_sympt'] + d['PCR_pozit_asymp']):,} ({round(((d['PCR_pozit_sympt'] + d['PCR_pozit_asymp']) / d['pocet_PCR_testy']) * 100, 2)}%)"

    # Deaths difference
    req = urllib.request.Request(url_umrti_now)
    req.add_header('accept', 'application/json')
    response = urllib.request.urlopen(req)
    d = json.load(response)

    result['rozdil_umrti'] = format_number(len(d))

    # Cured difference
    req = urllib.request.Request(url_vyleceni_now)
    req.add_header('accept', 'application/ld+json')
    response = urllib.request.urlopen(req)
    d = json.load(response)

    result['rozdil_vyleceni'] = format_number(d['hydra:totalItems'])

    # Download data from database
    # try:
    #     with mysql.connector.connect(host="remotemysql.com", user="9qMwE320zO", password="gmnNuBYtIX", database="9qMwE320zO") as conn:
    #         cur = conn.cursor(buffered=True)
    #         cur.execute('SELECT * FROM covid_summary ORDER BY id DESC LIMIT 2')
    #         response = cur.fetchall()
    #         if response is not None:
    #             # Get current values
    #             result['nakazeni'] = f"{response[0][2]:,}"
    #             result['vyleceni'] = f"{response[0][23]:,}"
    #             result['umrti'] = f"{response[0][19]:,}"
    #             result['ovlivneno'] = f"{response[0][10]:,}"

    #             # Get values difference
    #             if response[0][1] == datum_string_now and response[1][1] == datum_string_yesterday:
    #                 result['rozdil_nakazeni'] = format_number(response[0][11] + response[0][24])
    #                 result['rozdil_vyleceni'] = format_number(response[0][23] - response[1][23])
    #                 result['rozdil_umrti'] = format_number(response[0][19] - response[1][19])
    #                 result['rozdil_ovlivneno'] = format_number(response[0][10] - response[1][10])
    #         else:
    #             return {}

    # except mysql.connector.Error as e:
    #     print(e)

    return result

def thirty_day_summary_graph():
    graph = {}
    graph['days'] = []
    graph['values'] = []
    graph['colors'] = []
    graph['colors_border'] = []
    maximum_value = 0

    color_red = [255, 80, 80]
    color_green = [255, 191, 80]

    try:
        with mysql.connector.connect(host="remotemysql.com", user="9qMwE320zO", password="gmnNuBYtIX", database="9qMwE320zO") as conn:
            cur = conn.cursor(buffered=True)
            cur.execute('SELECT datum, SUM(nove_pripady) FROM covid_unikatni_okresy GROUP BY datum ORDER BY datum LIMIT 30')
            response = cur.fetchall()
            if response is not None:
                for row in response:
                    if (row[1]) > maximum_value:
                        maximum_value = row[1]
                for row in response:

                    # Calculate color gradient
                    value = row[1]
                    difference1 = value / maximum_value
                    difference2 = 1 - difference1
                    final_color = [round(color_red[0] * difference1 + color_green[0] * difference2), \
                                   round(color_red[1] * difference1 + color_green[1] * difference2), \
                                   round(color_red[2] * difference1 + color_green[2] * difference2)]

                    # 'rgb(255, 99, 132)'
                    date_format = datetime.strptime(row[0], '%Y-%m-%d')
                    graph['colors'].append(f"rgba({str(final_color[0])}, {str(final_color[1])}, {str(final_color[2])}, 0.8)")
                    graph['colors_border'].append(f"rgb({str(final_color[0] - 30)}, {str(final_color[1] - 30)}, {str(final_color[2] - 30)})")
                    graph['days'].append(date_format.strftime("%d.%m."))
                    graph['values'].append(row[1])

    except mysql.connector.Error as e:
        pass

    return graph

def thirty_day_map():
    global pocet_obyvatel
    data = {}
    try:
        with sqlite3.connect('sql/database.sqlite') as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM covid_datum_okres ORDER BY id DESC LIMIT 2400')
            response = cur.fetchall()
            if response is not None:
                for row in response:
                    if row[2] is None:
                        continue
                    if row[1] not in data:
                        data[row[1]] = {}
                    if row[2] not in data[row[1]]:
                        data[row[1]][row[2]] = {}
                    data[row[1]][row[2]]['nove_pripady'] = row[3]
                    data[row[1]][row[2]]['nove_pripady_sto_tisic'] = row[3] / (pocet_obyvatel[row[2]] / 100000)
                    data[row[1]][row[2]]['aktivni_pripady'] = row[4]
                    data[row[1]][row[2]]['aktivni_pripady_sto_tisic'] = row[4] / (pocet_obyvatel[row[2]] / 100000)
                    data[row[1]][row[2]]['nove_pripady_7'] = row[5]
                    data[row[1]][row[2]]['nove_pripady_14'] = row[6]
                    data[row[1]][row[2]]['nove_pripady_65_vek'] = row[7]

            for datum in data:
                count_aktivni = 0
                count_aktivni_sto_tisic = 0
                count_nove = 0
                count_nove_sto_tisic = 0
                max_nove = 0
                max_nove_sto_tisic = 0
                min_nove = 99999999
                min_nove_sto_tisic = 99999999
                max_aktivni = 0
                max_aktivni_sto_tisic = 0
                min_aktivni = 99999999
                min_aktivni_sto_tisic = 99999999
                # values_nove = []
                # values_aktivni = []
                for okres in data[datum]:
                    count_aktivni += data[datum][okres]['aktivni_pripady']
                    count_aktivni_sto_tisic += data[datum][okres]['aktivni_pripady_sto_tisic']
                    count_nove += data[datum][okres]['nove_pripady']
                    count_nove_sto_tisic += data[datum][okres]['nove_pripady_sto_tisic']
                    # values_nove.append(data[datum][okres]['nove_pripady'])
                    # values_aktivni.append(data[datum][okres]['aktivni_pripady'])
                    if data[datum][okres]['aktivni_pripady'] > max_aktivni: max_aktivni = data[datum][okres]['aktivni_pripady']
                    if data[datum][okres]['aktivni_pripady'] < min_aktivni: min_aktivni = data[datum][okres]['aktivni_pripady']
                    if data[datum][okres]['nove_pripady'] > max_nove: max_nove = data[datum][okres]['nove_pripady']
                    if data[datum][okres]['nove_pripady'] < min_nove: min_nove = data[datum][okres]['nove_pripady']
                    if data[datum][okres]['aktivni_pripady_sto_tisic'] > max_aktivni_sto_tisic: max_aktivni_sto_tisic = data[datum][okres]['aktivni_pripady_sto_tisic']
                    if data[datum][okres]['aktivni_pripady_sto_tisic'] < min_aktivni_sto_tisic: min_aktivni_sto_tisic = data[datum][okres]['aktivni_pripady_sto_tisic']
                    if data[datum][okres]['nove_pripady_sto_tisic'] > max_nove_sto_tisic: max_nove_sto_tisic = data[datum][okres]['nove_pripady_sto_tisic']
                    if data[datum][okres]['nove_pripady_sto_tisic'] < min_nove_sto_tisic: min_nove_sto_tisic = data[datum][okres]['nove_pripady_sto_tisic']
                data[datum]['max_aktivni'] = max_aktivni
                data[datum]['max_aktivni_sto_tisic'] = max_aktivni_sto_tisic
                data[datum]['min_aktivni'] = min_aktivni
                data[datum]['min_aktivni_sto_tisic'] = min_aktivni_sto_tisic
                data[datum]['max_nove'] = max_nove
                data[datum]['max_nove_sto_tisic'] = max_nove_sto_tisic
                data[datum]['min_nove'] = min_nove
                data[datum]['min_nove_sto_tisic'] = min_nove_sto_tisic
                data[datum]['avg_aktivni'] = count_aktivni / 76
                data[datum]['avg_nove'] = count_nove / 76
                # data[datum]['90th_percentile_nove'] = np.percentile(values_nove, 97)
                # data[datum]['90th_percentile_aktivni'] = np.percentile(values_aktivni, 97)

            # pprint.pprint(data)

    except sqlite3.Error as e:
        print(e)
        print(os.getcwd())
    
    return data

def checkUpToDate():
    print('[DATABASE-CHECKER] Checking if database is up-to-date')
    delta = 0
    url_obce = 'https://onemocneni-aktualne.mzcr.cz/api/v3/obce?page=1&itemsPerPage=10000&datum%5Bafter%5D=XYZ&datum%5Bbefore%5D=XYZ&apiToken=c54d8c7d54a31d016d8f3c156b98682a'
    url_prehled = 'https://onemocneni-aktualne.mzcr.cz/api/v3/zakladni-prehled?page=1&itemsPerPage=100&apiToken=c54d8c7d54a31d016d8f3c156b98682a'
    datum_string_now = datetime.now().strftime("%Y-%m-%d")
    datum_string_yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        with sqlite3.connect('sql/database.sqlite') as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM covid_datum_okres ORDER BY id DESC LIMIT 1')
            response = cur.fetchall()
            if response is not None:
                if response[0][1] != datum_string_yesterday:
                    # Data in database is not up to date...
                    date_yesterday = datetime.strptime(datum_string_yesterday, "%Y-%m-%d")
                    date_database = datetime.strptime(response[0][1], "%Y-%m-%d")
                    delta_days = (date_yesterday - date_database).days
                    delta = delta_days
                    print(delta_days)

                    # Update database
                    for i in range(delta_days):
                        update_date = (date_database + timedelta(days=i+1)).strftime("%Y-%m-%d")
                        current_url = url_obce.replace('XYZ', update_date)
                        req = urllib.request.Request(current_url)
                        req.add_header('accept', 'application/json')
                        response = urllib.request.urlopen(req)
                        obce = json.load(response)
                        dny = {}
                        for obec in obce:
                            if obec['okres_lau_kod'] not in dny:
                                dny[obec['okres_lau_kod']] = {}
                                dny[obec['okres_lau_kod']]['nove_pripady'] = obec['nove_pripady']
                                dny[obec['okres_lau_kod']]['aktivni_pripady'] = obec['aktivni_pripady']
                                dny[obec['okres_lau_kod']]['nove_pripady_7'] = obec['nove_pripady_7_dni']
                                dny[obec['okres_lau_kod']]['nove_pripady_14'] = obec['nove_pripady_14_dni']
                                dny[obec['okres_lau_kod']]['nove_pripady_65_vek'] = obec['nove_pripady_65']
                            else:
                                dny[obec['okres_lau_kod']]['nove_pripady'] += obec['nove_pripady']
                                dny[obec['okres_lau_kod']]['aktivni_pripady'] += obec['aktivni_pripady']
                                dny[obec['okres_lau_kod']]['nove_pripady_7'] += obec['nove_pripady_7_dni']
                                dny[obec['okres_lau_kod']]['nove_pripady_14'] += obec['nove_pripady_14_dni']
                                dny[obec['okres_lau_kod']]['nove_pripady_65_vek'] += obec['nove_pripady_65']
                        # print(dny)
                        for okres in dny:
                            cur.execute('INSERT INTO covid_datum_okres (datum, okres, nove_pripady, aktivni_pripady, nove_pripady_7, nove_pripady_14, nove_pripady_65_vek) VALUES (?, ?, ?, ?, ?, ?, ?)', \
                                [
                                    update_date,
                                    okres,
                                    dny[okres]['nove_pripady'],
                                    dny[okres]['aktivni_pripady'],
                                    dny[okres]['nove_pripady_7'],
                                    dny[okres]['nove_pripady_14'],
                                    dny[okres]['nove_pripady_65_vek'],
                                ])
                            conn.commit()
                        print(f"Downloaded data from {update_date}")

            cur = conn.cursor()
            cur.execute('SELECT * FROM zakladni_prehled ORDER BY id DESC LIMIT 1')
            response = cur.fetchall()
            if response is not None:
                if response[0][1] != datum_string_now:
                    req = urllib.request.Request(url_prehled)
                    req.add_header('accept', 'application/json')
                    response = urllib.request.urlopen(req)
                    prehled = json.load(response)[0]
                    if prehled['datum'] == datum_string_now:
                        cur.execute('INSERT INTO zakladni_prehled (datum, provedene_testy_celkem, potvrzene_pripady_celkem, aktivni_pripady, vyleceni, umrti, aktualne_hospitalizovani, provedene_testy_vcerejsi_den, potvrzene_pripady_vcerejsi_den, provedene_testy_vcerejsi_den_datum, potvrzene_pripady_vcerejsi_den_datum, provedene_antigenni_testy_celkem, provedene_antigenni_testy_vcerejsi_den, provedene_antigenni_testy_vcerejsi_den_datum, vykazana_ockovani_celkem, vykazana_ockovani_vcerejsi_den, vykazana_ockovani_vcerejsi_den_datum, potvrzene_pripady_65_celkem, potvrzene_pripady_65_vcerejsi_den, potvrzene_pripady_65_vcerejsi_den_datum, ockovane_osoby_celkem, ockovane_osoby_vcerejsi_den, ockovane_osoby_vcerejsi_den_datum) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', \
                            [
                                prehled['datum'],
                                prehled['provedene_testy_celkem'],
                                prehled['potvrzene_pripady_celkem'],
                                prehled['aktivni_pripady'],
                                prehled['vyleceni'],
                                prehled['umrti'],
                                prehled['aktualne_hospitalizovani'],
                                prehled['provedene_testy_vcerejsi_den'],
                                prehled['potvrzene_pripady_vcerejsi_den'],
                                prehled['provedene_testy_vcerejsi_den_datum'],
                                prehled['potvrzene_pripady_vcerejsi_den_datum'],
                                prehled['provedene_antigenni_testy_celkem'],
                                prehled['provedene_antigenni_testy_vcerejsi_den'],
                                prehled['provedene_antigenni_testy_vcerejsi_den_datum'],
                                prehled['vykazana_ockovani_celkem'],
                                prehled['vykazana_ockovani_vcerejsi_den'],
                                prehled['vykazana_ockovani_vcerejsi_den_datum'],
                                prehled['potvrzene_pripady_65_celkem'],
                                prehled['potvrzene_pripady_65_vcerejsi_den'],
                                prehled['potvrzene_pripady_65_vcerejsi_den_datum'],
                                prehled['ockovane_osoby_celkem'],
                                prehled['ockovane_osoby_vcerejsi_den'],
                                prehled['ockovane_osoby_vcerejsi_den_datum']
                            ])
                        conn.commit()
                    else:
                        pass

    except sqlite3.Error as e:
        print(e)
        # print(os.getcwd())

    if delta != 0:
        print("[DATABASE-CHECKER] Database updated with {delta} days")
        return False
    else:
        print('[DATABASE-CHECKER] Database is up-to-date')
        return True

# checkUpToDate()
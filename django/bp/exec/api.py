from datetime import datetime, timedelta
import sqlite3

pocet_obyvatel = {"CZ0100": 1275406, "CZ0201": 99323, "CZ0202": 96624,"CZ0203": 164493,"CZ0204": 103894,"CZ0205": 75683,"CZ0206": 109354,"CZ0207": 127592,"CZ0208": 101120,"CZ0209": 188384,"CZ020A": 151093,"CZ020B": 114366,"CZ020C": 54898,"CZ0311": 195533,"CZ0312": 60096,"CZ0313": 89283,"CZ0314": 70769,"CZ0315": 50230,"CZ0316": 69773,"CZ0317": 101363,"CZ0321": 54391,"CZ0322": 84614,"CZ0323": 188407,"CZ0324": 68918,"CZ0325": 80666,"CZ0326": 48770,"CZ0327": 52941,"CZ0411": 87958,"CZ0412": 110052,"CZ0413": 85200,"CZ0421": 126294,"CZ0422": 121480,"CZ0423": 117582,"CZ0424": 85381,"CZ0425": 106773,"CZ0426": 124472,"CZ0427": 116916,"CZ0511": 101962,"CZ0512": 90171,"CZ0513": 173890,"CZ0514": 71547,"CZ0521": 162400,"CZ0522": 78713,"CZ0523": 107973,"CZ0524": 78424,"CZ0525": 115073,"CZ0531": 103746,"CZ0532": 172224,"CZ0533": 102866,"CZ0534": 135682,"CZ0631": 93692,"CZ0632": 112415,"CZ0633": 71571,"CZ0634": 109183,"CZ0635": 117164,"CZ0641": 107912,"CZ0642": 379466,"CZ0643": 225514,"CZ0644": 114801,"CZ0645": 151096,"CZ0646": 92317,"CZ0647": 113462,"CZ0711": 36752,"CZ0712": 233588,"CZ0713": 107580,"CZ0714": 126613,"CZ0715": 118397,"CZ0721": 103445,"CZ0722": 139829,"CZ0723": 140171,"CZ0724": 188987,"CZ0801": 89547,"CZ0802": 212347,"CZ0803": 240319,"CZ0804": 149919,"CZ0805": 173753,"CZ0806": 312104}

def getData(range_from, range_to, type):
    return_data = {}
    all_requested_dates = []

    # Check for correct date
    try:
        d1 = datetime.strptime(range_from, '%Y-%m-%d')
        d2 = datetime.strptime(range_to, '%Y-%m-%d')
        if (d1 > d2):
            print('[API] Requested dates are not valid - from is larger than to')
            return 'Requested dates are not valid - from is larger than to'
    except Exception as e:
        print(f"[API] Requested dates are not valid - {e}")
        return 'Requested dates are not valid'

    # If correct, generate all needed dates
    count = 0
    while True:
        d = (datetime.strptime(range_from, '%Y-%m-%d') + timedelta(days=count)).strftime("%Y-%m-%d")
        all_requested_dates.append(d)
        if d == range_to:
            break
        count += 1

    # Get the data
    match type:
        case 'infection':
            try:
                with sqlite3.connect('sql/database.sqlite') as conn:
                    cur = conn.cursor()

                    # 27 because that is the first value in COVID database
                    celkem_pripady = 20
                    for date in all_requested_dates:
                        cur.execute('SELECT * FROM covid_datum_okres WHERE datum = ?', [date])
                        response = cur.fetchall()
                        return_data[date] = {}
                        return_data[date]['celkem_pripady'] = celkem_pripady
                        nove_pocet = 0
                        nove_max = 0
                        nove_min = 999999
                        nove_max_sto_tisic = 0
                        nove_min_sto_tisic = 999999
                        aktivni_pocet = 0
                        aktivni_max = 0
                        aktivni_min = 999999
                        aktivni_max_sto_tisic = 0
                        aktivni_min_sto_tisic = 999999
                        for okres in response:
                            if okres[2] is not None:
                                return_data[date][okres[2]] = {}
                                return_data[date][okres[2]]['nove_pripady'] = okres[3]
                                return_data[date][okres[2]]['aktivni_pripady'] = okres[4]
                                return_data[date][okres[2]]['nove_pripady_7'] = okres[5]
                                return_data[date][okres[2]]['nove_pripady_14'] = okres[6]
                                return_data[date][okres[2]]['nove_pripady_65_vek'] = okres[7]
                                return_data[date][okres[2]]['nove_pripady_sto_tisic'] = okres[3] / (pocet_obyvatel[okres[2]] / 100000)
                                return_data[date][okres[2]]['aktivni_pripady_sto_tisic'] = okres[4] / (pocet_obyvatel[okres[2]] / 100000)
                                nove_pocet += okres[3]
                                aktivni_pocet += okres[4]
                                if return_data[date][okres[2]]['nove_pripady'] > nove_max: nove_max = return_data[date][okres[2]]['nove_pripady']
                                if return_data[date][okres[2]]['nove_pripady'] < nove_min: nove_min = return_data[date][okres[2]]['nove_pripady']
                                if return_data[date][okres[2]]['nove_pripady_sto_tisic'] > nove_max_sto_tisic: nove_max_sto_tisic = return_data[date][okres[2]]['nove_pripady_sto_tisic']
                                if return_data[date][okres[2]]['nove_pripady_sto_tisic'] < nove_min_sto_tisic: nove_min_sto_tisic = return_data[date][okres[2]]['nove_pripady_sto_tisic']
                                if return_data[date][okres[2]]['aktivni_pripady'] > aktivni_max: aktivni_max = return_data[date][okres[2]]['aktivni_pripady']
                                if return_data[date][okres[2]]['aktivni_pripady'] < aktivni_min: aktivni_min = return_data[date][okres[2]]['aktivni_pripady']
                                if return_data[date][okres[2]]['aktivni_pripady_sto_tisic'] > aktivni_max_sto_tisic: aktivni_max_sto_tisic = return_data[date][okres[2]]['aktivni_pripady_sto_tisic']
                                if return_data[date][okres[2]]['aktivni_pripady_sto_tisic'] < aktivni_min_sto_tisic: aktivni_min_sto_tisic = return_data[date][okres[2]]['aktivni_pripady_sto_tisic']
                        return_data[date]['max_aktivni'] = aktivni_max
                        return_data[date]['min_aktivni'] = aktivni_min
                        return_data[date]['max_nove'] = nove_max
                        return_data[date]['min_nove'] = nove_min
                        return_data[date]['max_aktivni_sto_tisic'] = aktivni_max_sto_tisic
                        return_data[date]['min_aktivni_sto_tisic'] = aktivni_min_sto_tisic
                        return_data[date]['max_nove_sto_tisic'] = nove_max_sto_tisic
                        return_data[date]['min_nove_sto_tisic'] = nove_min_sto_tisic
                        return_data[date]['nove_celkovy_pocet'] = nove_pocet
                        return_data[date]['aktivni_celkovy_pocet'] = aktivni_pocet
                        celkem_pripady += nove_pocet
                        return_data[date]['celkem_pripady'] = celkem_pripady
            
            except sqlite3.Error as e:
                print(f"[API] Database error - {e}")
                return f"Database error - {e}"
        
        case 'vaccination':
            try:
                with sqlite3.connect('sql/database.sqlite') as conn:
                    cur = conn.cursor()
                    davka_2_doposud = 0
                    absolute_celkem = 0
                    okres_absolute_celkem = 0
                    for date in all_requested_dates:
                        cur.execute('SELECT * FROM ockovani_datum_okres WHERE datum = ?', [date])
                        response = cur.fetchall()
                        return_data[date] = {}
                        davka_1_max = 0
                        davka_1_min = 9999999
                        davka_2_max = 0
                        davka_2_min = 9999999
                        davka_3_max = 0
                        davka_3_min = 9999999
                        davka_4_max = 0
                        davka_4_min = 9999999

                        davka_1_max_sto_tisic = 0
                        davka_1_min_sto_tisic = 9999999
                        davka_2_max_sto_tisic = 0
                        davka_2_min_sto_tisic = 9999999
                        davka_3_max_sto_tisic = 0
                        davka_3_min_sto_tisic = 9999999
                        davka_4_max_sto_tisic = 0
                        davka_4_min_sto_tisic = 9999999

                        davka_1_doposud_max = 0
                        davka_1_doposud_min = 9999999
                        davka_2_doposud_max = 0
                        davka_2_doposud_min = 9999999
                        davka_3_doposud_max = 0
                        davka_3_doposud_min = 9999999
                        davka_4_doposud_max = 0
                        davka_4_doposud_min = 9999999

                        davka_1_doposud_max_sto_tisic = 0
                        davka_1_doposud_min_sto_tisic = 9999999
                        davka_2_doposud_max_sto_tisic = 0
                        davka_2_doposud_min_sto_tisic = 9999999
                        davka_3_doposud_max_sto_tisic = 0
                        davka_3_doposud_min_sto_tisic = 9999999
                        davka_4_doposud_max_sto_tisic = 0
                        davka_4_doposud_min_sto_tisic = 9999999

                        davka_celkem_den_max = 0 
                        davka_celkem_den_min = 9999999 
                        davka_celkem_den_max_sto_tisic = 0 
                        davka_celkem_den_min_sto_tisic = 9999999 
                        davka_celkem_doposud_max = 0 
                        davka_celkem_doposud_min = 9999999 
                        davka_celkem_doposud_max_sto_tisic = 0 
                        davka_celkem_doposud_min_sto_tisic = 9999999 
                        celkem_den = 0
                        celkem_doposud = 0
                        for okres in response:
                            if okres[2] is not None:
                                # Process data and get 100 thousand count
                                return_data[date][okres[2]] = {}
                                return_data[date][okres[2]]['davka_1_den'] = okres[3]
                                return_data[date][okres[2]]['davka_1_den_sto_tisic'] = okres[3] / (pocet_obyvatel[okres[2]] / 100000)
                                return_data[date][okres[2]]['davka_1_doposud'] = okres[4]
                                return_data[date][okres[2]]['davka_1_doposud_sto_tisic'] = okres[4] / (pocet_obyvatel[okres[2]] / 100000)
                                return_data[date][okres[2]]['davka_2_den'] = okres[5]
                                return_data[date][okres[2]]['davka_2_den_sto_tisic'] = okres[5] / (pocet_obyvatel[okres[2]] / 100000)
                                return_data[date][okres[2]]['davka_2_doposud'] = okres[6]
                                return_data[date][okres[2]]['davka_2_doposud_sto_tisic'] = okres[6] / (pocet_obyvatel[okres[2]] / 100000)
                                return_data[date][okres[2]]['davka_3_den'] = okres[7]
                                return_data[date][okres[2]]['davka_3_den_sto_tisic'] = okres[7] / (pocet_obyvatel[okres[2]] / 100000)
                                return_data[date][okres[2]]['davka_3_doposud'] = okres[8]
                                return_data[date][okres[2]]['davka_3_doposud_sto_tisic'] = okres[8] / (pocet_obyvatel[okres[2]] / 100000)
                                return_data[date][okres[2]]['davka_4_den'] = okres[9]
                                return_data[date][okres[2]]['davka_4_den_sto_tisic'] = okres[9] / (pocet_obyvatel[okres[2]] / 100000)
                                return_data[date][okres[2]]['davka_4_doposud'] = okres[10]
                                return_data[date][okres[2]]['davka_4_doposud_sto_tisic'] = okres[10] / (pocet_obyvatel[okres[2]] / 100000)
                                return_data[date][okres[2]]['davka_celkem_den'] = okres[11]
                                celkem_den += okres[11]
                                celkem_doposud += okres[12]
                                davka_2_doposud += okres[5]
                                absolute_celkem += (okres[3] + okres[5] + okres[7] + okres[9])
                                return_data[date][okres[2]]['davka_celkem_den_sto_tisic'] = okres[11] / (pocet_obyvatel[okres[2]] / 100000)
                                return_data[date][okres[2]]['davka_celkem_doposud'] = okres[12]
                                return_data[date][okres[2]]['davka_celkem_doposud_sto_tisic'] = okres[12] / (pocet_obyvatel[okres[2]] / 100000)

                                # Get minimums and maximums
                                if return_data[date][okres[2]]['davka_1_den'] > davka_1_max: davka_1_max = return_data[date][okres[2]]['davka_1_den']
                                if return_data[date][okres[2]]['davka_1_den'] < davka_1_min: davka_1_min = return_data[date][okres[2]]['davka_1_den']
                                if return_data[date][okres[2]]['davka_2_den'] > davka_2_max: davka_2_max = return_data[date][okres[2]]['davka_2_den']
                                if return_data[date][okres[2]]['davka_2_den'] < davka_2_min: davka_2_min = return_data[date][okres[2]]['davka_2_den']
                                if return_data[date][okres[2]]['davka_3_den'] > davka_3_max: davka_3_max = return_data[date][okres[2]]['davka_3_den']
                                if return_data[date][okres[2]]['davka_3_den'] < davka_3_min: davka_3_min = return_data[date][okres[2]]['davka_3_den']
                                if return_data[date][okres[2]]['davka_4_den'] > davka_4_max: davka_4_max = return_data[date][okres[2]]['davka_4_den']
                                if return_data[date][okres[2]]['davka_4_den'] < davka_4_min: davka_4_min = return_data[date][okres[2]]['davka_4_den']

                                if return_data[date][okres[2]]['davka_1_den_sto_tisic'] > davka_1_max_sto_tisic: davka_1_max_sto_tisic = return_data[date][okres[2]]['davka_1_den_sto_tisic']
                                if return_data[date][okres[2]]['davka_1_den_sto_tisic'] < davka_1_min_sto_tisic: davka_1_min_sto_tisic = return_data[date][okres[2]]['davka_1_den_sto_tisic']
                                if return_data[date][okres[2]]['davka_2_den_sto_tisic'] > davka_2_max_sto_tisic: davka_2_max_sto_tisic = return_data[date][okres[2]]['davka_2_den_sto_tisic']
                                if return_data[date][okres[2]]['davka_2_den_sto_tisic'] < davka_2_min_sto_tisic: davka_2_min_sto_tisic = return_data[date][okres[2]]['davka_2_den_sto_tisic']
                                if return_data[date][okres[2]]['davka_3_den_sto_tisic'] > davka_3_max_sto_tisic: davka_3_max_sto_tisic = return_data[date][okres[2]]['davka_3_den_sto_tisic']
                                if return_data[date][okres[2]]['davka_3_den_sto_tisic'] < davka_3_min_sto_tisic: davka_3_min_sto_tisic = return_data[date][okres[2]]['davka_3_den_sto_tisic']
                                if return_data[date][okres[2]]['davka_4_den_sto_tisic'] > davka_4_max_sto_tisic: davka_4_max_sto_tisic = return_data[date][okres[2]]['davka_4_den_sto_tisic']
                                if return_data[date][okres[2]]['davka_4_den_sto_tisic'] < davka_4_min_sto_tisic: davka_4_min_sto_tisic = return_data[date][okres[2]]['davka_4_den_sto_tisic']

                                if return_data[date][okres[2]]['davka_1_doposud'] > davka_1_doposud_max: davka_1_doposud_max = return_data[date][okres[2]]['davka_1_doposud']
                                if return_data[date][okres[2]]['davka_1_doposud'] < davka_1_doposud_min: davka_1_doposud_min = return_data[date][okres[2]]['davka_1_doposud']
                                if return_data[date][okres[2]]['davka_2_doposud'] > davka_2_doposud_max: davka_2_doposud_max = return_data[date][okres[2]]['davka_2_doposud']
                                if return_data[date][okres[2]]['davka_2_doposud'] < davka_2_doposud_min: davka_2_doposud_min = return_data[date][okres[2]]['davka_2_doposud']
                                if return_data[date][okres[2]]['davka_3_doposud'] > davka_3_doposud_max: davka_3_doposud_max = return_data[date][okres[2]]['davka_3_doposud']
                                if return_data[date][okres[2]]['davka_3_doposud'] < davka_3_doposud_min: davka_3_doposud_min = return_data[date][okres[2]]['davka_3_doposud']
                                if return_data[date][okres[2]]['davka_4_doposud'] > davka_4_doposud_max: davka_4_doposud_max = return_data[date][okres[2]]['davka_4_doposud']
                                if return_data[date][okres[2]]['davka_4_doposud'] < davka_4_doposud_min: davka_4_doposud_min = return_data[date][okres[2]]['davka_4_doposud']
                                

                                if return_data[date][okres[2]]['davka_1_doposud_sto_tisic'] > davka_1_doposud_max_sto_tisic: davka_1_doposud_max_sto_tisic = return_data[date][okres[2]]['davka_1_doposud_sto_tisic']
                                if return_data[date][okres[2]]['davka_1_doposud_sto_tisic'] < davka_1_doposud_min_sto_tisic: davka_1_doposud_min_sto_tisic = return_data[date][okres[2]]['davka_1_doposud_sto_tisic']
                                if return_data[date][okres[2]]['davka_2_doposud_sto_tisic'] > davka_2_doposud_max_sto_tisic: davka_2_doposud_max_sto_tisic = return_data[date][okres[2]]['davka_2_doposud_sto_tisic']
                                if return_data[date][okres[2]]['davka_2_doposud_sto_tisic'] < davka_2_doposud_min_sto_tisic: davka_2_doposud_min_sto_tisic = return_data[date][okres[2]]['davka_2_doposud_sto_tisic']
                                if return_data[date][okres[2]]['davka_3_doposud_sto_tisic'] > davka_3_doposud_max_sto_tisic: davka_3_doposud_max_sto_tisic = return_data[date][okres[2]]['davka_3_doposud_sto_tisic']
                                if return_data[date][okres[2]]['davka_3_doposud_sto_tisic'] < davka_3_doposud_min_sto_tisic: davka_3_doposud_min_sto_tisic = return_data[date][okres[2]]['davka_3_doposud_sto_tisic']
                                if return_data[date][okres[2]]['davka_4_doposud_sto_tisic'] > davka_4_doposud_max_sto_tisic: davka_4_doposud_max_sto_tisic = return_data[date][okres[2]]['davka_4_doposud_sto_tisic']
                                if return_data[date][okres[2]]['davka_4_doposud_sto_tisic'] < davka_4_doposud_min_sto_tisic: davka_4_doposud_min_sto_tisic = return_data[date][okres[2]]['davka_4_doposud_sto_tisic']
                                
                                if return_data[date][okres[2]]['davka_celkem_den'] > davka_celkem_den_max: davka_celkem_den_max = return_data[date][okres[2]]['davka_celkem_den']
                                if return_data[date][okres[2]]['davka_celkem_den'] < davka_celkem_den_min: davka_celkem_den_min = return_data[date][okres[2]]['davka_celkem_den']
                                if return_data[date][okres[2]]['davka_celkem_den_sto_tisic'] > davka_celkem_den_max_sto_tisic: davka_celkem_den_max_sto_tisic = return_data[date][okres[2]]['davka_celkem_den_sto_tisic']
                                if return_data[date][okres[2]]['davka_celkem_den_sto_tisic'] < davka_celkem_den_min_sto_tisic: davka_celkem_den_min_sto_tisic = return_data[date][okres[2]]['davka_celkem_den_sto_tisic']
                                if return_data[date][okres[2]]['davka_celkem_doposud'] > davka_celkem_doposud_max: davka_celkem_doposud_max = return_data[date][okres[2]]['davka_celkem_doposud']
                                if return_data[date][okres[2]]['davka_celkem_doposud'] < davka_celkem_doposud_min: davka_celkem_doposud_min = return_data[date][okres[2]]['davka_celkem_doposud']
                                if return_data[date][okres[2]]['davka_celkem_doposud_sto_tisic'] > davka_celkem_doposud_max_sto_tisic: davka_celkem_doposud_max_sto_tisic = return_data[date][okres[2]]['davka_celkem_doposud_sto_tisic']
                                if return_data[date][okres[2]]['davka_celkem_doposud_sto_tisic'] < davka_celkem_doposud_min_sto_tisic: davka_celkem_doposud_min_sto_tisic = return_data[date][okres[2]]['davka_celkem_doposud_sto_tisic']

                                if return_data[date][okres[2]]['davka_celkem_doposud'] > okres_absolute_celkem: okres_absolute_celkem = return_data[date][okres[2]]['davka_celkem_doposud']

                        return_data[date]['davka_1_max'] = davka_1_max
                        return_data[date]['davka_1_min'] = davka_1_min
                        return_data[date]['davka_2_max'] = davka_2_max
                        return_data[date]['davka_2_min'] = davka_2_min
                        return_data[date]['davka_3_max'] = davka_3_max
                        return_data[date]['davka_3_min'] = davka_3_min
                        return_data[date]['davka_4_max'] = davka_4_max
                        return_data[date]['davka_4_min'] = davka_4_min

                        return_data[date]['davka_1_max_sto_tisic'] = davka_1_max_sto_tisic
                        return_data[date]['davka_1_min_sto_tisic'] = davka_1_min_sto_tisic
                        return_data[date]['davka_2_max_sto_tisic'] = davka_2_max_sto_tisic
                        return_data[date]['davka_2_min_sto_tisic'] = davka_2_min_sto_tisic
                        return_data[date]['davka_3_max_sto_tisic'] = davka_3_max_sto_tisic
                        return_data[date]['davka_3_min_sto_tisic'] = davka_3_min_sto_tisic
                        return_data[date]['davka_4_max_sto_tisic'] = davka_4_max_sto_tisic
                        return_data[date]['davka_4_min_sto_tisic'] = davka_4_min_sto_tisic

                        return_data[date]['davka_1_doposud_max'] = davka_1_doposud_max
                        return_data[date]['davka_1_doposud_min'] = davka_1_doposud_min
                        return_data[date]['davka_2_doposud_max'] = davka_2_doposud_max
                        return_data[date]['davka_2_doposud_min'] = davka_2_doposud_min
                        return_data[date]['davka_3_doposud_max'] = davka_3_doposud_max
                        return_data[date]['davka_3_doposud_min'] = davka_3_doposud_min
                        return_data[date]['davka_4_doposud_max'] = davka_4_doposud_max
                        return_data[date]['davka_4_doposud_min'] = davka_4_doposud_min

                        return_data[date]['davka_1_doposud_max_sto_tisic'] = davka_1_doposud_max_sto_tisic
                        return_data[date]['davka_1_doposud_min_sto_tisic'] = davka_1_doposud_min_sto_tisic
                        return_data[date]['davka_2_doposud_max_sto_tisic'] = davka_2_doposud_max_sto_tisic
                        return_data[date]['davka_2_doposud_min_sto_tisic'] = davka_2_doposud_min_sto_tisic
                        return_data[date]['davka_3_doposud_max_sto_tisic'] = davka_3_doposud_max_sto_tisic
                        return_data[date]['davka_3_doposud_min_sto_tisic'] = davka_3_doposud_min_sto_tisic
                        return_data[date]['davka_4_doposud_max_sto_tisic'] = davka_4_doposud_max_sto_tisic
                        return_data[date]['davka_4_doposud_min_sto_tisic'] = davka_4_doposud_min_sto_tisic

                        return_data[date]['davka_celkem_den_max'] = davka_celkem_den_max
                        return_data[date]['davka_celkem_den_min'] = davka_celkem_den_min
                        return_data[date]['davka_celkem_den_max_sto_tisic'] = davka_celkem_den_max_sto_tisic
                        return_data[date]['davka_celkem_den_min_sto_tisic'] = davka_celkem_den_min_sto_tisic
                        return_data[date]['davka_celkem_doposud_max'] = davka_celkem_doposud_max
                        return_data[date]['davka_celkem_doposud_min'] = davka_celkem_doposud_min
                        return_data[date]['davka_celkem_doposud_max_sto_tisic'] = davka_celkem_doposud_max_sto_tisic
                        return_data[date]['davka_celkem_doposud_min_sto_tisic'] = davka_celkem_doposud_min_sto_tisic
                        return_data[date]['davka_celkem_den'] = celkem_den
                        return_data[date]['davka_celkem_doposud'] = celkem_doposud
                        return_data[date]['davka_2_doposud'] = davka_2_doposud
                    
                    return_data['absolute_celkem'] = absolute_celkem
                    return_data['okres_absolute_max'] = okres_absolute_celkem
            
            except sqlite3.Error as e:
                print(f"[API] Database error - {e}")
                return f"Database error - {e}"


    return return_data
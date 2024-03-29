import json
from urllib.request import urlopen
import urllib.parse
from datetime import datetime, timedelta
import sqlite3
from exec.cache import *
from exec.database import *
from exec.database_models import *

class Updater:
    _population = {"CZ0100": 1275406, "CZ0201": 99323, "CZ0202": 96624,"CZ0203": 164493,"CZ0204": 103894,"CZ0205": 75683,"CZ0206": 109354,"CZ0207": 127592,"CZ0208": 101120,"CZ0209": 188384,"CZ020A": 151093,"CZ020B": 114366,"CZ020C": 54898,"CZ0311": 195533,"CZ0312": 60096,"CZ0313": 89283,"CZ0314": 70769,"CZ0315": 50230,"CZ0316": 69773,"CZ0317": 101363,"CZ0321": 54391,"CZ0322": 84614,"CZ0323": 188407,"CZ0324": 68918,"CZ0325": 80666,"CZ0326": 48770,"CZ0327": 52941,"CZ0411": 87958,"CZ0412": 110052,"CZ0413": 85200,"CZ0421": 126294,"CZ0422": 121480,"CZ0423": 117582,"CZ0424": 85381,"CZ0425": 106773,"CZ0426": 124472,"CZ0427": 116916,"CZ0511": 101962,"CZ0512": 90171,"CZ0513": 173890,"CZ0514": 71547,"CZ0521": 162400,"CZ0522": 78713,"CZ0523": 107973,"CZ0524": 78424,"CZ0525": 115073,"CZ0531": 103746,"CZ0532": 172224,"CZ0533": 102866,"CZ0534": 135682,"CZ0631": 93692,"CZ0632": 112415,"CZ0633": 71571,"CZ0634": 109183,"CZ0635": 117164,"CZ0641": 107912,"CZ0642": 379466,"CZ0643": 225514,"CZ0644": 114801,"CZ0645": 151096,"CZ0646": 92317,"CZ0647": 113462,"CZ0711": 36752,"CZ0712": 233588,"CZ0713": 107580,"CZ0714": 126613,"CZ0715": 118397,"CZ0721": 103445,"CZ0722": 139829,"CZ0723": 140171,"CZ0724": 188987,"CZ0801": 89547,"CZ0802": 212347,"CZ0803": 240319,"CZ0804": 149919,"CZ0805": 173753,"CZ0806": 312104}
    _districts = {"CZ0100": 0, "CZ0201": 0, "CZ0202": 0,"CZ0203": 0,"CZ0204": 0,"CZ0205": 0,"CZ0206": 0,"CZ0207": 0,"CZ0208": 0,"CZ0209": 0,"CZ020A": 0, "CZ020B": 0,"CZ020C": 0,"CZ0311": 0,"CZ0312": 0,"CZ0313": 0,"CZ0314": 0,"CZ0315": 0,"CZ0316": 0,"CZ0317": 0,"CZ0321": 0,"CZ0322": 0,"CZ0323": 0,"CZ0324": 0,"CZ0325": 0,"CZ0326": 0,"CZ0327": 0,"CZ0411": 0,"CZ0412": 0,"CZ0413": 0,"CZ0421": 0,"CZ0422": 0,"CZ0423": 0,"CZ0424": 0,"CZ0425": 0,"CZ0426": 0,"CZ0427": 0,"CZ0511": 0,"CZ0512": 0,"CZ0513": 0,"CZ0514": 0,"CZ0521": 0,"CZ0522": 0,"CZ0523": 0,"CZ0524": 0,"CZ0525": 0,"CZ0531": 0,"CZ0532": 0,"CZ0533": 0,"CZ0534": 0,"CZ0631": 0,"CZ0632": 0,"CZ0633": 0,"CZ0634": 0,"CZ0635": 0,"CZ0641": 0,"CZ0642": 0,"CZ0643": 0,"CZ0644": 0,"CZ0645": 0,"CZ0646": 0,"CZ0647": 0,"CZ0711": 0,"CZ0712": 0,"CZ0713": 0,"CZ0714": 0,"CZ0715": 0,"CZ0721": 0,"CZ0722": 0,"CZ0723": 0,"CZ0724": 0,"CZ0801": 0,"CZ0802": 0,"CZ0803": 0,"CZ0804": 0,"CZ0805": 0,"CZ0806": 0}

    @staticmethod
    def download_data(type, day):
        if type == "infection":
            url = "https://onemocneni-aktualne.mzcr.cz/api/v3/obce?page=1&itemsPerPage=10000&datum%5Bafter%5D=XYZ&datum%5Bbefore%5D=XYZ&apiToken=c54d8c7d54a31d016d8f3c156b98682a"
        if type == "vaccination":
            url = "https://onemocneni-aktualne.mzcr.cz/api/v3/ockovani-geografie?page=1&itemsPerPage=10000&datum%5Bbefore%5D=XYZ&datum%5Bafter%5D=XYZ&apiToken=c54d8c7d54a31d016d8f3c156b98682a"
        if type == "death":
            url = "https://onemocneni-aktualne.mzcr.cz/api/v3/umrti?page=1&itemsPerPage=10000&datum%5Bbefore%5D=XYZ&datum%5Bafter%5D=XYZ&apiToken=c54d8c7d54a31d016d8f3c156b98682a"
        if type == "pcr_test":
            url = "https://onemocneni-aktualne.mzcr.cz/api/v3/kraj-okres-testy?page=1&itemsPerPage=100&datum%5Bbefore%5D=XYZ&datum%5Bafter%5D=XYZ&apiToken=c54d8c7d54a31d016d8f3c156b98682a"
        
        current_url = url.replace('XYZ', day)
        req = urllib.request.Request(current_url)
        req.add_header('accept', 'application/json')
        response = urllib.request.urlopen(req)
        data = json.load(response)
        return data
    
    @staticmethod
    def update_data():
        print('[DATABASE-UPDATER] Checking if database is up-to-date')

        updated_dates = []
        updated = False
        hour_now = datetime.now().hour
        date_string_7_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        db = SQLiteDatabase()

        try:
            with db.get_connection():

                latest_date = db.get_date_of_latest_record(None)
                if latest_date is not None:
                    if latest_date != date_string_7_days_ago:

                        # Data in database is not up to date... get all missing days
                        date_7_days_ago = datetime.strptime(date_string_7_days_ago, "%Y-%m-%d")
                        last_date_database = datetime.strptime(latest_date, "%Y-%m-%d")
                        delta_days = (date_7_days_ago - last_date_database).days

                        # Update database
                        for i in range(delta_days):
                            if i == delta_days - 1:
                                if hour_now < 8:
                                    continue
                    
                            # Get string of current date and add it into completed days (for cache updating)
                            update_date = (last_date_database + timedelta(days=i+1)).strftime("%Y-%m-%d")
                            update_date_yesterday = (last_date_database + timedelta(days=i)).strftime("%Y-%m-%d")
                            if update_date not in updated_dates:
                                updated_dates.append(update_date)

                            print(f"[DATABASE-UPDATER] Downloading all datasets for {update_date}...")

                            # **********************
                            # UPDATE INFECTIONS
                            # **********************

                            # Save day results here
                            infections_day_results = Updater._districts.copy()
                            
                            # Get data from MZCR for this day
                            towns = Updater.download_data("infection", update_date)

                            # Initialize districts dictionary
                            for district in infections_day_results:
                                infections_day_results[district] = {}
                                infections_day_results[district]['infections_new'] = 0
                                infections_day_results[district]['infections_active'] = 0
                                infections_day_results[district]['infections_new_7'] = 0
                                infections_day_results[district]['infections_new_14'] = 0
                                infections_day_results[district]['infections_new_65_age'] = 0

                            # Initialize empty district
                            infections_day_results["none"] = {}
                            infections_day_results["none"]['infections_new'] = 0
                            infections_day_results["none"]['infections_active'] = 0
                            infections_day_results["none"]['infections_new_7'] = 0
                            infections_day_results["none"]['infections_new_14'] = 0
                            infections_day_results["none"]['infections_new_65_age'] = 0

                            # Go through all districts for day
                            for town in towns:
                                town_name = town['okres_lau_kod'] if town['okres_lau_kod'] != None else "none"
                                infections_day_results[town_name]['infections_new'] += town['nove_pripady']
                                infections_day_results[town_name]['infections_active'] += town['aktivni_pripady']
                                infections_day_results[town_name]['infections_new_7'] += town['nove_pripady_7_dni']
                                infections_day_results[town_name]['infections_new_14'] += town['nove_pripady_14_dni']
                                infections_day_results[town_name]['infections_new_65_age'] += town['nove_pripady_65']

                            # Save all districts
                            for district in infections_day_results:

                                # Get district name
                                district_name = district if district != "none" else None

                                # All named districts

                                current_record = CovidInfectionDayDistrict.Builder()\
                                        .set_id(0)\
                                        .set_date(update_date)\
                                        .set_district(district_name)\
                                        .set_infections_new(infections_day_results[district]['infections_new'])\
                                        .set_infections_active(infections_day_results[district]['infections_active'])\
                                        .set_infections_new_7(infections_day_results[district]['infections_new_7'])\
                                        .set_infections_new_14(infections_day_results[district]['infections_new_14'])\
                                        .set_infections_new_65_age(infections_day_results[district]['infections_new_65_age'])\
                                        .build()
                                
                                db.insert_record("infection", current_record)

                            # **********************
                            # UPDATE VACCINATIONS
                            # **********************

                            # Save day results here
                            vaccinations_day_results = Updater._districts.copy()
                            
                            # Get data from MZCR for this day
                            vaccinations = Updater.download_data("vaccination", update_date)

                            # Initialize districts dictionary
                            for district in vaccinations_day_results:
                                vaccinations_day_results[district] = {}
                                vaccinations_day_results[district]['vaccination_1_dose_day'] = 0
                                vaccinations_day_results[district]['vaccination_2_dose_day'] = 0
                                vaccinations_day_results[district]['vaccination_3_dose_day'] = 0
                                vaccinations_day_results[district]['vaccination_4_dose_day'] = 0
                                vaccinations_day_results[district]['vaccination_1_dose_alltime'] = 0
                                vaccinations_day_results[district]['vaccination_2_dose_alltime'] = 0
                                vaccinations_day_results[district]['vaccination_3_dose_alltime'] = 0
                                vaccinations_day_results[district]['vaccination_4_dose_alltime'] = 0
                                vaccinations_day_results[district]['vaccination_doses_day'] = 0
                                vaccinations_day_results[district]['vaccination_doses_alltime'] = 0

                                # Add previous day's data to current data
                                response = db.get_record("vaccination", district, update_date_yesterday)
                                vaccinations_day_results[district]['vaccination_1_dose_alltime'] = response[4]
                                vaccinations_day_results[district]['vaccination_2_dose_alltime'] = response[6]
                                vaccinations_day_results[district]['vaccination_3_dose_alltime'] = response[8]
                                vaccinations_day_results[district]['vaccination_4_dose_alltime'] = response[10]
                                vaccinations_day_results[district]['vaccination_doses_alltime'] = response[12]

                            # Go through all vaccination records
                            for vaccination in vaccinations:

                                # Get basic info of vaccination record
                                orp_code = vaccination['orp_bydliste_kod']
                                district_code = None
                                vaccination_order = vaccination['poradi_davky']
                                number_of_doses = vaccination['pocet_davek']

                                # Convert ORP code to district
                                code = db.get_orp(orp_code)
                                if code is None:
                                    # Special Prague situation
                                    if vaccination['kraj_nuts_kod'] == "CZ010" and vaccination['orp_bydliste_kod'] == 0:
                                        district_code = "CZ0100"
                                    else:
                                        continue
                                else:
                                    district_code = code

                                # Now look at order of dose and add it into result (also add into total)
                                if vaccination_order == 1:
                                    vaccinations_day_results[district_code]['vaccination_1_dose_day'] += number_of_doses
                                    vaccinations_day_results[district_code]['vaccination_1_dose_alltime'] += number_of_doses
                                if vaccination_order == 2:
                                    vaccinations_day_results[district_code]['vaccination_2_dose_day'] += number_of_doses
                                    vaccinations_day_results[district_code]['vaccination_2_dose_alltime'] += number_of_doses
                                if vaccination_order == 3:
                                    vaccinations_day_results[district_code]['vaccination_3_dose_day'] += number_of_doses
                                    vaccinations_day_results[district_code]['vaccination_3_dose_alltime'] += number_of_doses
                                if vaccination_order == 4:
                                    vaccinations_day_results[district_code]['vaccination_4_dose_day'] += number_of_doses
                                    vaccinations_day_results[district_code]['vaccination_4_dose_alltime'] += number_of_doses

                                vaccinations_day_results[district_code]['vaccination_doses_day'] += number_of_doses
                                vaccinations_day_results[district_code]['vaccination_doses_alltime'] += number_of_doses

                            # After all records have been saved into result, push it into database
                            for district in vaccinations_day_results:
                                current_record = CovidVaccinationDayDistrict.Builder()\
                                        .set_id(0)\
                                        .set_date(update_date)\
                                        .set_district(district)\
                                        .set_dose_1_day(vaccinations_day_results[district]['vaccination_1_dose_day'])\
                                        .set_dose_1_alltime(vaccinations_day_results[district]['vaccination_1_dose_alltime'])\
                                        .set_dose_2_day(vaccinations_day_results[district]['vaccination_2_dose_day'])\
                                        .set_dose_2_alltime(vaccinations_day_results[district]['vaccination_2_dose_alltime'])\
                                        .set_dose_3_day(vaccinations_day_results[district]['vaccination_3_dose_day'])\
                                        .set_dose_3_alltime(vaccinations_day_results[district]['vaccination_3_dose_alltime'])\
                                        .set_dose_4_day(vaccinations_day_results[district]['vaccination_4_dose_day'])\
                                        .set_dose_4_alltime(vaccinations_day_results[district]['vaccination_4_dose_alltime'])\
                                        .set_doses_day(vaccinations_day_results[district]['vaccination_doses_day'])\
                                        .set_doses_alltime(vaccinations_day_results[district]['vaccination_doses_alltime'])\
                                        .build()

                                db.insert_record("vaccination", current_record)
                            

                            # **********************
                            # UPDATE DEATHS
                            # **********************

                            # Save day results here
                            deaths_day_results = Updater._districts.copy()

                            # Get data from MZCR for this day
                            deaths = Updater.download_data("death", update_date)

                            # Initialize districts dictionary
                            for district in deaths_day_results:
                                deaths_day_results[district] = {}
                                deaths_day_results[district]['deaths_day'] = 0
                                deaths_day_results[district]['deaths_alltime'] = 0

                                # Add previous day's data to current data
                                response = db.get_record("death", district, update_date_yesterday)
                                deaths_day_results[district]['deaths_alltime'] = response[4]

                            # Go through all death records
                            for death in deaths:
                                deaths_day_results[death['okres_lau_kod']]['deaths_day'] += 1
                                deaths_day_results[death['okres_lau_kod']]['deaths_alltime'] += 1

                            # Initialize districts dictionary
                            for district in deaths_day_results:

                                current_record = CovidDeathDayDistrict.Builder()\
                                        .set_id(0)\
                                        .set_date(update_date)\
                                        .set_district(district)\
                                        .set_deaths_day(deaths_day_results[district]['deaths_day'])\
                                        .set_deaths_alltime(deaths_day_results[district]['deaths_alltime'])\
                                        .build()
                                
                                db.insert_record("death", current_record)


                            # **********************
                            # UPDATE TESTS
                            # **********************

                            # Save day results here
                            pcr_testing_day_results = Updater._districts.copy()
                            
                            # Get data from MZCR for this day
                            districts = Updater.download_data("pcr_test", update_date)

                            # Initialize districts dictionary
                            for district in pcr_testing_day_results:
                                pcr_testing_day_results[district] = {}
                                pcr_testing_day_results[district]['pcr_tests_day'] = 0
                                pcr_testing_day_results[district]['pcr_tests_alltime'] = 0
                                pcr_testing_day_results[district]['pcr_tests_day_correction'] = 0
                                pcr_testing_day_results[district]['pcr_tests_alltime_correction'] = 0

                            # Go through all districts for day
                            for district in districts:
                                pcr_testing_day_results[district['okres_lau_kod']]['pcr_tests_day'] = district['prirustkovy_pocet_testu_okres']
                                pcr_testing_day_results[district['okres_lau_kod']]['pcr_tests_alltime'] = district['kumulativni_pocet_testu_okres']
                                pcr_testing_day_results[district['okres_lau_kod']]['pcr_tests_day_correction'] = district['prirustkovy_pocet_prvnich_testu_okres']
                                pcr_testing_day_results[district['okres_lau_kod']]['pcr_tests_alltime_correction'] = district['kumulativni_pocet_prvnich_testu_okres']

                            # Save all districts
                            for district in pcr_testing_day_results:

                                # current_record = CovidPcrTestDayDistrict(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p)
                                current_record = CovidPcrTestDayDistrict.Builder()\
                                        .set_id(0)\
                                        .set_date(update_date)\
                                        .set_district(district)\
                                        .set_tests_new(pcr_testing_day_results[district]['pcr_tests_day'])\
                                        .set_tests_alltime(pcr_testing_day_results[district]['pcr_tests_alltime'])\
                                        .set_tests_new_correction(pcr_testing_day_results[district]['pcr_tests_day_correction'])\
                                        .set_tests_alltime_correction(pcr_testing_day_results[district]['pcr_tests_alltime_correction'])\
                                        .build()
                                
                                db.insert_record("pcr_test", current_record)

                            updated = True
                            db.commit()
                            print(f"[DATABASE-UPDATER] Successfully downloaded all datasets for {update_date}")
            
        except sqlite3.Error as e:
            print(f"[DATABASE-UPDATER] There was an error while downloading and saving data, data have not been committed")
            print(e)

        if len(updated_dates) != 0:
            cache = Cache()
            cache.update_data(updated_dates)

        if updated == True:
            print(f"[DATABASE-UPDATER] Database updated")
            return False
        else:
            print('[DATABASE-UPDATER] Database is up-to-date')
            return True
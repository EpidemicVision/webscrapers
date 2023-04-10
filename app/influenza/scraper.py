import requests
from datetime import datetime
import os
from zipfile import ZipFile
from app.influenza.constants import (
    INFLUENZA_DATA_DIR,
    TRENDS_KEYWORDS,
    STATE_CODE_MAPPER,
)
from app.libs.pytrends.request import TrendReq
import pandas as pd
import os
import time
from random import randint
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import insert
import numpy as np
from decouple import config

current_year = int(datetime.now().strftime("%Y"))
year_2022_id = (
    62  # the ID for year 2022 is 62 on CDC. We need ID to fetch data based on year
)
end_id = current_year - 2022 + year_2022_id
start_id = end_id - 7

engine = create_engine(f'postgresql://{config("DB_USER")}:{config("DB_USER")}@{config("DB_LINK")}/{config("DB_NAME")}', echo=False)
connect = engine.connect()
meta = MetaData()
meta.reflect(bind=engine)


def cdc_ilinet_downloader(download_dir: str = INFLUENZA_DATA_DIR):
    """
    Downloads ilinet data for states and national level.
    Specify the absolute dir where you want to download the files.
    """
    print(
        f"Beginning downloading CDC ILINet data for National Level. Following are the start and end SeasonsDT params {start_id}-{end_id}"
    )

    request_dict_states = {
        "AppVersion": "Public",
        "DatasourceDT": [{"ID": 0, "Name": "WHO_NREVSS"}, {"ID": 1, "Name": "ILINet"}],
        "RegionTypeId": 5,
        "SubRegionsDT": [
            {"ID": 1, "Name": "1"},
            {"ID": 2, "Name": "2"},
            {"ID": 3, "Name": "3"},
            {"ID": 4, "Name": "4"},
            {"ID": 5, "Name": "5"},
            {"ID": 6, "Name": "6"},
            {"ID": 7, "Name": "7"},
            {"ID": 8, "Name": "8"},
            {"ID": 9, "Name": "9"},
            {"ID": 10, "Name": "10"},
            {"ID": 11, "Name": "11"},
            {"ID": 12, "Name": "12"},
            {"ID": 13, "Name": "13"},
            {"ID": 14, "Name": "14"},
            {"ID": 15, "Name": "15"},
            {"ID": 16, "Name": "16"},
            {"ID": 17, "Name": "17"},
            {"ID": 18, "Name": "18"},
            {"ID": 19, "Name": "19"},
            {"ID": 20, "Name": "20"},
            {"ID": 21, "Name": "21"},
            {"ID": 22, "Name": "22"},
            {"ID": 23, "Name": "23"},
            {"ID": 24, "Name": "24"},
            {"ID": 25, "Name": "25"},
            {"ID": 26, "Name": "26"},
            {"ID": 27, "Name": "27"},
            {"ID": 28, "Name": "28"},
            {"ID": 29, "Name": "29"},
            {"ID": 30, "Name": "30"},
            {"ID": 31, "Name": "31"},
            {"ID": 32, "Name": "32"},
            {"ID": 33, "Name": "33"},
            {"ID": 34, "Name": "34"},
            {"ID": 35, "Name": "35"},
            {"ID": 36, "Name": "36"},
            {"ID": 37, "Name": "37"},
            {"ID": 38, "Name": "38"},
            {"ID": 39, "Name": "39"},
            {"ID": 40, "Name": "40"},
            {"ID": 41, "Name": "41"},
            {"ID": 42, "Name": "42"},
            {"ID": 43, "Name": "43"},
            {"ID": 44, "Name": "44"},
            {"ID": 45, "Name": "45"},
            {"ID": 46, "Name": "46"},
            {"ID": 47, "Name": "47"},
            {"ID": 48, "Name": "48"},
            {"ID": 49, "Name": "49"},
            {"ID": 50, "Name": "50"},
            {"ID": 51, "Name": "51"},
            {"ID": 52, "Name": "52"},
            {"ID": 54, "Name": "54"},
            {"ID": 55, "Name": "55"},
            {"ID": 56, "Name": "56"},
            {"ID": 58, "Name": "58"},
            {"ID": 59, "Name": "59"},
        ],
        "SeasonsDT": [{"ID": i, "Name": str(i)} for i in range(start_id, end_id)],
    }

    request_dict_national = {
        "AppVersion": "Public",
        "DatasourceDT": [{"ID": 0, "Name": "WHO_NREVSS"}, {"ID": 1, "Name": "ILINet"}],
        "RegionTypeId": 3,
        "SeasonsDT": [{"ID": i, "Name": str(i)} for i in range(start_id, end_id)],
    }

    url = "https://gis.cdc.gov/grasp/flu2/PostPhase02DataDownload"

    # ---------- National level --------------------
    print(f"[INFO]: Beginning downloading ILINET National data.")
    try:
        resp = requests.post(url, json=request_dict_national, allow_redirects=True)
    except Exception as ex:
        print("Failed to download national data")
        raise ex

    download_file_path = os.path.join(download_dir, "ILINET-National.zip")
    print(
        f"[INFO]: Finished downloading ILINET National data. Extracting it in {download_file_path}"
    )
    # writing zip
    with open(download_file_path, "wb") as f:
        f.write(resp.content)

    # extracting only ILINet.csv in the download_dir
    with ZipFile(download_file_path, "r") as zip_ref:
        zip_ref.extract("ILINet.csv", download_dir)

    # renaming the CSV
    os.rename(
        os.path.join(download_dir, "ILINet.csv"),
        os.path.join(download_dir, "ILINet-National.csv"),
    )
    os.remove(download_file_path)

    # dumping it to db
    table = meta.tables['influenza_ilinet']
    df = pd.read_csv(os.path.join(download_dir, "ILINet-National.csv"), skiprows=[0], na_values="X")
    df.rename(columns={'REGION TYPE':'region_type',
        'REGION': 'region',
        'YEAR': 'year',
        'WEEK': 'week',
        '% WEIGHTED ILI': 'perc_weight_ili',
        '%UNWEIGHTED ILI': 'perc_unweight_ili',
        'AGE 0-4': 'age_0_4',
        'AGE 25-49': 'age_25_49',
        'AGE 25-64': 'age_25_64',
        'AGE 5-24': 'age_5_24',
        'AGE 50-64': 'age_50_64',
        'AGE 65': 'age_65',
        'ILITOTAL': 'ilitotal',
        'NUM. OF PROVIDERS': 'num_providers',
        'TOTAL PATIENTS': 'total_patients',
        },
        inplace=True
    )
    df = pd.DataFrame(df).replace({np.nan: None})

    insert_values = df.to_dict(orient='records')
    insrt_stmnt = insert(table).values(insert_values)

    do_nothing_stmt  = insrt_stmnt.on_conflict_do_nothing("unique_ilinet")#index_elements=["region_type", "region", "year", "week"])
    results = engine.execute(do_nothing_stmt)

    # ---------- State level --------------------
    print(f"[INFO]: Beginning downloading ILINET State data.")
    try:
        resp = requests.post(url, json=request_dict_states, allow_redirects=True)
    except Exception as ex:
        print("Failed to download state data")
        raise ex

    download_file_path = os.path.join(download_dir, "ILINET-State.zip")
    print(
        f"[INFO]: Finished downloading ILINET State data. Extracting it in {download_file_path}"
    )
    # writing zip
    with open(download_file_path, "wb") as f:
        f.write(resp.content)

    # extracting only ILINet.csv in the download_dir
    with ZipFile(download_file_path, "r") as zip_ref:
        zip_ref.extract("ILINet.csv", download_dir)

    # renaming the CSV
    os.rename(
        os.path.join(download_dir, "ILINet.csv"),
        os.path.join(download_dir, "ILINet-State.csv"),
    )
    os.remove(download_file_path)

    df = pd.read_csv(os.path.join(download_dir, "ILINet-State.csv"), skiprows=[0], na_values="X")
    df.rename(columns={'REGION TYPE':'region_type',
        'REGION': 'region',
        'YEAR': 'year',
        'WEEK': 'week',
        '% WEIGHTED ILI': 'perc_weight_ili',
        '%UNWEIGHTED ILI': 'perc_unweight_ili',
        'AGE 0-4': 'age_0_4',
        'AGE 25-49': 'age_25_49',
        'AGE 25-64': 'age_25_64',
        'AGE 5-24': 'age_5_24',
        'AGE 50-64': 'age_50_64',
        'AGE 65': 'age_65',
        'ILITOTAL': 'ilitotal',
        'NUM. OF PROVIDERS': 'num_providers',
        'TOTAL PATIENTS': 'total_patients',
        },
        inplace=True
    )
    df = pd.DataFrame(df).replace({np.nan: None})

    insert_values = df.to_dict(orient='records')
    insrt_stmnt = insert(table).values(insert_values)

    do_nothing_stmt  = insrt_stmnt.on_conflict_do_nothing(index_elements=["region_type", "region", "year", "week"])
    results = engine.execute(do_nothing_stmt)


def trends_scraper(download_dir: str = INFLUENZA_DATA_DIR) -> None:
    terms = TRENDS_KEYWORDS
    timeframe = "today 5-y"
    ggl_complete: pd.DataFrame = None
    table = meta.tables['influenza_gtrends'] # used later on to dump df to db
    requests_args = {
        'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
    }
    pytrends = TrendReq(hl="en-US", tz=360, requests_args=requests_args)

    # first we'll scrape national data
    area = "US"
    print(f"[INFO] Beginning trends scraping with {terms}, {area}, {timeframe}")
    for term in terms:
        pytrends.build_payload(kw_list= [term], timeframe = timeframe, geo = area)
        ggl = pytrends.interest_over_time()
        ggl = ggl.reset_index().drop(columns="isPartial")
        if ggl_complete is None:
            ggl_complete = ggl.copy(deep=True)
        else:
            ggl_complete = ggl_complete.merge(ggl, on="date")
        time.sleep(2)

    ggl_complete['week_number'] = ggl_complete['date'].dt.strftime('%U').astype(int)
    ggl_complete['year'] = ggl_complete['date'].dt.strftime('%Y').astype(int)
    ggl_complete['level'] = 'National'
    ggl_complete['state'] = None
    ggl_complete['state_code'] = None
    ggl_complete.rename(columns={'sore throat': 'sore_throat'}, inplace=True)

    # dumping to db
    insert_values = ggl_complete.to_dict(orient='records')
    insrt_stmnt = insert(table).values(insert_values)
    do_nothing_stmt  = insrt_stmnt.on_conflict_do_nothing("unique_gtrends")#, index_elements=["date", "level", "state", "state_code"])
    # print(do_nothing_stmt)
    results = engine.execute(do_nothing_stmt)

    # saving as csv as well
    ggl_complete.to_csv(os.path.join(download_dir, 'google_trends-National.csv'), index=False)
    print(f"[INFO] Data successfully scraped and saved to {download_dir}.\nData shape: {ggl_complete.shape}")

    complete_df = None
    # now we'll scrape state wise data
    for state_name, state_code in STATE_CODE_MAPPER.items():
        print(
            f"[INFO] Beginning trends scraping with {terms}, {state_code}, {timeframe}"
        )
        # first making a df of all the terms of one state
        state_df = None
        for term in terms:
            pytrends.build_payload(kw_list=[term], timeframe=timeframe, geo=state_code)
            column_df = pytrends.interest_over_time()
            column_df = column_df.reset_index().drop(columns="isPartial")
            if state_df is None:
                state_df = column_df.copy(deep=True)
            else:
                state_df = state_df.merge(column_df, on="date")
            time.sleep(randint(2, 5))

        state_df["state"] = state_name
        state_df["state_code"] = state_code
        state_df["week_number"] = state_df["date"].dt.strftime("%U").astype(int)
        state_df["year"] = state_df["date"].dt.strftime("%Y").astype(int)
        state_df["level"] = "State"
        state_df.rename(columns={'sore throat': 'sore_throat'}, inplace=True)

        # dumping to db
        insert_values = state_df.to_dict(orient='records')
        insrt_stmnt = insert(table).values(insert_values)
        do_nothing_stmt  = insrt_stmnt.on_conflict_do_nothing("unique_gtrends")
        # print(do_nothing_stmt)
        results = engine.execute(do_nothing_stmt)

        # then appending the state df to complete df
        if complete_df is None:
            complete_df = state_df.copy(deep=True)
        else:
            complete_df = pd.concat([complete_df, state_df])

    complete_df.to_csv(
        os.path.join(download_dir, "google_trends-State.csv"), index=False
    )
    print(
        f"[INFO] Data successfully scraped and saved to {download_dir}.\nData shape: {complete_df.shape}"
    )


def scrape_cdc_trends_data(data_dir: str = INFLUENZA_DATA_DIR) -> None:
    if not os.path.exists(INFLUENZA_DATA_DIR):
        os.mkdir(INFLUENZA_DATA_DIR)

    cdc_ilinet_downloader()
    trends_scraper()


if __name__ == "__main__":
    scrape_cdc_trends_data()

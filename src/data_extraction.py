import pandas as pd
from datetime import datetime
import pathlib
import os
from tqdm import tqdm
import time
from git import Repo
from app_config import Bot, git_path
import requests

from joblib import Parallel, delayed
from query_helper import query_id, query_latest_table, get_ids, get_dates

def do_task(_id):
    price_df = query_id(_id, ["prices_kl"])
    gics_df = query_latest_table(table="gics_kl")
    price_df["name"] = gics_df.set_index("id").loc[_id, "company_common_name"]
    price_df = price_df.loc[min_date:]
    return price_df

def run():
    ids = get_ids()
    dfs = Parallel(n_jobs=5)(delayed(do_task)(_id) for _id in tqdm(ids))
    df = pd.concat(dfs)
    df = df.reset_index()[['date', 'name', 'high', 'low']]
    df.to_csv(r'data/bursa_data.csv', index=False)

def send_telegram():
    requests.post(
        "https://api.telegram.org/bot{token}/sendMessage".format(token=Bot.token),
        data={
            "chat_id": Bot.chat_id,
            "text": "[pnf] done point and figure data extraction",
        },
    )


if __name__ == "__main__":

    PATH_OF_GIT_REPO = git_path # make sure .git folder is properly configured
    COMMIT_MESSAGE = "[bot] commit"
    repo = Repo(PATH_OF_GIT_REPO)
    origin = repo.remote(name="origin")
    origin.pull("main")

    min_date = get_dates()[-256]
    run()

    repo.index.add([r"data/bursa_data.csv"])
    repo.git.add(update=True)
    repo.index.commit(COMMIT_MESSAGE)
    origin.push("main")
    send_telegram()

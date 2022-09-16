import json
import pandas as pd
import requests as rq

params = {
    'stationCode': 82689,
    'startDate': '01/01/1984',
    'endDate': '01/03/1984'
}

resp = rq.get('http://server:8888/scrap', params=params)

[_json] = json.loads(resp.content)

_pd = pd.DataFrame(_json)

_pd.to_csv('data/test.csv')
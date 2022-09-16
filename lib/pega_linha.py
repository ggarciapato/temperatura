import os
import time
import json
import pandas as pd
import requests as rq
import datetime as dt


def itera_data(data_inicial, isAuto):
    dt_inicio = max([data_inicial, dt.datetime(1961, 1, 1)])
    data_limite = dt.datetime(2021, 12, 1)
    _di = dt_inicio
    while _di < data_limite:
        _df = _di + dt.timedelta(days=60 if isAuto else 150)
        if _df >= data_limite:
            _df = data_limite - dt.timedelta(days=1)
        out = (_di, _df)
        _di = _df + dt.timedelta(days=1)

        yield out
 

def pega_linha(row):

    estacao = row.CD_ESTACAO
    fn = 'data/estacoes/{n}_{i}_{f}.csv'
    _dt = row.DT_INICIO_OPERACAO

    isAuto = 'A' in estacao or 'B' in estacao

    if isAuto:
        new_cols = [
            'data', 'hora_utc', 'temperatura_C', 'temp_min_C', 'temp_max_C',
            'umidade_relativa', 'umidade_min', 'umidade_max', 
            'orvalho_C', 'orvalho_min_C', 'orvalho_max_C', 'pressao_hpa',
            'pressao_min_hpa', 'pressao_max_hpa', 'velocidade_vento_ms', 
            'direcao_vento_grad', 'rajada_vento_ms', 'radiacao_kjmq', 'chuva_mm'
        ]
    else:
        new_cols = [
            'data', 'hora_utc', 'temperatura_C', 'umidade_relativa',
            'pressao_hpa', 'velocidade_vento_ms', 'direcao_vento_grad', 
            'nebulosidade_dec', 'insolacao_h', 'temp_max_C', 
            'temp_min_C', 'chuva_mm'
        ]   

    for (dt_inicio, dt_final) in itera_data(_dt, isAuto):
        fp = fn.format(
            n=estacao, 
            i=dt_inicio.strftime('%Y-%m-%d'), 
            f=dt_final.strftime('%Y-%m-%d')
        )

        # print(fp, end=': ')

        if os.path.isfile(fp):
           # print('file found, skipping')
           continue

        params = {
            'stationCode': estacao,
            'startDate': dt_inicio.strftime('%d/%m/%Y'),
            'endDate': dt_final.strftime('%d/%m/%Y')
        }

        while True:
            try:
                resp = rq.get('http://server:8888/scrap', params=params)
                [_json] = json.loads(resp.content)
                break
            except ValueError:
                time.sleep(10)

        _pd = pd.DataFrame(_json)
        _pd = _pd.rename(columns=dict(zip(_pd.columns, new_cols)))
        _pd.to_csv(fp, index=False, sep=';')
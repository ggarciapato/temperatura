import re
import datetime as dt
import os
import pandas as pd
import utils.database as pg

loc_id = 0

reg_id = 0

files = ['data/' + loc for loc in os.listdir('data')]

rename_d = {
    'Precipitacao': 'precipitacao',
    'TempBulboSeco': 'temp_bulbo_seco',
    'TempBulboUmido': 'temp_bulbo_umido',
    'TempMaxima': 'temp_maxima',
    'TempMinima': 'temp_minima',
    'UmidadeRelativa': 'umidade_relativa',
    'PressaoAtmEstacao': 'pressao_atm_estacao',
    'PressaoAtmMar': 'pressao_atm_mar',
    'DirecaoVento': 'direcao_vento',
    'VelocidadeVentoInsolacao': 'velocidade_vento_insolacao',
    'Nebulosidade': 'nebulosidade',
    'Evaporacao Piche': 'evaporacao_piche',
    'Temp Comp Media': 'temp_comp_media',
    'Umidade Relativa Media': 'umidade_relativa_media',
    'Velocidade do Vento Media': 'velocidade_vento_media'
}


estacoes_pd = pd.read_csv('estacoes.csv', delimiter=';')

estacoes_pd = estacoes_pd.rename(columns={'NOME DA ESTAÇÃO': 'nome', 'CODIGO OMM': 'codigo_omm'})

loc_names = ['codigo_omm', 'latitude', 'longitude', 'altitude']


for file in files:

    print(file.replace('.txt', ''))

    content = ''

    loc_values = []

    with open(file, 'r') as f:
        for i in range(7):
            if i > 2:
                content = next(f)
                content = re.sub('[^0-9|\.\-]', '', content)
                loc_values.append(float(content))
            else:
                next(f)

    loc_values[0] = - int(loc_values[0])

    loc_d = dict(zip(loc_names, loc_values))

    [nome] = estacoes_pd.loc[estacoes_pd.codigo_omm == loc_d['codigo_omm']].nome.tolist()

    loc_d['nome'] = nome
    loc_d['localidade_id'] = loc_id
    loc_id += 1

    loc_pg = pg.Localidade(**loc_d)

    pg.session.add(loc_pg)

    file_pd = pd.read_csv(file, skiprows=16, delimiter=';', index_col=False)

    datetimes = []

    for row in file_pd.itertuples():
        [d, m, y] = [int(v) for v in row.Data.split('/')]
        h = int(row.Hora) / 100
        new_dt = dt.datetime(y, m, d, int(h))
        datetimes.append(new_dt)

    file_pd['datahora'] = datetimes

    file_pd = file_pd.rename(columns=rename_d)

    file_pd = file_pd.drop(columns=['Unnamed: 18', 'Estacao', 'Data', 'Hora'])

    file_pd = file_pd.where((pd.notnull(file_pd)), None)

    registros = file_pd.to_dict(orient='records')

    for reg_d in registros:
        reg_d['registro_id'] = reg_id
        reg_id += 1
        reg_pg = pg.Registro(**reg_d)
        loc_pg.registros.append(reg_pg)
        if not reg_id % 1000:
            pg.session.commit()

    pg.session.commit()

pg.session.close()


import os
import pandas as pd
import lib.pg_temperatura as pg


def insert_registry():
    registro_cols = [
        'data',
        'hora_utc',
        'temperatura_C',
        'umidade_relativa',
        'pressao_hpa',
        'velocidade_vento_ms',
        'direcao_vento_grad',
        'nebulosidade_dec',
        'insolacao_h',
        'temp_max_C',
        'temp_min_C',
        'chuva_mm',
        'umidade_min',
        'umidade_max',
        'orvalho_C',
        'orvalho_min_C',
        'orvalho_max_C',
        'pressao_min_hpa',
        'pressao_max_hpa',
        'rajada_vento_ms',
        'radiacao_kjmq'
    ]

    fd_in = 'data/estacoes'
    files = [os.path.join(fd_in, f) for f in os.listdir(fd_in)]

    counter_orm = (
        pg.session
        .query(pg.Registro)
        .order_by(pg.Registro._registro.desc())
        .first()
    )

    if counter_orm:
        counter = counter_orm._registro + 1
    else: 
        counter = 0

    for fp in files:
        station_number = fp.split('_')[0]
        station_orm = (
            pg.session
            .query(pg.Estacao)
            .filter(pg.Estacao.cd_estacao == station_number)
            .one()
        )
        f_pd = pd.read_csv(fp, sep=';', decimal=',')[registro_cols]
        for row_d in f_pd.to_dict(orient='records'):
            if row_d['temperatura_C']:
                entry = pg.Registro(**{'_registro': counter, **row_d})
                station_orm._registros.append(entry)
                # pg.session.add(entry)
                counter += 1

        if not counter % 10000:
            print(counter)
            pg.session.commit()

    pg.session.commit()


def insert_station():
    stations = pd.read_csv('data/estacoes.csv', sep='\t')
    stations = stations.rename(columns=lambda x: x.lower())

    counter_orm = (
        pg.session
        .query(pg.Estacao)
        .order_by(pg.Estacao._estacao.desc())
        .first()
    )

    if counter_orm:
        counter = counter_orm._estacao + 1
    else: 
        counter = 0

    for row_d in stations.to_dict(orient='records'):
        entry = pg.Estacao(**{"_estacao": counter, **row_d})
        counter += 1
        pg.session.add(entry)

    pg.session.commit()


def insert_altitude():
    altitude = pd.read_csv('data/altitude_grid.csv')
    counter_orm = (
        pg.session
        .query(pg.Altitude)
        .order_by(pg.Altitude._altitude.desc())
        .first()
    )

    if counter_orm:
        counter = counter_orm._altitude + 1
    else: 
        counter = 0

    for row_d in altitude.to_dict(orient='records'):
        entry = pg.Altitude(**{"_altitude": counter, **row_d})
        counter += 1
        pg.session.add(entry)

        if not counter % 1000:
            pg.session.commit()

    pg.session.commit()


def main():
    insert_station()
    insert_altitude()
    insert_registry()


if __name__ == "__main__":
    main()
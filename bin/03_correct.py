# %%
import pandas as pd
import datetime as dt
import lib.pg_temperatura as pg
from sqlalchemy import delete, update

# %%
# rep_q = (
#     pg.session
#     .query(pg.Estacao, pg.Registro)
#     .join(pg.Estacao._registros)
#     .filter(
#         pg.Estacao.cd_estacao == "83536", 
#         pg.Registro.data.between(
#             dt.datetime(1995, 9, 24), dt.datetime(1996, 2, 21)
#         )
#     )
# )

# rep_pd = pd.read_sql(rep_q.statement, pg.connect)

# # %%
# rep_pd[['data', '_registro']].sort_values(by='data').tail(10)
# # %%
# low_index = 6095407
# upp_index = 6095859

# indexes = list(range(low_index, upp_index + 1))

# # %%
# del_q = delete(pg.Registro).where(pg.Registro._registro.in_(indexes))
# pg.session.execute(del_q)

# # %%
# pg.session.commit()

# %%
station_pd = pd.read_sql(
    (
        pg.session
        .query(pg.Estacao)
        .filter(pg.Estacao.cd_estacao.like('8%'))
        .statement
    ), 
    pg.connect
)

to_correct = [lat < -100 or long < -100 for (lat, long) in zip(station_pd.vl_longitude, station_pd.vl_latitude)]

station_pd = station_pd.loc[to_correct]

# have to correct some points
station_pd = station_pd.assign(
    vl_longitude=[val / 1000 if val < -100 else val for val in station_pd.vl_longitude],
    vl_latitude=[val / 1000 if val < -100 else val for val in station_pd.vl_latitude]
)

# %%
for row in station_pd.to_dict(orient='records'):
    stmt = (
        update(pg.Estacao)
        .where(pg.Estacao._estacao == row["_estacao"])
        .values(
            vl_latitude=row["vl_latitude"],
            vl_longitude=row["vl_longitude"]
        )
    )

    pg.session.execute(stmt)

pg.session.commit()
# %%
import pandas as pd
import geopandas as gp
import lib.pg_temperatura as pg
import lib.pg_brasil as br
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import warnings
import numpy as np

warnings.filterwarnings('ignore')

plt.style.use('dark_background')

# %%
altitude_q = pg.session.query(pg.Altitude)
altitude_pd = pd.read_sql(altitude_q.statement, pg.connect)
altitude_gp = gp.GeoDataFrame(
    altitude_pd, 
    geometry=gp.points_from_xy(altitude_pd.longitude, altitude_pd.longitude)
)

station_pd = pd.read_sql(
    (
        pg.session
        .query(pg.Estacao)
        .filter(pg.Estacao.cd_estacao.like('8%'))
        .statement
    ), 
    pg.connect
)

station_gp = gp.GeoDataFrame(
    station_pd, 
    geometry=gp.points_from_xy(
        station_pd.vl_longitude,
        station_pd.vl_latitude
    )
)

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
          'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
           cmap(np.linspace(minval, maxval, n)))
    return new_cmap    


cmap = plt.get_cmap('terrain')
new_cmap = truncate_colormap(cmap, 0.23, 1)

# %%
ax = altitude_gp.plot(column='altitude', legend=True, markersize=0.1, cmap=new_cmap)
ax = station_gp.plot(column='vl_altitude', ax=ax, markersize=1)
# of = plt.axis('off')
# %%

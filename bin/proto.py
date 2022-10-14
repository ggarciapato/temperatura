# %%
import os
# import csv
# import pandas as pd
# import geopandas as gp
# import lib.pg_brasil as br
# import matplotlib.pyplot as plt

# plt.style.use('dark_background')

# %%
fd = 'data/estacoes'
files = os.listdir(fd)

files.sort()
print(files.index("83526_2013-02-03_2013-07-03.csv"))

# len(files)

# # %%
# colnames = []

# for file in files:
#     fp = os.path.join(fd, file)
#     with open(fp, 'r') as f:
#         it = csv.DictReader(f, delimiter=';')
#         first = next(it)
#         ks = first.keys()
#         for k in ks:
#             if k not in colnames:
#                 colnames.append(k)
# # %%
# for col in colnames:
#     print(f'{col} = Column(Float)')
# # %%
# estacoes = pd.read_csv("data/estacoes.csv", sep="\t")

# # %%
# estacoes = estacoes.rename(columns=lambda x: x.lower())

# # %%
# for col in estacoes.columns:
#     print(f'{col} = Column()')


# # %%
# brasil_q = br.session.query(br.UF)
# brasil_gp = gp.read_postgis(brasil_q.statement, br.connect, 'geometria')

# # %%
# brasil_gp.plot()
# plt.axis('off')

# # %%
# altitude = pd.read_csv('data/altitude_grid.csv')
# # %%
# altitude_gp = gp.GeoDataFrame(altitude, geometry=gp.points_from_xy(altitude.longitude, altitude.latitude))

# # %%
# altitude_gp.plot(column='altitude', markersize=0.1)
# a = plt.axis('off')
# plt.savefig('out/cover.png')
# # %%

#!/usr/bin/python3
import pandas as pd
import datetime as dt
from lib.pega_linha import pega_linha


def main():
    estacoes = pd.read_csv('data/estacoes_convencionais.csv', sep='\t')
    estacoes = estacoes.assign(
        DT_INICIO_OPERACAO=[    
            dt.datetime.strptime(d, '%d/%m/%Y')
            for d in estacoes.DT_INICIO_OPERACAO
        ]
    )

    for row in estacoes.itertuples():
        # print(row.CD_ESTACAO)
        pega_linha(row)


if __name__ == '__main__':
    main()
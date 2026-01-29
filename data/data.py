import pandas as pd

def Data():

    df = pd.read_csv('abastecimentos__01012020.csv', sep=';')

    # colunas numéricas com vírgula decimal
    colunas_float = [
        'abastecimentoqtd',
        'quantidade',
        'valor_unitario',
        'valor_total',
        'medicao_atual'
    ]

    for col in colunas_float:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(',', '.', regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # coluna inteira
    df['codigo_veiculo'] = pd.to_numeric(
        df['codigo_veiculo'],
        errors='coerce'
    ).astype('Int64')

    # data e hora
    df['data_hora'] = pd.to_datetime(
        df['data_hora'],
        dayfirst=True,
        errors='coerce'
    )

    df['ano'] = df['data_hora'].dt.year
    df['mes'] = df['data_hora'].dt.month


    return df
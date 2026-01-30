from pathlib import Path
import pandas as pd


base_dir = Path(__file__).resolve().parent
csv_path = base_dir / 'Abastecimentos _01012015.csv'
csv_path_secretaria = base_dir / 'centro_de_custos.csv'

def data():

    df = pd.read_csv(csv_path, sep=';')
    df_secretaria = pd.read_csv(csv_path_secretaria, sep='\t')

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
            .str.replace('R$', '', regex=False)
            .str.replace('.', '', regex=False)   # remove milhar
            .str.replace(',', '.', regex=False)  # decimal
            .str.strip()
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
    df['ano_mes'] = (
        df['ano'].astype(str) + '-' +
        df['mes'].astype(str).str.zfill(2)
    )


    df = df.merge(
        df_secretaria[['centro_de_custos', 'secretaria']],
        on='centro_de_custos',
        how='left'
    )

    return df

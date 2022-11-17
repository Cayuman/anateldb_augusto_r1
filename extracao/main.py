# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/main.ipynb.

# %% auto 0
__all__ = ['bump_version', 'get_modtimes', 'check_modify_row', 'add_aero', 'get_db']

# %% ../nbs/main.ipynb 2
from pathlib import Path
import json
from typing import Union
from datetime import datetime
from tqdm.auto import tqdm

import pandas as pd
from fastcore.test import *
from fastcore.script import call_parse, Param, store_true
from pyarrow import ArrowInvalid
from geopy.distance import geodesic
from rich import print
import pyodbc
from pymongo import MongoClient

from .constants import APP_ANALISE
from .reading import read_base, read_aero
from .merging import merge_aero
from .format import df_optimize, optimize_objects
from .merging import get_subsets, check_add_row, product, MAX_DIST

# %% ../nbs/main.ipynb 3
def bump_version(
    version: str,  # String com a versão atual
    part: int = 2,  # Parte da versão que será incrementada
) -> str:  # Retorna a versão atualizada
    version = version.split(".")
    version[part] = str(int(version[part]) + 1)
    for i in range(part + 1, 3):
        version[i] = "0"
    return ".".join(version)

# %% ../nbs/main.ipynb 4
def get_modtimes(
    pasta: Union[str, Path],  # Pasta onde estão os arquivos esperados de monitoramento
) -> dict:  # Retorna o mtime de todos os arquivos pertinentes da pasta
    """
    Retorna a data de modificação dos arquivos de dados contidos na pasta
    """
    # Pasta
    pasta = Path(pasta)
    if not pasta.is_dir():
        raise FileNotFoundError(f"Pasta {pasta} não encontrada")
    # Arquivos
    for suffix in [".parquet.gzip", ".fth", ".xlsx"]:
        if not (stel := pasta / f"stel{suffix}").is_file():
            raise FileNotFoundError(f"Arquivo {stel} não encontrado")
        if not (radcom := pasta / f"radcom{suffix}").is_file():
            raise FileNotFoundError(f"Arquivo {radcom} não encontrado")
        if not (mosaico := pasta / f"mosaico{suffix}").is_file():
            raise FileNotFoundError(f"Arquivo {mosaico} não encontrado")
        break
    if not (icao := pasta / "icao.xlsx").is_file():  # ICAO
        raise FileNotFoundError(f"Arquivo {icao} não encontrado")
    if not (pmec := pasta / "aisw.xlsx").is_file():  # PMEC
        raise FileNotFoundError(f"Arquivo {pmec} não encontrado")
    if not (geo := pasta / "aisg.xlsx").is_file():  # GEO
        raise FileNotFoundError(f"Arquivo {geo} não encontrado")
    # Modificação
    mod_stel = datetime.fromtimestamp(stel.stat().st_mtime).strftime(
        "%d/%m/%Y %H:%M:%S"
    )
    mod_radcom = datetime.fromtimestamp(radcom.stat().st_mtime).strftime(
        "%d/%m/%Y %H:%M:%S"
    )
    mod_mosaico = datetime.fromtimestamp(mosaico.stat().st_mtime).strftime(
        "%d/%m/%Y %H:%M:%S"
    )
    mod_icao = pd.read_excel(icao, engine="openpyxl", sheet_name="ExtractDate").columns[
        0
    ]
    mod_aisw = pd.read_excel(pmec, engine="openpyxl", sheet_name="ExtractDate").columns[
        0
    ]
    mod_aisg = pd.read_excel(geo, engine="openpyxl", sheet_name="ExtractDate").columns[
        0
    ]
    return {
        "STEL": mod_stel,
        "SRD": mod_radcom,
        "MOSAICO": mod_mosaico,
        "ICAO": mod_icao,
        "AISW": mod_aisw,
        "AISG": mod_aisg,
    }

# %% ../nbs/main.ipynb 5
def check_modify_row(
    df,  # DataFrame para mesclar adicionar o registro
    f,  # Frequência (MHz) em análise do registro
    rows,  # Lista de registros para mesclar
    dicts,  # Dicionário fonte dos registros
) -> pd.DataFrame:  # Retorna o DataFrame com o registro adicionado se necessário
    """Mescla os registros em `rows` de frequência `f` e os adiciona como uma linha do DataFrame `df`
    Os registros em `rows` somente são mesclados se ainda constarem nos dicionários fonte `dicts`
    Após a mesclagem, os registros são removidos dos dicionários fonte `dicts`
    """
    if all(row.Index in dict for row, dict in zip(rows, dicts)):
        lat = sum(row.Latitude for row in rows) / len(rows)
        long = sum(row.Longitude for row in rows) / len(rows)
        desc = " | ".join(row.Description for row in rows)
        d = {"Frequency": f, "Latitude": lat, "Longitude": long, "Description": desc}
        for row, dict in zip(rows, dicts):
            dict.pop(row.Index)
        for k, v in d.items():
            df.loc[row.Index, k] = v
    return df

# %% ../nbs/main.ipynb 6
def add_aero(
    base,  # Base Consolidada Anatel
    aero,  # Base da Aeronáutica
    dist: float = MAX_DIST,  # Distância máxima entre as coordenadas
) -> pd.DataFrame:  # Retorna o DataFrame com o registro adicionados e mesclados
    # sourcery skip: use-fstring-for-concatenation
    """Mescla os registros de frequência em comum da base da Aeronáutica com a base da Anatel
    Os registros são mesclados se a distância entre eles for menor que `MAX_DIST`
    do contrário são adicionados individualmente como uma linha na base da Anatel`
    """
    aero_freqs = set(aero.Frequency.unique())
    frequencies = set(base.Frequency.unique()).intersection(aero_freqs)
    extras = aero_freqs.difference(frequencies)
    extras = list(aero[aero.Frequency.isin(extras)].itertuples())
    for f in (pbar := tqdm(frequencies)):
        sa, sb = get_subsets(f, base, aero)
        while all([sa, sb]):
            combinations = list(product(sa.copy().values(), sb.copy().values()))
            for fa, fb in combinations:
                pbar.set_description(
                    f"Frequency {f}MHz, #Combinations {len(combinations)}"
                )
                if (
                    geodesic(
                        (fa.Latitude, fa.Longitude), (fb.Latitude, fb.Longitude)
                    ).km
                    <= dist
                ):
                    base.loc[fa.Index, "Description"] = (
                        fa.Description + " | " + fb.Description
                    )
                    sa.pop(fa.Index)
                    sb.pop(fb.Index)
                    break
            else:
                if sb:
                    d = pd.DataFrame(sb.values()).drop("Index", axis=1)
                    base = pd.concat([base, d], ignore_index=True)
                    sb = None
    for row in (pbar := tqdm(extras)):
        pbar.set_description(f"Frequency {row.Frequency}MHz - Extra")
        d = pd.DataFrame(
            {
                "Frequency": row.Frequency,
                "Latitude": row.Latitude,
                "Longitude": row.Longitude,
                "Description": row.Description,
            },
            index=[0],
        )
        base = pd.concat([base, d], ignore_index=True)
    return base

# %% ../nbs/main.ipynb 7
def get_db(
    path: Union[str, Path],  # Pasta onde salvar os arquivos",
    connSQL: pyodbc.Connection = None,  # Objeto de conexão do banco SQL Server
    clientMongoDB: MongoClient = None,  # Objeto de conexão do banco MongoDB
    dist: float = MAX_DIST,  # Distância máxima entre as coordenadas consideradas iguais
) -> pd.DataFrame:  # Retorna o DataFrame com as bases da Anatel e da Aeronáutica
    """Lê e opcionalmente atualiza as bases da Anatel, mescla as bases da Aeronáutica, salva e retorna o arquivo
    A atualização junto às bases de dados da Anatel é efetuada caso ambos objetos de banco `connSQL` e `clientMongoDB` forem válidos`
    """
    dest = Path(path)
    dest.mkdir(parents=True, exist_ok=True)
    print(":scroll:[green]Lendo as bases de dados da Anatel...")
    if not all([connSQL, clientMongoDB]):
        cached_file = dest / "AnatelDB.parquet.gzip"
        if cached_file.exists():
            return pd.read_parquet(cached_file)
    rd = read_base(path, connSQL, clientMongoDB)
    rd["Descrição"] = (
        "["
        + rd.Fonte.astype("string").fillna("NI")
        + "] "
        + rd.Status.astype("string").fillna("NI")
        + ", "
        + rd.Classe.astype("string").fillna("NI")
        + ", "
        + rd.Entidade.astype("string").fillna("NI").str.title()
        + " ("
        + rd.Fistel.astype("string").fillna("NI")
        + ", "
        + rd["Número_Estação"].astype("string").fillna("NI")
        + "), "
        + rd.Município.astype("string").fillna("NI")
        + "/"
        + rd.UF.astype("string").fillna("NI")
    )

    export_columns = [
        "Frequência",
        "Latitude",
        "Longitude",
        "Descrição",
        "Num_Serviço",
        "Número_Estação",
        "Classe_Emissão",
        "BW(kHz)",
    ]
    rd = rd.loc[:, export_columns]
    rd.columns = APP_ANALISE
    print(":airplane:[blue]Adicionando os registros da Aeronáutica.")
    aero = read_aero(path, update=False)  # NotImplemented update
    rd = add_aero(rd, aero, dist)
    print(":card_file_box:[green]Salvando os arquivos...")
    versiondb = json.loads((dest.parent / "VersionFile.json").read_text())
    mod_times = get_modtimes(path)
    mod_times["ReleaseDate"] = datetime.today().strftime("%d/%m/%Y %H:%M:%S")
    for c in ["Latitude", "Longitude"]:
        rd.loc[:, c] = rd.loc[:, c].fillna(-1).astype("float32")

    rd["Frequency"] = rd["Frequency"].astype("float64")
    rd["Description"] = rd["Description"].astype("string").fillna("NI")
    rd["Service"] = rd.Service.astype("string").fillna("-1")
    rd["Station"] = rd.Station.astype("string").fillna("-1")
    rd.loc[rd.Station == "", "Station"] = "-1"
    rd.loc[rd.BW == "", "BW"] = "-1"
    rd["BW"] = rd["BW"].astype("float32").fillna(-1)
    rd["Class"] = rd.Class.astype("string").fillna("NI")
    rd = (
        rd.drop_duplicates(keep="first")
        .sort_values(by=["Frequency", "Latitude", "Longitude"])
        .reset_index(drop=True)
    )
    rd["Id"] = [f"#{i+1}" for i in rd.index]
    rd["Id"] = rd.Id.astype("string")
    rd = rd.loc[
        :,
        [
            "Id",
            "Frequency",
            "Latitude",
            "Longitude",
            "Description",
            "Service",
            "Station",
            "Class",
            "BW",
        ],
    ]
    rd.to_parquet(f"{dest}/AnatelDB.parquet.gzip", compression="gzip", index=False)
    versiondb["anateldb"]["Version"] = bump_version(versiondb["anateldb"]["Version"])
    versiondb["anateldb"].update(mod_times)
    json.dump(versiondb, (dest.parent / "VersionFile.json").open("w"))
    print("Sucesso :zap:")
    return rd
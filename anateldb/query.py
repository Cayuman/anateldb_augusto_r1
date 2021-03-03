# AUTOGENERATED! DO NOT EDIT! File to edit: queries.ipynb (unless otherwise specified).

__all__ = ['ESTACOES', 'PLANO_BASICO', 'HISTORICO', 'COL_ESTACOES', 'COL_PLANO_BASICO', 'TELECOM', 'RADIODIFUSAO',
           'RADCOM', 'STEL', 'connect_db', 'update_radcom', 'update_stel', 'update_mosaico']

# Cell
import requests
from pathlib import Path
import pandas as pd
import pyodbc
from fastcore.test import *

# Cell
ESTACOES = 'http://sistemas.anatel.gov.br/se/public/file/b/srd/estacao_rd.zip'
PLANO_BASICO = 'http://sistemas.anatel.gov.br/se/public/file/b/srd/PlanoBasico.zip'
HISTORICO = 'http://sistemas.anatel.gov.br/se/public/file/b/srd/documento_historicos.zip'
COL_ESTACOES = ('@SiglaServico', '@state', '@entidade', '@fistel', '@cnpj', '@municipio', '@uf', '@id')
COL_PLANO_BASICO = ('@id', '@Classe', '@Frequencia', '@Latitude', '@Longitude')
TELECOM = ('Frequência', 'Serviço', 'Entidade', 'Fistel', 'Número da Estação', 'Município', 'UF', 'Latitude', 'Longitude')
RADIODIFUSAO = ('Frequência', 'Status', 'Classe', 'Entidade', 'Fistel', 'Número da Estação', 'Município', 'UF', 'Latitude', 'Longitude')

# Cell
RADCOM = """
       select f.MedFrequenciaInicial as 'Frequência',
       Sitarweb.dbo.FN_SRD_RetornaIndFase(PB.NumServico, Pr.idtPedidoRadcom) as 'Fase',
       Sitarweb.dbo.FN_SRD_RetornaSiglaSituacao(h.IdtHabilitacao, Es.IdtEstacao) as 'Situação',
       uf.SiglaUnidadeFrequencia as 'Unidade',
       e.NomeEntidade as 'Entidade',
       h.NumFistel as 'Fistel',
       es.NumEstacao as 'Número da Estação',
       m.NomeMunicipio as 'Município',
       pb.SiglaUF as 'UF',
       es.MedLatitudeDecimal as 'Latitude',
       es.MedLongitudeDecimal as 'Longitude',
       e.NumCnpjCpf as 'CNPJ'
from ENTIDADE e
inner join HABILITACAO h on h.IdtEntidade = e.IdtEntidade
inner join SRD_PEDIDORADCOM pr on pr.IdtHabilitacao = h.IdtHabilitacao
inner join SRD_PLANOBASICO pb on pb.IdtPlanoBasico = pr.IdtPlanoBasico
inner join estacao es on es.IdtHabilitacao = h.IdtHabilitacao
inner join FREQUENCIA f on f.IdtEstacao = es.IdtEstacao
inner join UnidadeFrequencia uf on uf.IdtUnidadeFrequencia = f.IdtUnidadeFrequencia
inner join Municipio m on m.CodMunicipio = pb.CodMunicipio
where h.NumServico = '231'
"""

# Cell
STEL = """IF OBJECT_ID('tempDB..##faixas','U') is not null
drop table ##faixas
create table ##faixas (id int not null, faixa varchar(20), inic float, fim float,);
insert into ##faixas values(0,'De 20 MHz - 6 GHz','20000', '6000000');

select distinct f.MedTransmissaoInicial as 'Frequência',
uf.SiglaUnidadeFrequencia as 'Unidade',
e.NumServico as 'Serviço',
ent.NomeEntidade as 'Entidade',
h.NumFistel as 'Fistel',
e.NumEstacao as 'Número da Estação',
mu.NomeMunicipio as 'Município',
e.SiglaUf as 'UF',
e.MedLatitudeDecimal as 'Latitude',
e.MedLongitudeDecimal as 'Longitude',
ent.NumCnpjCpf as 'CNPJ'
from contrato c
inner join estacao e on e.IdtContrato = c.Idtcontrato
inner join frequencia f on f.IdtEstacao = e.IdtEstacao
inner join HABILITACAO h on h.IdtHabilitacao = c.IdtHabilitacao
inner join entidade ent on ent.IdtEntidade = h.IdtEntidade
inner join endereco en on en.IdtEstacao = e.IdtEstacao
inner join Municipio mu on mu.CodMunicipio = en.CodMunicipio
inner join Servico s on s.NumServico = h.NumServico and s.IdtServicoAreaAtendimento = 4
left join UnidadeFrequencia uf on uf.IdtUnidadeFrequencia = f.IdtUnidadeTransmissao
left outer join ##faixas fx on (
(fx.inic <= f.MedRecepcaoInicialKHz and fx.fim >= f.MedRecepcaoInicialKHz)
or (fx.inic <= f.MedTransmissaoInicialKHz and fx.fim >= f.medtransmissaoinicialkhz)
or (fx.inic <= f.MedFrequenciaInicialKHz and fx.fim >= f.MedFrequenciaInicialKHz)
or (fx.inic <= f.MedFrequenciaFinalKHz and fx.fim >= f.MedFrequenciaFinalKHz)
)
where e.DataExclusao is null and
fx.faixa is not null and
f.MedTransmissaoInicial is not null
and h.NumServico <> '010'
"""

# Cell
def connect_db():
    """Conecta ao Banco ANATELBDRO01 e retorna o 'cursor' (iterador) do Banco pronto para fazer iterações"""
    conn = pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=ANATELBDRO01;"
        "Database=SITARWEB;"
        "Trusted_Connection=yes;"
        "MultipleActiveResultSets=True;"
    )

    return conn

# Cell
def update_radcom(folder):
    """Update the Radcom File querying the Database"""
    conn = connect_db()
    print("Lendo o Banco de Dados de Radcom")
    pd.read_sql_query(RADCOM, conn).to_feather(f'{folder}/radcom.fth')

def update_stel(folder):
    """Update the Stel File querying the Database"""
    conn = connect_db()
    print("Lendo o Banco de Dados do STEL. Processo Lento, aguarde...")
    pd.read_sql_query(STEL, conn).to_feather(f'{folder}/stel.fth')

def update_mosaico(pasta):
    """Update the Mosaico File by downloading the zipped xml file from the Spectrum E Web page"""
    print("Baixando as Estações do Mosaico...")
    file = requests.get(ESTACOES)
    with open(f'{pasta}/estações.zip', 'wb') as estações:
        estações.write(file.content)
    print("Baixando o Plano Básico das Estações...")
    file = requests.get(PLANO_BASICO)
    with open(f'{pasta}/plano_basico.zip', 'wb') as plano_basico:
        plano_basico.write(file.content)
    print("Baixando o Histórico de Atualizações...")
    file = requests.get(HISTORICO)
    with open(f'{pasta}/historico.zip', 'wb') as historico:
        historico.write(file.content)
    print("Kbô")
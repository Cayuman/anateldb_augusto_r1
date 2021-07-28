# Anatel - Consulta e Processamento do Banco de Dados
> Este reposit�rio concentra um conjunto de scripts para navegar e baixar informa��es dos principais bancos de dados da Anatel. Cujo dados ser�o utilizados em tarefas fiscalizat�rias. O p�blico alvo s�o os servidores do �rg�o, uma vez que a maioria dos sistemas utilizados aqui necessitam de autentica��o cujo acesso � restrito aos servidores da ANATEL.


## Instala��o

<code>pip install anateldb</code>

## Como utilizar

### M�todos para baixar ou atualizar os arquivos das bases de dados

```python
from anateldb.query import update_mosaico, update_radcom, update_stel
```

A fun��o seguinte baixa os dados diretamente da interface p�blica online do [Spectrum E](http://sistemas.anatel.gov.br/se/public/view/b/srd.php) 

```python
%%time
update_mosaico(pasta='D:\OneDrive - ANATEL\GR01FI3\BaseDados')
```

    Baixando as Esta��es do Mosaico...
    Baixando o Plano B�sico das Esta��es...
    Baixando o Hist�rico de Atualiza��es...
    Kb�
    Wall time: 8.12 s


```python
%%time
update_radcom('D:\OneDrive - ANATEL\GR01FI3\BaseDados')
```

    Lendo o Banco de Dados de Radcom
    Wall time: 1 s

A fun��o <code>update_stel</code> � bem mais lenta que as demais, dado que o banco de dados do STEL � antigo e abarca todos os registros de outorga de servi�os de telecomunica��es da ANATEL, com mais de **400.000** registros ativos. Esse banco de dados � atualizado 1 vez ao dia � meia-noite e remete ao estado do dia anterior, portanto n�o faz sentido atualiz�-lo mais de 1 vez por dia.

```python
%%time
update_stel('D:\OneDrive - ANATEL\GR01FI3\BaseDados')
```


### M�todos para ler as Bases de Dados


```python
from anateldb.parser import read_radcom, read_stel, read_mosaico
radcom = read_radcom(pasta='D:\OneDrive - ANATEL\GR01FI3\BaseDados') ; radcom.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Frequ�ncia</th>
      <th>Unidade</th>
      <th>Latitude</th>
      <th>Longitude</th>
      <th>Fase</th>
      <th>Situa��o</th>
      <th>Numero da Esta��o</th>
      <th>CNPJ</th>
      <th>Fistel</th>
      <th>Entidade</th>
      <th>Munic�pio</th>
      <th>UF</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>104.9</td>
      <td>MHz</td>
      <td>-24.861389</td>
      <td>-54.334722</td>
      <td>3</td>
      <td>A</td>
      <td>641168764</td>
      <td>00104477000117</td>
      <td>50011685115</td>
      <td>ACADEMIA CULTURAL DE SANTA HELENA - ACULT - ST...</td>
      <td>Santa Helena</td>
      <td>PR</td>
    </tr>
    <tr>
      <th>1</th>
      <td>87.9</td>
      <td>MHz</td>
      <td>-7.074444</td>
      <td>-36.731111</td>
      <td>3</td>
      <td>M</td>
      <td>682699349</td>
      <td>00284576000128</td>
      <td>50012524409</td>
      <td>ASSOCIACAO DOS MORADORES E PRODUT. RURAIS DE A...</td>
      <td>Assun��o</td>
      <td>PB</td>
    </tr>
    <tr>
      <th>2</th>
      <td>87.9</td>
      <td>MHz</td>
      <td>-20.323611</td>
      <td>-44.246944</td>
      <td>3</td>
      <td>H</td>
      <td>659028590</td>
      <td>00575697000129</td>
      <td>50011824689</td>
      <td>ASSOCIACAO BONFIM ESPERANCA- ABESPE</td>
      <td>Bonfim</td>
      <td>MG</td>
    </tr>
    <tr>
      <th>3</th>
      <td>104.9</td>
      <td>MHz</td>
      <td>-18.843611</td>
      <td>-46.792778</td>
      <td>3</td>
      <td>B</td>
      <td>631410937</td>
      <td>00792795000118</td>
      <td>50011398132</td>
      <td>ASSOCIACAO DOS TRABALHADORES DE GUIMARANIA (ATG)</td>
      <td>Guimar�nia</td>
      <td>MG</td>
    </tr>
    <tr>
      <th>4</th>
      <td>87.9</td>
      <td>MHz</td>
      <td>-19.466667</td>
      <td>-45.600000</td>
      <td>3</td>
      <td>M</td>
      <td>631412301</td>
      <td>00794510000188</td>
      <td>50011398990</td>
      <td>FUNDACAO ASSISTENCIAL LAR DA PAZ - FALP</td>
      <td>Dores do Indai�</td>
      <td>MG</td>
    </tr>
  </tbody>
</table>
</div>


Se o argumento <code>update=True</code> for fornecido ou arquivo local n�o existir, a base de dados � atualizada por meio da fun��o <code>update_radcom</code>. 

> *A fun��o <code>update_radcom</code> somente ir� funcionar caso o PC estiver plugado na rede interna cabeada da Anatel.*

```python
radcom = read_radcom(pasta='D:\OneDrive - ANATEL\GR01FI3\BaseDados', update=True) ; radcom.tail()
```

    Lendo o Banco de Dados de Radcom





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Frequ�ncia</th>
      <th>Unidade</th>
      <th>Latitude</th>
      <th>Longitude</th>
      <th>Fase</th>
      <th>Situa��o</th>
      <th>Numero da Esta��o</th>
      <th>CNPJ</th>
      <th>Fistel</th>
      <th>Entidade</th>
      <th>Munic�pio</th>
      <th>UF</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>4639</th>
      <td>87.9</td>
      <td>MHz</td>
      <td>-10.311667</td>
      <td>-48.162222</td>
      <td>1</td>
      <td>K</td>
      <td>1011036964</td>
      <td>08931976000190</td>
      <td>50411347829</td>
      <td>ASSOCIACAO AMIGOS DA CULTURA E DO MEIO AMBIENT...</td>
      <td>Palmas</td>
      <td>TO</td>
    </tr>
    <tr>
      <th>4640</th>
      <td>104.9</td>
      <td>MHz</td>
      <td>-10.005000</td>
      <td>-48.988889</td>
      <td>1</td>
      <td>A</td>
      <td>1011037472</td>
      <td>19001721000144</td>
      <td>50416345301</td>
      <td>ASSOCIACAO RADIO COMUNITARIA MONTE SANTO FM</td>
      <td>Monte Santo do Tocantins</td>
      <td>TO</td>
    </tr>
    <tr>
      <th>4641</th>
      <td>104.9</td>
      <td>MHz</td>
      <td>-5.586389</td>
      <td>-48.061111</td>
      <td>P</td>
      <td>M</td>
      <td>1011044797</td>
      <td>19332116000156</td>
      <td>50416480004</td>
      <td>ASSOCIACAO RADIO COMUNITARIA TOP FM</td>
      <td>Araguatins</td>
      <td>TO</td>
    </tr>
    <tr>
      <th>4642</th>
      <td>98.3</td>
      <td>MHz</td>
      <td>-28.682222</td>
      <td>-53.610278</td>
      <td>2</td>
      <td>K</td>
      <td>1011044940</td>
      <td>97538346000180</td>
      <td>50416390609</td>
      <td>ASSOCIACAO DE RADIODIFUSAO CIDADE DE CRUZ ALTA</td>
      <td>Cruz Alta</td>
      <td>RS</td>
    </tr>
    <tr>
      <th>4643</th>
      <td>104.9</td>
      <td>MHz</td>
      <td>-6.594722</td>
      <td>-35.055278</td>
      <td>1</td>
      <td>K</td>
      <td>1011110250</td>
      <td>10877144000184</td>
      <td>50411382063</td>
      <td>ASSOCIA��O DE DESENVOLVIMENTO CULTURAL DA R�DI...</td>
      <td>Mataraca</td>
      <td>PB</td>
    </tr>
  </tbody>
</table>
</div>


```python
stel = read_stel(pasta='D:\OneDrive - ANATEL\GR01FI3\BaseDados', update=True)
```
**Os dados do Stel n�o ser�o ilustrados aqui por se tratar de dados de telecomunica��o privados, os demais dados de radiodifus�o s�o p�blicos e dispon�veis para qualquer interessado consultar**

Se o argumento <code>update=True</code> for fornecido ou arquivo local n�o existir, a base de dados � atualizada por meio da fun��o <code>update_stel</code>. 

> *A fun��o  <code>update_stel</code> somente ir� funcionar caso o PC estiver plugado na rede interna cabeada da Anatel.*

```python
mosaico = read_mosaico(pasta='D:\OneDrive - ANATEL\GR01FI3\BaseDados') ; mosaico.tail()
```

    Baixando as Esta��es do Mosaico...
    Baixando o Plano B�sico das Esta��es...
    Baixando o Hist�rico de Atualiza��es...
    Kb�





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Servi�o</th>
      <th>Situa��o</th>
      <th>Entidade</th>
      <th>Fistel</th>
      <th>CNPJ</th>
      <th>Munic�pio</th>
      <th>UF</th>
      <th>Id</th>
      <th>N�mero da Esta��o</th>
      <th>Classe</th>
      <th>Frequ�ncia</th>
      <th>Latitude</th>
      <th>Longitude</th>
      <th>Num_Ato</th>
      <th>�rgao</th>
      <th>Data_Ato</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>21146</th>
      <td>RTVD</td>
      <td>TV-C2</td>
      <td>M. V. L - COMMUNICARE TELECOMUNICACOES LTDA</td>
      <td>50419656170</td>
      <td>12071310000186</td>
      <td>Parauapebas</td>
      <td>PA</td>
      <td>5f2068e65ace5</td>
      <td></td>
      <td>C</td>
      <td>503</td>
      <td>-6,0678</td>
      <td>-49,9037</td>
      <td>7588</td>
      <td>ORLE</td>
      <td>2020-12-10 18:21:09</td>
    </tr>
    <tr>
      <th>21147</th>
      <td>RTVD</td>
      <td>TV-C1</td>
      <td>MERCES COMUNICACOES LTDA</td>
      <td>50419663118</td>
      <td>11322505000199</td>
      <td>Delmiro Gouveia</td>
      <td>AL</td>
      <td>5f218fcfb0d84</td>
      <td></td>
      <td>C</td>
      <td>545</td>
      <td>-9,3853</td>
      <td>-37,9987</td>
      <td>9430</td>
      <td>ORLE</td>
      <td>2017-06-09 00:00:00</td>
    </tr>
    <tr>
      <th>21148</th>
      <td>RTVD</td>
      <td>TV-C1</td>
      <td>FUNDACAO EDUCACIONAL E CULTURAL DE IPANEMA</td>
      <td>50433856696</td>
      <td>04608796000110</td>
      <td>Sabar�</td>
      <td>MG</td>
      <td>5f32c1c918e6b</td>
      <td></td>
      <td>C</td>
      <td>207</td>
      <td>-19,89667</td>
      <td>-43,80722</td>
      <td>3301</td>
      <td>ORLE</td>
      <td>2020-06-23 00:00:00</td>
    </tr>
    <tr>
      <th>21149</th>
      <td>FM</td>
      <td>FM-C2</td>
      <td>RADIO ITAPIRANGA LTDA</td>
      <td>50433860456</td>
      <td>84375872000124</td>
      <td>Itapiranga</td>
      <td>SC</td>
      <td>5f68d432841a5</td>
      <td></td>
      <td>B1</td>
      <td>105,1</td>
      <td>-27,15778</td>
      <td>-53,69583</td>
      <td>567</td>
      <td>ORLE</td>
      <td>2021-01-26 17:20:30</td>
    </tr>
    <tr>
      <th>21150</th>
      <td>FM</td>
      <td>FM-C1</td>
      <td>EMISSORAS SUL BRASILEIRAS LTDA</td>
      <td>50433937009</td>
      <td>95818506000119</td>
      <td>Horizontina</td>
      <td>RS</td>
      <td>5f8dcc96f23f9</td>
      <td></td>
      <td>B1</td>
      <td>100,3</td>
      <td>-27,62833</td>
      <td>-54,30528</td>
      <td>3166</td>
      <td>ORLE</td>
      <td>2020-06-13 00:00:00</td>
    </tr>
  </tbody>
</table>
</div>


Se o argumento <code>update=True</code> for fornecido ou o arquivo local n�o existir, a base de dados � atualizada por meio da fun��o <code>update_mosaico</code>. 

> A fun��o <code>update_mosaico</code> usa a base de dados P�blica do Spectrum E, portanto basta somente estar conectado na internet &#x1F60E;.

"""Gera dois projetos estaticos a partir de dados municipais agregados."""
from pathlib import Path
import json,shutil,hashlib,csv,math
import pandas as pd
W=Path(__file__).resolve().parent;ROOT=W.parents[1];P=ROOT/'outputs/final_pndr';OUT=ROOT/'outputs/paineis_pndr'
base=pd.read_csv(P/'tabelas/indicadores_municipais.csv')
apoio=pd.read_csv(W/'apoio_municipal.csv')
base=base.merge(apoio,on='codmun',validate='one_to_one')
geo=json.loads((W/'municipios2022.geojson').read_text(encoding='utf-8'))
assert len(geo['features'])==5570 and len(base)==5570
assert {int(f['properties']['codmun']) for f in geo['features']}==set(base.codmun)
centers={int(r['codmun']):r for r in json.loads((W/'centroides.json').read_text())}
reference=json.loads((W/'referencia_dados.json').read_text(encoding='utf-8'))
ref={int(r['codmun2']):r for r in reference}
ufs={11:'RO',12:'AC',13:'AM',14:'RR',15:'PA',16:'AP',17:'TO',21:'MA',22:'PI',23:'CE',24:'RN',25:'PB',26:'PE',27:'AL',28:'SE',29:'BA',31:'MG',32:'ES',33:'RJ',35:'SP',41:'PR',42:'SC',43:'RS',50:'MS',51:'MT',52:'GO',53:'DF'}
base['uf_sigla']=base.uf.map(ufs)
base['lat']=base.codmun.map(lambda c:centers[c]['lat']);base['lon']=base.codmun.map(lambda c:centers[c]['lon'])
base['id_tipologia']=base.codmun.map(lambda c:str(ref.get(c,{}).get('id_tipologia','')))
base['tipologia_pndr']=base.codmun.map(lambda c:ref.get(c,{}).get('tipologia_pndr',''))
assert base.id_tipologia.ne('').all()
base['cobertura']=base.cobertura*100
for k in ['c201','c202','c301','c302']:base[k]=base[k].fillna(0).astype(int)
cut=pd.read_csv(P/'tabelas/cortes.csv').set_index('indicador')
scenarios=json.loads((P/'insumos/cenarios.json').read_text(encoding='utf-8'))
palettes=json.loads((P/'insumos/paletas.json').read_text(encoding='utf-8'))
def metric(key,label,digits=2,unit=''):
 return dict(key=key,label=label,digits=digits,unit=unit)
common=[metric('pop2022','População 2022',0,'habitantes'),metric('pib2022','PIB 2022',0,'R$ mil')]
metrics2=[metric('centralidade','Centralidade municipal',4),metric('art_i_hhi','Articulação dentro da RGI',4),metric('art_ie_hhi','Articulação dentro e fora da RGI',4),metric('L','Trabalho no próprio município',0,'pessoas'),metric('I','Trabalho em outra cidade da RGI',0,'pessoas'),metric('E','Trabalho em outra RGI brasileira',0,'pessoas'),metric('T','Trabalho com destino conhecido',0,'pessoas'),metric('hhi_i','IHH dos destinos dentro da RGI',4),metric('hhi_ie','IHH dos destinos dentro e fora da RGI',4),metric('destinos_i','Destinos dentro da RGI',0),metric('destinos_e','Destinos fora da RGI',0),metric('pib_medio_real','PIB médio real 2021–2023',0,'R$ mil de 2022'),metric('cobertura','Cobertura dos destinos de trabalho',2,'%'),metric('exterior','Trabalho no exterior',0,'pessoas'),metric('multiplos','Trabalho em múltiplos municípios',0,'pessoas'),metric('ignorado','Destino de trabalho não identificado',0,'pessoas')]
metrics3=[metric('taxa_anual','Variação populacional anual',3,'% a.a.'),metric('diferencial_br','Diferencial de crescimento frente ao Brasil',3,'p.p. a.a.'),metric('indice_renda','Rendimento relativo nacional',4),metric('pop2010','População 2010 compatibilizada',0,'habitantes'),metric('variacao_abs','Variação absoluta da população',0,'habitantes'),metric('imigrantes','Imigrantes internos · 2017–2022',0,'pessoas'),metric('emigrantes','Emigrantes internos · 2017–2022',0,'pessoas'),metric('saldo_migratorio','Saldo migratório interno · 2017–2022',0,'pessoas'),metric('eficacia_migratoria','Eficácia migratória',2,'%'),metric('imigrantes_100','Imigrantes por 100 residentes de 5+',2),metric('emigrantes_100','Emigrantes por 100 residentes de 5+',2),metric('saldo_100','Saldo por 100 residentes de 5+',2),metric('imigracao_int','Imigrantes internacionais · 2017–2022',0,'pessoas'),metric('pct_60','Pessoas de 60 anos ou mais',2,'%'),metric('pct_65','Pessoas de 65 anos ou mais',2,'%'),metric('indice_envelhecimento','Índice de envelhecimento · 60+/0–14',2),metric('cobertura_migracao','Cobertura da origem migratória',2,'%'),metric('cobertura_idade','Cobertura da informação de idade',2,'%'),metric('pop_60','População expandida de 60+',0,'pessoas'),metric('pop_0_14','População expandida de 0 a 14',0,'pessoas'),metric('pop_idade','População expandida com idade válida',0,'pessoas'),metric('pop_5','População expandida de 5+',0,'pessoas')]
BR=float(base.taxa_br.iloc[0])
def clean(v):
 if pd.isna(v):return None
 if isinstance(v,float) and v.is_integer():return int(v)
 return v
records=[{k:clean(v) for k,v in r.items()} for r in base.to_dict('records')]
for objective in [2,3]:
 repo=OUT/f'PNDR_OBJ{objective}test';repo.mkdir(parents=True,exist_ok=True)
 for sub in ['assets','data','documentos','preparacao']: (repo/sub).mkdir(exist_ok=True)
 for src,dest in [('index.html','index.html'),('style.css','assets/style.css'),('app.js','assets/app.js'),('core.js','assets/core.js'),('leaflet.js','assets/leaflet.js'),('leaflet.css','assets/leaflet.css'),('leaflet.LICENSE','assets/leaflet.LICENSE')]:shutil.copy2(W/src,repo/dest)
 (repo/'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#25345c"/><path d="M8 23V9h8a6 6 0 0 1 0 12h-3v2z" fill="#b2d7d0"/></svg>')
 ss=[]
 for src in scenarios:
  if src['objetivo']!=objective:continue
  sid=src['id'];x=src['x'];y=src['y'];cy=cut.loc[y];cx=cut.loc[x] if x in cut.index else None
  lim=[float(cx.q1),float(cx.q3)] if objective==2 else [-.1,.1] if sid==301 else [-BR,0]
  short={201:'Dentro da RGI',202:'Dentro e fora da RGI',301:'Faixa de estabilidade de 0,1% a.a.',302:'Trajetória em relação ao Brasil'}[sid]
  desc={201:'Articulação intrarregional: trabalho em outros municípios da mesma RGI, com diversidade de destinos.',202:'Articulação intra e interregional: trabalho em outros municípios brasileiros, com diversidade de destinos.',301:'Trajetória populacional entre 2010 e 2022, com uma faixa de estabilidade de −0,1% a +0,1% ao ano, cruzada com o rendimento relativo.',302:'Trajetória populacional: perda efetiva, crescimento abaixo do Brasil e crescimento igual ou superior ao Brasil, cruzada com o rendimento relativo.'}[sid]
  ss.append(dict(id=sid,objective=objective,x=x,y=y,short=short,description=desc,axisX='Centralidade municipal' if objective==2 else 'Trajetória demográfica',axisY='Articulação diversificada' if objective==2 else 'Rendimento relativo',labelsX=src['rotulos_x'],labelsY=src['rotulos_y'],cuts=lim+[float(cy.q1),float(cy.q3)],rule='right-closed' if objective==2 else 'closed-middle' if sid==301 else 'left-closed',formulaX=src['formula_x'],formulaY=src['formula_y'],explainX='Valores próximos de 1 indicam maior proximidade aos máximos de PIB e população da RGI; valores próximos de zero indicam menor porte relativo.' if objective==2 else 'Taxa geométrica anual de mudança do contingente residente. Na segunda proposta, o eixo usa o diferencial frente à taxa nacional, de '+str(round(BR,6)).replace('.',',')+'% ao ano.',explainY='Combina a participação do trabalho fora do município com a diversidade de seus destinos. Cada proposta possui seus próprios cortes nacionais.' if objective==2 else 'Índice nacional que compara os rendimentos médios por atividade, ponderados pela composição dos trabalhadores do município.'))
 config=dict(objective=objective,title='Centralidade e articulação dos territórios' if objective==2 else 'Trajetória populacional e rendimento dos territórios',subtitle='Compare o porte municipal e os vínculos de trabalho dentro e fora da RGI.' if objective==2 else 'Explore as trajetórias municipais, o rendimento relativo e as informações de migração e envelhecimento.',scenarios=ss,palette=palettes[f'objetivo{objective}'],macros=['Norte','Nordeste','Sudeste','Sul','Centro-Oeste'],metrics=common+(metrics2 if objective==2 else metrics3),updated='21 de novembro de 2026',methodIntro='O painel apresenta duas alternativas de classificação do Objetivo '+str(objective)+' da Política Nacional de Desenvolvimento Regional. Cada proposta combina dois eixos em três categorias, resultando em nove combinações municipais.',brazilGrowth=BR)
 (repo/'data/config.js').write_text('window.PNDR_CONFIG='+json.dumps(config,ensure_ascii=False,allow_nan=False,separators=(',',':'))+';',encoding='utf-8')
 # Manter somente os campos necessarios a cada painel.
 keep={'codmun','nome_municipio','uf_sigla','macro','rgi','nome_rgi','id_tipologia','tipologia_pndr','lat','lon','pop2010','pop2022','pib2022','n_municipios_rgi','tipo_lider','taxa_anual','centralidade','indice_renda','T'}
 keep.update(m['key'] for m in config['metrics']);keep.update('c'+str(s['id']) for s in ss)
 keep.update(['pop_60','pop_0_14','pop_idade','imigrantes','emigrantes','saldo_migratorio'] if objective==3 else [])
 rr=[{k:v for k,v in r.items() if k in keep} for r in records]
 payload=json.dumps(rr,ensure_ascii=False,allow_nan=False,separators=(',',':'))
 (repo/'data/municipios.js').write_text('window.PNDR_DATA='+payload+';',encoding='utf-8')
 (repo/'data/indicadores_municipais.json').write_text(payload,encoding='utf-8')
 pd.DataFrame(rr).to_csv(repo/'data/indicadores_municipais.csv',index=False,encoding='utf-8-sig')
 geodata=json.dumps(geo,ensure_ascii=False,separators=(',',':'))
 (repo/'data/geografia.js').write_text('window.PNDR_GEO='+geodata+';',encoding='utf-8')
 (repo/'data/cortes_referencia.csv').write_text('proposta,x,y,limite_x1,limite_x2,limite_y1,limite_y2,regra_x\n'+'\n'.join(','.join(map(str,[s['short'],s['x'],s['y'],*s['cuts'],s['rule']])) for s in ss),encoding='utf-8-sig')
 old=pd.read_csv(P/'tabelas/dicionario_variaveis.csv').set_index('variavel').descricao.to_dict()
 dictionary=[]
 for k in rr[0]:
  m=next((m for m in config['metrics'] if m['key']==k),None)
  dictionary.append(dict(variavel=k,rotulo=m['label'] if m else k,descricao=old.get(k,m['label'] if m else 'Identificador ou apoio territorial'),unidade=m['unit'] if m else '',fonte='IBGE; elaboracao do projeto'))
 pd.DataFrame(dictionary).to_csv(repo/'data/dicionario.csv',index=False,encoding='utf-8-sig')
 shutil.copy2(P/'relatorios/metodologia.pdf',repo/'documentos/metodologia.pdf')
 shutil.copy2(P/f'relatorios/comparativo_objetivo{objective}.pdf',repo/'documentos/comparativo.pdf')
 (repo/'.nojekyll').write_text('')
 (repo/'README.md').write_text(f'''# PNDR Objetivo {objective}

Painel municipal interativo de teste, com duas alternativas consolidadas e cortes personalizados.

## Publicar no GitHub Pages

1. Crie o repositorio `PNDR_OBJ{objective}test` em sua conta GitHub.
2. Extraia o ZIP e envie **o conteudo desta pasta** para a raiz do repositorio. `index.html` deve ficar diretamente na raiz, junto de `assets`, `data` e `documentos`.
3. Em **Settings > Pages**, selecione **Deploy from a branch**, a branch `main` e a pasta **/(root)**. Salve.
4. A publicacao esperada e `https://giovanigianetti.github.io/PNDR_OBJ{objective}test/`.

O site e estatico: dispensa instalacao, compilacao e servidor de dados. Tambem pode ser consultado localmente abrindo `index.html` depois de extrair o pacote completo. Os dados cartograficos e a biblioteca Leaflet estao incluidos; nenhuma requisicao externa e necessaria durante a consulta.

## Conteudo e reproducao

- `assets/core.js`: regras de classificacao e verificacao dos limites.
- `assets/app.js`: filtros, mapas, comparacoes, rankings, tabelas e exportacao.
- `data`: indicadores municipais agregados, geografia de 2022, dicionario e cortes.
- `documentos`: metodologia e comparativo das propostas finais.
- `preparacao`: preparacao e validacao; nenhum microdado individual e publicado.

A configuracao inicial reproduz os resultados finais do Stata 17. As simulacoes alteram somente os cortes. Filtros nao recalculam quartis nem normalizacoes. O resumo por ID da PNDR mantem a classificacao municipal; nao cria uma tipologia agregada.

Biblioteca cartografica: Leaflet 1.9.4, licenca BSD de duas clausulas, incluida em `assets/leaflet.LICENSE`. Malha municipal: IBGE, base territorial de 2022 simplificada para exibicao.

Edicao de 21/11/2026. Leia `VALIDACAO.json` para os resultados das verificacoes.
''',encoding='utf-8')
 shutil.copy2(W/'preparar.py',repo/'preparacao/preparar.py')
 shutil.copy2(W/'exportar_geografia.R',repo/'preparacao/exportar_geografia.R')
 if objective==3:
  shutil.copy2(W/'01_apoio.do',repo/'preparacao/01_apoio.do')
  shutil.copy2(W/'extrair_apoio.py',repo/'preparacao/extrair_apoio.py')
 print(repo,len(payload),len(geodata),flush=True)
(W/'configuracoes.json').write_text(json.dumps([json.loads((OUT/f'PNDR_OBJ{o}test/data/config.js').read_text(encoding='utf-8')[19:-1]) for o in []]))

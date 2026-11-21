"""Atualiza os arquivos de consulta a partir do CSV agregado do proprio pacote."""
from pathlib import Path
import csv,json
root=Path(__file__).resolve().parents[1]
with (root/'data/indicadores_municipais.csv').open(encoding='utf-8-sig',newline='') as f:
 rows=list(csv.DictReader(f))
text={'nome_municipio','uf_sigla','nome_rgi','id_tipologia','tipologia_pndr'}
for row in rows:
 for key,value in row.items():
  if key not in text:row[key]=float(value) if value else None
payload=json.dumps(rows,ensure_ascii=False,allow_nan=False,separators=(',',':'))
(root/'data/municipios.js').write_text('window.PNDR_DATA='+payload+';',encoding='utf-8')
(root/'data/indicadores_municipais.json').write_text(payload,encoding='utf-8')
print(len(rows),'municipios atualizados')

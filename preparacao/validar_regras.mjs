import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const require=createRequire(import.meta.url),core=require('../assets/core.js');
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
for(const obj of [2]){
 const p=root,scope={window:{}};
 vm.runInNewContext(fs.readFileSync(p+'/data/config.js','utf8'),scope);
 vm.runInNewContext(fs.readFileSync(p+'/data/municipios.js','utf8'),scope);
 const C=scope.window.PNDR_CONFIG,D=scope.window.PNDR_DATA;
 assert.equal(D.length,5570);assert.equal(new Set(D.map(r=>r.codmun)).size,5570);
 const result=[];
 for(const s of C.scenarios){
  const mismatches=D.filter(r=>core.classify(r,s)!==r['c'+s.id]);
  assert.equal(mismatches.length,0,JSON.stringify(mismatches.slice(0,3)));
  const bins=core.summary(D,s);assert.equal(Object.values(bins).reduce((v,b)=>v+b.n,0),5570);
  assert.equal(5570-bins[0].n,obj===2?5569:5567);
  assert.equal(core.validateCuts(s,s.cuts),'');
  assert.notEqual(core.validateCuts(s,[1,0,0,1]),'');
  const changed=[...s.cuts];changed[0]=obj===2?.1:-.25;changed[1]=obj===2?.5:.25;
  assert.equal(core.validateCuts(s,changed),'');
  const mods=D.filter(r=>core.classify(r,s,changed)!==core.classify(r,s)).length;
  assert.ok(mods>0);
  const mock={...D.find(r=>r['c'+s.id]),[s.x]:s.cuts[0],[s.y]:s.cuts[2]};
  const low=core.classify(mock,s);assert.equal(Math.floor(low/10),s.rule==='left-closed'?2:1===1&&s.rule==='closed-middle'?2:1);assert.equal(low%10,1);
  mock[s.x]=s.cuts[1];assert.equal(Math.floor(core.classify(mock,s)/10),s.rule==='left-closed'?3:2);
  result.push({proposta:s.id,municipios:5570,classificados:5570-bins[0].n,fora_matriz:bins[0].n,divergencias_stata:0,simulacao_municipios_alterados:mods,limites_inclusao:'conferidos'});
 }
 const A=C.scenarios[0],B=C.scenarios[1],common=D.filter(r=>core.classify(r,A)&&core.classify(r,B)),same=common.filter(r=>core.classify(r,A)===core.classify(r,B));
 assert.equal(same.length,obj===2?3529:4200);
 const report={status:'aprovado',objetivo:obj,cenarios:result,comparacao:{comuns:common.length,mesma_classe:same.length,mudam:common.length-same.length},geografia:5570,atualizacao:'2026-11-21'};
 fs.writeFileSync(p+'/VALIDACAO.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}

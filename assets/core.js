/* Calculos puros compartilhados pelo painel e pelas verificacoes. */
(function(root){
  'use strict';
  const finite=v=>typeof v==='number'&&Number.isFinite(v);
  function classify(row,scenario,cuts){
    const x=row[scenario.x],y=row[scenario.y];
    if(!finite(x)||!finite(y)||(scenario.objective===2&&row.n_municipios_rgi<2))return 0;
    const c=cuts||scenario.cuts;
    const a=scenario.rule==='closed-middle'?(x<c[0]?1:x<=c[1]?2:3):scenario.rule==='left-closed'?(x<c[0]?1:x<c[1]?2:3):(x<=c[0]?1:x<=c[1]?2:3);
    const b=y<=c[2]?1:y<=c[3]?2:3;
    return 10*a+b;
  }
  function validateCuts(s,c){
    if(c.length!==4||!c.every(finite))return 'Preencha os quatro limites com números válidos.';
    if(c[0]>=c[1]||c[2]>=c[3])return 'O primeiro limite deve ser menor que o segundo em cada eixo.';
    if(s.objective===2&&c.some(v=>v<0||v>1))return 'Os limites de centralidade e articulação devem estar entre 0 e 1.';
    if(s.objective===3&&(c[2]<0||c[3]<0))return 'O índice de rendimento admite limites a partir de zero.';
    if(s.id===301&&c[0]<-100)return 'A taxa de variação populacional deve ser maior ou igual a −100% ao ano.';
    return '';
  }
  const sum=(rows,key)=>rows.reduce((a,r)=>a+(finite(r[key])?r[key]:0),0);
  function summary(rows,scenario,cuts){
    const bins=Object.fromEntries([0,11,12,13,21,22,23,31,32,33].map(c=>[c,{n:0,pop:0,pib:0}]));
    rows.forEach(r=>{const b=bins[classify(r,scenario,cuts)];b.n++;b.pop+=r.pop2022||0;b.pib+=r.pib2022||0;});
    return bins;
  }
  const api={finite,classify,validateCuts,sum,summary};
  if(typeof module!=='undefined')module.exports=api;else root.PNDRCore=api;
})(typeof window!=='undefined'?window:globalThis);

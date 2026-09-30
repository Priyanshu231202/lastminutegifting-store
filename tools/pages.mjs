import fs from 'node:fs'; import vm from 'node:vm';
const js = fs.readFileSync('src-orig/assets/index-Dpe4gksW.js','utf8');
const start = js.indexOf('var Br={about:');
let i = js.indexOf('{', start), depth = 0, j = i;
for (; j < js.length; j++) { const c = js[j]; if (c === '`') { j = js.indexOf('`', j+1); continue; } if (c === '{') depth++; else if (c === '}') { depth--; if (depth === 0) break; } }
const obj = vm.runInNewContext('(' + js.slice(i, j+1) + ')');
const d = JSON.parse(fs.readFileSync('data.json','utf8')); d.pages = obj;
fs.writeFileSync('data.json', JSON.stringify(d, null, 1));
console.log(Object.keys(obj), obj.faq.qa.length);

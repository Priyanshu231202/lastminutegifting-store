import fs from 'node:fs';
const dir = process.argv[2];
const a = f => fs.readdirSync(dir + '/assets').find(n => n.startsWith(f + '-') && n.endsWith('.js'));
const url = f => new URL('file://' + dir + '/assets/' + a(f));
const products = (await import(url('products'))).default;
const catalog = (await import(url('categories'))).default;
const settings = (await import(url('settings'))).default;
fs.writeFileSync('data.json', JSON.stringify({products, catalog, settings}, null, 1));
console.log(products.length, catalog.categories.length, catalog.occasions.length, Object.keys(settings));

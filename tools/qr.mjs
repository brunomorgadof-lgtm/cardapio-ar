import QR from 'qrcode'; import fs from 'fs';
const base = process.argv[2]; fs.mkdirSync('../qr', { recursive: true });
for (const k of ['japonesa','pizzaria','lanchonete','hamburgueria'])
  fs.writeFileSync(`../site/qr/${k}.svg`, await QR.toString(`${base}menu.html?r=${k}`, { type: 'svg', margin: 1, errorCorrectionLevel: 'M' }));
console.log('ok', base);

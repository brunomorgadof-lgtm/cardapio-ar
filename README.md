# Cardápio em realidade aumentada

Protótipo de cardápio digital: o cliente escaneia o QR code da mesa e vê o prato em 3D, em tamanho real, pela câmera do celular. Funciona no navegador (Android e iPhone), sem instalar aplicativo.

**Site:** https://brunomorgadof-lgtm.github.io/cardapio-ar/

| Página | O que é |
|---|---|
| `index.html` | Vitrine com os 4 restaurantes de exemplo |
| `menu.html?r=japonesa` (ou `pizzaria`, `lanchonete`, `hamburgueria`) | Cardápio com botão **Ver na mesa** |
| `mesa.html?r=...` | Plaquinha com QR code para imprimir |

## Como editar
- Pratos, preços, cores e textos: `data.js`
- Número do WhatsApp para pedidos: `WHATSAPP` no topo de `data.js`
- Modelos 3D: `models/*.glb` (gerados por `tools/build.mjs` em escala real, em metros)
- QR codes: `cd tools && npm i && node qr.mjs https://brunomorgadof-lgtm.github.io/cardapio-ar/`

## Tecnologia
- [`<model-viewer>`](https://modelviewer.dev) do Google (WebXR / Scene Viewer no Android, Quick Look no iPhone)
- Modelos 3D ilustrativos do [Food Kit da Kenney](https://kenney.nl/assets/food-kit) (licença CC0, domínio público). Serão substituídos por modelos fotorrealistas de pratos reais na etapa 3.

## Créditos dos modelos 3D
- "Burger King's Avocado Whopper" (https://skfb.ly/opTUv) por seirogan, licença Creative Commons Attribution 4.0. Recortado e redimensionado para tamanho real (`tools/crop.mjs`).

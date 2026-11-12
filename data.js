// Dados do protótipo. Para trocar o número do WhatsApp, edite WHATSAPP abaixo.
window.WHATSAPP = ''; // ex.: '5511999999999' (vazio = botão de pedido escondido)

window.RESTAURANTES = {
  japonesa: {
    nome: 'Sakura Sushi Bar',
    culinaria: 'Japonesa',
    slogan: 'Peixe fresco, corte na hora',
    cor: '#d6455d',
    emoji: '🍣',
    pratos: [
      { id: 'combinado-uramaki', nome: 'Combinado de uramakis', preco: 79.9,
        desc: 'Seleção de uramakis variados com gengibre e wasabi, servidos na tábua de bambu.', destaque: true,
        credito: { titulo: 'Sushi', autor: '3DSCANPRO', link: 'https://skfb.ly/oKys6', licenca: 'CC BY 4.0' } },
    ],
  },
  pizzaria: {
    nome: 'Forno da Nonna',
    culinaria: 'Pizzaria',
    slogan: 'Massa de fermentação natural, forno a lenha',
    cor: '#c8481c',
    emoji: '🍕',
    pratos: [
      { id: 'pizza-parma', nome: 'Pizza Parma com rúcula', preco: 54.9,
        desc: 'Molho de tomate italiano, muçarela, presunto parma e rúcula fresca.', destaque: true,
        credito: { titulo: 'Pizza', autor: 'Rigsters', link: 'https://skfb.ly/6RqYo', licenca: 'CC BY 4.0' },
        tamanhos: [
          { rotulo: 'Broto 25 cm', escala: 25 / 35, preco: 44.9 },
          { rotulo: 'Média 30 cm', escala: 30 / 35, preco: 54.9 },
          { rotulo: 'Grande 35 cm', escala: 1, preco: 64.9 },
        ] },
      { id: 'pizza-pepperoni', nome: 'Pizza Pepperoni', preco: 52.9,
        desc: 'Molho de tomate, muçarela derretida e fatias generosas de pepperoni.',
        credito: { titulo: 'Pepperoni Pizza', autor: 'ScanTasticWorld', link: 'https://skfb.ly/pzr8n', licenca: 'CC BY 4.0' },
        tamanhos: [
          { rotulo: 'Broto 25 cm', escala: 25 / 35, preco: 42.9 },
          { rotulo: 'Média 30 cm', escala: 30 / 35, preco: 52.9 },
          { rotulo: 'Grande 35 cm', escala: 1, preco: 62.9 },
        ] },

    ],
  },
  lanchonete: {
    nome: 'Lanchonete da Esquina',
    culinaria: 'Lanches',
    slogan: 'O lanche de sempre, feito na hora',
    cor: '#2f8f5b',
    emoji: '🥪',
    pratos: [
      { id: 'baguete', nome: 'Baguete completa', preco: 22.9,
        desc: 'Pão francês longo, presunto, queijo, alface e tomate.', destaque: true },
      { id: 'hot-dog', nome: 'Cachorro-quente', preco: 14.9,
        desc: 'Salsicha, molho da casa, mostarda e ketchup.' },
      { id: 'sanduiche-natural', nome: 'Sanduíche natural', preco: 16.9,
        desc: 'Pão de forma, frango, cenoura, alface e requeijão.' },
      { id: 'taco', nome: 'Taco de carne', preco: 19.9,
        desc: 'Tortilha crocante, carne temperada, alface e queijo.' },
    ],
  },
  hamburgueria: {
    nome: 'Brasa Burger',
    culinaria: 'Hamburgueria',
    slogan: 'Blend 180 g na brasa',
    cor: '#e08a00',
    emoji: '🍔',
    pratos: [
      { id: 'hamburguer-classico', nome: 'Clássico da Brasa', preco: 29.9,
        desc: 'Pão com gergelim, blend 180 g na brasa, queijo, picles, cebola e maionese da casa.', destaque: true,
        credito: { titulo: "Burger King's Avocado Whopper", autor: 'seirogan', link: 'https://skfb.ly/opTUv', licenca: 'CC BY 4.0' } },
      { id: 'batata-frita', nome: 'Batata frita da casa', preco: 19.9,
        desc: 'Porção de batatas fritas sequinhas, temperadas com sal. Serve 1 a 2 pessoas.',
        credito: { titulo: 'French Fries', autor: 'lukealfonso', link: 'https://skfb.ly/p7EYP', licenca: 'CC BY 4.0' } },
      // Combo volta quando tivermos um modelo realista:
      // { id: 'combo-burger', nome: 'Combo Brasa', preco: 42.9, desc: 'Clássico da Brasa, batata frita e refrigerante.' },
    ],
  },
};

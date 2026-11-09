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
      { id: 'combinado-8', nome: 'Combinado 8 peças', preco: 59.9,
        desc: '3 niguiris (salmão e tamago) e 5 uramakis variados, servidos no prato.', destaque: true },
      { id: 'niguiri-salmao', nome: 'Niguiri de salmão (2 un.)', preco: 18.9,
        desc: 'Bolinho de arroz temperado coberto com fatia de salmão.' },
      { id: 'uramaki', nome: 'Trio de uramaki', preco: 24.9,
        desc: 'Salmão, ovas e vegetariano. Uma peça de cada.' },
    ],
  },
  pizzaria: {
    nome: 'Forno da Nonna',
    culinaria: 'Pizzaria',
    slogan: 'Massa de fermentação natural, forno a lenha',
    cor: '#c8481c',
    emoji: '🍕',
    pratos: [
      { id: 'pizza-margherita', nome: 'Pizza Margherita', preco: 49.9,
        desc: 'Molho de tomate italiano, muçarela, tomate e manjericão.', destaque: true,
        tamanhos: [
          { rotulo: 'Broto 25 cm', escala: 25 / 35, preco: 39.9 },
          { rotulo: 'Média 30 cm', escala: 30 / 35, preco: 49.9 },
          { rotulo: 'Grande 35 cm', escala: 1, preco: 59.9 },
        ] },
      { id: 'pizza-refri', nome: 'Pizza grande + refri', preco: 64.9,
        desc: 'Margherita grande e um refrigerante de 500 ml.' },
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
        desc: 'Pão brioche, blend 180 g, cheddar, alface e tomate.', destaque: true },
      { id: 'combo-burger', nome: 'Combo Brasa', preco: 42.9,
        desc: 'Clássico da Brasa, batata frita e refrigerante.' },
    ],
  },
};

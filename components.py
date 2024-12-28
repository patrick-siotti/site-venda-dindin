from fasthtml.common import *
from dotenv import get_key

import data

def html(
  title:str, 
  *args, 
  theme=[
    "light",
    "dark",
    "cupcake",
    "bumblebee",
    "emerald",
    "corporate",
    "synthwave",
    "retro",
    "cyberpunk",
    "valentine",
    "halloween",
    "garden",
    "forest",
    "aqua",
    "lofi",
    "pastel",
    "fantasy",
    "wireframe",
    "black",
    "luxury",
    "dracula",
    "cmyk",
    "autumn",
    "business",
    "acid",
    "lemonade",
    "night",
    "coffee",
    "winter",
    "dim",
    "nord",
    "sunset",
  ]
  ):  
  return_html = Title(title), Main(
    Html(      
      *args,
      Link(href='https://cdn.jsdelivr.net/npm/daisyui@4.12.22/dist/full.min.css', rel="stylesheet", type="text/css"),
      Link(href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css', rel="stylesheet", type="text/css"),
      Script(src='https://cdn.tailwindcss.com'),
      data_theme=theme if type(theme) == str else 'pastel',
    )
  )
  return return_html

def github():
    return A(I(cls='fa-brands fa-github text-4xl mr-2'), href='https://github.com/patrick-siotti', cls='w-24 justify-end', target='_blank')

def header():
    return Header(cls='navbar bg-secondary shadow-md flex justify-between items-center px-4 rounded-xl mb-4')(
        Div(cls='w-24'),
        H1('DinDins', cls='text-4xl font-bold'),
        github()
    )

def lista_dindin(user_dindin=None):
  if not data.Dindin.select().where(data.Dindin.estoque > 0):
    return H1(cls='text-2xl')('Nenhum dindin para comprar agora, volte mais tarde')
  return Section(cls='flex flex-wrap justify-center', id='venda')(
    *[Div(cls='card bg-secondary w-[340px] shadow-md m-2')(
      Div(cls='card-body font-bold')(
        H2(cls='text-2xl')(
          dindin.nome
        ),
        P(dindin.info),
        P(dindin.ingredientes),
        Div(cls='grid grid-cols-2 gap-4 mt-4')(
          Div(
            P(f'{dindin.estoque} disponiveis'),
            P(f'{dindin.valor:.2f} R$'.replace('.', ',')),
          ),
          Group(
            Button(cls='btn', value=dindin.nome, name='mais', hx_post='/add_dindin', hx_target='#venda', hx_swap='outerHTML',)('comprar'), 
          ) if dindin.nome not in user_dindin else
          Group(cls='bg-white flex rounded-3xl')(
            Button(cls='btn bg-white', value=dindin.nome, name='menos', hx_post='/add_dindin', hx_target='#venda', hx_swap='outerHTML',)('-'),
            P(user_dindin[dindin.nome], cls='text-center text-xl m-auto bg-white'),
            Button(cls='btn bg-white', value=dindin.nome, name='mais', hx_post='/add_dindin', hx_target='#venda', hx_swap='outerHTML',)('+'),
          )
        )
      )
    ) for dindin in data.Dindin.select() if dindin.estoque > 0]
  )
  
def botao_finalizar(user):
  return Div(id='finalizar', hx_swap_oob='true', cls='flex justify-center justify-items-center')(
    Button(cls='btn btn-accent w-full max-w-80', hx_get='/finalizar')(
    'finalizar'
    ) if user['dindins'] else None
  )

def carrinho(session):
  dindins = session['dindins']
  preco = define_preco(dindins)
  text = define_texto(dindins, preco)
  
  ret = Div()(
    cria_tabela(dindins, preco),
    editar(),
    botao_enviar(text, session)
  )
  
  return ret

def define_preco(dindins):
  return sum([data.Dindin.get(data.Dindin.nome==dindin).valor * quant for dindin, quant in dindins.items()])

def define_texto(dindins, preco):
  text = f'gostaria de fazer um pedido:\n'
  
  for dindin, quantidade in dindins.items():
    text += f'{quantidade} {dindin}\n'
  
  text += f'dando um total de {preco:.2f} R$'.replace('.', ',')
  return text

def cria_tabela(dindins, preco):
  return Div(cls='overflow-x-auto')(
    Table(cls='table table-zebra')(
      Thead(
        Tr(
          Th(),
          Th('dindin'),
          Th('quantidade'),
          Th('preço un.')
        )
      ),
      Tbody(
        *[Tr(
          Th(''),
          Td(dindin),
          Td(quant),
          Td(f'{data.Dindin.get(data.Dindin.nome==dindin).valor:.2f}'.replace('.', ','))
        ) for dindin, quant in dindins.items()]
      )
    ),
    P(f'dando um total de {preco:.2f} R$'.replace('.', ','))
  )

def editar():
  return Div(cls='flex justify-center mt-4')(A(href='/', cls='w-full max-w-80')(Button(P(cls='text-xl text-black')('Voltar'), cls='btn btn-secondary w-full')))

def botao_enviar(text, session):
  NUMERO = get_key('.env', 'WHATSAPP')
  
  espaco = '%20'
  enter = '%0A'
  
  link = f'https://wa.me/{NUMERO}?text={text.replace(' ', espaco).replace('\n', enter)}'
  session['link'] = link
  
  return Div(cls='flex justify-center mt-4')(A(href='/send_whats', cls='w-full max-w-80')(Button(P(cls='text-xl text-black')(I(cls='fa-brands fa-whatsapp mx-2'), 'Pedir'), cls='btn btn-accent w-full')))

def login():
  return Form(cls='m-auto bg-secondary p-4 max-w-[400px] rounded-xl b-4', hx_post='/auth/login', hx_target='#notify', hx_swap='innerHTML')(
    H1(cls='text-2xl mb-2')('Login'),
    Input(placeholder='User', name='user', type='text', cls='input'),
    Input(placeholder='Senha', name='passw', type='password', cls='input'),
    Button('Entrar', cls='btn'),
    Div(id='notify'),
  )

def comp_adm():
  return Section()( 
    muda_usuario_senha(),
    muda_numero_usuario(),
    muda_dindin(),
    botao_sair(),
    Div(id='notify')
  )
  
def muda_usuario_senha():
  return Article()(
    Form(hx_post='/config/login', hx_target='#notify', hx_swap='innerHTML')(
      H1(cls='text-2xl mb-2')('Mudar usuario ou senha:'),
      Input(cls='input input-bordered', placeholder='usuario', name='user', type='text'),
      Input(cls='input input-bordered', placeholder='senha', name='passw', type='password'),
      Button(cls='btn')('trocar')
    )
  )

def muda_numero_usuario():
  return Article()(
    Form(hx_post='/config/numero', hx_target='#notify', hx_swap='innerHTML')(
      H1(cls='text-2xl mb-2')('Mudar numero de contato:'),
      P(cls='mb-1')('Coloque 13 numeros, código do pais, ddd, numero 9, e depois o numero, ex: 5584987541801, sem espaços.'),
      Input(cls='input input-bordered', placeholder='Numero', name='num', type='tel', pattern="[0-9]{2}[0-9]{2}[0-9]{5}[0-9]{4}"),
      Button(cls='btn')('trocar')
    )
  )

def botao_sair():
  return Div(cls='flex justify-center mt-4')(A(href='/', cls='w-full max-w-80')(Button(P(cls='text-xl text-black')('Sair'), cls='btn btn-secondary w-full')))

def manda_alerta(tipo:bool, texto:str):
  return Div(cls='toast toast-end')(
    Div(cls=f'alert alert-{"success" if tipo else "error" if not tipo else "info"}')(
      Span(texto)
    )
  )
  
def muda_dindin():
  return Article(id='edit_dindin', hx_swap_oob='true')(
    Section(cls='flex flex-wrap justify-center', id='venda')(
      *[Form(cls='card bg-secondary w-[340px] shadow-md m-2', hx_post='/config/dindin', hx_target='#notify', hx_swap='innerHTML')(
        Div(cls='card-body font-bold')(
          
          Input(value=dindin.id, name='id', cls='hidden input'),
          Input(placeholder='nome', value=dindin.nome, name='nome', cls='input'),
          Input(placeholder='info', value=dindin.info, name='info', cls='input'),
          Input(placeholder='ingredientes', value=dindin.ingredientes, name='ingre', cls='input'),
          Input(placeholder='estoque', value=dindin.estoque, name='estoque', cls='input'),
          Input(placeholder='valor', value=dindin.valor, name='valor', cls='input'),
          
          Button(cls='btn')('salvar'),
          Button(cls='btn', hx_post='/config/delete', hx_target='#notify', hx_swap='innerHTML', name='id', value=dindin.id)('deletar')
        ),
      ) for dindin in data.Dindin.select()]
    ),
    Button(cls='btn btn-secondary')('Adicionar', hx_post='/config/adicionar', hx_target='#edit_dindin', hx_swap='innerHTML')
  )
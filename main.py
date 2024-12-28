from fasthtml.common import *
from dotenv import load_dotenv, get_key, set_key, unset_key
from uuid import uuid4
from datetime import datetime, timedelta

import components
import data

sess = {}

def before(session):
  if 'dindins' not in session:
    session['dindins'] = dict()

app, rt = fast_app(debug=True, live=True, before=before)

@rt('/')
def get(session):
  escolha_usuario = session.get('dindins')
  return components.html(
    'DinDins',
    Main(cls='container')(
      components.header(),
      components.lista_dindin(escolha_usuario),
      components.botao_finalizar(session),
    )
  )

@rt('/add_dindin')
def post(session, mais:str=None, menos:str=None):
  dindin = data.Dindin.get_or_none(data.Dindin.nome == mais if mais else data.Dindin.nome == menos)
  if not dindin:
    return

  session_dindin = session['dindins']
  if mais:
    if mais in session_dindin:
      if session_dindin[mais] < dindin.estoque:
        session_dindin[mais] += 1
    else:
      session_dindin[mais] = 1
  elif menos:
    if menos in session_dindin:
      if session_dindin[menos] == 1:
        del session_dindin[menos]
      else:
        session_dindin[menos] -= 1
  
  session['dindins'] = session_dindin
  return components.botao_finalizar(session), components.lista_dindin(session_dindin)

@rt('/finalizar')
def get(session):
  return Redirect('/carrinho')

@rt('/carrinho')
def get(session):
  if not session['dindins']:
    return Redirect('/')
  
  return components.html(
    'carrinho',
    Main(cls='container')(
      components.header(),
      components.carrinho(session)
    )
  )

@rt('/send_whats')
def get(session):
  if 'link' in session:
    session['dindins'] = dict()
    link = session['link']
    del session['link']
    return Redirect(link)
  else:
    return Redirect('/')

@rt('/adm')
def get(session):
  if verifica_sessao(session):
    return Redirect('/adm/ok')
  
  return components.html(
    'adm',
    Main(cls='container')(
      components.login()
    )
  )

@rt('/auth/login')
def post(session, user:str=None, passw:str=None):
  if verifica_sessao(session):
    return Redirect('/adm/ok')
  
  USUARIO = get_key('.env', 'USUARIO')
  SENHA = get_key('.env', 'SENHA')
  print(user, passw)
  if not user or not passw:
    return  P('Faltou o usuario ou senha.', cls='text-red-700')
  else:
    if user != USUARIO or passw != SENHA:
      return P('Usuario ou senha incorretos.', cls='text-red-700')
  
  if user == USUARIO or passw == SENHA:
    session['sess'] = str(uuid4())
    sess[session['sess']] = datetime.now() + timedelta(days=7)
    return Redirect('/adm/ok')

def verifica_sessao(session) -> bool:
  global sess
  if 'sess' not in session:
    return False
  else:
    sessao = session['sess']
  
  if sessao in sess:
    if sess[session['sess']] < datetime.now():
      del sess[session['sess']]
      return False
    else:
      return True
  else:
    del session['sess']
    return False

@rt('/adm/ok')
def get(session):
  if not verifica_sessao(session):
    return Redirect('/adm')
  
  return components.html(
    'adm',
    Main(cls='container')(
      components.comp_adm()
    )
  )

@rt('/config/login')
def post(user:str=None, passw:str=None):
  path = '.env'
  
  if not user or not passw:
    return components.manda_alerta(False, 'faltou usuario ou senha')
  
  set_key(path, 'USUARIO', user)
  set_key(path, 'SENHA', passw)
  
  return components.manda_alerta(True, f'usuario trocado para: {user}, senha trocada para: {passw}')
  
@rt('/config/numero')
def post(num:str=None):
  path = '.env'
  
  if not num:
    return components.manda_alerta(False, 'faltou numero')
  
  set_key(path, 'WHATSAPP', num)
  
  return components.manda_alerta(True, f'numero de contato trocado para {num}')

@rt('/config/dindin')
def post(id:int, nome:str, info:str, ingre:str, estoque:int, valor:float):
  try:
    dindin = data.Dindin.get(data.Dindin.id == id)
    
    dindin.nome = nome
    dindin.info = info
    dindin.ingredientes = ingre
    dindin.estoque = estoque
    dindin.valor = valor
    
    dindin.save()
    
    return components.manda_alerta(True, f'salvo com sucesso!')
  except:
    return components.manda_alerta(False, f'ouve um erro desconhecido.')

@rt('/config/delete')
def post(id:int):
  try:
    dindin = data.Dindin.get(data.Dindin.id == id)
    dindin.delete_instance()
    
    return components.manda_alerta(True, f'deletado com sucesso!'), components.muda_dindin()
  except:
    return components.manda_alerta(True, f'ouve um erro ao deletar!')

@rt('/config/adicionar')
def post():
  data.Dindin.create(nome='dindin', estoque=0, valor=0, info='', ingredientes='')
  return components.muda_dindin()

if __name__ == '__main__':
  load_dotenv()
  serve()
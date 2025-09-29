import requests
from requests.auth import HTTPBasicAuth
import json

BASE = 'http://127.0.0.1:5000'

def registrar():
    usuario = input('Usuario a registrar: ').strip()
    contraseña = input('Contraseña: ').strip()
    r = requests.post(f'{BASE}/registro', json={'usuario': usuario, 'contraseña': contraseña})
    try:
        print(r.status_code, r.json())
    except Exception:
        print(r.status_code, r.text)

def login():
    usuario = input('Usuario: ').strip()
    contraseña = input('Contraseña: ').strip()
    r = requests.post(f'{BASE}/login', json={'usuario': usuario, 'contraseña': contraseña})
    try:
        print(r.status_code, r.json())
    except Exception:
        print(r.status_code, r.text)

    return usuario, contraseña, r.status_code == 200

def ver_tareas(usuario, contraseña):
    # usare Auth de requests (genera Basic header automáticamente)
    r = requests.get(f'{BASE}/tareas', auth=HTTPBasicAuth(usuario, contraseña))
    print('Código:', r.status_code)
    print(r.text)

if __name__ == '__main__':
    while True:
        print('\n--- Cliente de Tareas ---')
        print('1) Registrar')
        print('2) Login')
        print('3) Ver /tareas (requiere credenciales)')
        print('0) Salir')
        opt = input('> ').strip()
        if opt == '1':
            registrar()
        elif opt == '2':
            usuario, contraseña, ok = login()
        elif opt == '3':
            try:
                usuario
            except NameError:
                print('No hay credenciales en memoria — usa Login primero o ingrésalas ahora')
                usuario = input('Usuario: ').strip()
                contraseña = input('Contraseña: ').strip()
            ver_tareas(usuario, contraseña)
        elif opt == '0':
            break
        else:
            print('Opción inválida')
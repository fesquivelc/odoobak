#!/usr/bin/python3

import os
import sys
from getopt import getopt, GetoptError
from datetime import datetime


def do_backup(web_container, db_container, db_name):
    print("""
    Se procede a generar el backup con los siguientes datos:
    
    Base de datos: {}
    Contenedor web: {}
    Contenedor de base de datos: {}
    """.strip().format(db_name, web_container, db_container))
    # Primero obtenemos el timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    # Nombre de fichero
    filename = '{}_{}'.format(timestamp, db_name)
    # Se extrae el filestore del container web
    os.system("docker cp {}:/var/lib/odoo/filestore/{} filestore".format(web_container, db_name))
    # Se genera el backup desde el contenedor web
    os.system("docker exec -it {} pg_dump -U odoo {} > dump.sql".format(db_container, db_name))
    # Comprimimos el resultado
    os.system("tar czf {}.tar.gz filestore dump.sql".format(filename))
    # Eliminamos residuos
    os.system("rm -rf dump.sql filestore")
    print("El backup se encuentra en el archivo {}.tar.gz".format(filename))


def do_restore():
    print('Aún no implementado')


if __name__ == '__main__':
    options = {
        '-b': do_backup,
        '-r': do_restore
    }

    try:
        opts, args = getopt(sys.argv[1:], 'brw:d:n:f:')
    except GetoptError as ex:
        print('author: Francis Esquivel')
        print('For backup: odoobak -b -w my_web_container -d my_db_container -n my_db_name')
        print('For restore: odoobak -r -w my_web_container -d my_db_container -f my_db_name.tar.gz')
        sys.exit(2)

    values = dict()

    for opt, arg in opts:
        if opt in ('-r', '-b'):
            if values.get('option'):
                raise ValueError('Solo puede especificar una opción -r o -b')
            values['option'] = opt

        if opt == '-w':
            values['web_container'] = arg

        if opt == '-d':
            values['db_container'] = arg

        if opt == '-n':
            values['db_name'] = arg

    action = values.pop('option')
    options[action](**values)

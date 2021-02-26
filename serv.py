import datetime
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import mysql.connector


class Serv(BaseHTTPRequestHandler):

    mydb = mysql.connector.connect(
        host="db4free.net",
        user="visie_user",
        password="visie_pass",
        database="visie_db"
    )

    mycursor = mydb.cursor()

    def do_GET(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path
        
        # Path da página inicial
        if path == '/':
            self.path = '/index.html'
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, 'utf-8'))

        # Este path retorna para o cliente um json com as informações
        # de id, nome e data_admissao de cada pessoa do banco de dados.
        elif path == '/pessoas/':
            self.mycursor.execute("SELECT * FROM pessoas")
            myresult = self.mycursor.fetchall()

            pessoas_dict = []
            for pessoa in myresult:
                p = {
                        'id': pessoa[0],
                        'nome': pessoa[1],
                        'data_admissao': pessoa[5].strftime('%d/%m/%Y')
                    }

                pessoas_dict.append(p)
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(pessoas_dict), 'utf-8'))
        

    def do_POST(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path

        length = int(self.headers['content-length'])
        post_data = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))

        # Este path executa a instrução DELETE no banco de dados
        # apagando a pessoa com o id_pessoa informado no POST.
        if path == '/pessoas/apagar/':
            id_pessoa = post_data['id_pessoa'][0]
            self.mycursor.execute("DELETE FROM pessoas WHERE id_pessoa = " + id_pessoa)

        # Este path executa a instrução INSERT no banco de dados
        # inserindo a pessoa com o nome e data_admissao informado no POST.
        elif path == '/pessoas/adicionar/':
            nome = post_data['nome'][0]
            data = post_data['data_admissao'][0]

            self.mycursor.execute(
                "INSERT INTO pessoas(nome,data_admissao) VALUES('" + nome + 
                "',STR_TO_DATE('" + data + "', '%Y-%m-%d'))")

        # Ao final do POST, redireciona para a página incial.
        self.path = '/'
        self.do_GET()


httpd = HTTPServer(('localhost', 8080), Serv)
httpd.serve_forever()

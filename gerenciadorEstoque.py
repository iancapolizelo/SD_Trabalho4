from __future__ import print_function
import Pyro5.api
import Pyro5.server
from produto import produto
from time import gmtime, strftime
from flask import Flask, Response, jsonify, request, abort
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler




app = Flask(__name__)

#app.config["REDIS_URL"] = "redis://127.0.0.1"
#app.register_blueprint(sse, url_prefix='/stream')

@app.route('/')
def index():
    return '<p>Gerenciador de Estoques</p>'

listaProdutos = [
    {
        'codigo' : "01",
        'nome' : "Cama",
        'descricao' : "King Size",
        'quantidade' : 10,
        'precoUnidade' : 1000,
        'estoqueMinimo' : 2,
        'acabou' : 0,
        'estoqueBaixo' : 0
    },
    {
        'codigo' : "02",
        'nome' : "Celular",
        'descricao' : "Smart",
        'quantidade' : 100,
        'precoUnidade' : 500,
        'estoqueMinimo' : 10,
        'acabou' : 0,
        'estoqueBaixo' : 0
    }
]

listaClientes = {}

registros = {}

#def publish_sse_message(message, channel):
#    with app.app_context():
#        sse.publish({"message": message}, type=channel, channel=channel)



#Método para cadastrar novos produtos no estoque
@app.route('/produto', methods=['POST'])
def cadastrarProdutoNovo():

    #{
    #    'codigo' : "Codigo do Produto",
    #    'nome' : "Nome do Produto",
    #    'descricao' : "Descrição",
    #    'quantidade' : 100,
    #    'precoUnidade' : 500,
    #    'estoqueMinimo' : 10,
    #    'acabou' : 0,
    #    'estoqueBaixo' : 0
    #}

    produto = request.get_json()

    for item in listaProdutos:
        if produto['codigo'] == item['codigo']:
            abort(400, "Produto já existe")

    listaProdutos.append(produto)

    horaCadastro = strftime("%d/%m/%Y - %H:%M:%S", gmtime())
    evento = "produto " + produto['codigo'] + " cadastrado"
    registros[horaCadastro] = evento

    return jsonify(success=True), 200

#Método para listar todos os produtos cadastrados no estoque
@app.route('/produto', methods=['GET'])
def listarProdutos():
    retorno = ''
    
    mensagem = "\nLista de produtos: \n"
    retorno += mensagem

    for produto in listaProdutos.keys():
        mensagem = "Código do produto: " + produto + " Nome: " + listaProdutos[produto].nome + " Quantidade: " + str(listaProdutos[produto].quantidade) + " Estoque mínimo: " + listaProdutos[produto].estoqueMinimo +"\n"
        retorno += mensagem

    return jsonify(retorno), 200


#Método para retirar produtos do estoque
@app.route('/produto', methods=['POST'])    
def retirarProduto():

    #{
    #    'codigo' : "Codigo do Produto",
    #    'qtdRetirar' : 1
    #}

    produto = request.get_json()

    for chave in listaProdutos.keys(): #Verifica se o produto existe
        if chave == produto['codigo']:

            nova_qtd = int(int(listaProdutos[chave].quantidade) - int(produto['qtdRetirar']))
            horarioEvento = strftime("%d/%m/%Y - %H:%M:%S", gmtime())

            if nova_qtd >= 0: #Verifica se o estoque é suficiente
                if nova_qtd >= int(listaProdutos[chave].estoqueMinimo): #Verifica se o estoque ficará acima do mínimo
                    listaProdutos[chave].quantidade = nova_qtd

                    evento = "retirado " + str(produto['qtdRetirar']) + " unidades do produto " + listaProdutos[chave].codigo + " do estoque"
                    registros[horarioEvento] = evento

                    print("\nRetirou " + str(produto['qtdRetirar']) + " unidades de " + listaProdutos[chave].nome + " do estoque. \n")
                    return jsonify(success=True), 200
                else:

                    if nova_qtd == 0: #Verifica se o estoque acabou
                        listaProdutos[chave].quantidade = nova_qtd
                        listaProdutos[chave].acabou = 1
                        listaProdutos[chave].estoqueBaixo = 1

                        evento = "retirado " + produto['qtdRetirar'] + " unidades do produto " + produto['codigo'] + " e ele ACABOU"
                        registros[horarioEvento] = evento

                        print("\nProduto " + listaProdutos[chave].nome + " acabou. \n")
                    
                        mensagem = "\nProduto: " + listaProdutos[chave].nome + " ACABOU.\n"
                        #publish_sse_message(mensagem, channel=str(listaProdutos[chave]))

                        return jsonify(success=True), 200
                    
                    else: #Verifica se o estoque ficará abaixo do mínimo
                        listaProdutos[chave].quantidade = nova_qtd
                        listaProdutos[chave].estoqueBaixo = 1

                        evento = "retirado " + produto['qtdRetirar'] + " unidades do produto " + produto['codigo'] + " e ele está ABAIXO DO MÍNIMO" 
                        registros[horarioEvento] = evento

                        print("\nEstoque de " + listaProdutos[chave].nome + " está abaixo do mínimo. \n")

                        mensagem = "\nProduto: " + listaProdutos[chave].nome + " ABAIXO DO ESTOQUE MÍNIMO.\n"
                        #publish_sse_message(mensagem, channel=str(listaProdutos[chave]))

                        return jsonify(success=True), 200
            else:
                print("\nNão foi possível retirar do estoque, estoque insuficiente. \n")
                return jsonify(success=False, res_code=500, message='Estoque insuficiente'), 200

    return jsonify(success=False, res_code=500, message='Produto não existe'), 200

#Método para quantidade de produtos já existentes ao estoque
@app.route('/produto', methods=['POST'])
def adicionarProduto():

    #{
    #    'codigo' : "Codigo do Produto",
    #    'qtdAdicionar' : 1
    #}

    novoProduto = request.get_json()

    horarioEvento = strftime("%d/%m/%Y - %H:%M:%S", gmtime())

    for chave in listaProdutos.keys(): 
        if chave == novoProduto['codigo']: #Verifica se o produto existe
            
            nova_qtd = int(int(listaProdutos[chave].quantidade) + int(novoProduto['qtdAdicionar']))
            listaProdutos[chave].quantidade = nova_qtd
            
            evento = "adicionado " + str(novoProduto['qtdAdicionar']) + " unidades do produto " + novoProduto['codigo'] + " ao estoque"
            registros[horarioEvento] = evento

            if listaProdutos[chave].acabou == 1:
                listaProdutos[chave].acabou = 0

                evento = "produto " + novoProduto['codigo'] + " voltou ao estoque"
                horaVoltou = strftime("%d/%m/%Y - %H:%M:%S", gmtime())
                registros[horaVoltou] = evento

            if listaProdutos[chave].estoqueBaixo == 1 and nova_qtd >= int(listaProdutos[chave].estoqueMinimo):
                listaProdutos[chave].estoqueBaixo = 0

                evento = "estoque do produto " + novoProduto['codigo'] + " voltou ao normal"
                horaVoltou = strftime("%d/%m/%Y - %H:%M:%S", gmtime())
                registros[horaVoltou] = evento


            print("\nAdicionou " + str(novoProduto['qtdAdicionar']) + " unidades de " + listaProdutos[chave].nome + " ao estoque. \n")
        
            return jsonify(success=True), 200

        
    print("\nNão foi possível adicionar ao estoque, produto não existe. \n")
    return jsonify(success=False, res_code=500, message='Produto não existe'), 200

#Método para registrar um novo gestor
@app.route('/clientes', methods=['POST'])
def registrarCliente():

    #{
    #    'nome' : "Nome do Cliente",
    #}

    cliente = request.get_json()

    if cliente['nome'] in listaClientes:
        print('\nCliente já cadastrado. \n')

        return jsonify(success=False, res_code=500, message='Cliente já cadastrado'), 200
    else:
        print("\nRegistrou cliente " + cliente['nome'] + "\n")
        listaClientes.append(cliente['nome'])
    
    print("Lista de clientes: \n")

    for chave in listaClientes.keys():
        print("Nome= " + listaClientes[chave])

    return jsonify(success=True), 200

#Método para gerar relatório de produtos que acabaram
@app.route('/produto', methods=['GET'])
def relatorioProdutosEstoque():

    retorno = ''

    mensagem = "\nRelatório de produtos em estoque: \n\n"
    retorno += mensagem

    for produto in listaProdutos.keys():
            
        mensagem = "Código do produto: " + produto + "\n"
        retorno += mensagem

        mensagem = "Nome: " + listaProdutos[produto].nome + "\n"
        retorno += mensagem

        mensagem = "Quantidade: " + str(listaProdutos[produto].quantidade) + "\n"
        retorno += mensagem

        mensagem = "Estoque mínimo: " + str(listaProdutos[produto].estoqueMinimo) + "\n"
        retorno += mensagem

        mensagem = "Registros: " + "\n"
        retorno += mensagem

        regProcura = "produto " + listaProdutos[produto].codigo

        for registro in registros.keys():
            if regProcura in  registros[registro]:
                mensagem = "  " + registro + " - " + registros[registro] + "\n"
                retorno += mensagem
            
        mensagem = "\n"
        retorno += mensagem

    return jsonify(retorno), 200

#Método para gerar relatório de registros
@app.route('/produto', methods=['GET'])
def relatorioRegistros():
    retorno = ''

    mensagem = "\nRelatório de registros: \n\n"
    retorno += mensagem

    for registro in registros.keys():
        mensagem = registro + " - " + registros[registro] + "\n"
        retorno += mensagem
    
    return jsonify(retorno), 200

#Método para gerar relatório de produtos que acabaram
@app.route('/produto', methods=['GET'])
def relatorioProdutosAcabaram():
    retorno = ''

    mensagem = "\nRelatório de produtos que acabaram: \n\n"
    retorno += mensagem

    for produto in listaProdutos.keys():
        if listaProdutos[produto].acabou == 1:
            mensagem = "Código do produto: " + produto + "\n"
            retorno += mensagem

            mensagem = "Nome: " + listaProdutos[produto].nome + "\n"
            retorno += mensagem

            mensagem = "Quantidade: " + str(listaProdutos[produto].quantidade) + "\n"
            retorno += mensagem

            mensagem = "Estoque mínimo: " + str(listaProdutos[produto].estoqueMinimo) + "\n"
            retorno += mensagem

            mensagem = "Registros: " + "\n"
            retorno += mensagem

            regProcura = "produto " + listaProdutos[produto].codigo

            for registro in registros.keys():
                if regProcura in  registros[registro]:
                    mensagem = "  " + registro + " - " + registros[registro] + "\n"
                    retorno += mensagem
            
            mensagem = "\n"
            retorno += mensagem

    return jsonify(retorno), 200

#Método para gerar relatório de fluxo de movimentação por período
@app.route('/produto', methods=['GET'])
def relatorioFluxoMovimentacao():
    #{
    #    'dataInicio' : "Data e hora de início",
    #    'dataFim' : "Data e hora de fim",
    #}

    intervalo = request.get_json()

    retorno = ''
    
    mensagem = "\nRelatório de fluxo de movimentação: \n\n"
    retorno += mensagem

    for registro in registros.keys():
        if intervalo['dataInicio'] <= registro <= intervalo['dataFim']:
            mensagem = registro + " - " + registros[registro] + "\n"
            retorno += mensagem
    
    return jsonify(retorno), 200


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.start()

    app.run(port=5000, host='127.0.0.1',debug=True)
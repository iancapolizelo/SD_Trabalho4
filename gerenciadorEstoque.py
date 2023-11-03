from __future__ import print_function
import Pyro5.api
import Pyro5.server
from produto import produto
from time import gmtime, strftime
from flask import Flask, Response, jsonify, request, abort
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler




app = Flask("Gerenciador de Estoque")
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')

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

registros = {}

def publish_sse_message(message, channel):
    with app.app_context():
        sse.publish({"message": message}, type=channel, channel=channel)




#Método para cadastrar novos produtos no estoque
@app.route('/produto', methods=['POST'])
@Pyro5.server.expose
def cadastrarProdutoNovo(self, nomeGestor, uriGestor, codigo, nome, descricao, quantidade, precoUnidade, estoqueMinimo):

    if codigo in listaProdutos:
        print('\n' + nomeGestor + ' tentou cadastradar produto que já existe. \n')
        return "\nProduto já existe.\n"

    listaProdutos[codigo] = produto(nomeGestor, uriGestor, codigo, nome, descricao, quantidade, precoUnidade, estoqueMinimo)

    print(nomeGestor +  " cadastrou produto " + nome + " com código " + str(codigo) + " no estoque.\n")
    horaCadastro = strftime("%d/%m/%Y - %H:%M:%S", gmtime())
    evento = "produto " + codigo + " cadastrado"
    registros[horaCadastro] = evento

    return "\nProduto cadastrado com SUCESSO.\n"

#Método para listar todos os produtos cadastrados no estoque
@app.route('/produto', methods=['POST'])
@Pyro5.server.expose
def listarProdutos(self):
    retorno = ''
    
    mensagem = "\nLista de produtos: \n"
    retorno += mensagem

    for produto in listaProdutos.keys():
        mensagem = "Código do produto: " + produto + " Nome: " + listaProdutos[produto].nome + " Quantidade: " + str(listaProdutos[produto].quantidade) + " Estoque mínimo: " + listaProdutos[produto].estoqueMinimo +"\n"
        retorno += mensagem

    return retorno


#Método para retirar produtos do estoque
@app.route('/produto', methods=['POST'])    
@Pyro5.server.expose
def retirarProduto(self,nomeCliente, codigo, qtdRetirar):

    user = Pyro5.api.Proxy(listaClientes[nomeCliente])

    for chave in listaProdutos.keys(): #Verifica se o produto existe
        if chave == codigo:

            nova_qtd = int(int(listaProdutos[chave].quantidade) - int(qtdRetirar))
            horarioEvento = strftime("%d/%m/%Y - %H:%M:%S", gmtime())

            if nova_qtd >= 0: #Verifica se o estoque é suficiente
                if nova_qtd >= int(listaProdutos[chave].estoqueMinimo): #Verifica se o estoque ficará acima do mínimo
                    listaProdutos[chave].quantidade = nova_qtd

                    evento = "retirado " + str(qtdRetirar) + " unidades do produto " + listaProdutos[chave].codigo + " do estoque"
                    registros[horarioEvento] = evento

                    print("\nRetirou " + str(qtdRetirar) + " unidades de " + listaProdutos[chave].nome + " do estoque. \n")
                    return "\nRetirado com SUCESSO.\n"
                else:

                    if nova_qtd == 0: #Verifica se o estoque acabou
                        listaProdutos[chave].quantidade = nova_qtd
                        listaProdutos[chave].acabou = 1
                        listaProdutos[chave].estoqueBaixo = 1

                        evento = "retirado " + qtdRetirar + " unidades do produto " + codigo + " e ele ACABOU"
                        registros[horarioEvento] = evento

                        print("\nProduto " + listaProdutos[chave].nome + " acabou. \n")
                        mensagem = "\nVocê retirou todo o estoque do produto: " + listaProdutos[chave].nome + "\n"
                        user.notificacao(mensagem)

                        mensagem = "\nProduto: " + listaProdutos[chave].nome + " ACABOU.\n"
                        userGestor = Pyro5.api.Proxy(listaProdutos[chave].uriGestorCriador)
                        userGestor.notificacao(mensagem)

                        return "\nRetirado com SUCESSO.\n"
                    else: #Verifica se o estoque ficará abaixo do mínimo
                        listaProdutos[chave].quantidade = nova_qtd
                        listaProdutos[chave].estoqueBaixo = 1

                        evento = "retirado " + qtdRetirar + " unidades do produto " + codigo + " e ele está ABAIXO DO MÍNIMO" 
                        registros[horarioEvento] = evento

                        print("\nEstoque de " + listaProdutos[chave].nome + " está abaixo do mínimo. \n")
                        mensagem = "\nVocê retirou " + str(qtdRetirar) + " unidades do produto: " + listaProdutos[chave].nome + "\n"
                        user.notificacao(mensagem)

                        mensagem = "\nProduto: " + listaProdutos[chave].nome + " ABAIXO DO ESTOQUE MÍNIMO.\n"
                        userGestor = Pyro5.api.Proxy(listaProdutos[chave].uriGestorCriador)
                        userGestor.notificacao(mensagem)

                        return "\nRetirado com SUCESSO.\n"
            else:
                print("\nNão foi possível retirar do estoque, estoque insuficiente. \n")
                return "\nEstoque insuficiente.\n"

    return "\nProduto não existe.\n"

#Método para quantidade de produtos já existentes ao estoque
@app.route('/produto', methods=['POST'])
@Pyro5.server.expose
def adicionarProduto(self, codigo, qtdAdicionar):

    horarioEvento = strftime("%d/%m/%Y - %H:%M:%S", gmtime())

    for chave in listaProdutos.keys(): 
        if chave == codigo: #Verifica se o produto existe
            
            nova_qtd = int(int(listaProdutos[chave].quantidade) + int(qtdAdicionar))
            listaProdutos[chave].quantidade = nova_qtd
            
            evento = "adicionado " + str(qtdAdicionar) + " unidades do produto " + codigo + " ao estoque"
            registros[horarioEvento] = evento

            if listaProdutos[chave].acabou == 1:
                listaProdutos[chave].acabou = 0

                evento = "produto " + codigo + " voltou ao estoque"
                horaVoltou = strftime("%d/%m/%Y - %H:%M:%S", gmtime())
                registros[horaVoltou] = evento

            if listaProdutos[chave].estoqueBaixo == 1 and nova_qtd >= int(listaProdutos[chave].estoqueMinimo):
                listaProdutos[chave].estoqueBaixo = 0

                evento = "estoque do produto " + codigo + " voltou ao normal"
                horaVoltou = strftime("%d/%m/%Y - %H:%M:%S", gmtime())
                registros[horaVoltou] = evento


            print("\nAdicionou " + str(qtdAdicionar) + " unidades de " + listaProdutos[chave].nome + " ao estoque. \n")
        
            return "\nUnidades adicionadas com SUCESSO.\n"

        
    print("\nNão foi possível adicionar ao estoque, produto não existe. \n")
    return "\nProduto não existe.\n"

#Método para registrar um novo gestor
@app.route('/clientes', methods=['POST'])
@Pyro5.server.expose
def registrarCliente(self, nomeCliente, uriCliente):
    if nomeCliente in listaClientes:
        print('\nCliente já cadastrado. \n')

        return "\nCliente já cadastrado.\n"
    else:
        print("\nRegistrou cliente " + nomeCliente + "\n")
        listaClientes[nomeCliente] = uriCliente
    
    print("Lista de clientes: \n")
    for chave in listaClientes.keys():
        print("Nome= " + chave + " e Uri = " + str(listaClientes[chave]))

    return "\nCliente cadastrado com SUCESSO.\n"

#Método para gerar relatório de produtos que acabaram
@app.route('/produto', methods=['POST'])
@Pyro5.server.expose
def relatorioProdutosEstoque(self):

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

    return retorno

#Método para gerar relatório de registros
@app.route('/produto', methods=['POST'])
@Pyro5.server.expose
def relatorioRegistros(self):
    retorno = ''

    mensagem = "\nRelatório de registros: \n\n"
    retorno += mensagem

    for registro in registros.keys():
        mensagem = registro + " - " + registros[registro] + "\n"
        retorno += mensagem
    
    return retorno

#Método para gerar relatório de produtos que acabaram
@app.route('/produto', methods=['POST'])
@Pyro5.server.expose
def relatorioProdutosAcabaram(self):
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

    return retorno

#Método para gerar relatório de fluxo de movimentação por período
@app.route('/produto', methods=['POST'])
@Pyro5.server.expose
def relatorioFluxoMovimentacao(self, dataInicio, dataFim):
    retorno = ''
    
    mensagem = "\nRelatório de fluxo de movimentação: \n\n"
    retorno += mensagem

    for registro in registros.keys():
        if dataInicio <= registro <= dataFim:
            mensagem = registro + " - " + registros[registro] + "\n"
            retorno += mensagem
    
    return retorno
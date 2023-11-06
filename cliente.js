const EventSource = require('eventsource');
const fetch = require('node-fetch');

const endpoint = 'http://127.0.0.1:5000/';

const eventSource = new EventSource(endpoint);
const readline = require('readline');


const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Tratamento de eventos SSE recebidos
//eventSource.addEventListener('message', event => {
//    const message = JSON.parse(event.data);
//    console.log('Nova mensagem recebida:', message);
//});


//eventSource.addEventListener('error', error => {
//    console.error('Erro na conexão SSE:', error);
//});

function cadastrarProduto() {
    rl.question("Digite o código do produto: ", (codigo) => {
        rl.question("Digite o nome do produto: ", (nome) => {
            rl.question("Digite a descrição do produto: ", (descricao) => {
                rl.question("Digite a quantidade do produto: ", (quantidade) => {
                    rl.question("Digite o preço por unidade do produto: ", (precoUnidade) => {
                        rl.question("Digite o estoque mínimo do produto: ", (estoqueMinimo) => {
                        const produto = {
                            codigo: codigo,
                            nome: nome,
                            descricao: descricao,
                            quantidade: quantidade,
                            precoUnidade: precoUnidade,
                            estoqueMinimo: estoqueMinimo,
                            acabou: 0,
                            estoqueBaixo: 0
                        };

                        fetch('http://http://127.0.0.1:5000/produto/', {
                            method: 'POST',
                            body: JSON.stringify(produto),
                            headers: { 'Content-Type': 'application/json' }
                        })
                            .then(response => response.json())
                            .then(data =>{
                                console.log(data);
                                iniciarCliente();
                            })
                            .catch(error => {
                                console.log("Erro ao cadastrar produto:", error);
                                iniciarCliente();
                            
                            });
                        }
                        );
                    });
                });
            });
        });
    });
}

function adicionarProduto() {
    rl.question("Digite o código do produto: ", (codigo) => {
        rl.question("Digite a quantidade do produto: ", (qtdAdicionar) => {
            const produto = {
                codigo: codigo,
                qtdAdicionar: qtdAdicionar
            };

            fetch('http://http://127.0.0.1:5000/produto/', {
                method: 'POST',
                body: JSON.stringify(produto),
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => response.json())
                .then(data =>{
                    console.log(data);
                    iniciarCliente();
                })
                .catch(error => {
                    console.log("Erro ao adicionar produto:", error);
                    iniciarCliente();
                
                });  
        });
    });
}

function retirarProduto() {
    rl.question("Digite o código do produto: ", (codigo) => {
        rl.question("Digite a quantidade do produto: ", (qtdRetirar) => {
            const produto = {
                codigo: codigo,
                qtdRetirar: qtdRetirar
            };

            fetch('http://http://127.0.0.1:5000/produto/', {
                method: 'POST',
                body: JSON.stringify(produto),
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => response.json())
                .then(data =>{
                    console.log(data);
                    iniciarCliente();
                }
                )
                .catch(error => {
                    console.log("Erro ao retirar produto:", error);
                    iniciarCliente();

                });
        });
    });
}

function listarProdutos() {
    fetch('http://http://127.0.0.1:5000/produto/', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data =>{
            console.log(data);
            iniciarCliente();
        }
        )
        .catch(error => {
            console.log("Erro ao listar produtos:", error);
            iniciarCliente();

        });
}

function relatorioProdutosEmEstoque() {
    fetch('http://http://127.0.0.1:5000/produto/', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data =>{
            console.log(data);
            iniciarCliente();
        }
        )
        .catch(error => {
            console.log("Erro ao listar produtos:", error);
            iniciarCliente();

        });
}

function relatorioMovimentacaoProdutos() {
    fetch('http://http://127.0.0.1:5000/produto/', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data =>{
            console.log(data);
            iniciarCliente();
        }
        )
        .catch(error => {
            console.log("Erro ao listar produtos:", error);
            iniciarCliente();

        });
}

function relatorioProdutosAcabaram() {
    fetch('http://http://127.0.0.1:5000/produto/', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data =>{
            console.log(data);
            iniciarCliente();
        }
        )
        .catch(error => {
            console.log("Erro ao listar produtos:", error);
            iniciarCliente();

        });
}

function relatorioFluxoMovimentacao() {
    rl.question("Qual a data de início do relatório? Digite no modelo: DD/MM/AAAA -  HH:MM:SS ", (dataInicio) => {
        rl.question("Qual a data de fim do relatório? Digite no modelo: DD/MM/AAAA -  HH:MM:SS ", (dataFim) => {
            const data = {
                dataInicio: dataInicio,
                dataFim: dataFim
            };
            
            fetch('http://http://127.0.0.1:5000/produto/', {
                method: 'GET',
                body: JSON.stringify(data),
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => response.json())
                .then(data =>{
                    console.log(data);
                    iniciarCliente();
                }
                )
                .catch(error => {
                    console.log("Erro ao listar produtos:", error);
                    iniciarCliente();

                });
        });
    });
}


function exibirMenu() {
    console.log("===== Menu do Cliente =====");
    console.log("1 - Cadastrar novo produto");
    console.log("2 - Adicionar produto existente");
    console.log("3 - Retirar produto");
    console.log("4 - Listar produtos");
    console.log("5 - Gerar relatórios");
    console.log("0. Sair");
    console.log("===========================");
}

function exibirMenuRelatorio() {
    console.log("===== Menu de Relatórios =====");
    console.log("a - Relatório de produtos em estoque");
    console.log("b - Relatório de registros de movimentação de produtos");
    console.log("c - Relatório de produtos que acabaram");
    console.log("d - Relatório do fluxo de movimentação por período");
    console.log("x - Sair");
    console.log("===========================");
}

function processarEscolhaRelatorio(escolha) {
    switch (escolha) {
        case 'a':
            relatorioProdutosEmEstoque();
            break;
        case 'b':
            relatorioMovimentacaoProdutos();
            break;
        case 'c':
           relatorioProdutosAcabaram();
            break;
        case 'd':
            relatorioFluxoMovimentacao();
            break;
        case  'x':
            iniciarCliente();
            break;
        default:
            console.log("Escolha inválida. Tente novamente.");
            break;
    }
}

function processarEscolha(escolha) {
    switch (escolha) {
        case '1':
            cadastrarProduto();
            break;
        case '2':
            adicionarProduto();
            break;
        case '3':
            retirarProduto();
            break;
        case '4':
            listarProdutos();
            break;

        case '5':
            exibirMenuRelatorio();
            rl.question("Digite sua escolha: ", (escolha) => {
                // Obtém o primeiro caractere da escolha
                const primeiroCaractere = escolha.charAt(0);

                // Chame a função processarEscolha com o primeiro caractere
                processarEscolhaRelatorio(primeiroCaractere);

                if (primeiroCaractere !== '0') {
                    iniciarCliente();
                }
            });
            break;

        case '0':
            rl.close();
            break;
            
        default:
            console.log("Escolha inválida. Tente novamente.");
            iniciarCliente();
            break;
    }
}


function iniciarCliente() {
    exibirMenu();

    rl.question("Digite sua escolha: ", (escolha) => {
        // Obtém o primeiro caractere da escolha
        const primeiroCaractere = escolha.charAt(0);

        // Chame a função processarEscolha com o primeiro caractere
        processarEscolha(primeiroCaractere);

        if (primeiroCaractere !== '0') {
            iniciarCliente();
        }
    });
}

iniciarCliente();
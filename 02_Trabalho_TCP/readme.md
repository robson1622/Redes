# Protocolos de comunicação
### Todos o protocolo está definido em [Protocolo.py](Protocolo.py)
#### Formato das Requisições: Como o cliente envia “Sair”, “Arquivo [Nome]”, “Chat [Msg]”.
```
[Cliente] Lista de comandos aceitos :
    sair                                - Encerra a conexão com o servidor.
    arquivo [NOME.EXTENSAO]             - Solicita o download do arquivo [NOME.EXTENSAO].
    chat [MENSAGEM]                     - Envia a mensagem de chat para o servidor.  
    ajuda                               - Exibe a lista de comandos aceitos.                
```
```
[Servidor] Lista de comandos aceitos :
    listar threads                      - Lista todas as threads ativas
    desligar                            - Desliga o servidor
    fechar thread [id/todas]            - Fecha thread específica ou todas
    msg "texto" [id/todas]              - Envia mensagem para thread(s)
    monitor threads [ativar/desativar]  - Configura monitoramento
    ajuda                               - Exibe esta ajuda 
```
### Formato das Respostas/Transferência de Arquivo: A ordem e o formato para enviar:
**Por parte do servidor, esta é uma requisição mal sucedida, seguida de uma bem sucessida com seus respectivos status.**
```
[Server]  Cliente conectado : ('127.0.0.1', 52175)
[Thread] [0] Conectado !   
[Thread] [0] Esperando mensagens ...   
[Server]  Mensagem recebida. arquivo [inexistente.pdf]
[Thread] [0] Enviando resposta :  Arquivo não encontrado. 
...
[Server]  Mensagem recebida. arquivo [virtualbox.dmg]
[Thread] [0] Enviando arquivo ...  virtualbox.dmg 
```
**Por parte do cliente para as mesmas requisições:**
````
[Cliente] >> arquivo [inexistente.pdf]
[Cliente] Mensagem enviada.
[Cliente] Mensagem recebida :  Arquivo não encontrado.
[Cliente] >> arquivo [virtualbox.dmg]
[Cliente] Mensagem enviada.
[Cliente] Mensagem recebida :  Arquivo encontrado.
[Cliente] Hash verificado : 4b6f048c4ffb50c2508e8e792c4aea684e7442ea1e956d647f9a1309a6a7fcd7
[Cliente] Arquivo salvo: ./arquivos_recebidos/cliente_virtualbox.dmg (138357293 bytes)
[Cliente] Arquivo recebido com sucesso.
````
**Tabela de Formato do Pacote de Transferência de Arquivo e seus metadados**
| Campo               | Tamanho (bytes) | Descrição                      |
|---------------------|-----------------|--------------------------------|
| TAMANHO_NOME        | 2               | Tamanho do nome do arquivo         |
| NOME                | 1 a 65k      | Nome do arquivo                 |
| TAMANHO_HASH       | 2               | Tamanho do hash SHA-256          |
| HASH                | 1 a 65k       | Hash SHA-256 do arquivo        |
| TAMANHO_DADOS       | 8               | Tamanho dos dados do arquivo      |
| DADOS               | 1 a 4.2G        | Dados do arquivo                |


### Hash SHA do arquivo completo.
O Hash aqui utilizado foi o padrão, SHA-256, que gera um hash de 64 caracteres hexadecimais (256 bits).
````
[Cliente] Hash verificado : 4b6f048c4ffb50c2508e8e792c4aea684e7442ea1e956d647f9a1309a6a7fcd7
````
### Os dados do arquivo (como serão segmentados/enviados sobre o stream TCP).
Também fou utilizado o padrão de segmentação de dados em streams TCP, onde o arquivo é lido em blocos (chunks) de 4096 bytes (4KB) e enviado sequencialmente até o final do arquivo.

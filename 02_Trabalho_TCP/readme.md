# Dcocumento de relatório do projeto.

### Requisitos do Servidor TCP (Multithread):

Inicialização: Deve ser executado antes de qualquer cliente.
Porta de Escuta: Deve aguardar conexões em uma porta TCP específica (escolhida pelo aluno, maior que 1024).
Gerenciamento de Conexões:
Aceitar conexões TCP de múltiplos clientes.
Para cada nova conexão aceita, o servidor deve criar uma thread dedicada para lidar exclusivamente com a comunicação daquele cliente.
Funcionalidades Dentro de Cada Thread do Servidor:

A thread dedicada a um cliente deve:

Loop de Requisições: Aguardar e processar requisições enviadas pelo cliente conectado até receber a requisição “Sair”.
Tratamento de Requisições: Implementar a lógica para as seguintes requisições (o formato exato faz parte do protocolo a ser definido pelo aluno):
Requisição “Sair”:
Fechar a conexão TCP com aquele cliente.
Encerrar a thread correspondente de forma limpa.
Requisição “Arquivo [Nome_Arquivo.ext]”:
Verificar se o arquivo [Nome_Arquivo.ext] existe no servidor.
Se o arquivo existir:
Calcular o hash SHA (ex: SHA-256) do conteúdo completo do arquivo. (O aluno deve pesquisar como implementar/usar bibliotecas padrão para cálculo de SHA).
Enviar o arquivo para o cliente, seguindo o protocolo de aplicação definido (ver seção “Protocolo de Aplicação”).
A transferência deve suportar arquivos grandes (> 10 MB).
Se o arquivo não existir:
Enviar uma mensagem de erro/status apropriada para o cliente, conforme definido no protocolo.
Requisição “Chat [Mensagem]” (Recebida do Cliente):
Exibir a [Mensagem] recebida na console do servidor (indicando de qual cliente veio, se possível).
Envio de Mensagens de Chat (Iniciadas pelo Servidor):
Permitir que texto digitado na console principal do servidor seja enviado como mensagem de chat para todos os clientes conectados (ou implementar um mecanismo para direcionar a um cliente específico, se desejado). Nota: Esta parte requer atenção à comunicação entre a thread principal/console e as threads dos clientes.
Requisitos do Cliente TCP:

Inicialização: Deve ser executado após o servidor estar ativo.
Conexão:
Permitir ao usuário especificar o endereço IP e a porta do servidor TCP.
Estabelecer uma conexão TCP com o servidor.
Interface do Usuário:
Oferecer um meio para o usuário escolher e enviar as seguintes requisições para o servidor: “Sair”, “Arquivo [Nome_Arquivo.ext]”, “Chat [Mensagem]”.
Processamento de Respostas do Servidor:
Resposta a “Sair”: Após enviar “Sair”, fechar a conexão do lado do cliente e encerrar o programa.
Resposta a “Arquivo”:
Receber os dados do arquivo (metadados e conteúdo) conforme a ordem definida no protocolo de aplicação.
Salvar o conteúdo recebido em um arquivo local.
Após receber todo o conteúdo, calcular o hash SHA do arquivo recebido.
Verificar a integridade: Comparar o hash calculado com o hash recebido do servidor. Informar ao usuário se o arquivo foi recebido corretamente ou se houve corrupção.
Deve ser capaz de receber e salvar arquivos grandes (> 10 MB).
Resposta a “Chat” (Mensagens recebidas do Servidor):
Exibir as mensagens de chat recebidas do servidor na tela do cliente.
Definição do Protocolo de Aplicação (Tarefa do Aluno):

O aluno deve definir e documentar um protocolo de aplicação simples sobre TCP para gerenciar a comunicação. Este protocolo deve especificar claramente:

Formato das Requisições: Como o cliente envia “Sair”, “Arquivo [Nome]”, “Chat [Msg]”.
Formato das Respostas/Transferência de Arquivo: A ordem e o formato para enviar:
Status da operação (ex: OK, ERRO_ARQUIVO_NAO_ENCONTRADO).
Metadados do arquivo (Nome do arquivo, Tamanho total).
Hash SHA do arquivo completo.
Os dados do arquivo (como serão segmentados/enviados sobre o stream TCP).
Formato das Mensagens de Chat.

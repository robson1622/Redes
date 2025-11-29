from enum import Enum


PORTA_SERVIDOR = 7070
HOST_PADRAO = 'localhost'
TAMANHO_QUEUE = 1024
BUFFER_SIZE = 1024
ENCODER_FORMACT = 'utf-8'
MONITOR_OF_THREADS  = True
MONITOR_OF_SERVER    = True
class IDENTIFIERS(Enum):
    CLIENTE    = "Cliente"
    SERVER  = "Server"
    THREAD  = "Thread"

class CLIENT_STATUS(Enum):
    CONNECTED            = "Conectado ! "
    DISCONNECTED         = "Desconectado ! "
    CLOSED               = "Thead encerrada ! "
    RECEIVED_MENSAGE     = "Mensagem recebida : "
    CLIENT_DISCONNECTED  = "Cliente desconectado ! "
    ARCHIVE_RECEIVED     = "Arquivo recebido ! "
    PROCESSING_EXIT      = "Processando saída ... "
    EXECUTING_CHAT       = "Executando chat ... "
    PROCESSING_ARCHIVE   = "Processando arquivo ... "
    INVALID_COMMAND      = "Comando inválido : "



class THREAD_STATUS(Enum):
    CONNECTING_STR          = "Conectando ... "
    CONNECTED_STR           = "Conectado ! "
    DISCONNECTED_STR        = "Desconectado ! "
    DISCONNECTING_STR       = "Desconectando ... "
    WAITING_MENSAGE_STR     = "Esperando mensagens ... "
    SENDING_FILE_STR        = "Enviando arquivo ... "
    CLOSING_CONNECTION_STR  = "Fechando conexão ... "
    CLOSED_STR              = "Thead encerrada ! "
    SENDING_MENSAGE_STR     = "Enviando mensagem ... "
    SENDING_RESPONSE_STR    = "Enviando resposta : "
    RECEIVED_MENSAGE_STR    = "Mensagem recebida : "
    CLIENT_DISCONNECTED_STR = "Cliente desconectado ! "
    TIMEOUT_STR             = "Timeout atigido ! "


    def CONNECTING(id,msg : str = ""):
        terminal(IDENTIFIERS.THREAD.value,id,f"{THREAD_STATUS.CONNECTING_STR.value} {msg} ")
    def CONNECTED(id,msg : str = ""):
        terminal(IDENTIFIERS.THREAD.value,id,f"{THREAD_STATUS.CONNECTED_STR.value} {msg} ")
    def DISCONNECTED(id,msg : str = ""):
        terminal(IDENTIFIERS.THREAD.value,id,f"{THREAD_STATUS.DISCONNECTED_STR.value} {msg} ")
    def DISCONNECTING(id,msg : str = ""):
        terminal(IDENTIFIERS.THREAD.value,id,f"{THREAD_STATUS.DISCONNECTING_STR.value} {msg} ")
    def WAITING_MENSAGE(id,msg : str = ""):
        terminal(IDENTIFIERS.THREAD.value,id,f"{THREAD_STATUS.WAITING_MENSAGE_STR.value} {msg} ")
    def SENDING_FILE(id,msg : str = ""):
        terminal(IDENTIFIERS.THREAD.value,id,f"{THREAD_STATUS.SENDING_FILE_STR.value} {msg} ")
    def CLOSING_CONNECTION(id,msg : str = ""):
        terminal(IDENTIFIERS.THREAD.value,id,f"{THREAD_STATUS.CLOSING_CONNECTION_STR.value} {msg} ")
    def CLOSED(id,msg : str = ""):
        terminal(IDENTIFIERS.THREAD.value,id,f"{THREAD_STATUS.CLOSED_STR.value} {msg} ")
    def SENDING_MENSAGE(id,msg : str = ""):
        terminal(IDENTIFIERS.THREAD.value,id,f"{THREAD_STATUS.SENDING_MENSAGE_STR.value} {msg} ")
    def RECEIVED_MENSAGE(id,msg : str = ""):
        terminal(IDENTIFIERS.THREAD.value,id,f"{THREAD_STATUS.RECEIVED_MENSAGE_STR.value} {msg} ")
    def CLIENT_DISCONNECTED(id,msg : str = ""):
        terminal(IDENTIFIERS.THREAD.value,id,f"{THREAD_STATUS.CLIENT_DISCONNECTED_STR.value} {msg} ")
    def TIMEOUT(id,msg : str = ""):
        terminal(IDENTIFIERS.THREAD.value,id,f"{THREAD_STATUS.TIMEOUT_STR.value} {msg} ")
    def SENDING_RESPONSE(id,msg : str = ""):
        terminal(IDENTIFIERS.THREAD.value,id,f"{THREAD_STATUS.SENDING_RESPONSE_STR.value} {msg} ")


# MENSAGENS QUE SOMENTE O SERVIDOR(E THREADS) ENVIAM PARA O USUÁRIO 
# OU MENSAGENS INTERNAS
class MENSAGE_SERVER_TYPE(Enum):
    # SERVIDOR -> CLIENTE
    MENSAGE_SERVER_TYPE_EXIST_ARCHIVE               = "Arquivo encontrado."
    MENSAGE_SERVER_TYPE_NO_EXIST_ARCHIVE            = "Arquivo não encontrado."
    MENSAGE_SERVER_TYPE_MENSAGE_RECEIVED            = "Mensagem recebida."
    MENSAGE_SERVER_TYPE_PREPARE_TO_SEND             = "Preparando para o envio..."
    # SERVIDOR -> SERVIDOR
    MENSAGE_SERVER_TYPE_LIST_THREADS                = "listar threads"
    MENSAGE_SERVER_TYPE_SHOTDOWN                    = "desligar"
    MENSAGE_SERVER_TYPE_CLOSE_THREAD                = "fechar thread" # fechar thread [todos] ou [51234]
    MENSAGE_SERVER_TYPE_SEND_MENSAGE_CLIENT         = "msg" # mensagem "minha mensagem." [51234] ou [todas]
    MENSAGE_SERVER_TYPE_CONFIGURE_MONITOR_THREAD    = "monitor threads" # monitor threads [ativar/desativar]
    MENSAGE_SERVER_TYPE_HELP                        = "ajuda"
    MENSAGE_SERVER_TYPE_COMMAND_NOT_FOUND           = "Comando não encontrado : "


# MENSAGENS QUE SOMENTE O USUÁRIO DEVE ENVIAR PARA O SERVIDOR (ELE NÃO DISTINGUE THREADS)
class MENSAGE_CLIENT(Enum):
    MENSAGE_CLIENT_EXIT               = "sair" # sair ou Sair
    MENSAGE_CLIENT_ARCHIVE            = "arquivo" # arquivo [nome.ext] ou Arquivo [nome.ext]
    MENSAGE_CLIENT_MENSAGE            = "chat"   # chat [mensagem em texto] ou Chat [mensagem em texo]
    MENSAGE_CLIENT_HELP               = "ajuda"  # ajuda ou Ajuda

class Mensage :
    def __init__(self):
        pass

class MensageQueue :
    def __init__(self,type : MENSAGE_SERVER_TYPE,conteudo : str):
        self.type = type
        self.conteudo = conteudo
        pass


def terminal(objeto: str,id : int = None,mensagem : str = None):
    identification = ""
    if id != None :
        identification = f"[{id}]"
    if MONITOR_OF_THREADS and objeto == IDENTIFIERS.THREAD.value :
        print(f"[{objeto}] {identification} {mensagem}")
    elif MONITOR_OF_SERVER and objeto == IDENTIFIERS.SERVER.value :
        print(f"[{objeto}] {identification} {mensagem}")
    elif objeto == IDENTIFIERS.CLIENTE.value :
        print(f"[{objeto}]{identification} {mensagem}")
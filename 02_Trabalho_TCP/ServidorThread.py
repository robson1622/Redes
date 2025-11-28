from Protocolo import *
from queue import Queue,Empty
from threading import Thread
import socket
import select
import os
import json
import struct

ECHO_MODE = True
TIMEOUT_IN_MS = 5000
SHOW_MENSAGE_ALIVE = False
#   V 0.2
#   -> Conseguir receber mensagem dos clientes na thread
#   -> Encerrar a thread se a mensagem for MENSAGE_SERVER_TYPE_CLOSE_THREAD

def ServidorThread(thread_socket : socket,queue : Queue,thread_id : int,callback):
    THREAD_STATUS.CONNECTED(thread_id)
    terminal(objeto=IDENTIFIERS.SERVER.value,id=None,mensagem=">>")
    msg = ""
    resposta = ""
    esperando = True
    contador = 0
    encerrar = False
    try:
        while ( not encerrar ):
            contador += 1
            if esperando:
                THREAD_STATUS.WAITING_MENSAGE(thread_id)
                esperando = False
            # Recebendo dados do cliente
            # msg = thread_socket.recv(BUFFER_SIZE).decode(ENCODER_FORMACT)

            ready_sockets, _, _ = select.select([thread_socket], [], [], 0.001)

            if ready_sockets:
                try :
                    msg_bytes = thread_socket.recv(BUFFER_SIZE)

                    if not msg_bytes:  # b'' = cliente desconectou
                        THREAD_STATUS.CLIENT_DISCONNECTED(thread_id)
                        encerrar = True
                        break
                    msg = msg_bytes.decode(ENCODER_FORMACT)
                    if ECHO_MODE:
                        THREAD_STATUS.RECEIVED_MENSAGE(thread_id, msg)
                    terminal(objeto=f"{IDENTIFIERS.SERVER.value}",id=None,mensagem=f"{MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_MENSAGE_RECEIVED.value} {msg}")
                    resposta = PegarResposta(msg)
                    if resposta == None :
                        thread_socket.send(MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_NO_EXIST_ARCHIVE.value.encode(ENCODER_FORMACT))
                    elif len(resposta) > 0:
                        # Responder
                        contador = 0
                        THREAD_STATUS.SENDING_RESPONSE(thread_id, str(resposta))
                        EnviarResposta(thread_socket, resposta, ENCODER_FORMACT)
                    elif (ready_sockets) :
                        THREAD_STATUS.CLIENT_DISCONNECTED(thread_id)
                        encerrar = True
                    elif (contador >= TIMEOUT_IN_MS) :
                        contador = 0
                        try :
                            if SHOW_MENSAGE_ALIVE :
                                THREAD_STATUS.SENDING_MENSAGE(thread_id,THREAD_STATUS.WAITING_MENSAGE_STR.value)
                                thread_socket.send(THREAD_STATUS.WAITING_MENSAGE_STR.value.encode(ENCODER_FORMACT))
                        except :
                            THREAD_STATUS.CLIENT_DISCONNECTED(thread_id)
                            encerrar = True
                            break
                    
                except :
                    THREAD_STATUS.CLIENT_DISCONNECTED(thread_id)
                    encerrar = True
                    break
            # mensagem do servidor
            try:
                queue_msg : MensageQueue = queue.get(block=True, timeout=0.001)
                if queue_msg.type == MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_CLOSE_THREAD:
                    THREAD_STATUS.DISCONNECTING(thread_id, "Comando do servidor")
                    esperando = False
                    break
                elif queue_msg.type == MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_SEND_MENSAGE_CLIENT:
                    THREAD_STATUS.SENDING_MENSAGE(thread_id,f" para : {thread_socket.getpeername()}")
                    thread_socket.send(queue_msg.conteudo.encode(ENCODER_FORMACT))
            except Empty :
                # Timeout - continua o loop
                continue
            terminal(objeto=f"{IDENTIFIERS.SERVER.value}",id=None,mensagem=f"{MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_MENSAGE_RECEIVED.value} {msg}")
            # Tratar a mensagem
            
            
    finally :
        # Fechando a conexão com o cliente
        thread_socket.close()
        THREAD_STATUS.CLOSED(thread_id)
        callback(thread_id)

def PegarResposta(comando: str):
    comando = comando.strip()
    if not comando or ' ' not in comando:
        return ""
    
    tipo, conteudo = comando.split(' ', 1)
    tipo = tipo.lower()
    conteudo = conteudo.strip()
    
    if tipo == "chat":
        return MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_MENSAGE_RECEIVED.value
    
    if tipo == "arquivo":
        caminho = os.path.join(conteudo)
        
        if not os.path.exists(caminho) or not os.path.isfile(caminho):
            return None
        
        with open(caminho, 'rb') as f:
            dados = f.read()
        
        nome = os.path.basename(conteudo)
        return (nome, dados)
    
    return ""

def EnviarResposta(socket, resposta, encoding='utf-8'):
    """
    Envia resposta: string ou tupla (nome_arquivo, dados)
    """
    if resposta is None:
        socket.send(MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_NO_EXIST_ARCHIVE.value.encode(encoding))
        return
    
    # Mensagem de texto
    if isinstance(resposta, str):
        socket.send(resposta.encode(encoding))
        return
    
    # Arquivo: (nome, dados)
    if isinstance(resposta, tuple):
        nome, dados = resposta
        nome_bytes = nome.encode(encoding)
        
        # Formato: TAMANHO_NOME (2 bytes) + NOME + TAMANHO_DADOS (8 bytes) + DADOS
        pacote = (
            struct.pack('!H', len(nome_bytes)) +  # 2 bytes: tamanho do nome
            nome_bytes +                           # nome do arquivo
            struct.pack('!Q', len(dados)) +        # 8 bytes: tamanho dos dados
            dados                                  # dados do arquivo
        )
        socket.sendall(pacote)

from Protocolo import *
import socket
from threading import Thread,Lock
import re
import time
import select
import struct
# V 0.2
# @brief Conseguir mandar mensagem para o servidor.
ECHO_MODE = True

class Client():
    def __init__(self):
        self.lock = Lock()
        self.thread_input = None
        self.thread_action = None
        self.host = None
        self.porta = None
        self.socket = None
        self.running = True
        self.first_config_complete = False
        pass
    
    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(f"=====================================\n"
              f"======== Sistema Cliente TCP ========\n"
              f"=====================================\n")
        self.print("Bem vindo cliente !.")
        self.print("Digite 'ajuda' para ver os comandos.")

        self.thread_input = Thread(target=self.inputThread,
                                   args=(),
                                   name="Cluente Imput Thread")
        self.thread_input.start()
        self.host = HOST_PADRAO
        self.porta = PORTA_SERVIDOR
        
        try:
            while (self.running):
                # while(not self.first_config_complete):
                #     if self.porta is None :
                #         self.porta = input(f"Digite a porta do servidor.\nPressione [return/enter] para porta padrão [{PORTA_SERVIDOR}].\n[{IDENTIFIERS.SERVER.value}] >> ")
                #         if self.porta == "" :
                #             self.print(f"Porta padrao setada : [{PORTA_SERVIDOR}]")
                #             self.porta = PORTA_SERVIDOR

                #     if self.host is None :
                #         self.host = input(f"Digite o host/IP do servidor.\nPressione [return/enter] para padrão [{HOST_PADRAO}].\n[{IDENTIFIERS.SERVER.value}] >> ")
                #         if self.host == "" :
                #             self.print(f"Host padrao setada : [{HOST_PADRAO}]")
                #             self.host = HOST_PADRAO
                            
                #     if self.host and self.porta :
                #         self.print(f"Solicitando conexão com servidor...")
                #         self.first_config_complete = True
                self.socket.connect((self.host,self.porta))
                print(f"[{IDENTIFIERS.CLIENTE.value}] Conectado ao servidor {self.host}:{self.porta}")
                self.first_config_complete = True
                while (self.running and self.first_config_complete):
                    ready_sockets, _, _ = select.select([self.socket], [], [], 0.001)

                    if ready_sockets:
                        try :
                            msg_bytes = self.socket.recv(BUFFER_SIZE)

                            if msg_bytes:  # b'' = cliente desconectou
                                # self.print(CLIENT_STATUS.DISCONNECTED.value)
                                # self.first_config_complete = False

                                mensagem = msg_bytes.decode(ENCODER_FORMACT) 
                                if ECHO_MODE:
                                    self.print(f"{CLIENT_STATUS.RECEIVED_MENSAGE.value} {mensagem}")
                                
                        except :
                            continue
        
        except ConnectionRefusedError:
            self.print("Erro: Não foi possível conectar ao servidor")
        except Exception as e:
            self.print(f"Erro: {e}")
        finally:
            self.socket.close()
            self.ActionExit()
            self.print("Programa encerrado.")
            exit(0)

    def inputThread(self):
        while(self.running):
            time.sleep(0.1)
            comando = input(f"[{IDENTIFIERS.CLIENTE.value}] >> ")
            self.thread_action = Thread(target=self.ActionThread,
                                        args=(comando,),
                                        name="Cliente Thread Action")
            self.thread_action.start()

    def ActionThread(self,mensagem: str):
        match = re.search(r'\[(.*?)\]', mensagem)
        msg = match.group(1) if match else ""
        palavras = mensagem.split()
        command = palavras[0].lower() if palavras else ""

        if MENSAGE_CLIENT.MENSAGE_CLIENT_EXIT.value == command :
            self.ActionExit()
            return
        elif MENSAGE_CLIENT.MENSAGE_CLIENT_MENSAGE.value == command :
            self.ActionSendMensage(msg)
            return
        elif MENSAGE_CLIENT.MENSAGE_CLIENT_ARCHIVE.value == command :
            self.ActionArquivo(msg)
            return
        
        self.print(f"Comando não encontrado : {mensagem}")
        return

    
    def ActionArquivo(self,local_path : str):
        archive_complete = False
        self.socket.send(local_path.encode(ENCODER_FORMACT))
                    
    def ActionSendMensage(self,mensage : str):
        with self.lock :
            self.socket.send(mensage.encode(ENCODER_FORMACT))
            self.print(f"Mensagem enviada.")

    def ActionExit(self) :
        self.running = False

    def print(self,msg : str):
        terminal(objeto=IDENTIFIERS.CLIENTE.value,id=None,mensagem=msg)

    def serverPrint(self,msg : str):
        terminal(objeto=IDENTIFIERS.SERVER.value,id=None,mensagem=msg)

if __name__ == "__main__":
    cliente = Client()
    cliente.run()
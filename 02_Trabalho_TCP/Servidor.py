from Protocolo import *
from queue import Queue
from threading import Thread,Lock
from ServidorThread import ServidorThread
from ThreadManager import ThreadManager
import socket
import re
import time
# V 0.1
# -> Versão deve conseguir criar uma thread
# -> Encerrar a thread e liberar a memória

class Servidor :

    def __init__(self):
        # socket
        self.servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor_socket.bind((HOST_PADRAO, PORTA_SERVIDOR))
        # threads
        self.thread_manager = ThreadManager()
        self.action = None
        self.input_thread = None
        self.action_thread = None
        self.wait_input = True

    def run(self):
        self.servidor_socket.listen(10)
        self.servidor_socket.settimeout(3.0)
        try:
            print(  f"============================================\n"
                    f"========= Servidor mult-thread TCP =========\n"
                    f"============================================\n \n \n \n"
                    f"[{IDENTIFIERS.SERVER.value}] Bem vindo ! \n"
                    f"[{IDENTIFIERS.SERVER.value}] Digite '{MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_HELP.value}' para ver os comandos."
                  )
            self.input_thread = Thread(target=self.inputThread,
                                       args=(),
                                       name="Input Thread")
            self.input_thread.start()
            while self.wait_input:
                # Aceitando uma conexão
                try:
                    cliente_socket, endereco = self.servidor_socket.accept()
                    print("\n")
                    self.print(f" Cliente conectado : {endereco}")
                    self.thread_manager.createThread(cliente_socket=cliente_socket)
                    
                except socket.timeout:
                    continue
                    
        except KeyboardInterrupt:
            print("\nServidor encerrado.")
        finally:
            self.servidor_socket.close()
            self.print("Finalizado.")
            exit(0)

    def inputThread(self):
        while (self.wait_input):
            time.sleep(0.001)
            comando = input(f"[{IDENTIFIERS.SERVER.value}] >> ")
            self.action_thread = Thread(target=self.ActionThread,
                                       args=(comando,),
                                       name="Action Thread")
            self.action_thread.start()
            
    def ActionThread(self,comando : str) -> None:
        if not self.ActionExecute(user_input=comando):
            if len(comando) > 0 :  self.errorCommand(comando)

    def errorCommand(self, user_input: str) -> None:
        self.print(f"[{IDENTIFIERS.SERVER.value}] {MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_COMMAND_NOT_FOUND.value}: '{user_input}'")

    def ActionExecute(self, user_input: str) -> bool:
        user_input_clean = user_input.strip()
    
        colchetes_part = self.getPartOfMensage(msg=user_input_clean, colchetes=True)
        aspas_part = self.getPartOfMensage(msg=user_input_clean)
        command_base = user_input_clean.split()[0] if user_input_clean else ""
        
        palavras = user_input_clean.split()
        command_base = palavras[0] if palavras else ""
        command_two_words = ' '.join(palavras[:2]) if len(palavras) >= 2 else command_base
        
        # Mapeamento de comandos para ações
        command_handlers = {
            MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_LIST_THREADS.value: 
                lambda: self._handle_list_threads(),
            
            MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_SHOTDOWN.value: 
                lambda: self._handle_shutdown(user_input),
            
            MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_CLOSE_THREAD.value: 
                lambda: self._handle_close_thread(user_input, colchetes_part),
            
            MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_SEND_MENSAGE_CLIENT.value: 
                lambda: self._handle_send_message(user_input, colchetes_part, aspas_part),
            
            MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_CONFIGURE_MONITOR_THREAD.value: 
                lambda: self._handle_monitor_threads(user_input, colchetes_part),
            
            MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_HELP.value: 
                lambda: self._handle_help(user_input, colchetes_part, aspas_part),
        }
        
        # Executa o handler correspondente
        if user_input_clean in command_handlers:
            return command_handlers[user_input_clean]()
        elif command_base in command_handlers:
            return command_handlers[command_base]()
        elif command_two_words in command_handlers:
            return command_handlers[command_two_words]()
        else:
            self.errorCommand(user_input)
            return False

    def _handle_list_threads(self) -> bool:
        return self.ActionListThreads()

    def _handle_shutdown(self, user_input: str) -> bool:
        if user_input != MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_SHOTDOWN.value:
            return False
        return self.ActionShotdown()

    def _handle_close_thread(self, user_input: str, colchetes_part: str) -> bool:
        expected_prefix = MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_CLOSE_THREAD.value
        if not user_input.startswith(expected_prefix + " ["):
            return False
        
        if colchetes_part.isdigit():
            return self.ActionCloseThread(id=int(colchetes_part))
        elif colchetes_part.lower() in ["todas", "all", "todos"]:
            return self.ActionCloseThread(id=-1)
        return False

    def _handle_send_message(self, user_input: str, colchetes_part: str, aspas_part: str) -> bool:
        expected_prefix = MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_SEND_MENSAGE_CLIENT.value
        if not user_input.startswith(expected_prefix + ' "'):
            return False
        
        if not aspas_part:
            return False
        
        if colchetes_part.isdigit():
            return self.ActionSendMensageToThread(id=int(colchetes_part), msg=aspas_part)
        elif colchetes_part.lower() in ["todas", "all", "todos"]:
            return self.ActionSendMensageAllThreads(msg=aspas_part)
        return False

    def _handle_monitor_threads(self, user_input: str, colchetes_part: str) -> bool:
        expected_prefix = MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_CONFIGURE_MONITOR_THREAD.value
        if not user_input.startswith(expected_prefix + " ["):
            return False
        
        if colchetes_part.lower() in ["ativar", "enable", "on"]:
            return self.ActionShowMonitorThreads(activate=True)
        elif colchetes_part.lower() in ["desativar", "disable", "off"]:
            return self.ActionShowMonitorThreads(activate=False)
        return False

    def _handle_help(self, user_input: str, colchetes_part: str, aspas_part: str) -> bool:
        if colchetes_part or aspas_part or user_input != MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_HELP.value:
            return False
        self.ActionShowHelp()
        return True

    # ========== AÇÕES PRINCIPAIS ==========

    def ActionListThreads(self) -> bool:
        try:
            self.thread_manager.listThreads()
            return True
        except Exception as e:
            self.print(f"Erro ao listar threads: {e}")
            return False

    def ActionShotdown(self) -> bool:
        try:
            self.print(f"Iniciando desligamento do servidor...")
            self.ActionCloseThread(id=-1)
            self.wait_input = False
            return True
        except Exception as e:
            self.print(f"Erro no desligamento: {e}")
            return False

    def ActionCloseThread(self, id: int) -> bool:
        try:
            if id == -1:
                self.print(f"Fechando TODAS as threads...")
            else:
                self.print(f"Fechando thread [{id}]...")

            self.thread_manager.deleteThread(thread_id=id)
            return True
        except Exception as e:
            self.print(f"Erro ao fechar thread: {e} id {id}")
            return False

    def ActionSendMensageToThread(self, id: int, msg: str) -> bool:
        try:
            self.thread_manager.sendMensageToThread(id=id,type=MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_SEND_MENSAGE_CLIENT,msg=msg)
            return True
        except Exception as e:
            self.print(f"Erro ao enviar mensagem: {e}")
            return False

    def ActionSendMensageAllThreads(self, msg: str) -> bool:
        try:
            self.print(f"Enviando mensagem para TODAS as threads: {msg}")
            self.thread_manager.sendMensageToThread(id=-1,type=MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_SEND_MENSAGE_CLIENT,msg=msg)
            return True
        except Exception as e:
            self.print(f"Erro no broadcast: {e}")
            return False

    def ActionShowMonitorThreads(self, activate: bool) -> bool:
        try:
            status = "ativado" if activate else "desativado"
            self.print(f"Monitor de threads {status}")
            global MONITOR_OF_THREADS
            MONITOR_OF_THREADS = activate
            return True
        except Exception as e:
            self.print(f"Erro ao configurar monitor: {e}")
            return False

    def ActionShowHelp(self) -> None:
        commands = [
            (MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_LIST_THREADS.value, "Lista todas as threads ativas"),
            (MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_SHOTDOWN.value, "Desliga o servidor"),
            (f"{MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_CLOSE_THREAD.value} [id/todas]", "Fecha thread específica ou todas"),
            (f'{MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_SEND_MENSAGE_CLIENT.value} "texto" [id/todas]', "Envia mensagem para thread(s)"),
            (f"{MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_CONFIGURE_MONITOR_THREAD.value} [ativar/desativar]", "Configura monitoramento"),
            (MENSAGE_SERVER_TYPE.MENSAGE_SERVER_TYPE_HELP.value, "Exibe esta ajuda \n"),
        ]
        
        self.print("Comandos disponíveis : ")
        for cmd, desc in commands:
            print(f"  {cmd:50} - {desc}")

    def getPartOfMensage(self, msg: str, colchetes: bool = False) -> str:
        if not msg or len(msg) < 3:
            return ""
        
        try:
            if colchetes:
                match = re.search(r'\[(.*?)\]', msg)
                return match.group(1) if match else ""
            else:
                match = re.search(r'\"(.*?)\"', msg)
                return match.group(1) if match else ""
        except Exception:
            return ""

    def print(self, msg: str) -> None:
        terminal(objeto=IDENTIFIERS.SERVER.value, mensagem=msg)



if __name__ == "__main__":
    serv = Servidor()
    serv.run()
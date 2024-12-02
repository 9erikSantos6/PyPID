#!/usr/bin/python3
import os
import random
import time
import psutil  # Biblioteca para manipulação e monitoramento de processos

def processo_de_dados():
    """
    Realiza um cálculo matemático aleatório para simular o processamento de dados.
    Retorna os operandos, a operação escolhida e o resultado.
    """
    num1 = random.randint(1, 100)  # Gera um número aleatório entre 1 e 100
    num2 = random.randint(1, 100)  # Gera outro número aleatório entre 1 e 100
    operacao = random.choice(['+', '-', '*', '/'])  # Escolhe aleatoriamente uma operação matemática

    # Realiza o cálculo com base na operação escolhida
    if operacao == '+':
        result = num1 + num2
    elif operacao == '-':
        result = num1 - num2
    elif operacao == '*':
        result = num1 * num2
    elif operacao == '/':
        result = num1 / num2 if num2 != 0 else 'undefined'  # Evita divisão por zero

    return num1, operacao, num2, result  # Retorna os operandos, operação e o resultado

def processo_filho(index_processo):
    """
    Simula o comportamento de um processo filho.
    Realiza um cálculo, simula tempo de execução e imprime seu estado.
    Também imprime o tempo total de execução.
    """
    pid = os.getpid()  # Obtém o PID do processo filho
    print(f"Processo filho iniciado! Index: {index_processo}, PID: {pid}")

    # Obtém o tempo de início
    inicio_tempo = time.time()

    # Obtém o status inicial do processo utilizando a biblioteca psutil
    atual_processo = psutil.Process()
    status = atual_processo.status()
    print(f"PID {pid} está no estado: {status}")

    # Executa um cálculo aleatório simulado
    num1, operacao, num2, resultado = processo_de_dados()
    print(f"Processo {index_processo} calculou: {num1} {operacao} {num2} = {resultado}")

    # Simula um tempo de execução baseado no índice do processo
    time.sleep(3 + index_processo)

    # Obtém o tempo de fim
    fim_tempo = time.time()

    # Calcula o tempo total de execução
    tempo_execucao = fim_tempo - inicio_tempo

    print(f"Processo filho finalizado! Index: {index_processo}, PID: {os.getpid()}")
    print(f"Tempo de execução do processo {index_processo}: {tempo_execucao:.2f} segundos")


def monitorar_filhos(pids_filhos):
    """
    Monitora os processos filhos em tempo real, coleta os processos em estado 'zombie' 
    e garante que todos sejam tratados antes de encerrar o programa.
    """
    try:
        while pids_filhos:  # Continua enquanto houver processos filhos na lista
            todos_zombie = True  # Assume inicialmente que todos os processos estão em estado zombie
            for pid in pids_filhos[:]:  # Itera sobre uma cópia da lista para evitar conflitos
                try:
                    processo = psutil.Process(pid)  # Obtém o processo pelo PID
                    status = processo.status()  # Obtém o status atual do processo
                    print(f"PID {pid} está no estado: {status}")
                    if status != psutil.STATUS_ZOMBIE:  # Se o processo não for zombie, redefine a flag
                        todos_zombie = False
                except psutil.NoSuchProcess:
                    # Trata o caso em que o processo já foi finalizado
                    print(f"PID {pid} finalizou e está sendo coletado.")
                    try:
                        os.waitpid(pid, 0)  # Coleta o status do processo filho
                    except ChildProcessError:
                        pass
                    pids_filhos.remove(pid)  # Remove o PID da lista de monitoramento

            # Se todos os processos restantes são zombies, coleta todos e encerra o loop
            if todos_zombie:
                print("Todos os processos restantes estão no estado zombie. Coletando...")
                for pid in pids_filhos:  # Itera sobre os processos restantes
                    try:
                        os.waitpid(pid, 0)  # Coleta o status de cada processo
                    except ChildProcessError:
                        pass
                pids_filhos.clear()  # Limpa a lista de PIDs, encerrando o loop

            time.sleep(1)  # Espera um segundo antes de verificar novamente
    except KeyboardInterrupt:
        # Trata interrupção do programa pelo usuário (CTRL+C)
        print("Monitoramento interrompido.")
        for pid in pids_filhos:
            try:
                os.waitpid(pid, 0)  # Coleta os processos restantes
            except ChildProcessError:
                continue

def processo_pai():
    """
    Gerencia os processos filhos: cria, monitora e garante que todos sejam finalizados corretamente.
    """
    pid_pai = os.getpid()  # Obtém o PID do processo pai
    inicio_tempo = time.time()
    print(f"Processo pai iniciado! PID: {pid_pai}")

    # Solicita ao usuário a quantidade de processos filhos a serem criados
    quantidade_filhos = int(input("Digite a quantidade de processos filhos desejados: "))
    pids_filhos = []  # Lista para armazenar os PIDs dos filhos criados

    
    print("Iniciando o monitoramento dos processos...\n")
    time.sleep(1)
    for i in range(quantidade_filhos):
        pid = os.fork()  # Cria um novo processo filho
        if pid == 0:  # Código executado pelo processo filho
            processo_filho(i + 1)  # Passa o índice do processo para identificação
            os._exit(0)  # Garante que o processo filho finalize após completar sua tarefa
        else:  # Código executado pelo processo pai
            pids_filhos.append(pid)  # Armazena o PID do processo filho criado

    time.sleep(1)  # Dá tempo para os filhos inicializarem antes de monitorá-los
    monitorar_filhos(pids_filhos)  # Monitora os processos filhos
    print("Todos os processos filhos terminaram. FIM!")
    fim_tempo = time.time()
    tempo_execucao = fim_tempo - inicio_tempo
    print(f"Processo pai finalizado! Tempo de execução: {tempo_execucao:.2f} segundos")

if __name__ == "__main__":
    # Ponto de entrada principal do programa
    processo_pai()

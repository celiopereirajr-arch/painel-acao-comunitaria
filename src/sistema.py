# Painel de Ação Comunitária
# Painel de ocorrências comunitárias de 3 bairros de Lisboa (Arroios, Penha de França e Areeiro).
# As ocorrências são todas inventadas, só para simulação.
# Só Python básico: funções, condicionais, laços, listas, tuplas, dicionários.

# Duas bibliotecas padrão do Python (já vêm instaladas), sugeridas pela IA:
import os    # monta o caminho da pasta data, para o programa achar os arquivos de qualquer lugar
import sys   # lê as opções --demo e --testes digitadas na linha de comando

# ----------------------------------------------------------------------
# 1. CONSTANTES (valores padronizados e regras que não mudam)
# ----------------------------------------------------------------------

DIA_ATUAL = 30                  # "hoje" na simulação (dias contados a partir de 1)
LIMITE_PENDENCIA_ANTIGA = 15    # a partir de quantos dias uma pendência é considerada antiga

CATEGORIAS = ["iluminacao", "acessibilidade", "limpeza", "conservacao"]
ROTULO_CATEGORIA = {
    "iluminacao": "Iluminação",
    "acessibilidade": "Acessibilidade",
    "limpeza": "Limpeza",
    "conservacao": "Conservação",
}

# Significado de cada situação:
#   aberta     = registrada, ninguém examinou ainda
#   em_analise = alguém está avaliando ou resolvendo
#   concluida  = resolvida
STATUS = ["aberta", "em_analise", "concluida"]
ROTULO_STATUS = {"aberta": "Aberta", "em_analise": "Em análise", "concluida": "Concluída"}

# Mudanças de situação permitidas (o que cada situação pode virar)
TRANSICOES = {
    "aberta": ["em_analise"],
    "em_analise": ["concluida"],
    "concluida": [],
}

CAMPOS_OBRIGATORIOS = ["id", "categoria", "descricao", "bairro", "local", "abertura", "status"]

# Pasta data, calculada a partir do lugar onde o sistema.py está guardado
PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


# ----------------------------------------------------------------------
# FUNÇÕES AUXILIARES (feitas à mão com laços e if, para não depender de recursos fora do curso)
# ----------------------------------------------------------------------

def pegar(dicionario, chave, padrao):
    """Valor da chave no dicionário; se a chave não existir, devolve o padrão."""
    if chave in dicionario:
        return dicionario[chave]
    return padrao


def posicao(lista, item):
    """Posição do item na lista (0 é a primeira). Devolve -1 se não achar."""
    for i in range(len(lista)):
        if lista[i] == item:
            return i
    return -1


def copiar_lista(lista):
    """Devolve uma cópia da lista, para mexer na cópia sem alterar a original."""
    copia = []
    for item in lista:
        copia.append(item)
    return copia


def ultimo(lista):
    """Último item da lista."""
    return lista[len(lista) - 1]


def juntar(lista, separador):
    """Junta os textos da lista em um texto só, com o separador entre eles."""
    texto = ""
    for i in range(len(lista)):
        if i > 0:
            texto = texto + separador
        texto = texto + lista[i]
    return texto


def repetir(caractere, vezes):
    """Repete o caractere o número de vezes pedido."""
    texto = ""
    for i in range(vezes):
        texto = texto + caractere
    return texto


def alinhar_esquerda(valor, largura):
    """Completa com espaços à direita até a largura pedida (para alinhar colunas)."""
    texto = str(valor)
    while len(texto) < largura:
        texto = texto + " "
    return texto


def alinhar_direita(valor, largura):
    """Completa com espaços à esquerda até a largura pedida."""
    texto = str(valor)
    while len(texto) < largura:
        texto = " " + texto
    return texto


def completar_codigo(valor):
    """Escreve o código com 3 dígitos, completando com zeros à esquerda (7 vira 007)."""
    texto = str(valor)
    while len(texto) < 3:
        texto = "0" + texto
    return texto


# ----------------------------------------------------------------------
# 2. ESTRUTURAS DE DADOS (criação do "sistema")
# ----------------------------------------------------------------------

def criar_sistema():
    """Cria todas as estruturas vazias, guardadas em um único dicionário."""
    return {
        "ocorrencias": [],      # LISTA: todas as ocorrências, para percorrer
        "indice": {},           # DICIONÁRIO: código -> ocorrência (acesso direto)
        "fila": [],             # FILA: códigos ainda não examinados (entra no fim, sai do início)
        "pilha": [],            # PILHA: últimos eventos (entra no fim, sai do fim)
        "historico": [],        # LISTA DE TUPLAS: (código, dia, de, para)
        "hierarquia": {},       # DICIONÁRIO ANINHADO: bairro -> categoria -> [códigos]
        "rejeitadas": [],       # registros que a validação recusou: (registro, erros)
        "ids_vistos": [],       # todos os códigos já usados, inclusive os rejeitados
    }


# ----------------------------------------------------------------------
# 3. LEITURA DOS ARQUIVOS
# ----------------------------------------------------------------------

def ler_arquivo(caminho):
    """Lê um arquivo de texto separado por ponto e vírgula. Devolve lista de listas."""
    linhas = []
    arquivo = open(caminho, encoding="utf-8")
    for linha in arquivo:
        linha = linha.strip()
        if linha != "":
            linhas.append(linha.split(";"))
    arquivo.close()
    return linhas


def carregar_dados(sistema):
    """Lê dados.csv. Registros inválidos vão para 'rejeitadas'; os válidos são adicionados."""
    linhas = ler_arquivo(os.path.join(PASTA_DADOS, "dados.csv"))
    cabecalho = linhas[0]
    for partes in linhas[1:]:
        registro = {}
        for i in range(len(cabecalho)):
            if i < len(partes):
                registro[cabecalho[i]] = partes[i].strip()
            else:
                registro[cabecalho[i]] = ""
        sistema["ids_vistos"].append(registro["id"])
        erros = validar_ocorrencia(registro, sistema["indice"])
        if len(erros) > 0:
            sistema["rejeitadas"].append((registro, erros))
        else:
            adicionar_ocorrencia(sistema, registro)


def carregar_historico(sistema):
    """Lê historico.csv e preenche a lista de histórico e a pilha de eventos."""
    linhas = ler_arquivo(os.path.join(PASTA_DADOS, "historico.csv"))
    for partes in linhas[1:]:
        codigo, dia, de, para = partes[0], int(partes[1]), partes[2], partes[3]
        if codigo in sistema["indice"] and de in STATUS and para in STATUS:
            evento = (codigo, dia, de, para)
            sistema["historico"].append(evento)
            sistema["pilha"].append(evento)


# ----------------------------------------------------------------------
# 4. VALIDAÇÃO E REGRAS LÓGICAS
# ----------------------------------------------------------------------

def validar_ocorrencia(registro, indice):
    """Devolve a lista de problemas encontrados. Lista vazia significa registro válido."""
    erros = []

    # Regra 1: nenhum campo obrigatório pode estar vazio
    for campo in CAMPOS_OBRIGATORIOS:
        if pegar(registro, campo, "") == "":
            erros.append("campo obrigatório ausente: " + campo)

    # Regra 2 (AND, NOT): categoria preenchida mas fora da lista permitida
    categoria = pegar(registro, "categoria", "")
    if categoria != "" and categoria not in CATEGORIAS:
        erros.append("categoria desconhecida: " + categoria)

    # Regra 3 (AND, NOT): situação preenchida mas desconhecida
    status = pegar(registro, "status", "")
    if status != "" and status not in STATUS:
        erros.append("situação desconhecida: " + status)

    # Regra 4 (AND, NOT): data de abertura que não é um número
    abertura = str(pegar(registro, "abertura", ""))
    if abertura != "" and not abertura.isdigit():
        erros.append("data de abertura inválida: " + abertura)

    # Regra 5: código repetido
    codigo = pegar(registro, "id", "")
    if codigo != "" and codigo in indice:
        erros.append("código já existe: " + codigo)

    return erros


def mudanca_permitida(atual, novo):
    """True se a mudança de situação segue as regras de TRANSICOES."""
    return novo in TRANSICOES[atual]


def pendencia_antiga(ocorrencia):
    """True se a ocorrência NÃO está concluída E está aberta há muitos dias."""
    dias_abertos = DIA_ATUAL - ocorrencia["abertura"]
    return (not ocorrencia["status"] == "concluida") and dias_abertos >= LIMITE_PENDENCIA_ANTIGA


def combina_filtro(ocorrencia, categoria, status):
    """Filtro opcional: texto vazio significa 'qualquer'. Usa OR dentro e AND entre os dois."""
    ok_categoria = categoria == "" or ocorrencia["categoria"] == categoria
    ok_status = status == "" or ocorrencia["status"] == status
    return ok_categoria and ok_status


# ----------------------------------------------------------------------
# 5. OPERAÇÕES (cadastro, consulta, atualização)
# ----------------------------------------------------------------------

def adicionar_ocorrencia(sistema, registro):
    """Coloca uma ocorrência já validada em todas as estruturas."""
    oc = {
        "id": registro["id"],
        "categoria": registro["categoria"],
        "descricao": registro["descricao"],
        "bairro": registro["bairro"],
        "local": registro["local"],
        "abertura": int(registro["abertura"]),
        "status": registro["status"],
    }
    sistema["ocorrencias"].append(oc)
    sistema["indice"][oc["id"]] = oc

    # hierarquia bairro -> categoria -> códigos
    bairro, categoria = oc["bairro"], oc["categoria"]
    if bairro not in sistema["hierarquia"]:
        sistema["hierarquia"][bairro] = {}
    if categoria not in sistema["hierarquia"][bairro]:
        sistema["hierarquia"][bairro][categoria] = []
    sistema["hierarquia"][bairro][categoria].append(oc["id"])

    # só as abertas esperam na fila de triagem
    if oc["status"] == "aberta":
        sistema["fila"].append(oc["id"])


def proximo_codigo(sistema):
    """Maior código já usado (inclusive rejeitados) mais 1, com 3 dígitos."""
    maior = 0
    for codigo in sistema["ids_vistos"]:
        if codigo.isdigit() and int(codigo) > maior:
            maior = int(codigo)
    return completar_codigo(maior + 1)


def cadastrar(sistema, categoria, descricao, bairro, local):
    """Cadastra uma nova ocorrência aberta. Devolve (True, código) ou (False, erros)."""
    registro = {
        "id": proximo_codigo(sistema),
        "categoria": categoria,
        "descricao": descricao.strip(),
        "bairro": bairro,
        "local": local.strip(),
        "abertura": str(DIA_ATUAL),
        "status": "aberta",
    }
    erros = validar_ocorrencia(registro, sistema["indice"])
    if len(erros) > 0:
        return False, erros
    sistema["ids_vistos"].append(registro["id"])
    adicionar_ocorrencia(sistema, registro)
    return True, registro["id"]


def buscar_por_codigo(sistema, codigo):
    """Acesso direto pelo dicionário. Devolve a ocorrência ou None."""
    codigo = completar_codigo(codigo.strip())
    if codigo in sistema["indice"]:
        return sistema["indice"][codigo]
    return None


def filtrar(sistema, categoria, status):
    """Percorre a lista e devolve as ocorrências que combinam com o filtro."""
    resultado = []
    for oc in sistema["ocorrencias"]:
        if combina_filtro(oc, categoria, status):
            resultado.append(oc)
    return resultado


def ordenar_por_abertura(lista):
    """Ordenação por inserção, feita à mão: mais antigas primeiro. Não altera a lista original."""
    ordenada = copiar_lista(lista)
    for i in range(1, len(ordenada)):
        atual = ordenada[i]
        j = i - 1
        while j >= 0 and ordenada[j]["abertura"] > atual["abertura"]:
            ordenada[j + 1] = ordenada[j]
            j = j - 1
        ordenada[j + 1] = atual
    return ordenada


def atualizar_status(sistema, codigo, novo):
    """Muda a situação, registra no histórico e na pilha. Devolve (ok, mensagem)."""
    oc = buscar_por_codigo(sistema, codigo)
    if oc is None:
        return False, "Ocorrência " + codigo + " não encontrada."
    if novo not in STATUS:
        return False, "Situação desconhecida: " + novo
    atual = oc["status"]
    if atual == novo:
        return False, "A ocorrência já está em " + ROTULO_STATUS[atual] + "."
    if not mudanca_permitida(atual, novo):
        return False, ("Mudança não permitida: de " + ROTULO_STATUS[atual]
                       + " para " + ROTULO_STATUS[novo] + ".")

    oc["status"] = novo
    # tira o código da fila (se estiver nela) montando uma fila nova sem ele
    nova_fila = []
    for c in sistema["fila"]:
        if c != oc["id"]:
            nova_fila.append(c)
    sistema["fila"] = nova_fila
    evento = (oc["id"], DIA_ATUAL, atual, novo)
    sistema["historico"].append(evento)
    sistema["pilha"].append(evento)
    return True, ("Ocorrência " + oc["id"] + " mudou de " + ROTULO_STATUS[atual]
                  + " para " + ROTULO_STATUS[novo] + ".")


def examinar_proxima(sistema):
    """Tira o primeiro da fila (quem chegou antes) e passa para 'em análise'."""
    if not sistema["fila"]:
        return False, "A fila está vazia: não há ocorrências esperando exame."
    codigo = sistema["fila"][0]
    return atualizar_status(sistema, codigo, "em_analise")


def eventos_recentes(sistema, quantidade):
    """Lê o topo da pilha: do evento mais novo para o mais antigo."""
    copia = copiar_lista(sistema["pilha"])
    recentes = []
    while len(copia) > 0 and len(recentes) < quantidade:
        recentes.append(copia.pop())
    return recentes


# ----------------------------------------------------------------------
# 6. INDICADORES
# ----------------------------------------------------------------------

def montar_matriz(sistema):
    """Matriz (lista de listas): linhas = categorias, colunas = situações."""
    matriz = []
    for categoria in CATEGORIAS:
        matriz.append([0] * len(STATUS))
    for oc in sistema["ocorrencias"]:
        i = posicao(CATEGORIAS, oc["categoria"])
        j = posicao(STATUS, oc["status"])
        matriz[i][j] = matriz[i][j] + 1
    return matriz


def tempo_medio_conclusao(sistema):
    """Média de (dia da conclusão - dia da abertura). None se nada foi concluído."""
    soma = 0
    quantidade = 0
    for codigo, dia, de, para in sistema["historico"]:
        if para == "concluida":
            soma = soma + (dia - sistema["indice"][codigo]["abertura"])
            quantidade = quantidade + 1
    if quantidade == 0:
        return None
    return soma / quantidade


def calcular_indicadores(sistema):
    """Calcula todos os indicadores e devolve em um dicionário."""
    matriz = montar_matriz(sistema)
    total = len(sistema["ocorrencias"])

    por_categoria = {}
    for i in range(len(CATEGORIAS)):
        por_categoria[CATEGORIAS[i]] = sum(matriz[i])

    por_status = {}
    for j in range(len(STATUS)):
        soma = 0
        for i in range(len(CATEGORIAS)):
            soma = soma + matriz[i][j]
        por_status[STATUS[j]] = soma

    pendencias = por_status["aberta"] + por_status["em_analise"]
    antigas = 0
    for oc in sistema["ocorrencias"]:
        if pendencia_antiga(oc):
            antigas = antigas + 1

    return {
        "total": total,
        "matriz": matriz,
        "por_categoria": por_categoria,
        "por_status": por_status,
        "pendencias": pendencias,
        "pendencias_antigas": antigas,
        "tempo_medio": tempo_medio_conclusao(sistema),
    }


def percentual(parte, total):
    """Proporção em porcentagem. Evita dividir por zero."""
    if total == 0:
        return 0.0
    return parte / total * 100


def interpretar(ind):
    """Gera frases curtas que explicam o que os números sugerem."""
    frases = []
    if ind["total"] == 0:
        return ["Não há ocorrências para interpretar."]

    maior = 0
    for categoria in CATEGORIAS:
        if ind["por_categoria"][categoria] > maior:
            maior = ind["por_categoria"][categoria]
    lideres = []
    for categoria in CATEGORIAS:
        if ind["por_categoria"][categoria] == maior:
            lideres.append(ROTULO_CATEGORIA[categoria])
    if len(lideres) == 1:
        frases.append("Categoria com mais demandas: " + lideres[0] + " (" + str(maior) + ").")
    else:
        frases.append("Categorias empatadas com mais demandas: " + juntar(lideres, ", ")
                      + " (" + str(maior) + " cada).")

    pct_pend = percentual(ind["pendencias"], ind["total"])
    if pct_pend >= 50:
        frases.append("A maior parte das demandas ({:.1f}%) ainda está pendente.".format(pct_pend))
    else:
        frases.append("A maior parte das demandas já foi concluída ({:.1f}% pendentes).".format(pct_pend))

    if ind["pendencias_antigas"] > 0:
        frases.append(str(ind["pendencias_antigas"]) + " pendências abertas há "
                      + str(LIMITE_PENDENCIA_ANTIGA) + " dias ou mais merecem prioridade.")

    if ind["tempo_medio"] is not None:
        frases.append("Quando uma demanda é concluída, leva em média {:.2f} dias.".format(ind["tempo_medio"]))
    return frases


# ----------------------------------------------------------------------
# 7. APRESENTAÇÃO (texto no terminal)
# ----------------------------------------------------------------------

def titulo(texto):
    print()
    print(texto)
    print(repetir("-", len(texto)))


def montar_linha(c1, c2, c3, c4, c5, c6):
    """Uma linha da listagem, com as colunas alinhadas."""
    return (alinhar_esquerda(c1, 5) + alinhar_esquerda(c2, 16) + alinhar_esquerda(c3, 20)
            + alinhar_esquerda(c4, 24) + alinhar_esquerda(c5, 12) + str(c6))


def cabecalho_listagem():
    print(montar_linha("Cód", "Categoria", "Bairro", "Local", "Situação", "Aberta no dia"))


def linha_ocorrencia(oc):
    print(montar_linha(oc["id"], ROTULO_CATEGORIA[oc["categoria"]], oc["bairro"],
                       oc["local"], ROTULO_STATUS[oc["status"]], oc["abertura"]))


def exibir_lista(lista):
    if len(lista) == 0:
        print("Nenhuma ocorrência encontrada.")
        return
    cabecalho_listagem()
    for oc in lista:
        linha_ocorrencia(oc)
    print("Total: " + str(len(lista)))


def exibir_ocorrencia(oc):
    print("Código:     " + oc["id"])
    print("Categoria:  " + ROTULO_CATEGORIA[oc["categoria"]])
    print("Descrição:  " + oc["descricao"])
    print("Bairro:     " + oc["bairro"])
    print("Local:      " + oc["local"])
    print("Aberta no dia " + str(oc["abertura"]) + " (há " + str(DIA_ATUAL - oc["abertura"]) + " dias)")
    print("Situação:   " + ROTULO_STATUS[oc["status"]])


def exibir_hierarquia(sistema):
    for bairro in sistema["hierarquia"]:
        print(bairro)
        for categoria in sistema["hierarquia"][bairro]:
            codigos = sistema["hierarquia"][bairro][categoria]
            print("   " + ROTULO_CATEGORIA[categoria] + ": " + juntar(codigos, ", "))


def exibir_indicadores(sistema):
    ind = calcular_indicadores(sistema)
    total = ind["total"]

    titulo("Dados de origem: matriz categoria x situação")
    cabecalho = alinhar_esquerda("", 16)
    for status in STATUS:
        cabecalho = cabecalho + alinhar_esquerda(ROTULO_STATUS[status], 13)
    print(cabecalho + "Total")
    for i in range(len(CATEGORIAS)):
        linha = alinhar_esquerda(ROTULO_CATEGORIA[CATEGORIAS[i]], 16)
        for j in range(len(STATUS)):
            linha = linha + alinhar_esquerda(ind["matriz"][i][j], 13)
        linha = linha + str(sum(ind["matriz"][i]))
        print(linha)

    titulo("Regra: proporção = quantidade / total x 100")
    print("Por categoria (total = " + str(total) + ")")
    for categoria in CATEGORIAS:
        qtd = ind["por_categoria"][categoria]
        print("   " + alinhar_esquerda(ROTULO_CATEGORIA[categoria], 16) + alinhar_esquerda(qtd, 4)
          + alinhar_direita("{:.1f}".format(percentual(qtd, total)), 6) + "%")
    print("Por situação")
    for status in STATUS:
        qtd = ind["por_status"][status]
        print("   " + alinhar_esquerda(ROTULO_STATUS[status], 16) + alinhar_esquerda(qtd, 4)
          + alinhar_direita("{:.1f}".format(percentual(qtd, total)), 6) + "%")

    titulo("Indicadores adicionais")
    print("Pendências (abertas + em análise): " + str(ind["pendencias"]))
    print("Pendências antigas (" + str(LIMITE_PENDENCIA_ANTIGA) + " dias ou mais): " + str(ind["pendencias_antigas"]))
    if ind["tempo_medio"] is None:
        print("Tempo médio até a conclusão: sem ocorrências concluídas")
    else:
        print("Tempo médio até a conclusão: {:.2f} dias simulados".format(ind["tempo_medio"]))

    titulo("O que os números sugerem")
    for frase in interpretar(ind):
        print("- " + frase)


def exibir_eventos(sistema, quantidade):
    recentes = eventos_recentes(sistema, quantidade)
    if len(recentes) == 0:
        print("Nenhum evento registrado.")
        return
    for codigo, dia, de, para in recentes:
        print("Dia " + alinhar_esquerda(dia, 3) + " ocorrência " + codigo + ": "
              + ROTULO_STATUS[de] + " -> " + ROTULO_STATUS[para])


def exibir_rejeitadas(sistema):
    if len(sistema["rejeitadas"]) == 0:
        print("Nenhum registro foi rejeitado.")
        return
    for registro, erros in sistema["rejeitadas"]:
        print("Registro " + pegar(registro, "id", "?") + " rejeitado:")
        for erro in erros:
            print("   - " + erro)


# ----------------------------------------------------------------------
# 8. ENTRADA DO USUÁRIO (menu)
# ----------------------------------------------------------------------

def escolher_numero(pergunta, minimo, maximo):
    """Pede um número entre minimo e maximo. Repete até acertar. Devolve None se o usuário só apertar Enter."""
    while True:
        texto = input(pergunta).strip()
        if texto == "":
            return None
        if texto.isdigit() and int(texto) >= minimo and int(texto) <= maximo:
            return int(texto)
        print("Entrada inválida. Digite um número de " + str(minimo) + " a " + str(maximo) + ".")


def escolher_categoria(pergunta):
    for i in range(len(CATEGORIAS)):
        print("  " + str(i + 1) + " - " + ROTULO_CATEGORIA[CATEGORIAS[i]])
    n = escolher_numero(pergunta, 1, len(CATEGORIAS))
    if n is None:
        return ""
    return CATEGORIAS[n - 1]


def escolher_status(pergunta):
    for i in range(len(STATUS)):
        print("  " + str(i + 1) + " - " + ROTULO_STATUS[STATUS[i]])
    n = escolher_numero(pergunta, 1, len(STATUS))
    if n is None:
        return ""
    return STATUS[n - 1]


def escolher_bairro(sistema):
    bairros = []
    for bairro in sistema["hierarquia"]:
        bairros.append(bairro)
    for i in range(len(bairros)):
        print("  " + str(i + 1) + " - " + bairros[i])
    n = escolher_numero("Bairro (número): ", 1, len(bairros))
    if n is None:
        return ""
    return bairros[n - 1]


def opcao_cadastrar(sistema):
    titulo("Cadastrar nova ocorrência (não escreva dados pessoais)")
    print("Categoria:")
    categoria = escolher_categoria("Categoria (número): ")
    descricao = input("Descrição breve: ")
    print("Bairro:")
    bairro = escolher_bairro(sistema)
    local = input("Local genérico (ex.: Praça Central): ")
    ok, resultado = cadastrar(sistema, categoria, descricao, bairro, local)
    if ok:
        print("Ocorrência cadastrada com o código " + resultado + " (situação: Aberta).")
    else:
        print("Não foi possível cadastrar:")
        for erro in resultado:
            print("   - " + erro)


def opcao_atualizar(sistema):
    titulo("Atualizar situação")
    codigo = input("Código da ocorrência: ")
    oc = buscar_por_codigo(sistema, codigo)
    if oc is None:
        print("Ocorrência " + codigo.strip() + " não encontrada.")
        return
    print("Situação atual: " + ROTULO_STATUS[oc["status"]])
    print("Nova situação:")
    novo = escolher_status("Nova situação (número): ")
    ok, mensagem = atualizar_status(sistema, oc["id"], novo)
    print(mensagem)


def mostrar_menu():
    titulo("PAINEL DE AÇÃO COMUNITÁRIA (dia simulado " + str(DIA_ATUAL) + ")")
    print(" 1 - Listar ocorrências (mais antigas primeiro)")
    print(" 2 - Buscar por código")
    print(" 3 - Filtrar por categoria e/ou situação")
    print(" 4 - Cadastrar nova ocorrência")
    print(" 5 - Examinar a próxima da fila")
    print(" 6 - Atualizar situação de uma ocorrência")
    print(" 7 - Ver últimas atualizações")
    print(" 8 - Ver bairros e categorias")
    print(" 9 - Ver indicadores")
    print("10 - Ver registros rejeitados na validação")
    print("11 - Demonstração automática")
    print("12 - Rodar os testes automáticos")
    print(" 0 - Sair")


def menu(sistema):
    while True:
        mostrar_menu()
        escolha = input("Escolha uma opção: ").strip()
        if escolha == "1":
            titulo("Ocorrências")
            exibir_lista(ordenar_por_abertura(sistema["ocorrencias"]))
        elif escolha == "2":
            codigo = input("Código (ex.: 014): ")
            oc = buscar_por_codigo(sistema, codigo)
            if oc is None:
                print("Ocorrência " + codigo.strip() + " não encontrada.")
            else:
                exibir_ocorrencia(oc)
        elif escolha == "3":
            titulo("Filtro (Enter deixa o campo livre)")
            print("Categoria:")
            categoria = escolher_categoria("Categoria (número ou Enter): ")
            print("Situação:")
            status = escolher_status("Situação (número ou Enter): ")
            exibir_lista(filtrar(sistema, categoria, status))
        elif escolha == "4":
            opcao_cadastrar(sistema)
        elif escolha == "5":
            ok, mensagem = examinar_proxima(sistema)
            print(mensagem)
            print("Ainda na fila: " + str(len(sistema["fila"])))
        elif escolha == "6":
            opcao_atualizar(sistema)
        elif escolha == "7":
            titulo("Últimas atualizações (a mais recente primeiro)")
            exibir_eventos(sistema, 5)
        elif escolha == "8":
            titulo("Bairros e categorias")
            exibir_hierarquia(sistema)
        elif escolha == "9":
            exibir_indicadores(sistema)
        elif escolha == "10":
            titulo("Registros rejeitados")
            exibir_rejeitadas(sistema)
        elif escolha == "11":
            # a demonstração usa um sistema novo, para não misturar com o que você mexeu
            novo = criar_sistema()
            carregar_dados(novo)
            carregar_historico(novo)
            demonstracao(novo)
        elif escolha == "12":
            rodar_testes()
        elif escolha == "0":
            print("Até logo.")
            break
        else:
            print("Opção inválida. Digite um número do menu.")


# ----------------------------------------------------------------------
# 9. DEMONSTRAÇÃO AUTOMÁTICA (opção 11 do menu ou python src/sistema.py --demo)
# ----------------------------------------------------------------------

def demonstracao(sistema):
    titulo("PASSO 1: dados carregados")
    print("Ocorrências válidas: " + str(len(sistema["ocorrencias"])))
    print("Eventos de histórico: " + str(len(sistema["historico"])))
    print("Registros rejeitados: " + str(len(sistema["rejeitadas"])))
    exibir_rejeitadas(sistema)

    titulo("PASSO 2: listagem ordenada por data de abertura")
    exibir_lista(ordenar_por_abertura(sistema["ocorrencias"]))

    titulo("PASSO 3: consulta, todas as ocorrências ABERTAS de ILUMINAÇÃO")
    exibir_lista(filtrar(sistema, "iluminacao", "aberta"))

    titulo("PASSO 4: cadastro válido")
    ok, resultado = cadastrar(sistema, "iluminacao", "Poste apagado na rua da escola",
                              "Arroios", "Praça Central")
    if ok:
        print("Cadastrado com o código " + resultado)
    else:
        print(resultado)
    novo_codigo = resultado

    titulo("PASSO 5: cadastro inválido (descrição vazia, categoria ausente)")
    ok, resultado = cadastrar(sistema, "", "", "Arroios", "Praça Central")
    if ok:
        print("Aceito")
    else:
        print("Recusado pela validação:")
    if not ok:
        for erro in resultado:
            print("   - " + erro)

    titulo("PASSO 6: alterar a ocorrência " + novo_codigo + " para Em análise")
    ok, mensagem = atualizar_status(sistema, novo_codigo, "em_analise")
    print(mensagem)

    titulo("PASSO 7: tentar uma mudança proibida (Concluída para Aberta)")
    ok, mensagem = atualizar_status(sistema, "001", "aberta")
    print(mensagem)

    titulo("PASSO 8: buscar um código que não existe")
    oc = buscar_por_codigo(sistema, "999")
    if oc is None:
        print("Ocorrência 999 não encontrada.")
    else:
        print("Encontrada")

    titulo("PASSO 9: últimas atualizações (pilha)")
    exibir_eventos(sistema, 3)

    titulo("PASSO 10: indicadores atualizados")
    exibir_indicadores(sistema)


# ----------------------------------------------------------------------
# 10. TESTES (opção 12 do menu ou python src/sistema.py --testes)
# ----------------------------------------------------------------------

def verificar(descricao, condicao):
    if condicao:
        print("OK      " + descricao)
    else:
        print("FALHOU  " + descricao)
    return condicao


def codigos_de(lista):
    """Só os códigos de uma lista de ocorrências."""
    codigos = []
    for oc in lista:
        codigos.append(oc["id"])
    return codigos


def soma_da_matriz(matriz):
    """Soma todos os números da matriz."""
    soma = 0
    for linha in matriz:
        for valor in linha:
            soma = soma + valor
    return soma


def soma_dos_percentuais(ind):
    """Soma as proporções por categoria (deve dar 100)."""
    soma = 0
    for categoria in CATEGORIAS:
        soma = soma + percentual(ind["por_categoria"][categoria], ind["total"])
    return soma


def rodar_testes():
    resultados = []
    s = criar_sistema()
    carregar_dados(s)
    carregar_historico(s)

    resultados.append(verificar("carrega 14 ocorrências válidas", len(s["ocorrencias"]) == 14))
    resultados.append(verificar("rejeita 2 registros (campo ausente e situação desconhecida)", len(s["rejeitadas"]) == 2))
    resultados.append(verificar("carrega 12 eventos de histórico", len(s["historico"]) == 12))
    resultados.append(verificar("fila começa com 6 abertas, a mais antiga primeiro",
                                len(s["fila"]) == 6 and s["fila"][0] == "003"))
    resultados.append(verificar("topo da pilha é o último evento (ocorrência 014)", ultimo(s["pilha"])[0] == "014"))

    resultados.append(verificar("busca por código existente", buscar_por_codigo(s, "14") is not None))
    resultados.append(verificar("busca por código inexistente devolve None", buscar_por_codigo(s, "999") is None))
    resultados.append(verificar("filtro iluminação + aberta devolve 1 (009)",
                                codigos_de(filtrar(s, "iluminacao", "aberta")) == ["009"]))
    resultados.append(verificar("filtro só por situação concluída devolve 4", len(filtrar(s, "", "concluida")) == 4))
    resultados.append(verificar("filtro sem critérios devolve todas", len(filtrar(s, "", "")) == 14))

    # lista de trás para frente, para provar que a ordenação realmente reorganiza
    invertida = []
    i = len(s["ocorrencias"]) - 1
    while i >= 0:
        invertida.append(s["ocorrencias"][i])
        i = i - 1
    ordenada = ordenar_por_abertura(invertida)
    em_ordem = True
    for i in range(1, len(ordenada)):
        if ordenada[i - 1]["abertura"] > ordenada[i]["abertura"]:
            em_ordem = False
    resultados.append(verificar("ordenação por abertura fica em ordem crescente", em_ordem))

    resultados.append(verificar("validação recusa categoria ausente",
                                len(validar_ocorrencia({"id": "050", "categoria": "", "descricao": "x", "bairro": "b",
                                                        "local": "l", "abertura": "3", "status": "aberta"}, {})) > 0))
    resultados.append(verificar("validação recusa categoria desconhecida",
                                len(validar_ocorrencia({"id": "050", "categoria": "barulho", "descricao": "x", "bairro": "b",
                                                        "local": "l", "abertura": "3", "status": "aberta"}, {})) > 0))
    resultados.append(verificar("validação aceita registro correto",
                                validar_ocorrencia({"id": "050", "categoria": "limpeza", "descricao": "x", "bairro": "b",
                                                    "local": "l", "abertura": "3", "status": "aberta"}, {}) == []))

    ok, _ = atualizar_status(s, "001", "aberta")
    resultados.append(verificar("recusa mudança Concluída para Aberta", not ok))
    ok, _ = atualizar_status(s, "003", "concluida")
    resultados.append(verificar("recusa pular etapa (Aberta direto para Concluída)", not ok))
    ok, _ = atualizar_status(s, "999", "em_analise")
    resultados.append(verificar("recusa atualizar código inexistente", not ok))
    ok, _ = atualizar_status(s, "003", "voando")
    resultados.append(verificar("recusa situação desconhecida", not ok))

    ok, codigo = cadastrar(s, "limpeza", "Teste de cadastro", "Penha de França", "Rua Teste")
    resultados.append(verificar("cadastro válido recebe o código 017", ok and codigo == "017"))
    resultados.append(verificar("nova ocorrência entra no fim da fila", ultimo(s["fila"]) == "017"))
    ok, _ = cadastrar(s, "limpeza", "", "Penha de França", "Rua Teste")
    resultados.append(verificar("cadastro sem descrição é recusado", not ok))

    ok, _ = examinar_proxima(s)
    resultados.append(verificar("examinar próxima tira o primeiro da fila (003)",
                                ok and s["indice"]["003"]["status"] == "em_analise" and s["fila"][0] == "006"))
    ok, _ = atualizar_status(s, "003", "concluida")
    resultados.append(verificar("atualização válida é aceita e vai para a pilha",
                                ok and ultimo(s["pilha"])[0] == "003" and ultimo(s["pilha"])[3] == "concluida"))

    s2 = criar_sistema()
    carregar_dados(s2)
    carregar_historico(s2)
    ind = calcular_indicadores(s2)
    resultados.append(verificar("matriz soma o total de ocorrências",
                                soma_da_matriz(ind["matriz"]) == ind["total"]))
    resultados.append(verificar("proporções por categoria somam 100%",
                                soma_dos_percentuais(ind) > 99.999 and soma_dos_percentuais(ind) < 100.001))
    resultados.append(verificar("tempo médio até a conclusão é 4,25 dias", ind["tempo_medio"] > 4.249 and ind["tempo_medio"] < 4.251))
    resultados.append(verificar("10 pendências e 7 delas antigas", ind["pendencias"] == 10 and ind["pendencias_antigas"] == 7))
    resultados.append(verificar("percentual com total zero não quebra", percentual(1, 0) == 0.0))

    passou = 0
    for r in resultados:
        if r:
            passou = passou + 1
    print()
    print("Resultado: " + str(passou) + " de " + str(len(resultados)) + " testes passaram.")
    return passou == len(resultados)


# ----------------------------------------------------------------------
# 11. PROGRAMA PRINCIPAL
# ----------------------------------------------------------------------

def main():
    if "--testes" in sys.argv:
        ok = rodar_testes()
        if ok:
            sys.exit(0)
        else:
            sys.exit(1)

    sistema = criar_sistema()
    carregar_dados(sistema)
    carregar_historico(sistema)

    if "--demo" in sys.argv:
        demonstracao(sistema)
        return

    print("Dados carregados: " + str(len(sistema["ocorrencias"])) + " ocorrências, "
          + str(len(sistema["rejeitadas"])) + " rejeitadas na validação.")
    menu(sistema)


main()

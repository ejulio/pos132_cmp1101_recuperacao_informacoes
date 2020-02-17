from argparse import ArgumentParser
import json
import re

import numpy as np


def parse_args():
    ap = ArgumentParser()

    ap.add_argument(
        '--documentos',
        type=str,
        required=True,
        help='Caminho para o arquivo .jl com os documentos para efetuar a busca'
    )

    ap.add_argument(
        '--n-resultados',
        type=int,
        required=False,
        default=10,
        help='Quantidade máxima de resultados (10 padrão) para retornar na busca.'
    )

    return ap.parse_args()


def main(args):
    print('Bem-vindo ao sistema de busca de livros.')
    print('> Para pesquisar, digite palavras separadas por um "AND"')
    print('> Pressione ENTER sem nenhuma palavras para sair')
    print('> Montando o índice para acelerar as consultas')
    documentos = list(ler_documentos(args.documentos))
    indice_invertido = construir_indice_invertido(documentos)
    indice_k_grams = construir_indice_k_grams(indice_invertido, k=3)
    (M, ids_termos) = construir_matriz_tf_idf(indice_invertido, documentos)
    while True:
        print('=' * 80)
        print('=' * 80)
        consulta = input('Qual é a sua consulta? ')
        consulta = consulta.strip()
        if not consulta:
            print('Saindo...')
            break

        termos = normalizar_tokens(consulta.split())
        termos_ = aplicar_correcao_ortografica(termos, indice_invertido, indice_k_grams)
        if termos_ != termos:
            termos = termos_
            print(f'Você quis dizer "{" ".join(termos)}"?')
        else:
            print(f'Resultados para {consulta}')

        print()
        resultados = consultar(termos, M, ids_termos, documentos)
        for (documento, i) in zip(resultados, range(args.n_resultados)):
            print(f'{i + 1}. {documento["titulo"]}')
            print(documento["url"])
            print('>', documento['descricao'][:100], '...')
            print()


def ler_documentos(caminho_documentos):
    with open(caminho_documentos, 'r') as f:
        for line in f:
            documento = json.loads(line)
            if documento['descricao']:
                yield documento


def construir_indice_invertido(documentos):
    '''
    Essa função constrói e retorna um índice invertido.
    Entrada: Lista de documentos (strings)
    Saída: Dicionário de termos para lista de documentos
    '''
    # Exercício 1
    indice_invertido = {}
    documentos_tokens = [obter_tokens(d['descricao']) for d in documentos]
    for (i, tokens) in enumerate(documentos_tokens):
        for token in tokens:
            if token not in indice_invertido:
                indice_invertido[token] = [i]
            else:
                # note a diferença do índice invertido do exercício anterior
                indice_invertido[token].append(i)

    return indice_invertido


def construir_indice_k_grams(indice_invertido, k=3):
    '''
    Constrói um índice que mapeia de k-grams para termos
    '''
    indice_k_grams = {}
    for termo in indice_invertido.keys():
        for k_gram in obter_k_grams(termo, k=k):
            if k_gram not in indice_k_grams:
                indice_k_grams[k_gram] = {termo}
            else:
                indice_k_grams[k_gram].add(termo)

    return indice_k_grams


def construir_matriz_tf_idf(indice_invertido, documentos):
    ids_termos = {}
    M = np.zeros((len(indice_invertido), len(documentos)))
    for (i, termo) in enumerate(indice_invertido):
        ids_termos[termo] = i
        for j in indice_invertido[termo]:
            M[i, j] += 1

    df = np.sum(M > 0, axis=1)
    N = M.shape[1]
    idf = np.log(N / df)
    # idf = idf.reshape(-1, 1)
    # M = idf * M
    for i in range(M.shape[0]):
        M[i, :] = M[i, :] * idf[i]

    return (M, ids_termos)


def obter_k_grams(termo, k=3):
    '''Retorna as substrings de tamanho k de termo.
    São adicionados k - 1 sinais especiais ($) no início e fim do termo.
    '''
    pad = k - 1
    termo_pad = ('$' * pad) + termo + ('$' * pad)
    return {termo_pad[i:i + k] for i in range(len(termo_pad) - pad)}


def obter_tokens(documento):
    '''Quebra um texto em sequências de palavras normalizadas em lower case'''
    tokens = re.findall(r'(?:\b(\w+)\b)', documento)
    return normalizar_tokens(tokens)


def normalizar_tokens(tokens):
    '''Coloca os tokens em lower case e remove espaços no começo/final'''
    return [t.strip().lower() for t in tokens]


def aplicar_correcao_ortografica(termos, indice_invertido, indice_k_grams):
    '''Retorna termos com correção ortográfica.
    Se o termo existe no índice inverto, mantém.
    Se não existe, encontra a melhor correção ortográfica.
    '''
    termos_corrigidos = []
    for termo in termos:
        if termo in indice_invertido:
            termos_corrigidos.append(termo)
        else:
            correcao = obter_termo_corrigido(termo, indice_k_grams)
            termos_corrigidos.append(correcao)

    return termos_corrigidos


def obter_termo_corrigido(termo, indice_k_grams):
    '''
    Encontra a melhor correção ortográfica de um determinado termo utilizando
    o índice k-grams.
    '''
    termos_candidados = set()
    k = len(next(iter(indice_k_grams.keys())))
    k_grams = obter_k_grams(termo, k=k)
    for k_gram in k_grams:
        termos_candidados = termos_candidados | indice_k_grams.get(k_gram, {})

    return max(jaccard(k_grams, termos_candidados, k), key=lambda x: x[0])[1]


def jaccard(k_grams, termos_candidados, k):
    for candidato in termos_candidados:
        candidato_k_grams = obter_k_grams(candidato, k)
        j = len(candidato_k_grams & k_grams) / len(candidato_k_grams | k_grams)
        yield (j, candidato)


def consultar(termos_consulta, M, ids_termos, documentos):
    '''
    Retorna todos os documentos que contém todos os termos de consulta.
    Como seria essa rotina se usássemos set() do python como estrutura de dados ao invés de list()?
    Como seriam as operações OR e NOT?
    '''
    # similaridade de cosenos
    q = np.zeros((M.shape[0], 1))
    tids = [ids_termos[t] for t in termos_consulta]
    q[tids] = 1
    # q = [0, 0, 0, 1, 1, 1, 0, 0]
    q_norm = np.sqrt(np.square(q).sum())
    similaridades = []
    for j in range(M.shape[1]):
        p = np.dot(q.T, M[:, j])[0]
        m_norm = np.sqrt(np.square(M[:, j]).sum())
        cs = p / (q_norm * m_norm)
        similaridades.append(cs)

    for doc_id in np.argsort(similaridades)[::-1]:
        yield documentos[doc_id]

if __name__ == '__main__':
    main(parse_args())

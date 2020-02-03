import json
import numpy as np
import re


def to_tokens(texto):
    tokens = re.findall(r'(\b\w+\b)+', texto)
    return [t.lower() for t in tokens]

documentos = []

with open('./books.jl', 'r') as f:
    for line in f:
        doc = json.loads(line)
        if doc['descricao'] is not None:
            documentos.append(doc)

index = {}
for (i, doc) in enumerate(documentos):
    for token in to_tokens(doc['descricao']):
        if token not in index:
            index[token] = [i]
        elif index[token][-1] != i:
            index[token].append(i)

termo_1 = index['life']
termo_2 = index['time']

resultado = set(termo_1) & set(termo_2)

for i in resultado:
    print(documentos[i]['titulo'])
    print(documentos[i]['url'])
    print()

import re


def parse(texto):
    regex = r'^(\d+)\.\s*([\w\s,.:;\-]+?)(?:\s+by\s+([\w\s]+))?\s\((\d+)\)$'
    match = re.search(regex, texto)
    return (match[1], match[2], match[3], match[4])


test_cases = [
    (
        '2. Pride and Prejudice by Jane Austen (1302)',
        ('2', 'Pride and Prejudice', 'Jane Austen', '1302')
    ),
    (
        '20. Pride and Prejudice by Jane Austen (1302)',
        ('20', 'Pride and Prejudice', 'Jane Austen', '1302')
    ),
    (
        '5. Beowulf: An Anglo-Saxon Epic Poem (658)',
        ('5', 'Beowulf: An Anglo-Saxon Epic Poem', None, '658')
    )
]

for (texto, resultado) in test_cases:
    assert parse(texto) == resultado, f'Erro {texto}'

print('Sucesso!')

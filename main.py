from pathlib import Path
from collections import defaultdict
import enum

TOKEN_TYPE = enum.Enum("TOKEN_TYPE", "text beta parse lemma all")

TOKEN_MAP = {
    TOKEN_TYPE.text: lambda x: x[1], 
    TOKEN_TYPE.beta: lambda x: x[2], 
    TOKEN_TYPE.parse: lambda x: x[3], 
    TOKEN_TYPE.lemma: lambda x: x[4:], 
    TOKEN_TYPE.all: lambda x: x, 
}

CHUNK_TYPE = enum.Enum("CHUNK_TYPE", "book chapter verse")

CHUNK_MAP = {
    CHUNK_TYPE.book: 0,
    CHUNK_TYPE.chapter: 1,
    CHUNK_TYPE.verse: 2,
}

MYPATH = Path(__file__).parent


def load_tokens(token_type):
    output = []
    mapper = TOKEN_MAP[token_type]
    with open(MYPATH / Path('output.txt'), 'r', encoding="UTF-8") as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split(' ')
            output.append(mapper(parts))
    return output
          

def load_tokens_by_chunk(token_type, chunk_type):
    output = defaultdict(list)
    mapper = TOKEN_MAP[token_type]
    chunk_target = CHUNK_MAP[chunk_type] + 1
    with open(MYPATH / Path('output.txt'), 'r', encoding="UTF-8") as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split(' ')
            ref = ':'.join(parts[0].split(":")[0:chunk_target])
            output[ref].append(mapper(parts))
    return output

if __name__ == '__main__':
    tokens = load_tokens_by_chunk(TOKEN_TYPE.text, CHUNK_TYPE.verse)
    print(tokens["PHP:1:1"])
    print(len(load_tokens(TOKEN_TYPE.text)))


    

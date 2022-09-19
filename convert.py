from collections import defaultdict
from beta_to_unicode_custom import standardise_beta_code, convert_beta_to_unicode
import glob
import re
from lxml import etree

convert = lambda x: convert_beta_to_unicode(standardise_beta_code(x))

def take_while(xs, f):
    output = []
    buffer = []
    for x in xs:
        if f(x):
            buffer.append(x)
            output.append(buffer)
            buffer = []
        else:
            buffer.append(x)
    return output

def drop_notes(xs):
    output = []
    dropping = False
    for x in xs:
        if x in ['{N', '{B']:
            dropping = True
        if not dropping:
            output.append(x)
        if x == '}' and dropping:
            dropping = False
        
    return output

VERSE_MKR = '     '
DIR = "byzantine-majority-text/parsed/"
DIR2 = 'byzantine-majority-text/textonly-beta-code/'
OUTPUT = defaultdict(list)
ACCENTED = defaultdict(dict)
DROPS = ['{P}']

def load_strongs():
    fpath = 'strongsgreek.xml'
    root = etree.parse(fpath)
    output = {}
    for entry in root.findall('//entry'):
        greek = entry.findall('./greek')
        snum = entry.find('./strongs').text
        print(snum)
        if greek:
            output[snum] = ', '.join([x.attrib['unicode'] for x in greek])
    return output


STRONGS = load_strongs()




def enum_verse(xs, tgt):
    for key, v in xs.items():
        if tgt in key:
            yield v


with open("output.txt", 'w', encoding="UTF-8") as o:
    for fpath in glob.glob(DIR + "*.UB5"):
        fname = fpath.split("/")[-1].replace('.UB5', '')
        print(fname)
        # if not "JAS" == fname:
        #     continue
        with open(fpath, 'r', encoding="UTF-8") as f:
            for line in f.read().replace('\n', ' ').split(VERSE_MKR):
                if not line.strip():
                    continue
                while '|' in line:
                    parts = line.split('|', maxsplit=3)
                    line = parts[0]  + parts[1]  + parts[-1]
                # xs= re.sub(r'VAR:.*?:END', '', line.strip()).split(' ')
                xs = line.strip().split(' ')
                ref = xs[0]
                assert ':' in ref
                words = []
                for x in take_while([x for x in xs[1:] if x and x != '|'], lambda z: '}' in z):
                    try:
                        if x[0][0] in '0123456789':
                            print("FAIL")
                    except:
                        print(f"{ref} '{x[0]}'")
                        print(x)
                        exit()
                    if x[0][0] not in '0123456789<' and not x[0].endswith('>'):
                        words.append(x)

                for i, part in enumerate(words):
                    OUTPUT[fname].append([f"{fname}:{ref}:{i+1}"] + part)
        with open(DIR2 + fname + '.CCT', 'r', encoding='UTF-8') as f:
            for line in f:
                if not line.startswith(VERSE_MKR):
                    continue
                parts = line.strip().split(' ')
                cpt, vrs = parts[0].split(':', maxsplit=1)

                if cpt.startswith('0'):
                    cpt = cpt[1:]
                if vrs.startswith('0'):
                    vrs = vrs[1:]
                ref = f"{cpt}:{vrs}"
                words = drop_notes(parts[1:])
                # if ref == '1:5':
                #     print(parts[1:])
                #     print(words)
                    
                for i, word in enumerate([convert(x) for x in words if not x in DROPS]):
                    ACCENTED[fname][f"{fname}:{ref}:{i+1}"] =  word
    assert list(OUTPUT.keys()) == list(ACCENTED.keys())
    print()
    for key, parsed in OUTPUT.items():
        words = ACCENTED[key]
        for part in parsed:
            ref = part[0]
            
            word = part[1]
            parse = part[-1].replace('{', '').replace('}', '')
            strongs = part[2:-1]
            if not ref in words:
                print(ref + " not in words")
                print(word)
                print(parse)
                print(strongs)
                verse_ref = ':'.join(ref.split(':')[:-1])
                vs = list(enum_verse(words, verse_ref))
                v_data = [ x for x in parsed if verse_ref in x[0]]
                print(len(vs), len(v_data))
                print( ' '.join(vs))
                for x in v_data:
                    print(x)
                exit()
            o.write(f"{ref} {words[ref]} {word} {parse} {' '.join([STRONGS.get(x, x) for x in strongs])}" + '\n')


            
            

               
               
               
                # for i, part in enumerate(parts):
                #     if len(part) < 1:
                #         continue
                #     word = part[0]
                #     parse = part[-1].replace('{', '').replace('}', '')
                #     strongs = part[1:-1]                    
                #     o.write(f"{fname}:{ref}:{i+1} {convert(word)} {parse} {' '.join(strongs)}" + '\n')
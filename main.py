from bs4 import BeautifulSoup
import urllib.request
import csv
import copy
import re

with open('labels.txt', 'r') as fin:
    supersenses = [line.strip() for line in fin.readlines()]

parens = re.compile(r'[\(\[].*?[\)\]]')

fin = open('output.csv', 'w')
writer = csv.writer(fin)
writer.writerow(['Sentence', 'Label', 'Notes'])

def append_sentence(sentence, role, fxn):
    number = [tag.extract().get_text() for tag in sentence.find_all(class_='exref')]
    bold = sentence.find(class_='usage')
    if bold:
        construal = bold.get('href')
        bold.string.replace_with(f'<{bold.text}><{construal.replace("/", "|")}>')
        bold.unwrap()
    for sub in sentence.find_all('sub'):
        try:
            sub.string.replace_with(f'{{{sub.text}}}')
        except:
            pass
    print(sentence)
    sentence = sentence.text.replace('/', '')
    notes = []
    for match in parens.findall(sentence):
        notes.append(match)
    sentence = parens.sub('', sentence).replace('|', '/')
    print(sentence)
    writer.writerow([sentence, '|'.join(number), '|'.join(notes)])


for role in supersenses:
    for fxn in supersenses:
        url = f'http://flat.nert.georgetown.edu/{role}--{fxn}/'
        with urllib.request.urlopen(url) as resp:
            soup = BeautifulSoup(resp, 'html.parser')
            for example in soup.find_all(class_='example'):
                # handle multiple options indicated by <u></u>
                # each option is a distinct sentence
                # this is O(#options^2) but fast enough for our purposes
                options = example.find_all('u')
                if options:
                    for i, option in enumerate(options):
                        sentence = copy.copy(example)
                        for j, remove in enumerate(sentence.find_all('u')):
                            if j != i: remove.decompose()
                        append_sentence(sentence, role, fxn)
                else:
                    append_sentence(example, role, fxn)
                    
fin.close()
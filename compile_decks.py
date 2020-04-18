import os
import re
import json
import sys

'''
JSON format:
[
    {
      "id": n,
      "cardType": "Q"/"A",
      "text": "",
      "numAnswers": 0/n, 
      "expansion": ""
   }
]
'''


def print_usage():
    print('Usage %s <opts> <filename>' % sys.argv[0])
    print('\t--full')
    print('\t--original')
    print('\t--non-original')
    print('\t--only deck')
    sys.exit()


filename = 'cards.json'
only_original = False
only_non_original = False
deck = False
full = False
if len(sys.argv) > 1:
    if sys.argv[1] == '--full':
        full = True
        filename = 'full.json'
    elif sys.argv[1] == '--original':
        only_original = True
        if len(sys.argv) > 2:
            filename = sys.argv[2]
    elif sys.argv[1] == '--non-original':
        only_non_original = True
        if len(sys.argv) > 2:
            filename = sys.argv[2]
    elif sys.argv[1] == '--only':
        if len(sys.argv) > 2:
            deck = sys.argv[2]
            if len(sys.argv) > 3:
                filename = sys.argv[3]
        else:
            print_usage()
    else:
        filename = sys.argv[1]


def treat_cards(card):
    # Trim
    # Fix ending punctuation
    # Convert to regular line breaks
    return re.sub(r'([^\.\?!])$', '\g<1>.', card.strip()).replace('\\n', '\n')


cardsJSON = []
ids = 1
blacks = 0
whites = 0
for deckDir in os.listdir('src/'):

    with open('src/%s/metadata.json' % deckDir) as j:
        deckCards = []
        metadata = json.load(j)
        if only_original and not metadata['official']:
            continue
        if only_non_original and metadata['official']:
            continue
        if deck and not deck == deckDir:
            continue
        with open('src/' + deckDir + '/black.md.txt') as f:
            for x in f.readlines():
                deckCards.extend(
                    [{'id': ids, 'cardType': 'Q', 'text': treat_cards(x), 'numAnswers': max(1, x.count('_')),
                      'expansion': metadata['name']}])
                ids = ids + 1
                blacks = blacks + 1
        with open('src/' + deckDir + '/white.md.txt') as f:
            for x in f.readlines():
                deckCards.extend(
                    [{'id': ids, 'cardType': 'A', 'text': treat_cards(x), 'numAnswers': 0,
                      'expansion': metadata['name']}])
                ids = ids + 1
                whites = whites + 1
        if full:
            deckDump = json.dumps(deckCards).encode('utf8')
            with open('decks/%s.json' % deckDir, 'w') as outfile:
                outfile.write(deckDump)
                outfile.flush()
        cardsJSON.extend(deckCards)

print('cards - b:%4u + w:%u = %7s' % (blacks, whites, '{:,}'.format(blacks + whites)))
fullDump = json.dumps(cardsJSON).encode('utf8')
with open('decks/%s' % filename, 'w') as outfile:
    outfile.write(fullDump)
    outfile.flush()

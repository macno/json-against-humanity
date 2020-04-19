import os
import re
import json
import argparse

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


parser = argparse.ArgumentParser(description='Build JSON cards.')
parser.add_argument("-f", "--file", dest='file', default='full.json', help="JSON filename",)
parser.add_argument("-l", "--single", default=False, help="Save decks in separate JSON",
                    action="store_true")
parser.add_argument('-s', '--source', dest="src", default='src',
                    help='source directory (default: src)')
parser.add_argument('-d', '--destination',dest="dest",  default='decks',
                    help='destination directory (default: decks)')
parser.add_argument("--original",  dest='only_original', help="Generate only original cards",
                    action="store_true")
parser.add_argument("--non-original", dest='only_non_original', help="Generate only original cards",
                    action="store_true")

args = parser.parse_args()

def treat_cards(card):
    # Trim
    # Fix ending punctuation
    # Convert to regular line breaks
    return re.sub(r'([^\.\?!])$', '\g<1>.', card.strip()).replace('\\n', '\n')


cardsJSON = []
ids = 1
blacks = 0
whites = 0
for deckDir in os.listdir('%s/' % args.src):

    with open('%s/%s/metadata.json' % (args.src, deckDir)) as j:
        deckCards = []
        metadata = json.load(j)
        if args.only_original and not metadata['official']:
            continue
        if args.only_non_original and metadata['official']:
            continue

        with open(args.src + '/' + deckDir + '/black.md.txt') as f:
            for x in f.readlines():
                deckCards.extend(
                    [{'id': ids, 'cardType': 'Q', 'text': treat_cards(x), 'numAnswers': max(1, x.count('_')),
                      'expansion': metadata['name']}])
                ids = ids + 1
                blacks = blacks + 1
        with open(args.src + '/' + deckDir + '/white.md.txt') as f:
            for x in f.readlines():
                deckCards.extend(
                    [{'id': ids, 'cardType': 'A', 'text': treat_cards(x), 'numAnswers': 0,
                      'expansion': metadata['name']}])
                ids = ids + 1
                whites = whites + 1
        if args.single:
            deckDump = json.dumps(deckCards).encode('utf8')
            with open('%s/%s.json' % (args.dest, deckDir), 'w') as outfile:
                outfile.write(deckDump)
                outfile.flush()
        cardsJSON.extend(deckCards)

print('cards - b:%4u + w:%u = %7s' % (blacks, whites, '{:,}'.format(blacks + whites)))
fullDump = json.dumps(cardsJSON).encode('utf8')
with open('%s/%s' % (args.dest, args.file), 'w') as outfile:
    outfile.write(fullDump)
    outfile.flush()

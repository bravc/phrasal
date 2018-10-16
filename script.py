import nltk
import sqlite3
import random
import math
from nltk.corpus import gutenberg
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.corpus import inaugural
from flask import Flask
from flask import request, abort, render_template, jsonify
app = Flask(__name__)


types = {
    'JJ': 'adjective',
    'JJR': 'adjective comparative',
    'JJS': 'superlative biggest',
    'NN': 'noun singular',
    'NNS': 'noun plural',
    'NNP': 'proper noun',
    'NNPS': 'proper noun plural',
    'POS': 'possesive ending s',
    'PRP': 'personal pronoun I, he, she',
    'PRP$': 'possessive pronoun, my, his , hers',
    'RB': 'adverb silently ',
    'RBR': 'adverb comparative better',
    'RBS': 'adverb superlative best',
    'VB': 'verb, base form take',
    'VBD': 'verb, past tense took',
    'VBG': 'verb, gerund/present participle taking',
    'VBN': 'verb, past participle taken',
    'VBZ': 'verb, 3rd person sing. present takes',
    'VBP': 'verb, sing. present, non-3d take'
}


@app.route("/")
def hello():
    name = 'it works'
    return render_template('body.html', name=name)


@app.route("/create", methods=['POST'])
def create():
    if not request.json:
        abort(400)
    else:
        return load_sentence()(request.json['sentence'])


@app.route("/upload", methods=['POST'])
def upload():
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
  
    if not request.json:
        abort(400)
    else:
        print(request.json['sentence'])
        c.execute("INSERT into custom_sentences(sentence) values(?)", (request.json['sentence'],))
        conn.commit()
        return jsonify(success=True)


@app.route("/random", methods=['GET'])
def get_rand():
    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    # get both converted and not from table
    c.execute("SELECT * from sentences")
    all_rows = c.fetchall()

    # choose a random sentence to madlib
    random_sent = random.choice(all_rows)
    return randomize(random_sent[0], random_sent[1])


def randomize(original, converted):
    list_o = nltk.word_tokenize(original)
    list_c = nltk.word_tokenize(converted)
    twd = TreebankWordDetokenizer()

    to_be_converted = []
    for index, word in enumerate(list_o):
        if list_c[index] in types:
            to_be_converted.append(index)

    num_to_convert = math.floor(len(to_be_converted) / 2)
    random_indexs = random.sample(to_be_converted, num_to_convert)

    for ran in random_indexs:
        list_o[ran] = list_c[ran]

    return twd.detokenize(list_o)


def load_sentence(original_sentence):
    # init db connection
    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    converted_sentence = ""

    # tokenize sentence
    tokens = nltk.word_tokenize(original_sentence)

    # convert to parts of speech
    words = nltk.pos_tag(tokens)

    for word in words:
        converted_sentence += word[1] + " "

    # store sentence and coverted sentence
    c.execute("INSERT into sentences(original, converted) values(?, ?)", [
              (original_sentence), (converted_sentence)])
    conn.commit()
    return converted_sentence

def sneak():
    twd = TreebankWordDetokenizer()
    sent = inaugural.sents('1789-Washington.txt')
    for s in sent:
        load_sentence(twd.detokenize(s))

sneak()
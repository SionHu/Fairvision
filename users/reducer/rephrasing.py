#from .nlp_loader import nlp

PREPOSITIONS = ("aboard", "about", "above", "across", "after", "against",
    "along", "amid", "among", "around", "as", "at", "before", "behind",
    "below", "beneath", "beside", "between", "beyond", "but", "by",
    "concerning", "considering", "despite", "down", "during", "except",
    "following", "for", "from", "in", "inside", "into", "like", "minus",
    "near", "next", "of", "off", "on", "onto", "opposite", "out", "outside",
    "over", "past", "per", "plus", "regarding", "round", "save", "since",
    "than", "through", "to", "toward", "under", "underneath", "unlike",
    "until", "up", "upon", "versus", "via", "with", "within", "without")
TWO_WORD_PREPOSITIONS = ("left of", "right of", "close to", "back to",
    "counter to", "far from", "other than")

def rephraseList(qaDict):
    return [rephrase(*i) for i in qaDict.items()]
def rephrase(q, a):
    _, is_are, *q_words = q.split()
    q_words[-1] = q_words[-1][:-1]
    prepLoc = getFirstIndex(q_words)
    if prepLoc is not None:
        if q_words[0] == 'the':
            prep = q_words[prepLoc]
            fragment = ' '.join(q_words[prepLoc+1:])
            if q_words[1] in ('color', 'pattern'):
                return ' '.join(['With most', IMG_PROMPT, fragment, is_are, a]) + "."
        fragment = ' '.join(q_words)
        return ' '.join(['With most', IMG_PROMPT, a, is_are, fragment]) + "."
    else:
        if q_words[0] == 'the' and 'is' in q_words:
            fragment = ' '.join(q_words[2:])
            return ' '.join(['With most', IMG_PROMPT, fragment, a]) + "."
        fragment = ' '.join(q_words)
        return ' '.join(['With most', IMG_PROMPT, fragment, is_are, a]) + "."
def getFirstIndex(input, matches=PREPOSITIONS):
    for index, word in enumerate(input):
        if word in matches:
            return index
    return None
def rephrase_old(q, a):
    sixws, is_are, *q_words = q.rstrip(' ?').split()
    fragment = ' '.join(q_words)
    if sixws == 'how' and is_are in ('much', 'many'):
        return ' '.join(['With most', IMG_PROMPT, a, fragment]) + "."
    if a.endswith(fragment):
        a = a[:len(a)-len(fragment)-1]
    if getFirstIndex(['as', 'has', 'is'], a.split()):
        return ' '.join(['With most', IMG_PROMPT, a]) + "."
    elif q_words[0] in PREPOSITIONS or ' '.join(q_words[:2]) in TWO_WORD_PREPOSITIONS:
        return ' '.join(['With most', IMG_PROMPT, a, is_are, fragment]) + "."
    else:
        return ' '.join(['With most', IMG_PROMPT, fragment, is_are, a]) + "."

def rephrase_new(q, a):
    q = q.rstrip(' ?')
    qwords = q.split()

    # Choose what to do by question word.
    qqword = qwords[0].lower()
    if qqword == 'what':
        qmain = ' '.join(qwords[1:])
        qdoc = nlp(qmain)

        # If the verb comes first, put the answer before it
        qverb = [token for token in qdoc if token.pos_ == 'VERB']
        if qverb and qmain.startswith(str(qverb[0])):
            out = ' '.join([a, *qwords[1:]])
        else:
            # TODO: Move verb after attr and before prep. Move nsubj after that and put the answer last.
            ...
            out = ' '.join([a, *qwords[1:]])
    elif qqword == 'who':
        out = ' '.join([a, *qwords[1:]])
    elif qqword == 'when':
        out = ' '.join([*qwords[1:], a])
        # Adjustment needed
    elif qqword == 'where':
        out = ' '.join([*qwords[1:], 'by', a])
        # Adjustment needed?
    elif qqword == 'how':
        if qwords[1].lower() in ('many', 'much'):
            qmain = ' '.join(qwords[2:])
            qdoc = nlp(qmain)

            # If the first phrase is a noun, replace it
            qnoun = list(qdoc.noun_chunks)
            if qnoun:
                qnoun0 = qnoun[0].text
                if a.endswith(qnoun0):
                    out = q.replace(qnoun0, a, 1)
                else:
                    out = a + ' ' + qmain
        elif qwords[1].lower() in ('does', 'do'):
            qmain = ' '.join(qwords[2:])
            qdoc = nlp(qmain)
            # TODO: Verb tense needs to change
            out = ' '.join([qmain, 'by', a])
            # Adjustment needed?
        else:
            # TODO: Think about more complex sentence structures in the future
            ...
            out = ' '.join([*qwords[1:], 'by', a])
    elif qqword == 'why':
        if a.startswith("because"):
            out = ' '.join([*qwords, a])
        else:
            out = ' '.join([*qwords, 'because', a])
    else:
        # TODO: Think about more complex sentence structures in the future
        ...
        out = ' '.join([a, 'is', *qwords[1:]])

    #if out.endswith("are there"):
    #    out = "there are " + out[:-10]
    #if out.endswith("is there"):
    #    out = "there is " + out[:-10]
    #out = out.replace("are there on ", "are on ").replace("is there on ", "is on ")
    return  ' '.join(['With most', IMG_PROMPT, out]) + "."

if __name__ == '__main__':
    IMG_PROMPT = input('Objects: ') + ','
    print()
    while True:
        q = input('Q: ')
        a = input('A: ')
        print(rephrase_old(q, a))
        print()
else:
    from django.conf import settings
    IMG_PROMPT = settings.OBJECT_NAME_PLURAL + ','

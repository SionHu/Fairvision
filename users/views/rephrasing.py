from django.conf import settings

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
IMG_PROMPT=settings.KEY.split('/')[1]+'s,'

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
    _, is_are, *q_words = q.split()
    fragment = ' '.join(q_words)[:-1]
    if a.endswith(fragment):
        a = a[:len(a)-len(fragment)-1]
    if getFirstIndex(['as', 'has', 'is'], a.split()):
        return ' '.join(['With most', IMG_PROMPT, a]) + "."
    elif q_words[0] in PREPOSITIONS or ' '.join(q_words[:2]) in TWO_WORD_PREPOSITIONS:
        return ' '.join(['With most', IMG_PROMPT, a, is_are, fragment]) + "."
    else:
        return ' '.join(['With most', IMG_PROMPT, fragment, is_are, a]) + "."

if __name__ == '__main__':
    IMG_PROMPT = input('Objects: ') + ','
    print()
    while True:
        q = input('Q: ')
        a = input('A: ')
        print(rephrase_old(q, a))
        print()

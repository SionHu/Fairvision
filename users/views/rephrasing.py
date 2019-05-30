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
PLURAL_NAME_OF_OBJECT = 'planes'

def rephrase(q, a, img=PLURAL_NAME_OF_OBJECT+','):
    _, is_are, *q_words = q.split()
    q_words[-1] = q_words[-1][:-1]
    prepLoc = getFirstIndex(q_words)
    if prepLoc is not None:
        if q_words[0] == 'the':
            prep = q_words[prepLoc]
            fragment = ' '.join(q_words[prepLoc+1:])
            if q_words[1] in ('color', 'pattern'):
                return ' '.join(['With most', img, fragment, 'should be', a]) + "."
        fragment = ' '.join(q_words)
        return ' '.join(['With most', img, a, 'should be', fragment]) + "."
    else:
        if q_words[0] == 'the' and 'is' in q_words:
            fragment = ' '.join(q_words[2:])
            return ' '.join(['With most', img, fragment, a]) + "."
        fragment = ' '.join(q_words)
        return ' '.join(['With most', img, fragment, 'should be', a]) + "."
def getFirstIndex(input, matches=PREPOSITIONS):
    for index, word in enumerate(input):
        if word in matches:
            return index
    return None

def rephrase_old(q, a, img=PLURAL_NAME_OF_OBJECT+','):
    _, is_are, *q_words = q.split()
    fragment = ' '.join(q_words)[:-1]
    if q_words[0] in PREPOSITIONS or ' '.join(q_words[:2]) in TWO_WORD_PREPOSITIONS:
        return ' '.join(['With most', img, a, 'should be', fragment]) + "."
    else:
        return ' '.join(['With most', img, fragment, 'should be', a]) + "."

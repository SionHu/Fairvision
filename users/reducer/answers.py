"""
Script to create a list of question and single answer to them. The answers that pass a certain merge
threshold will be given only.
"""

# import spacy

from collections import defaultdict
from operator import itemgetter
from more_itertools import partition

from . import word2num
from .nlp_loader import nlp
numWords = set(word2num.__ones__) | set(word2num.__tens__) | set(word2num.__groups__)

def num2text(text):
    words = text.replace('-', ' ').split(' ')
    if sum(1 for w in words if w in numWords):
        wordSet = set(words) - numWords
        for w in wordSet:
            words.remove(w)
        text = ' '.join(words)
        return str(word2num.parse(text))
    return text

def remove_taboo_words(question, taboo_list=("what", "is", "are", "of", "which", "the")):
    for word in question.split():
        word = word.lower()
        if word not in taboo_list:
            yield num2text(word)


class AnswerReducer:
    """
    Class to contain all methods to reduce the redundancy for answers
    """
    def grouper(self, answers):
        """
        Method to group the answers based on their ID to a given question
        :return: Count of groups made
        """
        grouped_questions = defaultdict(list)
        for text, qid in answers:
            grouped_questions[qid].append(text)
        return grouped_questions

    def remove_redundant_answers(self, answers):
        """
        method will return a new list of  unique questions and a dict of the ID'd merged.
        :param answers: The set of answers [answer, id]
        :return: new list of reduced answers and id merge list
        """

        # Remove taboo words from the answers
        all_new = [' '.join(remove_taboo_words(answer)) for answer in answers]
        all_old = []
        old_new_pairs = defaultdict(list)

        for qid_new, q_new in zip(answers, all_new):
            real_doc_new = nlp(q_new)
            if q_new.isnumeric():
                if q_new in all_old:
                    old_new_pairs[q_new].append(q_new)
                else:
                    all_old.append(q_new)
                continue

            for qid_old, q_old in zip(all_old, all_old):
                doc_new = real_doc_new
                doc_old = nlp(q_old)
                doc_old_break = set(doc_old.text.split())
                doc_new_break = set(q_new.split())

                diff_old = " ".join(doc_old_break - doc_new_break)
                diff_new = " ".join(doc_new_break - doc_old_break)
                #print("diffs: "  + diff_old + ", " + diff_new)
                if diff_old and diff_new:
                    doc_old = nlp(diff_old)
                    doc_new = nlp(diff_new)
                else:
                    old_new_pairs[qid_old].append(qid_new)
                    break

                # Uncomment the Prints below to see output. Remove them for production version
                val = doc_new.similarity(doc_old)
                if val > 0.70:
                    #print(doc_old.text)
                    #print(doc_new.text)
                    #print(val)
                    #print("\n_______________________\n")
                    old_new_pairs[qid_old].append(qid_new)
                    break
            else: # if not broken
                # If code reaches this point merge the questions
                all_old.append(qid_new)

        return old_new_pairs

    def reduce_within_groups(self, answers):
        """
        Reduces answers in groups and returns the answers.
        Example if three out of 4 answers are similar then it will make those into a group and give them
        :return: common answer and its id
        """
        from users.models import Question
        qid_to_ans = {}
        for question, answers in self.grouper(answers).items():
            answers, blanks = partition((lambda a: a == ''), answers)
            numBlanks = sum(1 for _ in blanks)
            old_new_pairs = self.remove_redundant_answers(list(answers))
            lens = [(k,len(v)) for k, v in old_new_pairs.items()]
            lens.append((None, numBlanks))
            lens.sort(key=itemgetter(1), reverse=True) # sort by number of matching questions
            print(f"'{Question.objects.get(id=question)}': {lens}")
            if len(lens) == 0 or (len(lens) == 2 and lens[0][1] == lens[1][1]):
                qid_to_ans[question] = [None, 0]
            else:
                qid_to_ans[question] = lens[0]
        return qid_to_ans


def dry_run():
    """
    Get all the queries for answer and question from database and locate the final answers. This function
    does not update the database in any way. It only returns the final answers.
    """
    from ..models import Answer
    return AnswerReducer().reduce_within_groups(Answer.objects.filter(question__isFinal=True).values_list('text', 'question_id'))


if __name__ == "__main__":
    questions = [
        ["how does a plane travel", 1],
        ["what are the airplanes powered by", 2],
        # ["what are those big machines", 3],
        # ["what color is the background of the airplane pics", 4],
        # ["what Direction are these planes facing", 5],
        # ["what is near the airplane background", 6],
        # ["what is the colour of the second plane",7 ],
        # ["what is the purpose of these planes", 8],
        # ["what position level are the airplanes at", 9],
        # ["where are the airplanes", 10],
        # ["where are the flags logo located on the planes", 11],
        # ["where these pictures were taken", 12]
    ]
    answers = [
        ["flying", 1],
        ["the plane is traveled by flying", 1],
        ["flying in the air", 1],
        ["electricity", 2],
        ["gasoline", 2],
        ["fuel", 2]
        # ["airplanes", 3],
        # ["green", 4],
        # ["right to me", 5],
        # ["airport", 6]
    ]

    old_questions = [
        ["What is the color of the cat", 1],
        ["How many legs does the cat have", 2]
    ]
    old_answers = [
        ["The color is blue", 1],
        ["the cat is blue", 1],
        ["The sheep is pink", 1],
        ["The shape is pink", 1],
        ["The cat has 4 legs", 2],
        ["The cat has four legs", 2]
    ]
    i = AnswerReducer().reduce_within_groups(answers)
    print(i)

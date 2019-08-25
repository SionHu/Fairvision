"""
Script to create a list of question and single answer to them. The answers that pass a certain merge
threshold will be given only.
"""

# import spacy

from csgame.nlp_loader import nlp
from collections import defaultdict
from operator import itemgetter


def remove_taboo_words(question, taboo_list=("what", "is", "are", "of", "which", "the")):
    for word in question.split():
        if word.lower() not in taboo_list:
            yield word


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

        # Remove taboo words from the sentence
        all_new = (' '.join(remove_taboo_words(answer)) for answer in answers)
        all_old = []
        old_new_pairs = defaultdict(list)
        docs_old = list(map(nlp, all_old))

        for qid_new, q_new in zip(answers, all_new):
            doc_new = nlp(q_new)
            for qid_old, doc_old in zip(all_old, docs_old):
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
                docs_old.append(doc_new)

        return old_new_pairs

    def reduce_within_groups(self, answers):
        """
        Reduces answers in groups and returns the answers.
        Example if three out of 4 answers are similar then it will make those into a group and give them
        :return: common answer and its id
        """
        qid_to_ans = {}
        for question, answers in self.grouper(answers).items():
            old_new_pairs = self.remove_redundant_answers(answers)
            lens = [(k,len(v)) for k, v in old_new_pairs.items()]
            lens.sort(key=itemgetter(1)) # sort by number of matching questions
            if len(lens) == 0 or (len(lens) == 2 and lens[0][1] == lens[1][1]):
                qid_to_ans[question] = [None, 0]
            else:
                qid_to_ans[question] = lens[0]
        return qid_to_ans


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

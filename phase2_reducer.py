"""
Script to create a list of question and single answer to them. The answers that pass a certain merge
threshold will be given only.
"""

# import spacy
import RedundancyV1
from csgame.nlp_loader import nlp
from collections import defaultdict
from operator import itemgetter


class AnswerReducer:
    """
    Class to contain all methods to reduce the redundancy for answers
    """
    def __init__(self, answers=None, questions=None):
        """
        Class initializer.
        """
        if answers is None or not isinstance(answers[0], list):
            raise ValueError("No answer value is given. Or answer is not in form [[ans, id]]")
        if questions is None or not isinstance(questions[0], list):
            raise ValueError("No question value is given. Or question is not the form [[ques, id]]")
        self.answers = answers
        self.questions = questions
        self.grouped_questions = {}
        self.reducer = RedundancyV1.RedundancyRemover()

    def grouper(self):
        """
        Method to group the answers based on their ID to a given question
        :return: Count of groups made
        """
        for each in self.answers:
            if each[1] in self.grouped_questions.keys():
                self.grouped_questions[each[1]].append(each[0])
            else:
                print("Came here")
                self.grouped_questions.setdefault(each[1], [each[0]])

    def remove_redundant_answers(self, answers):
        """
        method will return a new list of  unique questions and a dict of the ID'd merged.
        :param answers: The set of answers [answer, id]
        :return: new list of reduced answers and id merge list
        """

        # Remove taboo words from the sentence
        all_new = (' '.join(RedundancyV1.remove_taboo_words(answer)) for answer in answers)
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

    def reduce_within_groups(self):
        """
        Reduces answers in groups and returns the answers.
        Example if three out of 4 answers are similar then it will make those into a group and give them
        :return: common answer and its id
        """
        qid_to_ans = {}
        for question, answers in self.grouped_questions.items():
            old_new_pairs = self.remove_redundant_answers(answers)
            lens = [(k,len(v)) for k, v in old_new_pairs.items()]
            lens.sort(key=itemgetter(1)) # sort by number of matching questions
            if len(lens) == 0 or (len(lens) == 2 and lens[0][1] == lens[1][1]):
                qid_to_ans[question] = []
            else:
                qid_to_ans[question] = lens[0][0]
        return qid_to_ans


if __name__ == "__main__":
    questions = [
        ["What is the color of the cat", 1],
        ["How many legs does the cat have", 2]
    ]
    answers = [
        ["The color is blue", 1],
        ["the cat is blue", 1],
        ["The sheep is pink", 1],
        ["The shape is pink", 1],
        ["The cat has 4 legs", 2],
        ["The cat has four legs", 2]
    ]
    test_obj = AnswerReducer(questions=questions, answers=answers)
    test_obj.grouper()
    i = test_obj.reduce_within_groups()
    print(i)

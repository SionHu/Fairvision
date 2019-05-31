"""
This is the first version of the code to reduce redundancy for the attributes given by the users.
The code uses SpaCy to find similarities. The code assumes the model is given as a param for the initializer.
About the model used -> English multi-task CNN trained on OntoNotes, with GloVe vectors trained on Common Crawl.
Assigns word vectors, context-specific token vectors, POS tags, dependency parse and named entities.
Model Name  - en_core_web_md
"""

# Imports
import warnings
import spacy


def remove_taboo_words(question, taboo_list=("what", "is", "are", "of", "which", "the")):
    for word in question.split():
        if word.lower() not in taboo_list:
            yield word


class RedundancyRemover:
    """
    Class to handle all machine based redundancy removal.
    """
    def __init__(self, model):
        """
        Class initializer
        """
        # self.file_handle = open(file_path)
        # self.csv_reader = csv.reader(self.file_handle, delimiter=',')
        self.nlp = model  # spacy.load('en_core_web_md')  # The SpaCy handle to the Language model
        if not isinstance(self.nlp, spacy.lang.en.English):
            raise TypeError("Model given is not of type {}.".format("spacy.lang.en.English"))

    def get_reduced_records(self, new_ques, old_ques):
        """
        Method to run an immediate validation on the data for redundancy.
        Method only check questions.
        :param new_ques: List of new questions. [string, id]
        :param old_ques: List of all existing questions from the database
        :return: List of new questions and merge id list and a dictionary
         mapping the new question ids to the old ones for those that are similar
        """
        if len(old_ques) == 0:
            warnings.warn("This is the first write no redundancy check is possible.")
            return new_ques
        # Remove taboo words from the sentence
        all_new = (' '.join(remove_taboo_words(question)) for question, _ in new_ques)
        all_old = (' '.join(remove_taboo_words(question)) for question, _ in old_ques)
        new_old_pairs = {}
        docs_old = list(map(self.nlp, all_old))

        for qid_new, q_new in zip(new_ques, all_new):
            doc_new = self.nlp(q_new)
            for qid_old, doc_old in zip(old_ques, docs_old):
                # Uncomment the Prints below to see output. Remove them for production version
                val = doc_new.similarity(doc_old)
                if val > 0.80:
                    # print(doc_old.text)
                    # print(doc_new.text)
                    # print(val)
                    # print("\n_______________________\n")
                    new_old_pairs[qid_new[1]] = qid_old[1]
                    break
            else:
                # If code reaches this point merge the questions
                old_ques.append(qid_new)
                docs_old.append(doc_new)

        return old_ques, new_old_pairs

    def remove_redundant_answers(self, answers):
        """
        method will return a new list of  unique questions and a dict of the ID'd merged.
        :param answers: The set of answers [answer, id]
        :return: new list of reduced answers and id merge list
        """

        # Remove taboo words from the sentence
        all_new = (' '.join(remove_taboo_words(question)) for question, _ in answers)
        all_old = []  # (' '.join(remove_taboo_words(question)) for question, _ in old_ques)
        new_old_pairs = {}
        old_ans = []
        docs_old = list(map(self.nlp, all_old))

        for qid_new, q_new in zip(answers, all_new):
            doc_new = self.nlp(q_new)
            for qid_old, doc_old in zip(old_ans, docs_old):
                # Uncomment the Prints below to see output. Remove them for production version
                val = doc_new.similarity(doc_old)
                if val > 0.80:
                    # print(doc_old.text)
                    # print(doc_new.text)
                    # print(val)
                    # print("\n_______________________\n")
                    new_old_pairs[qid_new[1]] = qid_old[1]
                    break
            else:
                # If code reaches this point merge the questions
                old_ans.append(qid_new)
                docs_old.append(doc_new)

        return old_ans, new_old_pairs

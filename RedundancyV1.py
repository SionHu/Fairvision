"""
This is the first version of the code to reduce redundancy for the attributes given by the users.
The code uses SpaCy to find similarities. The code assumes the model is given as a param for the initializer.
About the model used -> English multi-task CNN trained on OntoNotes, with GloVe vectors trained on Common Crawl.
Assigns word vectors, context-specific token vectors, POS tags, dependency parse and named entities.
Model Name  - en_core_web_md
"""

# Imports
import warnings
import datetime
import spacy


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
        :return: List of new questions and merge id list
        """
        if len(old_ques) == 0:
            warnings.warn("This is the first write no redundancy check is possible.")
            return new_ques
        # Remove taboo words from the sentence
        all_new = (' '.join(removeTabooWords(question)) for question, _ in new_ques)
        all_old = (' '.join(removeTabooWords(question)) for question, _ in old_ques)
        docs_old = list(map(self.nlp, all_old))

        for i_new, q_new in enumerate(all_new):
            doc_new = self.nlp(q_new)
            for doc_old in docs_old:
                # Uncomment the Prints below to see output. Remove them for production version
                val = doc_new.similarity(doc_old)
                print(doc_old.text)
                print(doc_new.text)
                print(val)
                print("\n_______________________\n")
                if val > 0.80:
                    break
            else:
                # If code reaches this point merge the questions
                old_ques.append(new_ques[i_new])
                docs_old.append(doc_new)

        return old_ques

def removeTabooWords(question, taboo_list=("what", "is", "are", "of", "which", "the")):
    for word in question.split():
        if word.lower() not in taboo_list:
            yield word

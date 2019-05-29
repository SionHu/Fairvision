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
        assert isinstance(self.nlp, spacy.lang.en.English), "Model given is not of type {}.".format("spacy.lang.en.English")

    def get_reduced_records(self, new_ques, old_ques):
        """
        Method to run an immediate validation on the data for redundancy.
        Method only check questions.
        :param new_ques: List of new questions. [string, id]
        :param old_ques: List of all existing questions from the database
        :return: List of the IDs of the dissimilar questions and merge id list and a dictionary
         mapping the new question ids to the old ones for those that are similar
        """

        if len(old_ques) == 0:
            warnings.warn("This is the first write no redundancy check is possible.")
            return new_ques, None
        # Remove taboo words from the sentence
        all_new = (' '.join(removeTabooWords(question)) for question, _ in new_ques)
        all_old = (' '.join(removeTabooWords(question)) for question, _ in old_ques)


        # Remove taboo words from the sentences and accept the ones that are dissimilar to old sentences
        all_old = [(self.nlp(' '.join(removeTabooWords(question))), id) for question, id in old_ques]
        for ques_new, id_new in new_ques:
            doc_new = self.nlp(' '.join(removeTabooWords(ques_new)))
            for doc_old, id_old in all_old:
                # Uncomment the Prints below to see output. Remove them for production version
                val = doc_new.similarity(doc_old)
                if val > 0.80:
                    #print(doc_old.text)
                    #print(doc_new.text)
                    #print(val)
                    #print("\n_______________________\n")
                    new_old_pairs[id_new] = id_old
                    break
            else: # if no break (https://docs.quantifiedcode.com/python-anti-patterns/correctness/not_using_else_in_a_loop.html)
                # If code reaches this point merge the questions
                accepted_ids.append(id_new)
                all_old.append((doc_new, id_new))

        return accepted_ids, new_old_pairs

def removeTabooWords(question, taboo_list=("what", "is", "are", "of", "which", "the")):
    for word in question.split():
        if word.lower() not in taboo_list:
            yield word
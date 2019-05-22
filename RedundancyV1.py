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
        self.taboo_list = ["what", "is", "are", "of", "which", "the"]
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
        # Assuming records already exist
        all_new = []
        all_old = []
        for each in new_ques:
            all_new.append(each[0])
        for each in old_ques:
            all_old.append(each[0])
        # Remove taboo words from the sentence
        for i in range(0, len(all_new)):
            words = all_new[i].split()
            result_words = [word for word in words if word.lower() not in self.taboo_list]
            result = ' '.join(result_words)
            all_new[i] = result
        for i in range(0, len(all_old)):
            words = all_old[i].split()
            result_words = [word for word in words if word.lower() not in self.taboo_list]
            result = ' '.join(result_words)
            all_old[i] = result

        for i_new in range(0, len(all_new)):
            for j_old in range(0, len(all_old)):
                doc_new = self.nlp(all_new[i_new])
                doc_old = self.nlp(all_old[j_old])
                # Uncomment the Prints below to see output. Remove them for production version
                print(doc_old.text)
                print(doc_new.text)
                print(doc_new.similarity(doc_old))
                print("\n_______________________\n")
                val = doc_new.similarity(doc_old)
                if val > 0.80:
                    break
            # If code reaches this point merge the questions
            old_ques.append(new_ques[i_new])

        return old_ques

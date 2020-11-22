import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    file_dict = {} # Initialise a dictionary to map fileness to content

    for file in os.listdir(directory): # Iterate through given directory
        if file.endswith('.txt'):
            file_path = os.path.join(directory, file)
            with open(file_path, 'r') as f:
                contents = f.read()
                file_dict[file] = contents
            f.close()

    return file_dict


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    word_list = [] # Initialise list for words in document input 
    tokens = nltk.word_tokenize(document) # Tokenise the document
    
    for word in tokens:
        word = word.lower()
        if word not in string.punctuation and word not in nltk.corpus.stopwords.words("english"):
            word_list.append(word)
    
    return word_list


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idfs = {} # Initialise a dictionary of idfs
    for doc in documents:
        for word in documents[doc]:
            if word in idfs: # Word already calculated
                continue
            word_occurences = 1
            for doc2 in documents:
                if doc2 == doc: # Skip word iteration we are looking at
                    continue
                if word in documents[doc2]:
                    word_occurences += 1
            idfs[word] = math.log(len(documents) / word_occurences)
    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    file_scores = {} # Dicitonary to hold scores of files

    for doc in files: # Iterate through docs
        file_scores[doc] = 0 # Intiliase score
        for word in query: # Iterate through words in query
            if word in files[doc]:
                score = files[doc].count(word)
                file_scores[doc] += score * idfs[word]

    sorted_files = sorted([filename for filename in files], key = lambda x : file_scores[x], reverse=True) # Sort

    return sorted_files[:n] # return n best files


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentence_score = {}

    for sentence in sentences: # Iterate through sentences
        sentence_score[sentence] = [0, 0] # Initialise matching word measure, query term density
        for word in query: # Iterate through words in query
            if word in sentences[sentence]:
                sentence_score[sentence][0] += idfs[word]
        query_terms = 0
        for word in sentences[sentence]:
            if word in query:
                query_terms += 1
        sentence_score[sentence][1] += query_terms / len(sentences[sentence])
    
    sorted_sentences = sorted([sentence for sentence in sentences], key= lambda x: (sentence_score[x][0], sentence_score[x][1]), reverse=True) # Sort

    return sorted_sentences[:n] # return n best sentences


if __name__ == "__main__":
    main()

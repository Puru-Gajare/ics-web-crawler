
# Runtime Complexity: O(N) where n is # of characters in file
# since as n grows, the amount of time our program will take in
# the worst-case will grow linearly, as we are iterating through
# each character in the file one time
# def tokenize(TextFilePath):
#     '''
#     returns a list of all alphanumeric words in the inputted text file
#     '''

#     result = []
#     currentWord = ""


#     try:
#         # using context manager since it automatically closes the file
#         with open(TextFilePath, 'r') as file:
#             while 1:
#                 char = file.read(1)             # get character from file

#                 if not char:            # if character doesn't exist, break loop
#                     break

#                 if char.isalnum() and ord(char) <= 127:
#                     # if current character is alphanumeric, then add
#                     currentWord += char.lower()
#                 else:
#                     # if current character is not alphanumeric, reset
#                     if currentWord != "":
#                         result.append(currentWord)
#                     currentWord = ""

#         # add last word if it exists
#         if currentWord != "":
#             result.append(currentWord)
#     except FileNotFoundError:
#         pass


#     return result

import sys


stopWords = {'but', 'by', 'it', 'out', 'up', "couldn't", 'ours', 'ourselves', 'of', 'whom', 'further', 'both', 'would', 'not', 'should', 'how', 'again', 'why', 'theirs', 'who', "where's", 'there', "hasn't", 'more', 'which', 'we', 'no', 'above', 'at', "we'd", 'before', 'they', 'ought', 'them', "won't", 'nor', "you're", 'myself', 'that', 'below', "you'd", 'as', "they've", 'is', 'then', 'our', 'when', "you'll", 'where', "it's", 'those', 'do', 'was', 'into', 'while', 'its', 'only', 'between', 'does', 'any', 'did', 'and', 'me', 'his', 'than', 'an', 'yourself', 'these', 'against', 'himself', 'be', 'because', 'each', "how's", 'are', 'most', 'some', 'have', "there's", 'all', 'she', 'so', "who's", "he's", 'through', 'themselves', 'been', "isn't", 'he', 'down', 'under', 'had', "mustn't", "shan't", "can't", "when's", 'i', 'for', 'very', "weren't", 'itself', 'with', 'her', "wasn't", 'a', 'herself', "we're", 'has', 'were', "she'll", "i'd", 'off', 'could', "he'd", "she's", "they're", "doesn't", "haven't", 'here', 'him', 'on', "i'll", 'over', 'too', 'about', "why's", 'your', "aren't", 'same', "that's", 'doing', 'their', 'in', 'cannot', "hadn't", 'my', 'having', 'yours', 'if', 'what', 'during', "i'm", 'hers', "let's", 'this', "shouldn't", 'to', 'other', 'you', "they'd", 'such', 'yourselve', 'until', "we'll", 'own', "here's", "they'll", 'few', 'or', 'being', "what's", "i've", "she'd", "wouldn't", "you've", "he'll", 'after', 'the', 'am', 'once', 'from', "didn't", "we've", "don't"}

def tokenizeString(string: str):
    current_index = 0
    result = []
    currentWord = ""
    string_len = len(string)

    while current_index < string_len:
        char = string[current_index]             # get character from file

        if char.isalnum() and ord(char) <= 127:
            # if current character is alphanumeric, then add
            currentWord += char.lower()
        else:
            # if current character is not alphanumeric, reset
            if currentWord != "" and not currentWord in stopWords:
                result.append(currentWord)
            currentWord = ""
        current_index += 1

    # add last word if it exists
    if currentWord != "":
        result.append(currentWord)

    return result

    


# Runtime Complexity: O(N), where n is the number of values in
# the argument tokenList; This is because we are iterating through
# each item in tokenList one time, so as n grows, the runtime of our
# program will grow linearly
def computeWordFrequencies(tokenList):
    '''
    Returns a dictionary containing the frequency of each word
    in tokenList
    '''

    result = dict()

    # for every token in list, increment its frequency
    for token in tokenList:
        #if token already exists in dictionary, increment it's value
        if token in result:
            result[token] += 1

        # if token doesn't exist as key in dictionary, initialize it's value to 1
        else:
            result[token] = 1

    return result


# Runtime Complexity: O(NlogN), where n is the number of
# key-value pairs in wordCount; sorting through Python's
# sorted function runs in nlogn time in the average case
# since it uses Timsort, which is derived from merge
# sort(nlogn) and insertion sort(n^2)
def printFrequencies(wordCount):
    '''
    Prints the frequencies of the inputted dictionary in
    sorted descending order, breaking ties with alphabetic order
    '''

    # if no tokens exist, output 0
    if len(wordCount) == 0:
        print(0)
        return

    # sort dictionary
    sortedDict = dict(sorted(wordCount.items(), key = lambda x: (-x[1], x[0])))

    # print every value in sorted dict
    for key, value in sortedDict.items():
        print(str(key) + " " + str(value))

    return


if __name__ == "__main__":
    arguments = sys.argv
    tokens = tokenizeString(arguments[1])
    print(tokens)

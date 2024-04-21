
# Runtime Complexity: O(N) where n is # of characters in file
# since as n grows, the amount of time our program will take in
# the worst-case will grow linearly, as we are iterating through
# each character in the file one time
def tokenize(TextFilePath):
    '''
    returns a list of all alphanumeric words in the inputted text file
    '''

    result = []
    currentWord = ""


    try:
        # using context manager since it automatically closes the file
        with open(TextFilePath, 'r') as file:
            while 1:
                char = file.read(1)             # get character from file

                if not char:            # if character doesn't exist, break loop
                    break

                if char.isalnum() and ord(char) <= 127:
                    # if current character is alphanumeric, then add
                    currentWord += char.lower()
                else:
                    # if current character is not alphanumeric, reset
                    if currentWord != "":
                        result.append(currentWord)
                    currentWord = ""

        # add last word if it exists
        if currentWord != "":
            result.append(currentWord)
    except FileNotFoundError:
        pass


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
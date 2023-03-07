import threading
import re


def DistributedSearch(textfile, StringToSearch, nThreads, Delta):
    """
    The main function for this procedure. Will implement partition into threads,
    will open the file and export it into an array for partitioning.
    First: Function will create the regex expression (so it will only be created once)
    Second: The function will open the text file and create an array
    Third: The function will create threads -> each wil activate the inner functions
    ...
    :param textfile: The text file to search in
    :param StringToSearch: The string to search in the text file
    (it contains only letters & digits and no spaces)
    :param nThreads: How many threads will be created for the search
    :param Delta: The delta (distance) between letters to search in the file.
    :return: The program output is the location of all occurrences of string in the file in the format
     [line,location]. Otherwise, output "not found" (If all threads returned None)
    """
    res = []
    expression = GetRegexExpression(StringToSearch, Delta)

    # Open file and split to lines
    with open(textfile, 'r', encoding='utf-8') as file:
        text = file.read()
    lines_array = text.split('\n')  # Split the text with new line as delimiter, store in array

    # Calculate workload for each thread
    section_size = len(lines_array) // nThreads  # The number of lines each thread gets

    threads = []
    results = []

    for i in range(nThreads):  # Divide long array into sections for threads
        # Each section indexes starts after the index of its proportional size
        # Start line
        start_i = i * section_size
        # End line
        end_i = (i + 1) * section_size
        # In case the last section needs to be bigger
        if i == nThreads - 1:
            t = threading.Thread(target=ScanDataInFile, args=(lines_array[start_i:], expression, results, start_i))
        else:
            t = threading.Thread(target=ScanDataInFile, args=(lines_array[start_i:end_i], expression, results, start_i))

        threads.append(t)  # Create a list of all the threads
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Finish
    if not results == []:
        for i in range(len(results)):
            print(results[i])

    else:
        return "not found"


def ScanDataInFile(Array, expression, res, start_line):
    """
    1st sub function will implement the check over a given array of string.
    This function will be given to the thread.
    :param Array: sub array of textfile.
    :param expression: The already made regex expression to search
    :param res: The return array the function returns values to
    :param start_line: The first line this thread got
    :return: This function appends all the indexes found into the list res (input).
    If no matches found - nothing will be added
    """
    for i, line in enumerate(Array):
        tmp = LookInLine(line, start_line + i, expression)
        res.extend(tmp)


def LookInLine(line, lineindex, expression):
    """
    2nd sub function will check a given string (line) to look for StringToSearch.
    :param line: A string (AKA a line from the imported file)
    :param lineindex: The index of the checked line at the moment. Will be passed by ScanDataInFile
    :param expression: The already made regex expression to search
    :return: The indexes inside the line in which the string was found
    in format [lineindex,index-in-line]. If no matches are found, returns []
    """
    # Find all the matches of the pattern in the string
    matches = expression.finditer(line)

    # Get the indexes of each match
    indexes = [match.start() for match in matches]
    res = [(lineindex, i) for i in indexes]  # Return

    return res


def GetRegexExpression(StringToSearch, Delta):
    """
    This sub function creates the regex expression that will be the search parameter
     for the rest of the program
    :param StringToSearch: The original string (line) from file
    :param Delta: The delta (distance) between letters to search in the file.
    :return: A regex expression as template
    """
    # Modify StringToSearch to into a Regex expression to be searched for
    exp = list(StringToSearch)
    for i in range(len(exp)):
        if i == len(exp) - 1:  # Avoid \s{Delta} (space) in the end fo the expression
            break
        exp[i] = exp[i] + "\s{" + str(Delta) + '}'  # Modified Regex Pattern
    expression = ''.join(exp)  # Re-join into an expression

    # Create regex expression
    regex_expression = re.compile(expression)  # Compile into Regex
    return regex_expression


Alice = "C:\\Users\\shaha\\PycharmProjects\\mamah_04_python_threads\\Alice.txt"
Rick_Wobba = "C:\\Users\\shaha\\PycharmProjects\\mamah_04_python_threads\\Rick.txt"
print(DistributedSearch(Alice, "Alice", 8, 0))
print(DistributedSearch(Rick_Wobba, "dub", 16, 0))
print(DistributedSearch(Rick_Wobba, "sha", 16, 0))





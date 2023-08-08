# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import os.path
import shutil


class IndexWriter:
    def __init__(self, inputFile, dir):
        """Given product review data, creates an on disk
        index
        inputFile is the path to the file containing the
        review data
        dir is the path of the directory in which all index
        files will be created
        if the directory does not exist, it should be
        created"""

        if not os.path.isfile(inputFile):
            print("error: invalid file path")
            exit(-1)
        if not os.path.isdir(dir):
            # print("creating directory")
            os.makedirs(dir)
        # else:
        #      # print("directory already created")
        reviewDictionary = self.read_from_file(inputFile)
        files = {"reviews.tbl", "texts.dic", "products.dic", "collection.data"}

        for file in files:  # this loop will open files and write the information by calling write_to_Indexfile() function
            filePath = os.path.join(dir, file)
            if not os.path.isfile(filePath):

                f = open(filePath, "x")
                self.write_to_Indexfile(reviewDictionary, f, file, dir)
                f.close()


            else:  # if file already exist
                # print("file {} is already exists".format(file))
                f = open(filePath, "w")
                self.write_to_Indexfile(reviewDictionary, f, file, dir)
                f.close()

    def remove(self, dir):
        """Delete all index files by removing the given
        directory
        dir is the path of the directory to be deleted"""

        if os.path.isdir(dir):
            # remove directory and all its content

            shutil.rmtree(dir)
        else:
            print("Error: Path {} is not a file or dir.".format(dir))

    def read_from_file(self, inputFile):
        """this function open the inputFile the read all details about reviews, then fill the details in Dictionary
        then return it"""
        reviewDictionary = []
        i = -1

        with open(inputFile) as f:
            while True:
                """ this loop read from inputFile the details and fill it in Dictionary"""
                line = f.readline()
                """ this if's : search the details words in string that have what they read from inputFile, then do substring"""

                if (line.find('product/productId:') >= 0):
                    i = i + 1
                    Pid = line[line.find('product/productId:') + len('product/productId:'):].replace(" ", "").replace(
                        "\n", "")

                    reviewDictionary.append([Pid])  # fill in Dictionary


                elif (line.find('review/helpfulness:') >= 0):
                    helpfulness = line[line.find('review/helpfulness:') + len('review/helpfulness:'):].replace(" ",
                                                                                                               "").replace(
                        "\n", "")
                    helpfulness_Numerator = helpfulness[:helpfulness.find('/')]
                    helpfulness_Denominator = helpfulness[helpfulness.find('/') + 1:]
                    reviewDictionary[i].append(helpfulness_Numerator)  # fill in Dictionary
                    reviewDictionary[i].append(helpfulness_Denominator)  # fill in Dictionary

                elif (line.find('review/score:') >= 0):
                    score = line[line.find('review/score:') + len('review/score:'):].replace(" ", "").replace("\n", "")
                    reviewDictionary[i].append(score)

                elif (line.find('review/text:') >= 0):
                    text = line[line.find('review/text:') + len('review/text:') + 1:].replace("\n", "")
                    list_words = self.Splite_by_alpha(text.lower())
                    reviewDictionary[i].append(str((len(list_words))))
                    # reviewDictionary[i].append(text)
                    reviewDictionary[i].append(list_words)

                if not line:
                    break

        f.close()

        return reviewDictionary

    def write_to_Indexfile(self, Dictionary, indexFile, type, dir):
        """ this function receive Dictioanry: data structures have reviews information, indexfile : file what to write to  , type : which file want to write to , dir : directory of file"""
        """ the function write to each index file the information they we want to be for this file """

        list_all_words = [] # list have all text review words
        uniqueProducts = [] # for products without Repetition
        if type == "reviews.tbl": # write to reviews.tbl file

            row1 = "|  reviewID  |  productID  |  helpfulness Numerator  |  helpfulness Denominator  |  score  |  length  |\n"
            row2 = '-' * len(row1) + "\n"
            indexFile.write(row1 + row2)

            i = 1
            for ele in Dictionary:
                WriteTable = "|  " + str(i) + " " * (10 - len(str(i))) + "|  " + ele[0] + " " * (
                            11 - len(ele[0])) + "|  " \
                             + str(ele[1]) + str(" " * (23 - len(ele[1]))) + "|  " \
                             + str(ele[2]) + str(" " * (25 - len(str(ele[2])))) + "|  " \
                             + str(ele[3]) + str(" " * (7 - len(str(ele[3])))) + "|  " \
                             + str(ele[4]) + str(" " * (8 - len(str(ele[4])))) + "|\n"
                indexFile.write(WriteTable)
                i = i + 1
        elif type == "texts.dic": # write to  texts.dic file

            file_lst_Path = os.path.join(dir, "texts.lst")
            if not os.path.isfile(file_lst_Path):
                file_lst = open(file_lst_Path, "x")
            else:
                file_lst = open(file_lst_Path, "w")
            list_words_was_count = []
            count_seek_word = 0

            row1 = "|  word                |  amount of reviews  |  index  |\n"
            row2 = '-' * len(row1) + "\n"

            indexFile.write(row1 + row2)
            allwords = []
            for ele in Dictionary:

                list_words = ele[5]
                list_all_words.extend(list_words)

                for word in list_words:
                    # if self.existIn(word,allwords) < 0:
                        allwords.append(word)
            allwords.sort()
            # print("allwords ->",allwords)
            for word in allwords:
                if not word in list_words_was_count:
                    list_words_was_count.append(word)

                    count_text_len, Dic_word_freq = self.count_word_in_reviews(Dictionary, word)
                    WriteTable = "|  " + word + " " * (20 - len(str(word))) \
                                 + "|  " + str(count_text_len) + " " * (19 - len(str(count_text_len))) \
                                 + "|  " + str(count_seek_word) + " " * (7 - len(str(count_seek_word))) + "|\n"
                    count_seek_word += len(str(Dic_word_freq))

                    indexFile.write(WriteTable)
                    file_lst.write(str(Dic_word_freq))


            file_lst.close()
        elif type == "products.dic": # write products.dic file
            row1 = "|  productID   |  amount of reviews  |  index  |\n"
            row2 = '-' * len(row1) + "\n"

            reviewId = 1
            for ele in Dictionary:
                isExist = self.existIn(ele[0], uniqueProducts)
                if isExist >= 0:
                    uniqueProducts[isExist][1] += 1
                    uniqueProducts[isExist][3].append(reviewId)
                else:
                    temp = [ele[0], 1, -1, [reviewId]]
                    uniqueProducts.append(temp)
                reviewId += 1
            uniqueProducts.sort()
            string = ""
            for product in uniqueProducts:
                product[2] = len(string)
                string += str(product[3]).replace("[", "").replace("]", "").replace(",", "") + " "
            file_lst_Path = os.path.join(dir, "products.lst")
            if not os.path.isfile(file_lst_Path):
                file_lst = open(file_lst_Path, "x")
            else:
                file_lst = open(file_lst_Path, "w")

            file_lst.write(string)
            string = ""
            for product in uniqueProducts:
                string += "|  " + str(product[0]) + "  |  " + str(product[1]) + (19 - len(str(product[1]))) * (
                    " ") + "|  " + str(product[2]) + (5 - len(str(product[2]))) * " " + "  |\n"
            indexFile.write(row1 + row2 + string)
            file_lst.close()

        elif type == "collection.data":# write collection.data file

            count_text_len = 0
            for ele in Dictionary:
                count_text_len += int(ele[4])
            write_to_file = str(len(Dictionary)) + '\n' + str(count_text_len)
            indexFile.write(write_to_file)

    def existIn(self, name, productsDicArray):
        """this function check if element  are exist in  productsDicArray  """
        index = 0
        for product in productsDicArray:
            if name in product:
                return index
            index += 1
        return -1

    def Splite_by_alpha(self, string_splite):
        """ this function  split text to words by alphabet and numeric and return it in list"""
        pos = 0
        list = []

        while pos < len(string_splite):
            if string_splite[pos].isalpha() or string_splite[pos].isnumeric():

                pos += 1
                if (pos == 20):
                    str = string_splite[:pos]
                    if str != "":
                        list.append(str)
                    string_splite = string_splite[pos :]
                    pos = 0
            else:
                str = string_splite[:pos]
                if str != "":
                    list.append(str)
                string_splite = string_splite[pos + 1:]
                pos = 0

        if string_splite != "":
            list.append(string_splite)
        return list

    def count_word_in_reviews(self, Dictionary, word):
        """ this function receive Dictionary : data strecture , word: the word we want to count  check if the word are exist in review and count how many times """
        count_for_all = 0
        index = 1
        Dic_word_count = {}

        for ele in Dictionary:

            words = ele[5]

            if word in words:
                count_for_each = self.count_occurrence(words, word)
                count_for_all += 1
                Dic_word_count[index] = count_for_each
            index += 1

        return count_for_all, Dic_word_count

    def count_occurrence(self, words, word_to_count):
        """ count how many times the word are exist"""
        count = 0
        for word in words:
            if word == word_to_count:
                # update counter variable
                count = count + 1
        return count

import os.path

import numpy as np

from TolerantIndexWriter import TolerantIndexWriter
from IndexReader import IndexReader
class TolerantIndexReader:
    reviews_dic = []
    token_str = None
    collections_data = []
    Texts_File_Contents = []
    products_dic_fxd = []
    Texts_lpv_Contents = None
    products_lst_vrnt_str = None
    bigrams_list = []

    bigrams_ids = None
    read = None

    def __init__(self, dir):
        """Creates a CompressedIndexReader object which will
        read from the given directory
        dir is the path of the directory that contains the
        index files"""
        files = {"reviews.tbl" ,  "collection.data" , "texts.dic.tbl", "texts.lst.lpv" , "products.dic.fxd" , 'products.lst.vrnt' , "bigram.dic" , "bigram.lst"}


        for file in files:
            self.Read_From_Files(dir, file)

    def getProductId(self, reviewId):
        """Returns the product identifier for the given
        review
        Returns None if there is no review with the given
        identifier"""
        for ele in self.reviews_dic:

            if str(ele[0]) == str(reviewId):
                return ele[1]

        return None

    def getReviewScore(self, reviewId):
        """Returns the score for a given review
        Returns None if there is no review with the given
        identifier"""
        for ele in self.reviews_dic:

            if str(ele[0]) == str(reviewId):
                return ele[4] + '.' + ele[5]

        return None

    def getReviewHelpfulnessNumerator(self, reviewId):
        """Returns the numerator for the helpfulness of a
        given review
        Returns None if there is no review with the given
        identifier"""
        for ele in self.reviews_dic:

            if str(ele[0]) == str(reviewId):
                return ele[2]

        return None

    def getReviewHelpfulnessDenominator(self, reviewId):
        """Returns the denominator for the helpfulness of a
        given review
        Returns None if there is no review with the given
        identifier"""
        for ele in self.reviews_dic:

            if str(ele[0]) == str(reviewId):
                return ele[3]

        return None

    def getReviewLength(self, reviewId):
        """Returns the number of tokens in a given review
        Returns None if there is no review with the given
        identifier"""
        for ele in self.reviews_dic:

            if str(ele[0]) == str(reviewId):
                return ele[6]

        return None

    def getTokenFrequency(self, token):
        """Return the number of reviews containing a given
        token (i.e., word)
        Returns 0 if there are no reviews containing this
        token"""

        # Return the number of reviews
        result = self.get_Token_Details(token , 1)
        if(result[0] == None):
            return 0
        else:
            return result[0]

    def getTokenCollectionFrequency(self, token):
        """Return the number of times that a given token
        (i.e., word) appears in
        the reviews indexed
        Returns 0 if there are no reviews containing this
        token"""

        # Return the number of pointer
        Pointer_cur, pointer_next= self.get_Token_Details(token, 2)
        if(pointer_next == None or pointer_next == None):
            return 0

        List = list(self.Texts_lpv_Contents[Pointer_cur : pointer_next])
        # a =list(IndexReader.getReviewsWithToken(IndexReader('data'), "a"))

        List_No_Gap =  self.ungappingForLpv(self.unlpv(self.readingAndCompressingForLvp(List)))
        sum_number = 0
        for freq in range(len(List_No_Gap) ):
            if not int(freq) % 2 == 0:
                sum_number+=List_No_Gap[freq]

        return sum_number


    def getReviewsWithToken(self, token):
        """Returns a series of integers of the form id-1,
        freq-1, id-2, freq-2, ... such
        that id-n is the n-th review containing the given
        token and freq-n is the
        number of times that the token appears in review idn
        Note that the integers should be sorted by id
        Returns an empty Tuple if there are no reviews
        containing this token"""
        Tuple = ()
        Pointer_cur, pointer_next = self.get_Token_Details(token, 2)
        if (pointer_next == None or pointer_next == None):
            return Tuple

        Tuple = list(self.Texts_lpv_Contents[Pointer_cur: pointer_next])

        result = tuple(self.ungappingForLpv(self.unlpv(self.readingAndCompressingForLvp(Tuple))))

        return result

    def getNumberOfReviews(self):
        """Return the number of product reviews available in
        the system"""
        return self.collections_data[0]


    def getTokenSizeOfReviews(self):
        """Return the number of tokens in the system
        (Tokens should be counted as many times as they
        appear)"""
        return self.collections_data[1]

    def getProductReviews(self, productId):
        """Return the ids of the reviews for a given product
        identifier
        Note that the integers returned should be sorted by
        id
        Returns an empty Tuple if there are no reviews for
        this product"""
        Pontier_cur = 0
        Pontier_next = 0
        Find_Product = False
        for products_index in range(len(self.products_dic_fxd)):
            if(self.products_dic_fxd[products_index][0] == productId) :

                if(products_index == len(self.products_dic_fxd) -1) :
                    Pontier_cur = self.products_dic_fxd[products_index][2]
                    Pontier_next = len(self.products_lst_vrnt_str)
                    Find_Product = True

                else:
                    Find_Product = True
                    Pontier_cur = self.products_dic_fxd[products_index][2]
                    Pontier_next = self.products_dic_fxd[products_index +1][2]
                break

        if(Find_Product) :

          return tuple( self.ungaping(self.myunvariant( self.readingAndCompressingForVariant(list(self.products_lst_vrnt_str[Pontier_cur: Pontier_next])))))
        else:
            return ()

    def getTokenSimilarWildcard(self, token):
        """Return a series of wildcard-ed words (i.e. words
        that match the wildcard query) alphabetically sorted
        token – a string containing *
        if the token does not contain any *, returns the
        token itself"""
        if (token == '*'):
            return self.get_all_tokens()
        list_of_split_token_star = self.Split_by_alpha_with_star(self.fixstars(token))
        filtered_token_with_star = self.convert_list_to_string(list_of_split_token_star)
        withoutStar = filtered_token_with_star.split('*')
        list_of_split_token = self.Split_by_alpha(filtered_token_with_star)

        filtered_token = self.convert_list_to_string(list_of_split_token)
        # filtered_token = 's*1'
        bigrams_list = self.convert_token_to_bigram(filtered_token_with_star)

        return self.get_token_by_ids(bigrams_list, filtered_token_with_star)

    def getTokenSimilarSpelling(self, token,
                                jaacard_threshold,
                                distance):
        """Return a series of words similar to the query (as
               defined above).
               token – the query
               jaacard_threshold – the minimum jaacard coefficient
               of the bigrams of the word
               distance – the maximum edit distance of the words
               """
        list_of_split_token = self.Split_by_alpha(token)
        filtered_token = self.convert_list_to_string(list_of_split_token)
        tokenbigrams = self.convert_token_to_bigram(filtered_token)
        allsimilarwordslist = self.get_tokens_by_bigrams(tokenbigrams)
        wordstocheckdistance = []

        for word in allsimilarwordslist:
            if self.jaacard(filtered_token, word) >= jaacard_threshold:
                wordstocheckdistance.append(word)

        finalResult = []
        for word in wordstocheckdistance:


            if self.distanceCalculator(filtered_token, word) <= distance:
                finalResult.append(word)
        return finalResult

    def get_tokens_by_bigrams(self, list_of_bigrams):  # returns all words thar contains the received bigram from word
        tokens_list = []
        ids_list = []
        all_ids_list = []
        currr_pontier = 0
        next_pontier = 0
        minires = []

        for index in range(len(list_of_bigrams)):
            if list_of_bigrams[index] == '*$' or list_of_bigrams[index] == '$*':
                continue

            if list_of_bigrams[index][0] == '*':
                for bigram_index in range(len(self.bigrams_list)):
                    if self.bigrams_list[bigram_index][0][1] == list_of_bigrams[index][1] and self.bigrams_list[bigram_index][0][0] != '$':

                        if (bigram_index + 1 < len(self.bigrams_list)):
                            currr_pontier = int(self.bigrams_list[bigram_index][1])
                            next_pontier = int(self.bigrams_list[bigram_index + 1][1])
                        else:
                            currr_pontier = int(self.bigrams_list[bigram_index][1])
                            next_pontier = int(len(self.bigrams_ids))
                        ids_list_per_bigram = self.Split_by_alpha(self.bigrams_ids[currr_pontier: next_pontier])
                        for id in ids_list_per_bigram:
                            if id not in all_ids_list:
                                all_ids_list.append(id)
            elif list_of_bigrams[index][1] == '*':
                for bigram_index in range(len(self.bigrams_list)):

                    if self.bigrams_list[bigram_index][0][0] == list_of_bigrams[index][0] and self.bigrams_list[bigram_index][0][1] != '$' :

                        if (bigram_index + 1 < len(self.bigrams_list)):
                            currr_pontier = int(self.bigrams_list[bigram_index][1])
                            next_pontier = int(self.bigrams_list[bigram_index + 1][1])
                        else:
                            currr_pontier = int(self.bigrams_list[bigram_index][1])
                            next_pontier = int(len(self.bigrams_ids))
                        ids_list_per_bigram = self.Split_by_alpha(self.bigrams_ids[currr_pontier: next_pontier])

                        for id in ids_list_per_bigram:
                            if id not in all_ids_list:
                                all_ids_list.append(id)

            else:

                for bigram_index in range(len(self.bigrams_list)):
                    if (list_of_bigrams[index] == self.bigrams_list[bigram_index][0]):
                        if (bigram_index + 1 < len(self.bigrams_list)):
                            currr_pontier = int(self.bigrams_list[bigram_index][1])
                            next_pontier = int(self.bigrams_list[bigram_index + 1][1])
                        else:
                            currr_pontier = int(self.bigrams_list[bigram_index][1])
                            next_pontier = int(len(self.bigrams_ids))

                ids_list_per_bigram = self.Split_by_alpha(self.bigrams_ids[currr_pontier: next_pontier])


                for id in ids_list_per_bigram:
                    if id not in all_ids_list:
                        all_ids_list.append(id)




        word_list = self.get_all_tokens()  # getting all words

        for id in all_ids_list:
            tokens_list.append(word_list[int(id) - 1])  # searching along all words with id

        return tokens_list

    def jaacard(self, token, anyword):  # returns the value of the jaacard form two words using intersection and Union
        tokenBigrams = self.convert_token_to_bigram(token)
        anywordBigrams = self.convert_token_to_bigram(anyword)

        numerator = len(self.intersection(tokenBigrams, anywordBigrams))
        denominator = len(self.Union(tokenBigrams, anywordBigrams))
        return numerator / denominator

    def distanceCalculator(self, token, word):  #getting two words and then calculating the distance using dynamic programming
        s = token
        t = word
        n = len(s) + 1
        m = len(t) + 1
        if n == 0:
            return m
        elif m == 0:
            return n
        d = np.zeros([n, m])
        d[0, 0:m] = np.ogrid[0: m]
        d[0:n, 0] = np.ogrid[0: n]
        for i in range(1, n):
            for j in range(1, m):
                if s[i - 1] == t[j - 1]:
                    cost = 0
                else:
                    cost = 1

                d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + cost)
        return d[n - 1, m - 1]



    def intersection(self, lst1, lst2):# receives two lists and returns their intersection
        lst3 = [value for value in lst1 if value in lst2]
        return lst3

    def Union(self, lst1, lst2):# receives two lists and returns their union
        res = []
        for i in lst1:
            if i not in res:
                res.append(i)
        for i in lst2:
            if i not in res:
                res.append(i)
        return res

    def fixstars(self , s):
        res = ''
        toRemove = False
        for letter in s:
            if letter == '*':
                if toRemove == False:
                    toRemove = True
                    res += letter
            else:
                res += letter
                toRemove = False
        return res


    # this function get all words in dictionary
    def get_all_tokens(self):
        count_words_len = 0
        list_of_word = []
        Block_index = 0
        # this loop move on all words blocks to get all word.
        for index in range(len(self.Texts_File_Contents)):
         # this condition if they reach end of blocks
          if(Block_index < 7) :
            if index + 1 < len(self.Texts_File_Contents):

                curr_word_len = self.Texts_File_Contents[index][3]
                list_of_word.append(self.token_str[count_words_len:count_words_len + curr_word_len])
                count_words_len += self.Texts_File_Contents[index][3]
            else:
                next_block = len(self.token_str)
                list_of_word.append(self.token_str[count_words_len: next_block])
            Block_index+=1
          else:
              # this condition read other words
              if index+1 < len(self.Texts_File_Contents):
                  next_block = self.Texts_File_Contents[index + 1][0]
                  list_of_word.append(self.token_str[count_words_len : next_block])

              else:
                  next_block  = len(self.token_str)
                  list_of_word.append(self.token_str[count_words_len: next_block])
              count_words_len += next_block - count_words_len
              Block_index = 0
        return list_of_word




    def get_Token_Details(self, token , info):
        """ this function return a detalis about token, they receive toke and integer that mean:
        # if 1 =>  Return the number of reviews
        # if 2 => return pontier for texts.lst.lpv"""

        Count_Len = 0  # count words length
        Block_From_List = 0  # this variable help to move on List_of_Blocks_Index
        Position_in_Block = 0  # index
        List_of_Blocks_Index = []  # list of all blocks index
        Texts_File_Contents_Index = 0

        # this loop get all Blocks Index and fill them in list
        for Word_Details in range(len(self.Texts_File_Contents)):
            if Word_Details == len(self.Texts_File_Contents) - 1:
                List_of_Blocks_Index.append(self.Texts_File_Contents[Word_Details][0])
            if Position_in_Block == 7:
                List_of_Blocks_Index.append(self.Texts_File_Contents[Word_Details][0])
                Position_in_Block = -1
            Position_in_Block += 1
        Position_in_Block = 0

        # this loop find the token by Block Method help
        for Word_Details in self.Texts_File_Contents:
            Block_Index = Word_Details[0]

            # the last index in Texts_File_Contents list
            if (Texts_File_Contents_Index == len(self.Texts_File_Contents) - 1):
                Word_len = len(self.token_str) - (Count_Len + Block_Index)

            # index 7 is the last word in block, they don't have the word length

            elif (Position_in_Block == 7):
                Block_From_List += 1
                Word_len = List_of_Blocks_Index[Block_From_List] - (Count_Len + Block_Index)
                Position_in_Block = 0

            else:

                Word_len = Word_Details[3]
                Position_in_Block += 1


            if (self.token_str[Block_Index + Count_Len: Block_Index + Count_Len + Word_len] == token.lower()):

                if (Texts_File_Contents_Index != len(self.Texts_File_Contents) - 1):
                    return Word_Details[info] , self.Texts_File_Contents[Texts_File_Contents_Index + 1][info]
                else:
                    return Word_Details[info], len(self.Texts_lpv_Contents)




            Count_Len += Word_len
            Texts_File_Contents_Index += 1
            if (Position_in_Block == 0):
                Count_Len = 0

        return None , None


    # this function receive token and return all 2-bigrams token
    # def get_tokens_by_bigrams(self , list_of_bigrams):
    #     tokens_list = []
    #     ids_list = []
    #     all_ids_list = []
    #     currr_pontier = 0
    #     next_pontier = 0
    #     # this loop get word pointer from bigram.dic file.
    #     for index in range(len(list_of_bigrams)):
    #         for bigram_index in range(len(self.bigrams_list)):
    #             if (list_of_bigrams[index] == self.bigrams_list[bigram_index][0]):
    #                 if (bigram_index + 1 < len(self.bigrams_list)):
    #                     currr_pontier = int(self.bigrams_list[bigram_index][1])
    #                     next_pontier = int(self.bigrams_list[bigram_index + 1][1])
    #                 else:
    #                     currr_pontier = int(self.bigrams_list[bigram_index][1])
    #                     next_pontier = int(len(self.bigrams_ids))
    #         # go to bigram.lst to get ids
    #         ids_list_per_bigram = self.Split_by_alpha(self.bigrams_ids[currr_pontier: next_pontier])
    #
    #         for id in ids_list_per_bigram:
    #             if id not in all_ids_list:
    #                 all_ids_list.append(id)
    #
    #     # get the words by ids
    #     word_list = self.get_all_tokens()
    #
    #     for id in all_ids_list:
    #         tokens_list.append(word_list[int(id) - 1])
    #
    #     return tokens_list

    # this function receive token and list of bigrams, then get all word have same bigrams and do post process on this words.
    def  get_token_by_ids(self , list_of_bigrams , token):

        filtered_tokens_list = []
        # get words with same bigrams
        tokens_list = self.get_tokens_by_bigrams(list_of_bigrams)

        index_token = 0
        index_str = 0
        bool = True

     # this loop do post process
        for str in tokens_list:

            while True:

                if index_token >= len(token) and index_str < len(str) or (index_token < len(token) and index_str >= len(str)):
                    bool = False
                    break

                if index_str >= len(str)and  index_token >= len(token):
                    break

                if (str[index_str] == token[index_token] ):

                      index_str += 1
                      index_token+=1
                elif (token[index_token] != '*' and str[index_str] != token[index_token]):
                    bool = False
                    break
                elif (str[index_str] != '*' and token[index_token]== '*' ):

                    while index_token + 1 < len(token) and token[index_token + 1] == '*':
                            index_token += 1
                    index_str += 1
                    index_token += 1
                    if index_token >= len(token) and index_str <len(str):
                       break

                    while index_str < len(str) and  index_token < len(token):
                        if str[index_str] == token[index_token] :
                            if index_token+1 == len(token) or token[index_token+1] != '*' :
                               while token[index_token : ] in str[index_str + 1:]:
                                 index_str = index_str + str[index_str + 1:].find(token[index_token: ])+1

                            break
                        elif(str[index_str] != token[index_token]):
                            index_str += 1

            if bool :
              filtered_tokens_list.append(str)
            index_token = 0
            index_str = 0
            bool = True


        return filtered_tokens_list



     # this function convert list to string
    def convert_list_to_string(self , list_of_split_token):
        filtered_token =''
        for index in list_of_split_token:
            filtered_token += index
        return filtered_token


   # this function get all 2-bigrams for token they receive
    def convert_token_to_bigram(self, token):
        list_of_bigrams = []
        last_index = 2
        bigram = '$'
        bigram += token[0: 1]
        list_of_bigrams.append(bigram)

        for first_index in range(len(token)-1):
            bigram = ''
            bigram += token[first_index : last_index]
            list_of_bigrams.append(bigram)
            last_index+=1
        if(len(token) >= 1):
           list_of_bigrams.append(token[len(token)-1 : ] + '$')
        return list_of_bigrams
    # def organizeStarAndConverting(self,token):
    #     splittedToken = token.split("*")

    def existIn(self, name, productsDicArray):     # checks if an element exist in the array and returns its index
        index = 0
        for product in productsDicArray:
            if name in product:
                return index
            index += 1
        return -1
   # this function splite the sentnce to words have just alpha and number
    def Split_by_alpha(self, string_splite):
        pos = 0
        list = []

        while pos < len(string_splite):
            if string_splite[pos].isalpha() or string_splite[pos].isnumeric():

                pos += 1
                if (pos == 20):
                    str = string_splite[:pos]
                    if str != "":
                        list.append(str)
                    string_splite = string_splite[pos + 1:]
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

    # this function splite the sentnce to words have just alpha and numbers and star
    def Split_by_alpha_with_star(self, string_splite):
        pos = 0
        list = []

        while pos < len(string_splite):
            if string_splite[pos].isalpha() or string_splite[pos].isnumeric() or string_splite[pos] == '*':

                pos += 1
                if (pos == 20):
                    str = string_splite[:pos]
                    if str != "":
                        list.append(str)
                    string_splite = string_splite[pos + 1:]
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

    def unlpcfornumber(self, string):
        result = 0
        s = int(string[:2], 2) + 1

        number = '00' + string[2:]

        result = int(number[:8 * s], 2)
        return result

    def unlpv(self, array):
        res = []
        for number in array:
            bytes = 0
            temp = number
            while int(temp / 256) > 0:
                bytes += 1
                temp = int(temp / 256)
            if temp % 256 > 0:
                bytes += 1
            s = '{:0' + str(bytes * 8) + 'b}'

            s = s.format(int(number))
            res.append(self.unlpcfornumber(s))

        return res

    def readingAndCompressingForLvp(self, Array):
        res = []
        s = ''
        length = 0
        for i in range(len(Array)):
            if length > 0:
                length -= 1
            else:
                s = '{:08b}'.format(Array[i])
                length = int(s[:2], 2)
                for j in range(length):
                    s = s + '{:08b}'.format(Array[i + j + 1])
                res.append(int(s, 2))
        return res

    def Read_From_Files(self, dir, type):
        File_Path = os.path.join(dir, type)

        if type == "collection.data":
            File = open(File_Path, 'r')
            self.collections_data.append(File.readline().replace(" ", "").replace("\n", ""))
            self.collections_data.append(File.readline().replace(" ", "").replace("\n", ""))

        if type == "reviews.tbl":

           File = open(File_Path , 'r')
           File.readline()
           File.readline()

           while True:
             line = File.readline()
             if not line:
                 break
             list_row = self.Split_by_alpha(line)
             if type == "reviews.tbl":
                 self.reviews_dic.append(list_row)

        if type == "texts.dic.tbl":
            File_Path_Token = os.path.join(dir, "texts.dic.str")
            File = open(File_Path_Token, "r")
            self.token_str = File.read()


            File =  open(File_Path, "rb")
            size_block_in_Binary = format(len(self.token_str), 'b')
            Size_per_Block_pointer = self.howManyBytesInStrBinary(len(size_block_in_Binary))
            i = 0
            Pointer_Block = 0

            while True:

                if (i  == 8 or i == 0):
                   Pointer_Block_byte = File.read(Size_per_Block_pointer)
                   if not Pointer_Block_byte:
                       break
                   Pointer_Block = int.from_bytes(Pointer_Block_byte, "big")

                   i= 0
                Frequncy = int.from_bytes( File.read(4), "big")
                Pionter_To_Token_Str = int.from_bytes(File.read(4), "big")

                if (i < 7 ):
                    Token_Len_Byte = File.read(1)
                    if not Token_Len_Byte:
                        self.Texts_File_Contents.append([Pointer_Block, Frequncy, Pionter_To_Token_Str])
                        break
                    Token_Len = int.from_bytes(Token_Len_Byte, "big")
                    self.Texts_File_Contents.append([Pointer_Block, Frequncy, Pionter_To_Token_Str, Token_Len])
                else:
                    self.Texts_File_Contents.append([Pointer_Block, Frequncy, Pionter_To_Token_Str])

                i+=1

        if type == "texts.lst.lpv" :
                File = open(File_Path, "rb")
                self.Texts_lpv_Contents = File.read()

        if type == 'products.lst.vrnt':
             File = open(File_Path, "rb")
             self.products_lst_vrnt_str = File.read()



        if type == "products.dic.fxd":
            File = open(File_Path, "rb")

            while True:
                 List = []
                 read_product = File.read(10).decode('ascii')
                 if not read_product :
                     break
                 List.append(read_product)
                 List.append(int.from_bytes( File.read(4), "big"))
                 List.append(int.from_bytes(File.read(4), "big"))
                 self.products_dic_fxd.append(List)

        if type == "bigram.dic":
            File = open(File_Path, "r")
            while True:
                line = File.readline()
                if not line:
                    break

                filtered_line = line.split()
                self.bigrams_list.append(filtered_line)

        if type == "bigram.lst":
            File = open(File_Path, "r")
            self.bigrams_ids = File.read()




    def ungappingForLpv(self, Array):
        res = []
        ungaps = []
        for i in range(len(Array)):
            if i % 2 == 0:
                ungaps.append(Array[i])
        ungaps = self.ungaping(ungaps)
        for i in range(len(Array)):
            if i % 2 == 0:
                res.append(ungaps[int(i / 2)])
            else:
                res.append(Array[i])
        return res

    def ungaping(self, Array):
        res = [Array[0]]
        for i in range(1, len(Array)):
            res.append(Array[i] + res[i - 1])
        return res

    def howManyBytesInStrBinary(self, number):
        bytes = 0
        temp = number
        if (temp < 8):
            return 1
        while temp > 0:
            bytes += 1
            temp = temp - 8

        return bytes
    def howManyBytes(self, number):
        bytes = 0
        temp = number
        while int(temp / 256) > 0:
            bytes += 1
            temp = temp / 256

        if temp % 256:
            bytes += 1
        return bytes



    def myunvariant(self, numbersArray):  # array of numbers
        result = []
        for num in numbersArray:
            s = '{:0'
            s += str(self.howManyBytes(num) * 8)
            s += 'b}'
            number = s.format(num)
            if len(number) < 8 or len(number) % 8 != 0:

                return -1
            bytes = []
            for i in range(int(len(number) / 8)):
                bytes.append(number[i * 8: (i + 1) * 8])

            res = ''
            for i in bytes:
                res += i[1:]
            result.append(int(res, 2))
        return result

    def readingAndCompressingForVariant(self, Array):
        res = []
        length = 0
        for i in range(len(Array)):
            if length > 0:
                length -= 1
            else:
                if Array[i] >= 128:
                    res.append(Array[i])
                else:
                    s = ''
                    while (Array[i] < 128):
                        s += '{:08b}'.format(Array[i])
                        i += 1
                        length += 1
                    s += '{:08b}'.format(Array[i])
                    res.append(int(s, 2))
        return res



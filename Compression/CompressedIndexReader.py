import os.path
from IndexReader import IndexReader

class CompressedIndexReader:
    reviews_dic = []
    token_str = None
    collections_data = []
    Texts_File_Contents = []
    products_dic_fxd = []
    Texts_lpv_Contents = None
    products_lst_vrnt_str = None

    def __init__(self, dir):
        """Creates a CompressedIndexReader object which will
        read from the given directory
        dir is the path of the directory that contains the
        index files"""
        files = {"reviews.tbl" ,  "collection.data" , "texts.dic.tbl", "texts.lst.lpv" , "products.dic.fxd" , 'products.lst.vrnt'}

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
        # print( "pointeeeeeeeer" , list(self.Texts_lpv_Contents[Pointer_cur : pointer_next]) )
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
        # print( "pointeeeeeeeer" , list(self.Texts_lpv_Contents[Pointer_cur : pointer_next]) )
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



    def existIn(self, name, productsDicArray):     # checks if an element exist in the array and returns its index
        index = 0
        for product in productsDicArray:
            if name in product:
                return index
            index += 1
        return -1

    def Splite_by_alpha(self, string_splite):
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

    def unlpcfornumber(self, string):
        result = 0
        s = int(string[:2], 2) + 1
        # print(s)
        number = '00' + string[2:]
        # print(number)
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
             list_row = self.Splite_by_alpha(line)
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
                # print(len(number), len(number) % 8)
                return -1
            bytes = []
            for i in range(int(len(number) / 8)):
                bytes.append(number[i * 8: (i + 1) * 8])
            # print(bytes)
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
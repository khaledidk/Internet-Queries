import os.path


class IndexReader:
    reviews_dic = []
    words_dic = []
    token_dic = None
    collections_data = []
    product_dic = []


    def __init__(self, dir):
        """Creates a FirstIndexReader object which will read
        from the given directory
        dir is the path of the directory that contains the
        index files"""
        files = {"reviews.tbl", "texts.dic", "texts.lst", "products.dic","collection.data"}
        for file in files:
            self.Read_and_split(dir, file)



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

        for ele in self.words_dic:

            if str(ele[0]) == str(token).lower():
                return int(ele[1])

        return 0

    def getTokenCollectionFrequency(self, token):
        """Return the number of times that a given token
        (i.e., word) appears in
        the reviews indexed
        Returns 0 if there are no reviews containing this
        token"""
        index_before = 0
        index_after = 0
        sum_Frequency = 0
        for ele in range(len(self.words_dic)):
            if self.words_dic[ele][0] == str(token).lower() and ele == len(self.words_dic) - 1:
                index_before = int(self.words_dic[ele][2])
                index_after = int(len(self.token_dic))
                break

            if self.words_dic[ele][0] == str(token).lower():
                index_before = int(self.words_dic[ele][2])
                index_after = int(self.words_dic[ele + 1][2])
                break
        str_before = self.token_dic[index_before: index_after]
        str_after = self.Splite_by_alpha(str_before)

        for i in range(len(str_after)):

            if not int(i) % 2 == 0:
                sum_Frequency += int(str_after[i])

        return sum_Frequency

    def getReviewsWithToken(self, token):
        """Returns a series of integers of the form id-1,
        freq-1, id-2, freq-2, ... such
        that id-n is the n-th review containing the given
        token and freq-n is the
        number of times that the token appears in review idn
        Note that the integers should be sorted by id
        Returns an empty Tuple if there are no reviews
        containing this token"""
        index_before = 0
        index_after = 0
        reviewsArray = []
        for ele in range(len(self.words_dic)):


            if self.words_dic[ele][0] == str(token).lower() and ele == len(self.words_dic)-1:
                index_before = int(self.words_dic[ele][2])
                index_after = int(len(self.token_dic))
                break

            if self.words_dic[ele][0] == str(token).lower():
                index_before = int(self.words_dic[ele][2])
                index_after = int(self.words_dic[ele + 1][2])
                break
        str_before = self.token_dic[index_before: index_after]
        str_after = self.Splite_by_alpha(str_before)

        if len(str_after) == 0:
            return ()
        for ele in str_after:
          reviewsArray.append(int(ele))
        return tuple(reviewsArray)


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
        result = []
        for i in self.reviews_dic:
            if i[1] == productId:
                result.append(int(i[0]))

        return tuple(result)

    def existIn(self, name, productsDicArray):
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

    def Read_and_split(self, dir, type):
        filePath_reviews = os.path.join(dir, type)
        file_reviews = open(filePath_reviews)
        if type == "texts.lst":
            self.token_dic = file_reviews.readline()
        if type == "collection.data":
            self.collections_data.append(file_reviews.readline().replace(" ", "").replace("\n", ""))
            self.collections_data.append(file_reviews.readline().replace(" ", "").replace("\n", ""))
        file_reviews.readline()
        file_reviews.readline()

        while True:

            line = file_reviews.readline()
            if not line:
                break
            list_row = self.Splite_by_alpha(line)
            if type == "reviews.tbl":
                self.reviews_dic.append(list_row)
            elif type == "texts.dic":
                self.words_dic.append(list_row)
            elif type == "products.dic":
                self.product_dic.append(list_row)

        file_reviews.close()

import os
import shutil

from IndexReader import IndexReader


class CompressedIndexWriter:
    read = None

    def __init__(self, in_dir, out_dir):
        """Given uncompressed product review data, creates
        an on disk compressed index
        in_dir is the path of the directory where the
        uncompressed files are
        out_dir is the path of the directory in which the
        compressed files will be created
        if the out directory does not exist, it should be
        created"""
        if not os.path.isdir(in_dir):
            print("error: invalid directory path")
            exit(-1)
        if not os.path.isdir(out_dir):
            print("creating directory")
            os.makedirs(out_dir)
        else:
            print("directory already created")
        read = IndexReader(in_dir)

        files = {"reviews.tbl", "products.dic.fxd", "texts.dic.str", "collection.data"}

        for file in files:  # this loop will open files and write the information by calling write_to_Indexfile() function
            self.startFile(out_dir, in_dir, file, read)

    def remove(self, dir):
        """Delete all index files by removing the given
        directory
        dir is the path of the directory to be deleted"""

        if os.path.isdir(dir):
            # remove directory and all its content

            shutil.rmtree(dir)
        else:
            print("Error: Path {} is not a file or dir.".format(dir))

    def startFile(self, Out_Dir, In_Dir, file, data):  # starting all files

        if file == "reviews.tbl":  # write to reviews.tbl file
            Path_Out_Dir = os.path.join(Out_Dir, file)
            Path_In_Dir = os.path.join(In_Dir, file)
            f = open(Path_Out_Dir, "w")
            shutil.copyfile(Path_In_Dir, Path_Out_Dir)
            f.close()

        if file == "collection.data":  # write to collection.data file
            Path_Out_Dir = os.path.join(Out_Dir, file)
            Path_In_Dir = os.path.join(In_Dir, file)
            f = open(Path_Out_Dir, "w")
            shutil.copyfile(Path_In_Dir, Path_Out_Dir)
            f.close()

        """write the all words by using one string  to texts.dic.str"""
        if file == "texts.dic.str":
            resultToWrite2 = []
            textStrSize = 0
            file = os.path.join(Out_Dir, file)

            f = open(file, "w")
            for i in range(len(data.words_dic)):  # getting data structure resultToWrite2 ready to write to other files
                f.write(data.words_dic[i][0])  # writing data to text.dic.str file
                textStrSize += len(data.words_dic[i][0])  # (1 , 7, 5 , 9 , 64 , 64)
                '''resultToWrite2 [[word, word length,[calculated gaps (reviewswithtoken)], lpvc result, result size in bytes]]'''  # data structure description
                resultToWrite2.append([data.words_dic[i][0], len(data.words_dic[i][0]), self.calculateGapsForlvp(
                    list(data.getReviewsWithToken(data.words_dic[i][0]))), self.lpvCode(
                    self.calculateGapsForlvp(list(data.getReviewsWithToken(data.words_dic[i][0]))))])
                bytes = 0
                for n in resultToWrite2[i][3]:
                    bytes += self.howManyBytes(n)
                resultToWrite2[i].append(bytes)
            # print("resultToWrite2 :", resultToWrite2)
            f.close()

            """write the list gaps (id's) to texts.dic.tbl file"""
            file = "texts.dic.tbl"
            file = os.path.join(Out_Dir, file)
            f = open(file, "wb")
            place = 0
            Block_index = 0
            count_tokens = 0
            size_block_in_Binary = format(textStrSize, 'b')  # organizing data for blocking
            Size_per_Block_pointer = self.howManyBytesInStrBinary(len(size_block_in_Binary))
            # print("size : " , Size_per_Block_pointer)
            for i in range(len(resultToWrite2)):  # start writing with blocking method
                if count_tokens == 8 or i == 0:
                    f.write(bytearray(self.divideIntToShortSpecific(Block_index, Size_per_Block_pointer)))
                    count_tokens = 0
                f.write(bytearray(self.divideIntToShort(data.getTokenFrequency(resultToWrite2[i][0]))))
                f.write((bytearray(self.divideIntToShort(place))))
                if count_tokens < 7 and i != len(resultToWrite2) - 1:  # checking if its the last word in block
                    f.write((bytearray(self.divideIntToShortSpecific(resultToWrite2[i][1], 1))))
                Block_index += resultToWrite2[i][1]
                place += resultToWrite2[i][4]
                count_tokens += 1
            f.close()  # closing file

            """write the list gaps (id , frequency) to text.lst.lpv file"""
            file = "texts.lst.lpv"
            file = os.path.join(Out_Dir, file)
            f = open(file, "wb")
            for i in range(len(resultToWrite2)):  # writing to lpv file
                for n in resultToWrite2[i][3]:
                    f.write(bytearray(self.divideIntToShortSpecific(n, self.howManyBytes(n))))  # start writing
            f.close()

        elif file == "products.dic.fxd":  # starting file products.dic.fxd
            file = os.path.join(Out_Dir, file)
            uniqueProducts = []
            resultToWrite = []
            for i in range(len(data.product_dic)):  # starting data structure resultToWrite
                if data.existIn(data.product_dic[i][0], uniqueProducts) < 0:
                    uniqueProducts.append(data.product_dic[i][0])
                    resultToWrite.append([data.product_dic[i][0]])

            f = open(file, "wb")
            place = 0
            ''' resultToWrite = [[productID, [list with reviews id for the product], how many reviews for the product, variantcode for reviews list for the product]'''
            for i in range(
                    len(resultToWrite)):  # filling data to resultToWrite data structure in order to use it to write in vriant file
                resultToWrite[i].append(list(data.getProductReviews(resultToWrite[i][0])))
                resultToWrite[i].append(len(list(data.getProductReviews(resultToWrite[i][0]))))
                resultToWrite[i].append('')
                variant = self.variantCode(self.calculateGaps(list(data.getProductReviews(resultToWrite[i][0]))))
                resultToWrite[i][3] = (str(variant)).replace("[", "").replace("]", "").replace(" ", "").replace(",",
                                                                                                                "").replace(
                    "'", "")
                f.write(bytearray(self.fillNameWithNull(resultToWrite[i][0], 10), 'ascii'))  # writing to fixed file
                f.write(bytearray(self.divideIntToShort(resultToWrite[i][2])))
                f.write(bytearray(self.divideIntToShort(place)))
                place += self.howManyBytesInStrBinary(len(resultToWrite[i][3]))
            f.close()
            """write the list gaps (id's) to products.lst.vrnt file"""
            file = "products.lst.vrnt"
            file = os.path.join(Out_Dir, file)
            f = open(file, "wb")
            res = ''
            for i in range(len(resultToWrite)):
                res += resultToWrite[i][3]

            f.write(bytearray(self.variantValueToNumber(res)))
            f.close()

    def fillNameWithNull(self, name, length):  # filling product ids with null or '\0' til it reach length
        res = name
        if len(name) <= length:
            for i in range(len(name), length):
                res = res + b'\x00'.decode()
            return res
        else:
            return res[:length]

    def divideIntToShortSpecific(self, number,
                                 short):  # divide number into bytes so it can be written in bytearray() function example 256 = [1, 0], 255 = [0]
        result = []
        for i in range(short):
            right = number % 256
            number = int(number / 256)
            result.append(right)
        return result[::-1]

    def howManyBytes(self, number):  # calculating how many bytes the number needs to be written
        bytes = 0
        temp = number
        while int(temp / 256) > 0:
            bytes += 1
            temp = temp / 256

        if temp % 256:
            bytes += 1
        return bytes

    def unlpcfornumber(self, string):  # decoding number that written in length preceded variant to normal number
        result = 0
        s = int(string[:2], 2) + 1
        # print(s)
        number = '00' + string[2:]
        # print(number)
        result = int(number[:8 * s], 2)
        return result

    def unlpv(self,
              array):  # decoding array of numbers tha been written in length preceded variant to normal array of numbers
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

    def lpvCode(self, array):  # encoding array of numbers into array of length preceded variant numbers
        res = []
        for number in array:
            res.append(self.numToLvp(number))
        return res

    def zerosString(self, num):  # creating string of zeros with length of num
        s = ''
        for i in range(num):
            s += '0'
        return s

    def numToLvp(self, number):  # encoding normal number into length preceded variant number

        s = '00' + bin(number)[2:]
        if len(s) <= 8:
            return int(s, 2)
        elif len(s) <= 16:
            return int(('01' + self.zerosString(14 - (len(s[2:]))) + s[2:]), 2)
        elif len(s) <= 24:
            return int(('10' + self.zerosString(22 - (len(s[2:]))) + s[2:]), 2)
        elif len(s) <= 32:
            return int(('11' + self.zerosString(30 - (len(s[2:]))) + s[2:]), 2)

    def calculateGapsForlvp(self,
                            Array):  # calculates review ids gaps example => (1, 2, 5, 5, 12, 8) = (1, 2, 4, 5, 7, 8)
        gapping = []
        for i in range(len(Array)):
            if i % 2 == 0:
                gapping.append(Array[i])
        gapping = self.calculateGaps(gapping)
        for i in range(len(Array)):
            if i % 2 != 0:
                gapping.insert(i, Array[i])
        return gapping

    def calculateGaps(self, array):  # calculates gaps example => (1, 3, 5, 12, 22) = (1, 2, 2, 7, 10)
        res = []
        res.append(array[0])
        for i in range(len(array) - 1):
            res.append(array[i + 1] - array[i])
        return res

    def variantValueToNumber(self, string):  # decoding variant number into normal number
        res = []
        for i in range(int(len(string) / 8)):
            res.append(int(string[i * 8:(i + 1) * 8], 2))
        return res

    def divideIntToShort(self,
                         number):  # writing number to binary array with length of 4 bytes example 256 = [0,0,1,0], 255 = [0,0,0,255]
        result = []
        for i in range(4):
            right = number % 256
            number = int(number / 256)
            result.append(right)
        return result[::-1]

    def variantCodeForNumber(self, number):  # normal number into variant string number 16 = 1010000
        bytes = ''
        while True:
            bytes = (str('{:08b}'.format(int(number % 128)))) + bytes
            if number < 128:
                break
            number = number / 128
        return bytes[:len(bytes) - 8] + '1' + bytes[len(bytes) - 7:]

    def variantCode(self, numbersArray):  # encoding array of numbers into array of variant method numbers
        res = []
        for i in range(len(numbersArray)):
            res.append(self.variantCodeForNumber(numbersArray[i]))
        return res

    def howManyBytesInStrBinary(self, number):  # calculating how many bytes the number needs to be written
        bytes = 0
        temp = number
        if (temp < 8):
            return 1
        while temp > 0:
            bytes += 1
            temp = temp - 8

        return bytes

    def myunvariant(self, numbersArray):  # decoding array of variant numbers into array of normal numbers
        result = []
        for number in numbersArray:
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


# def countSize(howManyRev):
#     print("(int({}/8))*((9*8-1)+2) =".format(howManyRev), (int(howManyRev / 8)) * ((9 * 8 - 1) + 2))

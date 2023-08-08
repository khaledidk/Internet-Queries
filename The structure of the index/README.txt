Students :
Name: Khaled Idkedik ID: 207395153
Name: Salah Aldin Jawabreh ID: 086958006

Internet queries course Students

1st Exercise : The structure of the index

this ZIP file contains :
--IndexWriter.py :exercise requirment code for writing from reviews storage to seperated text files (products.lst/dic, text.lst/dic, review.tbl/ collection.data)
--IndexReader.py :exercise requirment code for reading from created dictionaries from IndexWriter.py class 
--readme file :which is this file


extra function we used:
IndexWriter.py
def write_to_Indexfile(self,Dictionary  , indexFile, type , save_lst_file ): receive Dictioanry: data structures have reviews information, indexfile : file what to write to  , type : which file want to write to , dir : directory of file
the function write to each index file the information they we want to be for this file """
def read_from_file(self , inputFile):opens the inputFile the read all details about reviews, then fill the details in Dictionary
        then return it"""
def count_word_in_reviews(self ,Dictionary , word):runs along the data structure and counts how many words were exist and how many times

IndexWriter.py + IndexReader.py
def existIn(self, name, productsDicArray):receives an array and and object and returns the index of the object in the array if exist, else it returns -1
def Splite_by_alpha(self, string_splite): split given string into only words and numbers
def Read_and_split(self, dir, type):reads from different files and saves data into data structures
def count_occurrence(self , words, word_to_count):counts how many times the word are exist

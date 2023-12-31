/*
fastunpack.c
************

:author: Aleph Fell <habisain@gmail.com>
:copyright: 2012-2015
:license: GNU Public License version 3

Quick unpackData function written in C. This should
be interesting, especially as it should enable removal
of multiprocessing from unpackers in favor of threading
(as C Extensions release GIL)
*/

void unpackData(unsigned int key, unsigned int len, unsigned char * data); # DEF

void unpackData(unsigned int key, unsigned int len, unsigned char * data){
  int count;
  unsigned int* idata = (unsigned int*) data;
  for (count = 0; count < len; count++){
      idata[count] = idata[count] ^ key;
      key = (key * 7 + 3) & 0xFFFFFFFF;
  }
}

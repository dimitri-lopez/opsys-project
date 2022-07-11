#!/usr/bin/env python3

# Implementing the random bit generators needed. These are pulled from the man pages.
# The following excerpts explain how srand48 and drand48. See below:



# All the functions work by generating a sequence of 48-bit integers, Xi,
# according to the linear congruential formula:
#
#     Xn+1 = (aXn + c) mod m, where n >= 0
#
# The  parameter  m = 2^48, hence 48-bit integer arithmetic is performed.
# Unless lcong48() is called, a and c are given by:
#
#     a = 0x5DEECE66D
#     c = 0xB
#
# The value returned  by  any  of  the  functions  drand48(),  erand48(),
# lrand48(), nrand48(), mrand48(), or jrand48() is computed by first gen‐
# erating the next 48-bit Xi in the sequence.  Then the appropriate  num‐
# ber  of  bits,  according  to  the type of data item to be returned, is
# copied from the high-order bits of Xi and transformed into the returned
# value.
#
# The functions drand48(), lrand48(), and mrand48() store the last 48-bit
# Xi  generated  in  an  internal  buffer.   The   functions   erand48(),
# nrand48(), and jrand48() require the calling program to provide storage
# for the successive Xi values in the array argument  xsubi.   The  func‐
# tions are initialized by placing the initial value of Xi into the array
# before calling the function for the first time.
#  asd
# The initializer function srand48() sets the high order 32-bits of Xi to
# the  argument  seedval.  The low order 16-bits are set to the arbitrary
# value 0x330E.



# Generate a new 48bits
def drand48():
    try: Xn
    except: raise Exception("srand48() must be called before drand48() is used.")
    a = 0x5DEECE66D # from man pages
    c = 0xB         # from man pages
    m = 2**48       # The  parameter  m = 2^48, hence 48-bit integer arithmetic is performed.

    # Xn+1 = (aXn + c) mod m, where n >= 0
    Xn1 = ((a * Xn) + c) % m

    Xn = Xn1
    return Xn1

# Seed the random number generator
def srand48(seedval):
    # The initializer function srand48() sets the high order 32-bits of Xi to
    # the  argument  seedval.  The low order 16-bits are set to the arbitrary
    # value 0x330E.

    # bin(0x330E) = 0b11001100001110
    # bin(0x330E)[2:] = 11001100001110
    highorder = bin(seedval)[2:]
    loworder = bin(0x330E)[2:]
    global Xn
    Xn = int(highorder + loworder)

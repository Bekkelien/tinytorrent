
# PI last piece size = (354404132%131072)%2**14 -> 1828
# GIMP last piece size = (265283496%262144)%2**14 -> 10152

import math

size = 265283496
piece_length = 262144
block_size = 2**14

print((size%piece_length)%block_size)

print(265283496%262144)

blocks = math.ceil(piece_length / block_size)

print("Blocks:", blocks)

print("size per block:", block_size)

print((piece_length)*1013)
print((piece_length)*1012)

print(size-(piece_length)*1011)


print(math.ceil((size-(piece_length)*1011) / block_size))




  # PI last piece size = (354404132%131072)%2**14 -> 1828
                    # GIMP last piece size = (265283496%262144)%2**14 -> 10152
size = 265283496
piece_length = 262144

print((size%piece_length)%2**14)

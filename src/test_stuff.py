test = "sdklgndsgsdlkg http"

if any(x in test for x in ['http', 'https']):

    print("OK")



# ADD TO TESTS?:
# THIS IS WRONG BUG: SHOULD BE: urlencode
from urllib import parse
info_hash = b'\x12\x34\x56\x78\x9a\xbc\xde\xf1\x23\x45\x67\x89\xab\xcd\xef\x12\x34\x56\x78\x9a'
print(parse.quote(info_hash))
print("%124Vx%9A%BC%DE%F1%23Eg%89%AB%CD%EF%124Vx%9A")

assert(info_hash != "%124Vx%9A%BC%DE%F1%23Eg%89%AB%CD%EF%124Vx%9A")


test = [b'']
print(len(test))
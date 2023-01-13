import urllib.parse



test =  "magnet:?xt=urn:btih:7fb62bc4f6fc6ff70a322085fd73787b5e016e73&dn=lubuntu-16.04.3-desktop-i386.iso"

if __name__ == '__main__':

    parsed = urllib.parse.urlparse(test)
    print(parsed)
    key_values = urllib.parse.parse_qs(parsed.query)
    print(key_values)
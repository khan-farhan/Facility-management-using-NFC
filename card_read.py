import nfc
import time


def after5s(started):

    return time.time() - started > 5


def read():

    clf = nfc.ContactlessFrontend('usb')

    def after5s(): return time.time() - started > 5
    started = time.time()

    tag = clf.connect(rdwr={'on-connect': lambda tag: False}, terminate=after5s)

    tag = str(tag)

    tag = tag.split(" ")[-1]

    return tag[3:-1]


if __name__ == '__main__':

    tag = read()
    print (tag)

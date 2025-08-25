import base64
import os
import datetime


def generator_hash(length=8):
    start = datetime.datetime.now()
    with open('hash.txt', 'w') as file:
        for i in range(10 ** 10):
            random_bytes = os.urandom(10)
            coded_bytes = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
            coded_bytes.replace('=', '')

            file.write(f"{coded_bytes[:length]}\n")
        file.close()
    finish = datetime.datetime.now()
    print(str(finish-start))


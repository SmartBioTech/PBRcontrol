import socket

from Crypto.Cipher import AES


PAD_CHAR = ' '
DELIMITER = ';'
ESCAPE_CHAR = '\\'


def remote_control(host_address, host_port, encryption_key, command, timeout=10):
    unescaped = DELIMITER
    escaped = ESCAPE_CHAR + DELIMITER
    while len(encryption_key.encode("utf8")) < 16:
        encryption_key += ' '
    secret_key = encryption_key.encode("utf8")[:16]
    encrypter = AES.new(secret_key, AES.MODE_ECB)
    decrypter = AES.new(secret_key, AES.MODE_ECB)
    empty_block = (PAD_CHAR * 16).encode("utf8")
    result = []
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host_address, host_port))

        com_msg = command.replace(unescaped, escaped) + DELIMITER
        data = com_msg.encode("utf8") + empty_block
        while len(data) % 16 != 0:
            data += empty_block[0:1]
        cipher_text = encrypter.encrypt(data)
        sock.send(cipher_text)
        recv_buffer = ""
        packet = decrypter.decrypt(sock.recv(4096)).decode("utf-8")

        for c in packet:
            if c == DELIMITER and (len(recv_buffer) == 0 or recv_buffer[-1] != ESCAPE_CHAR):
                result.append(recv_buffer.replace(escaped, unescaped))
                recv_buffer = ""
            else:
                recv_buffer += c
        sock.close()
    except socket.timeout:
        print("Warning: socket timed out")
    return result


# command = "Demo1->flashLED()"
#
# # ["Demo1->flashLED()", "Demo1->logCustomData(mydata, 1.3, units)", "Demo1->setAux1(1)",
# # "Demo1->measurePH()", "Demo1->measureTemperature()"]
# key_code = 't2ih72c0husyrayh'
# response = remote_control(host_address='localhost', host_port=6161,
#                                encryption_key=key_code, command=command, timeout=10)
#
# print('sent command:', command, ' got response:', response)

# import
import socket
import config  # setting for this project
from contextlib import closing


# list for the student that have already vote
stu_id_list = []

# load the vote history
try:
    f = open('./list.txt', 'r')
    for line in f:
        stu_id_list.append(line)
except Exception as e:
    print('read file error')
    f.close()
    exit()
else:
    print('load file done\n')

# build socket
with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as connection:
    # Connect to the card reader
    connection.connect(config.ADDRESS)

    # Clear all card reader history
    cmd = config.CMD_CLEAR_ALL
    connection.send(bytes(cmd))

    while True:
        # read the list record
        cmd = config.CMD_READ_LAST
        connection.send(bytes(cmd))

        # get reading list record result
        return_value_byte = connection.recv(config.BUFFER_SIZE)
        return_value_hex = [hex(byte) for byte in return_value_byte]

        # check if that is a card id or not
        if return_value_hex[1] == '0x1d':
            # change card id from hex to dex
            return_value_dec = [int(hex_string, 0) for hex_string in return_value_hex]

            # format card id (length have to be 5)
            card_id_site = str(return_value_dec[19] * 256 + return_value_dec[20])
            card_id_card = str(return_value_dec[23] * 256 + return_value_dec[24])
            for card_id_part in [card_id_site, card_id_card]:
                not_enough_len = 5 - len(card_id_site)
                if not not_enough_len:
                    for index in range(0, not_enough_len):
                        card_id_part = '0{0}'.format(card_id_part)

                card_id += card_id_part

            # print the card id that get this time
            # print(card_id)

            # if the card id have not vote write into list.txt
            if card_id not in stu_id_list:
                stu_id_list.append(card_id)
                with open('./list.txt', 'a') as stu_id_list_file:
                    stu_id_list_file.write('{0}\n'.format(card_id))

                print('{0} have not vote before'.format(card_id))
            else:
                print('{0} have already vote before'.format(card_id))

            # clear the record
            card_id = ''
            cmd = config.CMD_CLEAR_LAST
            connection.send(bytes(cmd))

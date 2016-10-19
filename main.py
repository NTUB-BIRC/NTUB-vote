# import
import socket
import config  # setting for this project
from contextlib import closing


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
            print(card_id)

            # clear the record
            card_id = ''
            cmd = config.CMD_CLEAR_LAST
            connection.send(bytes(cmd))

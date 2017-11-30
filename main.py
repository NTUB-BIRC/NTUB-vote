# import
import socket
import config  # setting for this project
from contextlib import closing
from gui import VoteGUI
import traceback
import time


# globel
stu_id_list = []  # list for the student that have already vote
last_stu_id = None
counter = 0
vote_gui = VoteGUI()


# load the vote history
def load_file():
    try:
        f = open('./list.txt', 'r')
        for line in f:
            stu_id_list.append(line.replace('\n', ''))
    except Exception as e:
        print('read file error')
        return False
    else:
        print('load file done\n')
        return True
    finally:
        f.close()


# parse the return hex value and print the card id out
# if the id haven't vote before write it to file
def card_id_process(return_value_hex):
    global last_stu_id
    global counter

    # initial
    card_id = ''

    # change card id from hex to dex
    return_value_dec = [int(hex_string, 0) for hex_string in return_value_hex]

    # format card id (length have to be 5)
    card_id_site = str(return_value_dec[19] * 256 + return_value_dec[20])
    card_id_card = str(return_value_dec[23] * 256 + return_value_dec[24])
    for card_id_part in [card_id_site, card_id_card]:
        not_enough_len = 5 - len(card_id_part)
        if not_enough_len:
            for index in range(0, not_enough_len):
                card_id_part = '0{0}'.format(card_id_part)

        card_id += card_id_part

    if last_stu_id == card_id:
        return

    counter = 0
    last_stu_id = card_id

    # if the card id have not vote write into list.txt
    if card_id not in stu_id_list:
        stu_id_list.append(card_id)
        with open('./list.txt', 'a') as stu_id_list_file:
            stu_id_list_file.write('{0}\n'.format(card_id))

        print('{0} have not vote before'.format(card_id))
        vote_gui.change_text('歡迎 {} 投票～'.format(card_id))  # set gui lable text
    else:
        print('{0} have already vote before'.format(card_id))
        vote_gui.change_text('{} 已經投過票了'.format(card_id))  # set gui lable text


# build socket
def connect_and_read_input():
    global last_stu_id
    global counter

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as connection:
        # Connect to the card reader
        try:
            connection.connect(config.ADDRESS)
        except Exception as e:
            print('can\'t connect to card reader, please check it')
            connection.close()
            exit()

        # give the connection to gui (know what to close)
        vote_gui.connection = connection

        # start gui
        vote_gui.start()

        # Clear all card reader history
        connection.send(bytes(config.CMD_CLEAR_ALL))

        
        while True:
            # read the list record
            connection.send(bytes(config.CMD_READ_LAST))

            # get reading list record result
            return_value_byte = connection.recv(config.BUFFER_SIZE)
            return_value_hex = [hex(byte) for byte in return_value_byte]

            # check if that is a card id or not
            if return_value_hex[1] == '0x21':
                card_id_process(return_value_hex)

                # clear the id from card reader that get this time
                connection.send(bytes(config.CMD_CLEAR_LAST))

            counter += 1
            time.sleep(0.1)
            if counter >= 50:
                last_stu_id = None
                counter = 0
                vote_gui.change_text('歡迎～')


# main
def main():
    try:
        if load_file():
            connect_and_read_input()
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        exit()


if __name__ == '__main__':
    main()

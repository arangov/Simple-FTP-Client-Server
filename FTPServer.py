import socket
import shutil
import os
import sys

#Victor Arango
#creation of the client socket
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#takes the port number from the command line argument
args = sys.argv

port = int(args[1])

#socket binds to specific hostname/port
s.bind(("", port))
#socket begins to listen for client
s.listen(1)




while True:
    #client makes connection and server accepts
    c, addr = s.accept()
    """each c.send() in the body of the next while loop sends the information to the client
    over the control connection"""
    #send welcome message to client after control connection is made
    sys.stdout.write("220 COMP 431 FTP server ready.\r\n")
    c.send(bytes("220 COMP 431 FTP server ready.\r\n", 'utf-8'))

    # reads through the files given input
    user_confirmed = False
    pass_confirmed = False
    quit = False
    port = False
    logged_in = False
    order = True
    #creates variables in order to obtain the IP and port info for the data connection
    IP_addr = ''
    port_data = 0

    while True:
        #in the case that a quit command is called the inside while loop is broken
        if quit is True:
            break
        # list of commands that valid commands
        command_list = []
        #listens for commands sent from the client
        a = ''
        a = c.recv(4096).decode('utf-8')


        command_list.append(a)
        commands = ["USER ", "PASS ", "TYPE ", "SYST", "NOOP", "QUIT", "PORT ", "RETR "]

        # keeps track of the line of input for current command being processed
        i = -1

        # booleans see whether a valid USER/PASS/PORT/QUIT call has been made in order to

        num_files = 0
        # loops through each line in the list of commands provided
        #parses through command sent from client
        for line in command_list:
            # booleans for whether or not the username/password are valid/invalid
            username = True
            password = True

            # helps monitor whether or not the retr command is valid
            retr = True
            '''monitors the amount of commas in the PORT command, 5 means that there are enough
            arguments for there to be a valid PORT command, other checks see whether those
            arguments are valid ints'''
            num_commas = 0

            not_all_spaces = False

            # checks to see if there is a leading slash in the file name of a RETR command
            slash = False

            skip_rest = False

            # i determines the index of the command we are on from command_list
            i = i + 1

            # process the command through a character by character representation
            represent = repr(command_list[i])

            # all the criteria that needs to be checked for the USER command
            if commands[0] in command_list[i].upper():
                # loops through each char of the line to check for ascii char higher than 127
                # also checks whether or not a valid username was given
                for line in represent[5:-1]:
                    if ord(line) < 128:
                        if line is represent[-5] and not_all_spaces is False:
                            break
                        elif line is represent[-1] and not_all_spaces is False:
                            break
                        elif line is not ' ':
                            not_all_spaces = True
                    elif not_all_spaces is False or ord(line) >= 128:
                        # CRLF
                        sys.stdout.write(command_list[i])
                        sys.stdout.write("501 Syntax error in parameter.\r\n")
                        c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                        username = False
                        break
                # username boolean true if all ASCII values were ord < 128
                # username given, then checks for CRLF, CRLF there, command ok
                if username is True:
                    if not_all_spaces is False:
                        # username error
                        sys.stdout.write(command_list[i])
                        sys.stdout.write("501 Syntax error in parameter.\r\n")
                        c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                        not_all_spaces = False
                    elif '\\r' in represent or '\\n' in represent:
                        sys.stdout.write(command_list[i])
                        user_confirmed = True
                        sys.stdout.write("331 Guest access OK, send password.\r\n")
                        c.send(bytes("331 Guest access OK, send password.\r\n", 'utf-8'))
                    else:
                        # CRLF error
                        sys.stdout.write(command_list[i])
                        sys.stdout.write("501 Syntax error in parameter.\r\n")
                        c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                else:
                    username = True
                    continue
            # all the criteria that needs to be checked for the PASS command
            elif commands[1] in command_list[i].upper():
                # follows the same format/checks as the USER commands if-block
                # uses the password boolean rather than username for clarification
                for line in represent[5:-1]:
                    if ord(line) < 128:
                        if line is represent[-5] and not_all_spaces is False:
                            break
                        elif line is represent[-1] and not_all_spaces is False:
                            break
                        elif line is not ' ':
                            not_all_spaces = True
                    elif not_all_spaces is False or ord(line) >= 128:
                        # password error
                        sys.stdout.write(command_list[i])
                        sys.stdout.write("501 Syntax error in parameter.\r\n")
                        c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                        password = False
                        break
                if password is True:
                    if not_all_spaces is False:
                        # password error
                        sys.stdout.write(command_list[i])
                        sys.stdout.write("501 Syntax error in parameter.\r\n")
                        c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                        not_all_spaces = False
                    elif '\\r' in represent or '\\n' in represent:
                        # checks whether PASS command is following a valid user command
                        # also checks whether a valid USER/PASS pair has already been called
                        if user_confirmed is False or logged_in is True:
                            sys.stdout.write(command_list[i])
                            sys.stdout.write("503 Bad sequence of commands.\r\n")
                            c.send(bytes("503 Bad sequence of commands.\r\n", 'utf-8'))
                        else:
                            sys.stdout.write(command_list[i])
                            pass_confirmed = True
                            sys.stdout.write("230 Guest login OK.\r\n")
                            c.send(bytes("230 Guest login OK.\r\n", 'utf-8'))
                            logged_in = True
                    else:
                        # CRLF error
                        sys.stdout.write(command_list[i])
                        sys.stdout.write("501 Syntax error in parameter.\r\n")
                        c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                else:
                    password = True
                    continue
            # all the criteria that needs to be checked for the TYPE command
            elif commands[2] in command_list[i].upper():
                # checks for type-code
                if 'A' in represent or 'I' in represent:
                    # checks to see if type-code is right before checking for CRLF
                    if represent[-6] is 'A':
                        if '\\n' in represent or '\\r' in represent:
                            # checks to see if a valid USER/PASS pair has been called
                            if represent[-7] is not ' ' or represent[-5] is not '\\':
                                # CRLF error
                                sys.stdout.write(command_list[i])
                                sys.stdout.write("501 Syntax error in parameter.\r\n")
                                c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                            elif logged_in is False:
                                # if not, checks to see if a valid USER call has been made
                                # distinguishes between Not logged in and Bad sequence errors
                                if user_confirmed is False:
                                    sys.stdout.write(command_list[i])
                                    sys.stdout.write("530 Not logged in.\r\n")
                                    c.send(bytes("530 Not logged in.\r\n", 'utf-8'))
                                else:
                                    sys.stdout.write(command_list[i])
                                    sys.stdout.write("503 Bad sequence of commands.\r\n")
                                    c.send(bytes("503 Bad sequence of commands.\r\n", 'utf-8'))
                            else:
                                sys.stdout.write(command_list[i])
                                sys.stdout.write("200 Type set to A.\r\n")
                                c.send(bytes("200 Type set to A.\r\n", 'utf-8'))
                        else:
                            # CRLF
                            sys.stdout.write(command_list[i])
                            sys.stdout.write("501 Syntax error in parameter.\r\n")
                            c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                    # the same concept as when represent[-6] is A, but this time for I
                    elif represent[-6] is 'I':
                        if '\\n' in represent or '\\r' in represent:
                            if represent[-7] is not ' ' or represent[-5] is not '\\':
                                # CRLF error
                                sys.stdout.write(command_list[i])
                                sys.stdout.write("501 Syntax error in parameter.\r\n")
                                c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                            elif logged_in is False:
                                if user_confirmed is False:
                                    sys.stdout.write(command_list[i])
                                    sys.stdout.write("530 Not logged in.\r\n")
                                    c.send(bytes("530 Not logged in.\r\n", 'utf-8'))
                                else:
                                    sys.stdout.write(command_list[i])
                                    sys.stdout.write("503 Bad sequence of commands.\r\n")
                                    c.send(bytes("503 Bad sequence of commands.\r\n", 'utf-8'))
                            else:
                                sys.stdout.write(command_list[i])
                                sys.stdout.write("200 Type set to I.\r\n")
                                c.send(bytes("200 Type set to I.\r\n", 'utf-8'))
                        else:
                            # CRLF error
                            sys.stdout.write(command_list[i])
                            sys.stdout.write("501 Syntax error in parameter.\r\n")
                            c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                    else:
                        # CRLF error
                        sys.stdout.write(command_list[i])
                        sys.stdout.write("501 Syntax error in parameter.\r\n")
                        c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                else:
                    # type-code error
                    sys.stdout.write(command_list[i])
                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                    c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
            # all the criteria that needs to be checked for the SYST command
            elif commands[3] in command_list[i].upper():
                # checks for invalid whitespace/characters between command and CRLF
                if represent[5] is not '\\':
                    # CRLF
                    sys.stdout.write(command_list[i])
                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                    c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                else:
                    # checks for CRLF as the other commands also check for it
                    if '\\n' in represent or '\\r' in represent:
                        # does the same checks as the TYPE command for USER/PASS pair and USER call
                        if logged_in is False:
                            if user_confirmed is False:
                                sys.stdout.write(command_list[i])
                                sys.stdout.write("530 Not logged in.\r\n")
                                c.send(bytes("530 Not logged in.\r\n", 'utf-8'))
                            else:
                                sys.stdout.write(command_list[i])
                                sys.stdout.write("503 Bad sequence of commands.\r\n")
                                c.send(bytes("503 Bad sequence of commands.\r\n", 'utf-8'))
                        else:
                            sys.stdout.write(command_list[i])
                            sys.stdout.write("215 UNIX Type: L8.\r\n")
                            c.send(bytes("215 UNIX Type: L8.\r\n", 'utf-8'))
                    else:
                        # CRLF error
                        sys.stdout.write(command_list[i])
                        sys.stdout.write("501 Syntax error in parameter.\r\n")
                        c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))

            # all the criteria that needs to be checked for the NOOP command
            elif commands[4] in command_list[i].upper():
                # uses the same checks as the SYST command, besides the command check itself
                if represent[5] is not '\\':
                    # CRLF error
                    sys.stdout.write(command_list[i])
                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                    c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                else:
                    if '\\n' in represent or '\\r' in represent:
                        # does the same checks as the SYST/TYPE commands
                        if logged_in is False:
                            if user_confirmed is False:
                                sys.stdout.write(command_list[i])
                                sys.stdout.write("530 Not logged in.\r\n")
                                c.send(bytes("530 Not logged in.\r\n", 'utf-8'))
                            else:
                                sys.stdout.write(command_list[i])
                                sys.stdout.write("503 Bad sequence of commands.\r\n")
                                c.send(bytes("503 Bad sequence of commands.\r\n", 'utf-8'))
                        else:
                            sys.stdout.write(command_list[i])
                            sys.stdout.write("200 Command OK.\r\n")
                            c.send(bytes("200 Command OK.\r\n", 'utf-8'))

                    else:
                        # CRLF error
                        sys.stdout.write(command_list[i])
                        sys.stdout.write("501 Syntax error in parameter.\r\n")
                        c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))

            # all the criteria that needs to be checked for the QUIT command
            elif commands[5] in command_list[i].upper():
                '''uses the same checks as the NOOP command, besides the command check 
                itself and checking to see whether we are logged in.'''
                # QUIT can be called any time.
                if represent[5] is not '\\':
                    # CRLF error
                    sys.stdout.write(command_list[i])
                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                    c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                else:
                    #command changed to 221 Goodbye.
                    if '\\n' in represent or '\\r' in represent:
                        sys.stdout.write(command_list[i])
                        quit = True
                        sys.stdout.write("221 Goodbye.\r\n")
                        c.send(bytes("221 Goodbye.\r\n", 'utf-8'))
                        c.close()
                        # sys.exit()
                    else:
                        # CRLF error
                        sys.stdout.write(command_list[i])
                        sys.stdout.write("501 Syntax error in parameter.\r\n")
                        c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
            # all the criteria that needs to be checked for the PORT command
            elif commands[6] in command_list[i].upper():
                # ftpdatasocket.connect(host_address, port_num)
                # makes an initial check for the CRLF in command call
                if '\\r' not in represent or '\\n' not in represent:
                    sys.stdout.write(command_list[i])
                    print("1")
                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                    c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                    retr = False
                else:
                    # does the same thing as the beginning for loop for the USER/PASS commands
                    for line in represent[5:-1]:
                        if ord(line) < 128:
                            if line is represent[-5] and not_all_spaces is False:
                                break
                            elif line is represent[-1] and not_all_spaces is False:
                                break
                            elif line is not ' ':
                                not_all_spaces = True
                        elif not_all_spaces is False or ord(line) >= 128:
                            # CRLF error
                            print("2")
                            sys.stdout.write(command_list[i])
                            sys.stdout.write("501 Syntax error in parameter.\r\n")
                            c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                            port = False
                            skip_rest = True
                            break
                    '''a, b, c, d, g, and h are where I store the host address and
                    port numnber variables given to me in the command call'''
                    a = ''
                    b = ''
                    ca = ''
                    d = ''
                    g = ''
                    h = ''
                    for line in represent[6:-5]:
                        # a second check to see if the parameter was all spaces/had an invalid ASCII character
                        if skip_rest is True:
                            break
                        elif line is not ' ':
                            # keeps track of number of commas to see if there are less than 5
                            if line is ',':
                                num_commas = num_commas + 1
                                if (num_commas > 5):
                                    sys.stdout.write(command_list[i])
                                    print("3")
                                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                                    c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                                    skip_rest = True
                                    port = False
                                    break
                            # checks for the off chance the for loop reaches the end of the command
                            elif line is '\\':
                                 # checks for amount of commas already counted
                                if num_commas < 5 or num_commas > 5:
                                    sys.stdout.write(command_list[i])
                                    print("4")
                                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                                    c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                                    skip_rest = True
                                    port = False
                                    break
                                else:
                                     break
                            elif num_commas == 0:
                                a = a + line
                            elif num_commas == 1:
                                b = b + line
                            elif num_commas == 2:
                                ca = ca + line
                            elif num_commas == 3:
                                d = d + line
                            elif num_commas == 4:
                                g = g + line
                            elif num_commas == 5:
                                h = h + line
                        # checks for a space in the middle of the host address/port number
                        elif a is not '':
                            sys.stdout.write(command_list[i])
                            print("5")
                            sys.stdout.write("501 Syntax error in parameter.\r\n")
                            c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                            port = False
                            skip_rest = True
                            break
                    # check to see if 5 strings were given separated by 5 commas
                    if (a.isdigit() and b.isdigit() and ca.isdigit()
                        and d.isdigit() and g.isdigit() and h.isdigit()) and skip_rest is False:
                        if int(a) <= 255 and int(b) <= 255 and int(ca) <= 255 and int(d) <= 255 and int(
                            g) <= 255 and int(
                            h) <= 255:
                            if num_commas == 5 and a is not '' and b is not '' and ca is not '' and d is not '' and g is not '' and h is not '' and skip_rest is False:
                                # does the same USER/PASS and USER call checks TYPE/SYST/NOOP command do
                                if logged_in is False:
                                    if user_confirmed is False:
                                        sys.stdout.write(command_list[i])
                                        sys.stdout.write("530 Not logged in.\r\n")
                                        c.send(bytes("530 Not logged in.\r\n", 'utf-8'))
                                    else:
                                        sys.stdout.write(command_list[i])
                                        sys.stdout.write("503 Bad sequence of commands.\r\n")
                                        c.send(bytes("503 Bad sequence of commands.\r\n", 'utf-8'))
                                else:
                                    # makes sure the strings given for a, b, c, d, g, h can be cast into ints

                                    port_num = int(g) * 256 + int(h)
                                    host_address = a + "." + b + "." + ca + "." + d
                                    port = True
                                    #set the variables to the correct IP and port for the data connection
                                    IP_addr = host_address
                                    port_data = port_num
                                    sys.stdout.write(command_list[i])
                                    sys.stdout.write("200 Port command successful " + "(" + host_address + "," + str(
                                        port_num) + ").\r\n")
                                    c.send(bytes("200 Port command successful " + "(" + host_address + "," + str(port_num) + ").\r\n",'utf-8'))
                        else:
                            sys.stdout.write(command_list[i])
                            print("6")
                            sys.stdout.write("501 Syntax error in parameter.\r\n")
                            c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                            port = False
                    # deals with the case where a variable doesn't receive a value (e.g. a = '' still)
                    elif skip_rest is False:
                        sys.stdout.write(command_list[i])
                        print("7")
                        sys.stdout.write("501 Syntax error in parameter.\r\n")
                        c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                        port = False
            # all the criteria that needs to be checked for the RETR command
            elif commands[7] in command_list[i].upper():
                # checks for CRLF
                if '\\r' not in represent or '\\n' not in represent:
                    sys.stdout.write(command_list[i])
                    sys.stdout.write("501 Syntax error in parameter.\r\n")
                    c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                    retr = False
                else:
                    for line in represent[5:-1]:
                        if ord(line) >= 128:
                            order = False
                            sys.stdout.write(command_list[i])
                            sys.stdout.write("501 Syntax error in parameter.\r\n")
                            c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                            retr = False
                            break
                    if order is True:
                        # y helps deal with the situation where there is a leading slash
                        y = 5
                        # does essentially the same job as the beginning for loops in USER/PASS/PORT
                        for line in represent[5:-1]:
                             if ord(line) < 128:
                                if represent[-5] is line and not_all_spaces is False:
                                    # makes sure the leading '\' is not the '\' from the '\r'
                                    if represent[y - 1] is ' ' and represent[y + 1] is 'r' and represent[y + 2] is '\\':
                                        break
                                    else:
                                        # if it is not, claims there is a leading slash
                                        slash = True
                                        break
                                # off chance there is no CRLF
                                elif line is represent[-1] and not_all_spaces is False:
                                    break
                                # first instance of a non-space character
                                elif line is not ' ':
                                    # helps deal with the situation where no file name is given
                                    not_all_spaces = True
                                    # helps deal with the situation of a leading slash
                                    if line is '\\' or line is '/':
                                        slash = True
                                        break
                                    # for the case where the non-space character is not a slash
                                    else:
                                        break
                             # chance where no file name is given or there is an invalid ASCII character
                             elif not_all_spaces is False or ord(line) >= 128:
                                # CRLF error
                                sys.stdout.write(command_list[i])
                                sys.stdout.write("501 Syntax error in parameter.\r\n")
                                c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                                retr = False
                                break
                             y = y + 1
                        # Divided dealing with the file name of the RETR command into two cases:
                        # The case where there is a leading slash ('/' or '\')

                        if slash:
                            # second check to make sure a file name was given with valid ASCII chars
                            if retr is False:
                                sys.stdout.write(command_list[i])
                                sys.stdout.write("501 Syntax error in parameter.\r\n")
                                c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                                retr = False
                            # same USER/PASS pair and USER checks as TYPE, SYST, etc.
                            # checks to see if the file exists in the case of a '/' or a '\\'
                            elif os.path.exists(os.curdir + "/" + represent[y + 1:-5]) or os.path.exists(
                                os.curdir + "/" + represent[y + 2:-5]):
                                # the case for '//'
                                if os.path.exists(os.curdir + "/" + represent[y + 2:-5]):
                                    num_files = num_files + 1
                                    # if a file already exists from previous run, OVERWRITE
                                    # directory should essentially be empty after each run of the program
                                    sys.stdout.write(command_list[i])
                                    sys.stdout.write("150 File status okay.\r\n")
                                    c.send(bytes("150 File status okay.\r\n", 'utf-8'))

                                    """makes sure the connection can be made between server to client
                                    before continuing to send file to client, if not sends 425 error"""
                                    try:
                                        ftpdatasocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                        ftpdatasocket.connect((IP_addr, port_data))
                                        f = open(represent[y+2:-5], "rb")
                                        data = f.read(4096)
                                        # print("Here to open up")
                                        while data:
                                            # print("Inside of ")
                                            ftpdatasocket.send(data)
                                            data = f.read(4096)
                                        ftpdatasocket.close()
                                        f.close()
                                        c.send(bytes("250 Requested file action completed.\r\n", 'utf-8'))
                                        sys.stdout.write("250 Requested file action completed.\r\n")

                                        port = False
                                    except:
                                        sys.stdout.write("425 Can not open data connection.\r\n")
                                        c.send(bytes("425 Can not open data connection.\r\n", 'utf-8'))
                                else:
                                    # the case for '/'
                                    num_files = num_files + 1
                                    # if a file already exists from previous run, OVERWRITE
                                    # directory should essentially be empty after each run of the program
                                    # os.rename(dst_file, new_file_name)
                                    sys.stdout.write(command_list[i])
                                    sys.stdout.write("150 File status okay.\r\n")
                                    c.send(bytes("150 File status okay.\r\n", 'utf-8'))
                                    #does the same thing as the case above for the case of a leading '/'
                                    try:
                                        ftpdatasocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                        ftpdatasocket.connect((IP_addr, port_data))

                                        f = open(represent[y+1:-5], "rb")
                                        data = f.read(4096)
                                        # print("Here to open up")
                                        while data:
                                            # print("Inside of ")
                                            ftpdatasocket.send(data)
                                            data = f.read(4096)
                                        ftpdatasocket.close()
                                        f.close()
                                        c.send(bytes("250 Requested file action completed.\r\n", 'utf-8'))
                                        sys.stdout.write("250 Requested file action completed.\r\n")
                                        port = False
                                    except:
                                        sys.stdout.write("425 Can not open data connection.\r\n")
                                        c.send(bytes("425 Can not open data connection.\r\n", 'utf-8'))
                            else:
                                # if the file doesn't exist, if no valid PORT command was called it is a bad sequence error
                                # otherwise it is a file cannot be found error
                                if port is False:
                                    sys.stdout.write(command_list[i])
                                    sys.stdout.write("503 Bad sequence of commands.\r\n")
                                    c.send(bytes("503 Bad sequence of commands.\r\n", 'utf-8'))
                                elif port is True:
                                    sys.stdout.write(command_list[i])
                                    sys.stdout.write("550 File not found or access denied.\r\n")
                                    c.send(bytes("550 File not found or access denied.\r\n", 'utf-8'))
                        # or the case where there is no leading slash
                        else:
                            # the same situation as above for the case of no leading slash
                            if retr is False or not_all_spaces is False:
                                sys.stdout.write(command_list[i])
                                sys.stdout.write("501 Syntax error in parameter.\r\n")
                                c.send(bytes("501 Syntax error in parameter.\r\n", 'utf-8'))
                                retr = False
                            elif logged_in is False:
                                if user_confirmed is False:
                                    sys.stdout.write(command_list[i])
                                    sys.stdout.write("530 Not logged in.\r\n")
                                    c.send(bytes("530 Not logged in.\r\n", 'utf-8'))
                                else:
                                    sys.stdout.write(command_list[i])
                                    sys.stdout.write("503 Bad sequence of commands.\r\n")
                                    c.send(bytes("503 Bad sequence of commands.\r\n", 'utf-8'))
                            elif port is False:
                                sys.stdout.write(command_list[i])
                                sys.stdout.write("503 Bad sequence of commands.\r\n")
                                c.send(bytes("503 Bad sequence of commands.\r\n", 'utf-8'))
                            # checks to see if the file exists
                            # makes no changes to the value of y because it doesn't have to ignore a slash
                            elif os.path.exists(os.curdir + "/" + represent[y:-5]):
                                num_files = num_files + 1
                                # if a file already exists from previous run, OVERWRITE
                                # directory should essentially be empty after each run of the program
                                sys.stdout.write(command_list[i])
                                sys.stdout.write("150 File status okay.\r\n")
                                c.send(bytes("150 File status okay.\r\n", 'utf-8'))
                                #does the same thing as the previous cases for the case of no leading slashes
                                try:
                                    ftpdatasocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    ftpdatasocket.connect((IP_addr, port_data))

                                    f = open(represent[y:-5], "rb")
                                    data = f.read(4096)
                                    # print("Here to open up")
                                    while data:
                                        # print("Inside of ")
                                        ftpdatasocket.send(data)
                                        data = f.read(4096)
                                    ftpdatasocket.close()
                                    f.close()
                                    c.send(bytes("250 Requested file action completed.\r\n", 'utf-8'))
                                    sys.stdout.write("250 Requested file action completed.\r\n")
                                    port = False
                                except:
                                    sys.stdout.write("425 Can not open data connection.\r\n")
                                    c.send(bytes("425 Can not open data connection.\r\n", 'utf-8'))
                            else:
                                if port is False:
                                    sys.stdout.write(command_list[i])
                                    sys.stdout.write("503 Bad sequence of commands.\r\n")
                                    c.send(bytes("503 Bad sequence of commands.\r\n", 'utf-8'))
                                elif port is True:
                                    sys.stdout.write(command_list[i])
                                    sys.stdout.write("550 File not found or access denied.\r\n")
                                    c.send(bytes("550 File not found or access denied.\r\n", 'utf-8'))
            # check to see if none of the commands matched
            else:
                sys.stdout.write(command_list[i])
                sys.stdout.write("502 Command not implemented.\r\n")
                c.send(bytes("502 Command not implemented.\r\n", 'utf-8'))
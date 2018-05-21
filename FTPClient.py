import socket
import sys
import os
import shutil

#Victor Arango
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#port_NUM = 9387

#made the reply parser into a function called confirmReply()
"""once a reply is received from the server, the client uses this function to parse
through that reply and confirm that it is valid"""
#only changes made to the reply parser were based on semantics of output
def confirmReply(a):
    # system reads through a file that contains list of inputted replies
    command_list = []
    command_list.append(a)

    # index for list of inputted replies
    i = -1

    # runs through each reply in the list of inputted replies
    for line in command_list:

        # incrementing index
        i = i + 1

        # keeps track of whether an error has already occurred
        error = False

        # Initial variable for reply code inputted value
        temp = command_list[i][0:3]

        # character representation of reply string
        represent = repr(command_list[i])

        # variable for reply code int value
        code = 0

        # variable for reply text string value
        text = ""

        # confirms reply code string value can be interpreted as a digit
        if (temp.isdigit()):
            # converts reply code string to int and initializes
            # both reply code and reply text to variables code and text, respectively
            code = int(command_list[i][0:3])
            text = command_list[i][4:-1]
        # calls an error if reply code is not actually an integer
        else:
            #sys.stdout.write(command_list[i])
            print("ERROR -- reply-code")
            error = True
        # confirms that reply code is between assigned reply code boundaries
        #  and is not just a space
        if code > 599 or code < 100 or command_list[i][3] is not " ":
            if error is False:
                #sys.stdout.write(command_list[i])
                print("ERROR -- reply-code")
                error = True
        # confirms reply has <CRLF> and no errors have been called before
        elif '\\r' in represent or '\\n' in represent and error is False:
            # checks to see if reply text contains values ASCII < 128 char
            for line in command_list[i]:
                if ord(line) >= 128:
                    #sys.stdout.write(command_list[i])
                    print("ERROR -- reply-text")
                    error = True
                    break
            # in the case of a valid FTP reply
            if error is False:
                code_txt = str(code)
                #sys.stdout.write(command_list[i])
                print("FTP reply " + code_txt + " accepted. Text is: " + text)
        # checks for errors in reply text before calling <CRLF> error
        elif error is False:
            # does the same check as in the block above before calling <CRLF> error
            for line in command_list[i]:
                if ord(line) >= 128:
                    #sys.stdout.write(command_list[i])
                    print("ERROR -- reply-text")
                    error = True
                    break
            if error is False:
                #sys.stdout.write(command_list[i])
                print("ERROR -- <CRLF>")
                error = True

connect = False
client = True
args = sys.argv
port_val = int(args[1])
num_files = 0
while client:
    # beginning of client command input parser
    # reading through the file with inputted commands
    command_list = []
    command_list.append(str(input() + "\n"))

    # possible commands the client can process
    commands = ["CONNECT ", "GET ", "QUIT"]

    # incrementing variable to go through list of inputted commands
    i = -1

    # initial port value


    # gathering the correct host information in order to convert it to the
    host_num = socket.gethostbyname(socket.gethostname())
    a = ""
    b = ""
    c = ""
    d = ""
    g = 0



    for line in host_num:
        if line is ".":
            g = g + 1
        elif g is 0:
            a = a + line
        elif g is 1:
            b = b + line
        elif g is 2:
            c = c + line
        elif g is 3:
            d = d + line
    host_number = a + "," + b + "," + c + "," + d

    # initial state of the client, not being connected to a host/port
    #connect = False

    # runs through each command received as input until a QUIT command is called
    # or if the command_list runs out of commands to process

    for line in command_list:

        i = i + 1
        # all the checks needed to process the CONNECT command
        if commands[0] in command_list[i].upper():

            first = True
            end_first = False
            space_port = False
            space_host = False
            error = False

            # host/port strings where port (if possible) will be converted to an int
            host = ""
            port = ""

            # variables that help determine the starting index and ending index for host/port
            x = 7
            y = 7
            m = 7
            n = 7
            # loops through CONNECT request
            # extracts server host and server port
            # makes sure server host and server port are valid
            for line in command_list[i][7:-1]:
                # checks for valid characters of ASCII < 128
                if ord(line) >= 128:
                    # calls the error according to which token was being monitored
                    if host is "":
                        sys.stdout.write(command_list[i])
                        print("ERROR -- server-host")
                        error = True
                        break
                    else:
                        sys.stdout.write(command_list[i])
                        print("ERROR -- server-port")
                        error = True
                        break
                elif line is ' ':
                    # if the program finds a space in between the server port number it calls an error
                    if space_port is True:
                        sys.stdout.write(command_list[i])
                        print("ERROR -- server-port")
                        error = True
                        break
                    # extracts server host after second space is found
                    elif end_first is True:
                        host = command_list[i][x:y]
                        m = y + 1
                        n = y + 1
                        first = False
                    # finding the correct indices for server port
                    elif end_first is True and first is False:
                        m = m + 1
                        n = n + 1
                    # going through the first spaces after the CONNECT command is read
                    else:
                        x = x + 1
                        m = m + 1
                        y = y + 1
                        n = n + 1
                    continue
                # calls end_first as true and begins finding indices for server host
                elif first is True:
                    end_first = True
                    y = y + 1
                # begins finding first character for server port once server host
                # has already been found
                elif first is False:
                    space_port = True
                    n = n + 1
            # in the case that no server host is extracted an error occurs
            if host is "" and error is False:
                sys.stdout.write(command_list[i])
                print("ERROR -- server-host")
                error = True
            elif error is False:
                # server port is extracted based on the indices m and n
                port = command_list[i][m:n]

                # in the case that no server port is extracted an error occurs
                if port is "":
                    sys.stdout.write(command_list[i])
                    print("ERROR -- server-port")
                    error = True
                # if a server port is extracted, check if it is a number
                elif port.isdigit():
                    # make sure the number extracted is between valid port number values
                    if int(port) > 65535 or int(port) < 0:
                        sys.stdout.write(command_list[i])
                        print("ERROR -- server-port")
                        error = True
                    # if it is in between valid port number values the CONNECT request is valid
                    else:
                        # attempts to make a connection with the server on the control socket
                        # if the connection fails, prints CONNECT failed...
                        # if the connection is successful it sends and receives each command/reply one by one
                        try:
                            s.connect((host, int(port)))
                            sys.stdout.write(command_list[i])
                            print("CONNECT accepted for FTP server at host " + host + " and port " + port)
                            confirmReply(s.recv(4096).decode('utf-8'))
                            sys.stdout.write("USER anonymous\r\n")
                            s.send(bytes("USER anonymous\r\n", 'utf-8'))
                            confirmReply(s.recv(4096).decode('utf-8'))

                            sys.stdout.write("PASS guest@\r\n")
                            s.send(bytes("PASS guest@\r\n", 'utf-8'))
                            confirmReply(s.recv(4096).decode('utf-8'))

                            sys.stdout.write("SYST\r\n")
                            s.send(bytes("SYST\r\n", 'utf-8'))
                            confirmReply(s.recv(4096).decode('utf-8'))

                            sys.stdout.write("TYPE I\r\n")
                            s.send(bytes("TYPE I\r\n", 'utf-8'))
                            confirmReply(s.recv(4096).decode('utf-8'))
                            connect = True
                        except IOError:
                            sys.stdout.write(command_list[i])
                            print("CONNECT accepted for FTP server at host " + host + " and port " + port)
                            sys.stdout.write("CONNECT failed\n")
                # in the case that the server port extracted ends up not being a digit
                else:
                    sys.stdout.write(command_list[i])
                    print("ERROR -- server-port")
                    error = True
        # all the checks needed to process the GET command
        elif commands[1] in command_list[i].upper():
            # different variables that monitor the state of the GET request
            file = ""
            space = True
            error = False
            all_spaces = True

            # calculations for the port number
            e = "31"
            l = port_val - (int(e) * 256)

            # where the first character may begin after the required space
            f = 4
            # looping through request to check for valid pathname and extract pathname
            # checks for ASCII < 128 and an actual pathname existing
            for line in command_list[i][4:-1]:
                if ord(line) >= 128:
                    sys.stdout.write(command_list[i])
                    print("ERROR -- pathname")
                    error = True
                    break
                elif line is " " and space is True and file is "":
                    f = f + 1
                    continue
                else:
                    file = command_list[i][f:-1]
                if line is not " ":
                    all_spaces = False
            # if the pathname cannot be extracted because no pathname was entered
            if all_spaces:
                sys.stdout.write(command_list[i])
                print("ERROR -- pathname")
                error = True
            # if the GET request is valid
            elif connect and error is False:
                ftpdatasocket = socket.socket()
                firstly = ''
                secondly = ''
                # attempts to create the data control socket
                # if the creation of the socket fails, outputs GET failed...
                """if the creation succeeds it sends the host IP and port then checks to see if the file exists"""
                try:
                    sys.stdout.write(command_list[i])
                    sys.stdout.write("GET accepted for " + file + "\n")
                    # begin FTP data socket/welcoming socket
                    ftpdatasocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    # s.send(bytes("PORT " + host_number + "," + e + "," + str(l) + "\r\n", 'utf-8'))
                    #print(port_val)
                    #print(host_num)
                    ftpdatasocket.bind((host_num, int(port_val)))  # This is where you bind the socket to the port number
                    ftpdatasocket.listen(1)
                    sys.stdout.write("PORT " + host_number + "," + e + "," + str(l) + "\r\n")
                    s.send(bytes("PORT " + host_number + "," + e + "," + str(l) + "\r\n", 'utf-8'))
                    confirmReply(s.recv(4096).decode('utf-8'))
                    sys.stdout.write("RETR " + file + "\r\n")
                    s.send(bytes("RETR " + file + "\r\n", 'utf-8'))
                    firstly = s.recv(4096).decode('utf-8')
                    confirmReply(firstly)
                except:
                    sys.stdout.write(command_list[i])
                    sys.stdout.write("GET failed, FTP-data port not allowed.\r\n")
                # given that the file exists, the client waits to receive a connection from the server
                # if the connection fails, client waits to receive 425 reply
                # if connection succeeds, client receives 250 reply and continues to receive file bytes over the connection
                try:
                    if "150" in firstly:
                        conn, addr = ftpdatasocket.accept()
                        num_files = num_files + 1

                        f = open(os.path.join(os.curdir, "retr_files/"+"file" + str(num_files)), "wb")
                        while True:
                            data = conn.recv(4096)
                            while (data):
                                f.write(data)
                                data = conn.recv(4096)

                            """deals with leading slashes in file name if necessary, 
                            copys file over to retr_files directory, and closes data connection"""
                            if '//' in file[0:2] or '\\' in file[0:2]:
                                p = file[2:]
                            elif file[0] is '/':
                                p = file[1:]
                            else:
                                p = file

                            f.close()
                            conn.close()
                            break
                        secondly = s.recv(4096).decode('utf-8')
                        confirmReply(secondly)
                        # increments port value for each file received
                        port_val = port_val + 1
                    else:
                        continue
                except IOError:
                    #confirmReply(s.recv(4096).decode('utf-8'))
                    print("yes")
            # if a valid CONNECT request has not been called yet
            elif error is False:
                sys.stdout.write(command_list[i])
                print("ERROR -- expecting CONNECT")
        # all the checks needed to process the QUIT command
        elif commands[2] in command_list[i].upper():
            # QUIT can only be called after a valid CONNECT command
            if connect:
                # Makes sure that QUIT has nothing trailing the command besides <EOL> char
                if len(command_list[i]) is 5:
                    sys.stdout.write(command_list[i])
                    quit = True
                    print("QUIT accepted, terminating FTP client")
                    sys.stdout.write("QUIT\r\n")
                    s.send(bytes("QUIT\r\n", 'utf-8'))
                    confirmReply(s.recv(4096).decode('utf-8'))
                    client = False
                    # client closes control connection once valid QUIT command is called
                    s.close()
                # if QUIT has something trailing it (i.e. " ", "a", etc.)
                else:
                    sys.stdout.write(command_list[i])
                    sys.stdout.write("ERROR -- request")
            # next two blocks are the same situation as before but
            # when a valid CONNECT command has not been made
            elif len(command_list[i]) is 5:
                sys.stdout.write(command_list[i])
                print("ERROR -- expecting CONNECT")
            else:
                sys.stdout.write(command_list[i])
                print("ERROR -- request")
        # command being processed doesn't have a valid command call (i.e. COMMAND, GET, QUIT)
        else:
            sys.stdout.write(command_list[i])
            print("ERROR -- request")
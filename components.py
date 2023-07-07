def process_command(line):
    # stored as an integer initially  as a safe way of verifying that there is no subroutine in the line
    subroutine = 0

    # but if it is a subroutine, store the name of it and strip if from the line so it can be processed
    if (":" in line):
        subroutine = line[0:line.find(":")]
        line = line[line.find(":") + 1:]
    line = line.strip()

    # check for and process every command
    if (line[0:5] == "ADD.D"):

        # this means all registers are in single digits
        if (len(line) == 14):
            dest = line[7]
            src1 = line[10]
            src2 = line[13]

        # this means one register is in double digits
        elif (len(line) == 15):
            if (line[7:9].isdigit()):
                dest = line[7:9]
                src1 = line[11]
                src2 = line[14]
            elif (line[10:12].isdigit()):
                dest = line[7]
                src1 = line[10:12]
                src2 = line[14]
            else:
                dest = line[7]
                src1 = line[10]
                src2 = line[13:]

        # this means 2 registers are in double digits
        elif (len(line) == 16):
            if (line[7:9].isdigit()):
                dest = line[7:9]

                if (line[11:13].isdigit()):
                    src1 = line[11:13]
                    src2 = line[15]
                else:
                    src1 = line[11]
                    src2 = line[14:]
            else:
                dest = line[7]
                src1 = line[10:12]
                src2 = line[14:]

        # length would be 17 and all 3 registers are in double digits
        else:
            dest = line[7:9]
            src1 = line[11:13]
            src2 = line[15:]

        return line[0:5], int(dest), int(src1), int(src2)

    elif (line[0:4] == "ADDI"):

        # this means all registers are in single digits
        if (len(line) == 12):
            dest = line[6]
            src1 = line[9]
            src2 = line[11]

        # this means one register is in double digits
        elif (len(line) == 13):
            if (line[6:8].isdigit()):
                dest = line[6:8]
                src1 = line[10]
                src2 = line[12]
            elif (line[9:11].isdigit()):
                dest = line[6]
                src1 = line[9:11]
                src2 = line[12]
            else:
                dest = line[6]
                src1 = line[9]
                src2 = line[11:]

        # this means 2 registers are in double digits
        elif (len(line) == 14):
            if (line[6:8].isdigit()):
                dest = line[6:8]

                if (line[10:12].isdigit()):
                    src1 = line[10:12]
                    src2 = line[13]
                else:
                    src1 = line[10]
                    src2 = line[12:]
            else:
                dest = line[6]
                src1 = line[9:11]
                src2 = line[12:]

        # length would be 17 and all 3 registers are in double digits
        else:
            dest = line[6:8]
            src1 = line[10:12]
            src2 = line[13:]

        return line[0:4], int(dest), int(src1), int(src2)

    elif (line[0:5] == "SUB.D"):

        # this means all registers are in single digits
        if (len(line) == 14):
            dest = line[7]
            src1 = line[10]
            src2 = line[13]

        # this means one register is in double digits
        elif (len(line) == 15):
            if (line[7:9].isdigit()):
                dest = line[7:9]
                src1 = line[11]
                src2 = line[14]
            elif (line[10:12].isdigit()):
                dest = line[7]
                src1 = line[10:12]
                src2 = line[14]
            else:
                dest = line[7]
                src1 = line[10]
                src2 = line[13:]

        # this means 2 registers are in double digits
        elif (len(line) == 16):
            if (line[7:9].isdigit()):
                dest = line[7:9]

                if (line[11:13].isdigit()):
                    src1 = line[11:13]
                    src2 = line[15]
                else:
                    src1 = line[11]
                    src2 = line[14:]
            else:
                dest = line[7]
                src1 = line[10:12]
                src2 = line[14:]

        # length would be 17 and all 3 registers are in double digits
        else:
            dest = line[7:9]
            src1 = line[11:13]
            src2 = line[15:]

        return line[0:5], int(dest), int(src1), int(src2)

    elif (line[0:5] == "MUL.D"):

        # this means all registers are in single digits
        if (len(line) == 14):
            dest = line[7]
            src1 = line[10]
            src2 = line[13]

        # this means one register is in double digits
        elif (len(line) == 15):
            if (line[7:9].isdigit()):
                dest = line[7:9]
                src1 = line[11]
                src2 = line[14]
            elif (line[10:12].isdigit()):
                dest = line[7]
                src1 = line[10:12]
                src2 = line[14]
            else:
                dest = line[7]
                src1 = line[10]
                src2 = line[13:]

        # this means 2 registers are in double digits
        elif (len(line) == 16):
            if (line[7:9].isdigit()):
                dest = line[7:9]

                if (line[11:13].isdigit()):
                    src1 = line[11:13]
                    src2 = line[15]
                else:
                    src1 = line[11]
                    src2 = line[14:]
            else:
                dest = line[7]
                src1 = line[10:12]
                src2 = line[14:]

        # length would be 17 and all 3 registers are in double digits
        else:
            dest = line[7:9]
            src1 = line[11:13]
            src2 = line[15:]

        return line[0:5], int(dest), int(src1), int(src2)

    elif (line[0:5] == "DIV.D"):

        # this means all registers are in single digits
        if (len(line) == 14):
            dest = line[7]
            src1 = line[10]
            src2 = line[13]

        # this means one register is in double digits
        elif (len(line) == 15):
            if (line[7:9].isdigit()):
                dest = line[7:9]
                src1 = line[11]
                src2 = line[14]
            elif (line[10:12].isdigit()):
                dest = line[7]
                src1 = line[10:12]
                src2 = line[14]
            else:
                dest = line[7]
                src1 = line[10]
                src2 = line[13:]

        # this means 2 registers are in double digits
        elif (len(line) == 16):
            if (line[7:9].isdigit()):
                dest = line[7:9]

                if (line[11:13].isdigit()):
                    src1 = line[11:13]
                    src2 = line[15]
                else:
                    src1 = line[11]
                    src2 = line[14:]
            else:
                dest = line[7]
                src1 = line[10:12]
                src2 = line[14:]

        # length would be 17 and all 3 registers are in double digits
        else:
            dest = line[7:9]
            src1 = line[11:13]
            src2 = line[15:]

        return line[0:5], int(dest), int(src1), int(src2)

    elif (line[0:3] == "ADD"):

        # this means all registers are in single digits
        if (len(line) == 12):
            dest = line[5]
            src1 = line[8]
            src2 = line[11]

        # this means one register is in double digits
        elif (len(line) == 13):
            if (line[5:7].isdigit()):
                dest = line[5:7]
                src1 = line[9]
                src2 = line[12]
            elif (line[8:10].isdigit()):
                dest = line[5]
                src1 = line[8:10]
                src2 = line[12]
            else:
                dest = line[5]
                src1 = line[8]
                src2 = line[11:]

        # this means 2 registers are in double digits
        elif (len(line) == 14):
            if (line[5:7].isdigit()):
                dest = line[5:7]

                if (line[9:11].isdigit()):
                    src1 = line[9:11]
                    src2 = line[13]
                else:
                    src1 = line[9]
                    src2 = line[12:]
            else:
                dest = line[5]
                src1 = line[8:10]
                src2 = line[12:]

        # length would be 17 and all 3 registers are in double digits
        else:
            dest = line[5:7]
            src1 = line[9:11]
            src2 = line[13:]

        return line[0:3], int(dest), int(src1), int(src2)

    elif (line[0:3] == "SUB"):

        # this means all registers are in single digits
        if (len(line) == 12):
            dest = line[5]
            src1 = line[8]
            src2 = line[11]

        # this means one register is in double digits
        elif (len(line) == 13):
            if (line[5:7].isdigit()):
                dest = line[5:7]
                src1 = line[9]
                src2 = line[12]
            elif (line[8:10].isdigit()):
                dest = line[5]
                src1 = line[8:10]
                src2 = line[12]
            else:
                dest = line[5]
                src1 = line[8]
                src2 = line[11:]

        # this means 2 registers are in double digits
        elif (len(line) == 14):
            if (line[5:7].isdigit()):
                dest = line[5:7]

                if (line[9:11].isdigit()):
                    src1 = line[9:11]
                    src2 = line[13]
                else:
                    src1 = line[9]
                    src2 = line[12:]
            else:
                dest = line[5]
                src1 = line[8:10]
                src2 = line[12:]

        # length would be 17 and all 3 registers are in double digits
        else:
            dest = line[5:7]
            src1 = line[9:11]
            src2 = line[13:]

        return line[0:3], int(dest), int(src1), int(src2)

    elif (line[0:3] == "BEQ"):

        if (line[5:7].isdigit()):
            src1 = line[5:7]
            if (line[9:11].isdigit()):
                src2 = line[9:11]
                branch = line[12:]
            else:
                src2 = line[9]
                branch = line[11:]
        else:
            src1 = line[5]
            if (line[8:10].isdigit()):
                src2 = line[8:10]
                branch = line[11:]
            else:
                src2 = line[8]
                branch = line[10]

        return line[0:3], int(src1), int(src2), branch

    elif (line[0:3] == "BNE"):

        if (line[5:7].isdigit()):
            src1 = line[5:7]
            if (line[9:11].isdigit()):
                src2 = line[9:11]
                branch = line[12:]
            else:
                src2 = line[9]
                branch = line[11:]
        else:
            src1 = line[5]
            if (line[8:10].isdigit()):
                src2 = line[8:10]
                branch = line[11:]
            else:
                src2 = line[8]
                branch = line[10:]

        return line[0:3], int(src1), int(src2), branch

    elif (line[0:3] == "L.D"):

        if(line[line.index("(") + 1] != "$"):
            line = "($".join(line.split("("))

        # this means all registers are in single digits
        if (len(line) == 12):
            dest = line[5]
            offset = line[7]
            address = line[10]

        # this means one register is in double digits
        elif (len(line) == 13):
            if (line[5:7].isdigit()):
                dest = line[5:7]
                offset = line[8]
                address = line[11]
            elif (line[7:9].isdigit()):
                dest = line[5]
                offset = line[7:9]
                address = line[11]
            else:
                dest = line[5]
                offset = line[7]
                address = line[10:12]

        # this means 2 registers are in double digits
        elif (len(line) == 14):
            if (line[5:7].isdigit()):
                dest = line[5:7]

                if (line[7:9].isdigit()):
                    offset = line[7:9]
                    address = line[12]
                else:
                    offset = line[8]
                    address = line[11:13]
            else:
                dest = line[5]
                offset = line[7:9]
                address = line[11:13]

        # length would be 15 and all 3 inputs are in double digits
        else:
            dest = line[5:7]
            offset = line[8:10]
            address = line[12:14]
        return line[0:3], int(dest), int(offset), int(address)

    elif (line[0:3] == "S.D"):

        # this means all registers are in single digits
        if (len(line) == 12):
            dest = line[5]
            offset = line[7]
            address = line[10]

        # this means one register is in double digits
        elif (len(line) == 13):
            if (line[5:7].isdigit()):
                dest = line[5:7]
                offset = line[8]
                address = line[11]
            elif (line[7:9].isdigit()):
                dest = line[5]
                offset = line[7:9]
                address = line[11]
            else:
                dest = line[5]
                offset = line[7]
                address = line[10:12]

        # this means 2 registers are in double digits
        elif (len(line) == 14):
            if (line[5:7].isdigit()):
                dest = line[5:7]

                if (line[7:9].isdigit()):
                    offset = line[7:9]
                    address = line[12]
                else:
                    offset = line[8]
                    address = line[11:13]
            else:
                dest = line[5]
                offset = line[7:9]
                address = line[11:13]

        # length would be 15 and all 3 inputs are in double digits
        else:
            dest = line[5:7]
            offset = line[8:10]
            address = line[12:14]
        return line[0:3], int(dest), int(offset), int(address)

    elif (line[0:2] == "LW"):

        if(line[line.index("(") + 1] != "$"):
            line = "($".join(line.split("("))

        # to let me reuse code
        line = [] + line

        # this means all registers are in single digits
        if (len(line) == 12):
            dest = line[5]
            offset = line[7]
            address = line[10]

        # this means one register is in double digits
        elif (len(line) == 13):
            if (line[5:7].isdigit()):
                dest = line[5:7]
                offset = line[8]
                address = line[11]
            elif (line[7:9].isdigit()):
                dest = line[5]
                offset = line[7:9]
                address = line[11]
            else:
                dest = line[5]
                offset = line[7]
                address = line[10:12]

        # this means 2 registers are in double digits
        elif (len(line) == 14):
            if (line[5:7].isdigit()):
                dest = line[5:7]

                if (line[7:9].isdigit()):
                    offset = line[7:9]
                    address = line[12]
                else:
                    offset = line[8]
                    address = line[11:13]
            else:
                dest = line[5]
                offset = line[7:9]
                address = line[11:13]

        # length would be 15 and all 3 inputs are in double digits
        else:
            dest = line[5:7]
            offset = line[8:10]
            address = line[12:14]

        # restore it
        line = line[1:]

        return line[0:2], int(dest), int(offset), int(address)

    elif (line[0:2] == "SW"):

        # to let me reuse code
        line = [] + line

        # this means all registers are in single digits
        if (len(line) == 12):
            dest = line[5]
            offset = line[7]
            address = line[10]

        # this means one register is in double digits
        elif (len(line) == 13):
            if (line[5:7].isdigit()):
                dest = line[5:7]
                offset = line[8]
                address = line[11]
            elif (line[7:9].isdigit()):
                dest = line[5]
                offset = line[7:9]
                address = line[11]
            else:
                dest = line[5]
                offset = line[7]
                address = line[10:12]

        # this means 2 registers are in double digits
        elif (len(line) == 14):
            if (line[5:7].isdigit()):
                dest = line[5:7]

                if (line[7:9].isdigit()):
                    offset = line[7:9]
                    address = line[12]
                else:
                    offset = line[8]
                    address = line[11:13]
            else:
                dest = line[5]
                offset = line[7:9]
                address = line[11:13]

        # length would be 15 and all 3 inputs are in double digits
        else:
            dest = line[5:7]
            offset = line[8:10]
            address = line[12:14]

        # restore it
        line = line[1:]

        return line[0:2], int(dest), int(offset), int(address)

    elif (line[0:2] == "LI"):

        if (line[4:6].isdigit()):
            dest = line[4:6]
            if (len(line) == 9):
                immediate = line[7:]
            else:
                immediate = line[7]
        else:
            dest = line[4]
            immediate = line[6:]

        return line[0:2], int(dest), int(immediate), ""

    elif (line[0] == "J"):
        jmp_address = line[2:]

        return line[0], line[2:], "", ""



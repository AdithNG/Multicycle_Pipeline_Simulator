from components import process_command  # import the process command function


# This class is an instruction object
# It holds its type, and other attributes
class Instruction:
    def __init__(self, full_name, instruction_name, parameter1, parameter2=None, parameter3=None):

        # the full line as a string
        self.full_name = full_name

        # the name of the instruction, a string
        self.instruction = instruction_name

        # the 3 parameters pulled from the process_command function
        self.parameter1 = parameter1
        self.parameter2 = parameter2
        self.parameter3 = parameter3

        # how many times more it needs to run through the execute
        self.cycles_left = 0

        # when the instruction has done everything
        self.completed = False

        # if a data dependency is detected in the decode stage
        self.shouldStall = False

        # will hold data that will need to be written once it reaches the right stage
        self.to_mem = ""
        self.to_int_reg = ""
        self.to_fp_reg = ""

        # indicates that the source registers (neither, one, or both of them) need the their data forwarded to them
        self.forwarding1 = False
        self.forwarding2 = False

        # -1 denotes that it dosn't apply to instruction, but this is for cache misses
        self.mem_cycles_left = -1

    # this function will determine the instruction, and how many execute cycles it needs
    def decode(self):

        if (self.instruction == "L.D"):
            self.cycles_left = 1
        elif (self.instruction == "S.D"):
            self.cycles_left = 1
        elif (self.instruction == "LI"):
            self.cycles_left = 1
        elif (self.instruction == "LW"):
            self.cycles_left = 1
        elif (self.instruction == "SW"):
            self.cycles_left = 1
        elif (self.instruction == "ADD"):
            self.cycles_left = 1
        elif (self.instruction == "ADDI"):
            self.cycles_left = 1
        elif (self.instruction == "ADD.D"):
            self.cycles_left = 2
        elif (self.instruction == "SUB.D"):
            self.cycles_left = 2
        elif (self.instruction == "SUB"):
            self.cycles_left = 1
        elif (self.instruction == "MUL.D"):
            self.cycles_left = 10
        elif (self.instruction == "DIV.D"):
            self.cycles_left = 40
        elif (self.instruction == "BEQ"):
            self.cycles_left = 1
        elif (self.instruction == "BNE"):
            self.cycles_left = 1
        elif (self.instruction == "J"):
            self.cycles_left = 1


# the lifeblood of the project
class Processor:
    def __init__(self):

        # how many cycles different commands need
        self.fp_adder_pipeline_cycles = 2
        self.fp_multiplier_pipeline_cycles = 10
        self.fp_divider_pipeline_cycles = 40
        self.integer_unit_cycles = 1

        # defining registers and pre-loading memory
        self.fp_registers = [0.0] * 32
        self.int_registers = [0] * 32
        self.memory = [45, 12, 0, 92, 10, 135, 254, 127, 18, 4, 55, 8, 2, 98, 13, 5, 233, 158, 167]

        # for branching
        self.branch_prediction = 1

        self.instructions = []  # holds instruction strings
        self.instruction_objects = []  # holds instruction objects

        self.next_instruction = 0  # to be loaded into the IF stage
        self.fetched_instruction = ""  # IF stage
        self.decoded_instruction = ""  # Decode Stage
        self.executed_instruction = ""  # EX stage
        self.memory_instruction = ""  # Memory stage
        self.writeback_instruction = ""  # Writeback Stage

        # if a register is here and a source for a future instruction, a data dependency is recognized
        self.busy_fp_registers = []
        self.busy_int_registers = []

        # this is where results are forwarded
        self.forwarding_int = {}
        self.forwarding_fp = {}

        # keep track of clock cycles
        self.clock_cycle = 0

        # keep track of whether stages need to stall
        self.IF_stall = False
        self.ID_stall = False
        self.EX_stall = False
        self.MEM_stall = False
        self.EX_repeat = False

        # store subroutines
        self.subroutines = {}

        # the 4 cache blocks
        self.cache = [(-1, 0), (-1, 0), (-1, 0), (-1, 0)]

        # to hold the results
        self.pipeLineResults = []

    # read the instruction file and load the instructions
    def process_instruction_file(self, filename):
        with open(filename, 'r') as file:
            instructions = file.readlines()
        instructions = [line.strip() for line in instructions]
        self.instructions = instructions

        for i in range(len(self.instructions)):

            if (":" in self.instructions[i]):
                subroutine = self.instructions[i][0:self.instructions[i].find(":")]
                self.subroutines[subroutine] = i

    # fetch the next instruction based on the index given
    def fetch_instruction(self, index):
        if index < len(self.instructions):
            self.fetched_instruction = self.instructions[index]

            self.instruction_objects.append("")
            self.pipeLineResults.append([self.fetched_instruction])
            for i in range(0, self.clock_cycle + 1):
                self.pipeLineResults[len(self.pipeLineResults) - 1].append("  ")
        else:
            self.fetched_instruction = ""
        return self.fetched_instruction

    # convert the instruction to an instruction object
    # and search for data dependencies
    def decode_instruction(self, line):
        self.decoded_instruction = line

        # fall safe against empty instruction objects
        if (line != ""):

            # get the relevant instruction stsring
            row = self.find_index(line)

            if 'wb' in self.pipeLineResults[row]:
                self.decoded_instruction = ""
                return

            # get the parameters of the instruction
            name, par1, par2, par3 = process_command(line)

            # make it into an object
            instruction = Instruction(line, name, par1, par2, par3)
            self.instruction_objects[row] = instruction

            # decode it to get the number of cycles
            instruction.decode()

            # fetch next instruction if not stall or branch instruction
            if "id" not in self.pipeLineResults[row]:
                if (name in ["BEQ", "BNE"] and self.branch_prediction == 1) or name == "J":
                    subroutine = line.split()[-1].split(",")[-1]
                    self.next_instruction = self.subroutines[subroutine]
                else:
                    self.next_instruction += 1
            else:
                self.next_instruction += 1

            # second and third parameters read from registers
            if (instruction.instruction in ["ADD", "ADD.D", "SUB.D", "SUB", "MUL.D", "DIV.D"]):

                # seeing if any source int registers are pending results from a prior instruction
                if (instruction.instruction in ["ADD", "SUB"]):
                    if (
                            instruction.parameter2 in self.busy_int_registers or instruction.parameter3 in self.busy_int_registers):
                        instruction.shouldStall = True
                        self.ID_stall = True
                        self.IF_stall = True
                    else:
                        instruction.shouldStall = False
                        self.ID_stall = False
                        self.IF_stall = False
                        if instruction.parameter2 in self.forwarding_int:
                            instruction.forwarding1 = True
                        elif instruction.parameter3 in self.forwarding_int:
                            instruction.forwarding2 = True
                else:
                    if (
                            instruction.parameter2 in self.busy_fp_registers or instruction.parameter3 in self.busy_fp_registers):
                        instruction.shouldStall = True
                        self.ID_stall = True
                        self.IF_stall = True
                    else:
                        instruction.shouldStall = False
                        self.ID_stall = False
                        self.IF_stall = False
                        if instruction.parameter2 in self.forwarding_fp:
                            instruction.forwarding1 = True
                        elif instruction.parameter3 in self.forwarding_fp:
                            instruction.forwarding2 = True

            # first parameter reads from a register, search for data dependencies in the floating point registers
            elif (instruction.instruction in ["S.D", "SW"]):
                if (instruction.instruction == "S.D"):
                    if (instruction.parameter1 in self.busy_fp_registers):
                        instruction.shouldStall = True
                        self.ID_stall = True
                        self.IF_stall = True
                    else:
                        instruction.shouldStall = False
                        self.ID_stall = False
                        self.IF_stall = False
                        if instruction.parameter1 in self.forwarding_fp:
                            instruction.forwarding1 = True
                            instruction.forwarding2 = True

                else:
                    if (instruction.parameter1 in self.busy_int_registers):
                        instruction.shouldStall = True
                        self.ID_stall = True
                        self.IF_stall = True
                    else:
                        instruction.shouldStall = False
                        self.ID_stall = False
                        self.IF_stall = False
                        if instruction.parameter1 in self.forwarding_int:
                            instruction.forwarding1 = True
                            instruction.forwarding2 = True

            # second parameter reads from a register, special case, but still possibility for data dependencies
            elif (instruction.instruction == "ADDI"):
                if (instruction.parameter2 in self.busy_int_registers):
                    instruction.shouldStall = True
                    self.ID_stall = True
                    self.IF_stall = True
                else:
                    instruction.shouldStall = False
                    self.ID_stall = False
                    self.IF_stall = False
                    if instruction.parameter2 in self.forwarding_int:
                        instruction.forwarding1 = True
                        instruction.forwarding2 = True

            # load from memory, since mems happen in order, there should be no hazards here
            # LI only puts it in the register in the Writeback stage, so also, no memory hazards
            elif (instruction.instruction in ["L.D", "LW", "LI"]):
                if ('$' in line.split()[-1]):
                    if instruction.parameter3 in self.busy_int_registers:
                        instruction.shouldStall = True
                        self.ID_stall = True
                        self.IF_stall = True
                    else:
                        instruction.shouldStall = False
                        self.ID_stall = False
                        self.IF_stall = False
                        if instruction.parameter3 in self.forwarding_int:
                            instruction.forwarding1 = True
                            instruction.forwarding2 = True
                else:
                    instruction.shouldStall = False
                    self.ID_stall = False
                    self.IF_stall = False


            # once again, search for data dependencies in the source registers, here its the first and/or second parameters
            elif (instruction.instruction in ["BEQ", "BNE"]):
                if instruction.parameter1 in self.busy_int_registers or instruction.parameter2 in self.busy_int_registers:
                    instruction.shouldStall = True
                    self.ID_stall = True
                    self.IF_stall = True
                else:
                    instruction.shouldStall = False
                    self.ID_stall = False
                    self.IF_stall = False
                    if instruction.parameter1 in self.forwarding_int:
                        instruction.forwarding1 = True
                    if instruction.parameter2:
                        instruction.forwarding2 = True

            # if the instruction has no data dependencies, then add their destination to the busy registers list
            if (instruction.instruction in ["L.D", "ADD.D", "SUB.D", "MUL.D", "DIV.D"]):
                if not (instruction.shouldStall):
                    self.busy_fp_registers.append(instruction.parameter1)
            elif (instruction.instruction in ["LI", "LW", "ADD", "ADDI", "SUB"]):
                if not (instruction.shouldStall):
                    self.busy_int_registers.append(instruction.parameter1)

    # this function executes the ALU dependent instructions
    def execute_instruction(self, line):
        self.executed_instruction = line

        if line != "":
            row = self.find_index(line)
            if 'wb' in self.pipeLineResults[row]:
                self.executed_instruction = ""
                return
            instruction = self.instruction_objects[self.find_index(line)]

            # see how many cycles are left, only compute on the final cycle
            if (instruction.cycles_left > 1):
                instruction.cycles_left -= 1
                self.EX_repeat = True
            else:
                instruction.cycles_left -= 1
                instruction.completed = True

                # Load instructions read in mem stage and write in wb
                if (instruction.instruction == "L.D"):
                    if ('$' in line.split()[-1]):
                        self.busy_fp_registers.remove(
                            instruction.parameter3) if instruction.parameter3 in self.busy_fp_registers else None
                        if instruction.forwarding1:

                            instruction.parameter3 = self.forwarding_int[instruction.parameter3]
                        else:

                            instruction.parameter3 = self.fp_registers[instruction.parameter3]

                # pull the data from the registers or forwarding dictionary
                # will be written in mem stage
                elif (instruction.instruction == "S.D"):
                    if instruction.forwarding1:
                        instruction.to_mem = self.forwarding_fp[instruction.parameter1]
                    else:
                        instruction.to_mem = self.fp_registers[instruction.parameter1]

                # nothing to do here yet
                elif (instruction.instruction == "LI"):
                    pass
                elif (instruction.instruction == "LW"):
                    pass

                # same logic as S.D, but with int registers
                elif (instruction.instruction == "SW"):
                    if instruction.forwarding1:
                        instruction.to_mem = self.forwarding_int[instruction.parameter1]
                    else:
                        instruction.to_mem = self.int_registers[instruction.parameter1]

                # "ALU Ops" Compute and store the result in the to_xx where xx is the destination location, either an int or fp register
                elif (instruction.instruction == "ADD"):
                    if instruction.forwarding1:
                        param2 = self.forwarding_int[instruction.parameter2]
                    else:
                        param2 = self.int_registers[instruction.parameter2]
                    if instruction.forwarding2:
                        param3 = self.forwarding_int[instruction.parameter3]
                    else:
                        param2 = self.int_registers[instruction.parameter3]
                    instruction.to_int_reg = param2 + param3
                    self.forwarding_int[instruction.parameter1] = instruction.to_int_reg

                # ALU ops continued
                elif (instruction.instruction == "ADDI"):
                    if instruction.forwarding1:
                        param2 = self.forwarding_int[instruction.parameter2]
                    else:
                        param2 = self.int_registers[instruction.parameter2]

                    instruction.to_int_reg = param2 + instruction.parameter3
                    self.forwarding_int[instruction.parameter1] = instruction.to_int_reg

                elif (instruction.instruction == "ADD.D"):
                    if instruction.forwarding1:
                        param2 = self.forwarding_fp[instruction.parameter2]
                    else:
                        param2 = self.fp_registers[instruction.parameter2]
                    if instruction.forwarding2:
                        param3 = self.forwarding_fp[instruction.parameter3]
                    else:
                        param2 = self.fp_registers[instruction.parameter3]

                    instruction.to_fp_reg = param2 + param3
                    self.forwarding_fp[instruction.parameter1] = instruction.to_fp_reg

                elif (instruction.instruction == "SUB.D"):
                    if instruction.forwarding1:
                        param2 = self.forwarding_fp[instruction.parameter2]
                    else:
                        param2 = self.fp_registers[instruction.parameter2]
                    if instruction.forwarding2:
                        param3 = self.forwarding_fp[instruction.parameter3]
                    else:
                        param2 = self.fp_registers[instruction.parameter3]

                    instruction.to_fp_reg = param2 - param3
                    self.forwarding_fp[instruction.parameter1] = instruction.to_fp_reg

                elif (instruction.instruction == "SUB"):
                    if instruction.forwarding1:
                        param2 = self.forwarding_int[instruction.parameter2]
                    else:
                        param2 = self.int_registers[instruction.parameter2]
                    if instruction.forwarding2:
                        param3 = self.forwarding_int[instruction.parameter3]
                    else:
                        param2 = self.int_registers[instruction.parameter3]

                    instruction.to_int_reg = param2 - param3
                    self.forwarding_int[instruction.parameter1] = instruction.to_int_reg

                elif (instruction.instruction == "MUL.D"):
                    if instruction.forwarding1:
                        param2 = self.forwarding_fp[instruction.parameter2]
                    else:
                        param2 = self.fp_registers[instruction.parameter2]
                    if instruction.forwarding2:
                        param3 = self.forwarding_fp[instruction.parameter3]
                    else:
                        param2 = self.fp_registers[instruction.parameter3]

                    instruction.to_fp_reg = param2 * param3
                    self.forwarding_fp[instruction.parameter1] = instruction.to_fp_reg

                elif (instruction.instruction == "DIV.D"):
                    if instruction.forwarding1:
                        param2 = self.forwarding_fp[instruction.parameter2]
                    else:
                        param2 = self.fp_registers[instruction.parameter2]
                    if instruction.forwarding2:
                        param3 = self.forwarding_fp[instruction.parameter3]
                    else:
                        param2 = self.fp_registers[instruction.parameter3]

                    instruction.to_fp_reg = param2 / param3
                    self.forwarding_fp[instruction.parameter1] = instruction.to_fp_reg


                # branching also uses the "ALU"
                elif (instruction.instruction == "BEQ"):
                    if instruction.forwarding1:
                        param1 = self.forwarding_int[instruction.parameter1]
                    else:
                        param1 = self.int_registers[instruction.parameter1]

                    if instruction.forwarding2:
                        param2 = self.forwarding_int[instruction.parameter2]
                    else:
                        param2 = self.int_registers[instruction.parameter2]

                    # if path taken and branch prediction are different, flush pipieline
                    if (param1 == param2 and self.branch_prediction == 0):
                        self.branch_prediction = 1
                        self.flush_pipeline()
                    elif (param1 != param2 and self.branch_prediction == 1):
                        self.branch_prediction = 0
                        self.flush_pipeline()

                elif (instruction.instruction == "BNE"):
                    if instruction.forwarding1:
                        param1 = self.forwarding_int[instruction.parameter1]
                    else:
                        param1 = self.int_registers[instruction.parameter1]

                    if instruction.forwarding2:
                        param2 = self.forwarding_int[instruction.parameter2]
                    else:
                        param2 = self.int_registers[instruction.parameter2]

                    # if path taken and branch prediction are different, flush pipieline
                    if (param1 != param2 and self.branch_prediction == 0):
                        self.branch_prediction = 1
                        self.flush_pipeline()
                    elif (param1 == param2 and self.branch_prediction == 1):
                        self.branch_prediction = 0
                        self.flush_pipeline()

                elif (instruction.instruction == "J"):
                    pass

                if instruction.instruction in ["ADD.D", "SUB.D", "MUL.D", "DIV.D"]:
                    self.busy_fp_registers.remove(
                        instruction.parameter1) if instruction.parameter1 in self.busy_fp_registers else None
                else:
                    self.busy_int_registers.remove(
                        instruction.parameter1) if instruction.parameter1 in self.busy_int_registers else None

    # this step is for reading and writing to memory
    def mem_instruction(self, line):
        self.memory_instruction = line

        # fail safe for blank instructions
        if line != "":
            row = self.find_index(line)
            if 'wb' in self.pipeLineResults[row]:
                self.memory_instruction = ""
                return

            # pull instruction
            instruction = self.instruction_objects[self.find_index(line)]

            # holds true for anything that has to do with cache, irrelevant otherwise

            if (instruction.instruction in ["L.D", "S.D", "SW", "LW"]):
                mem_location = (instruction.parameter3 + instruction.parameter2) % 19
                cache_location = mem_location % 4

            # try and search the cache, apply the miss penalty if needed
            if (instruction.instruction == "L.D"):
                # first time trying to check cache
                if (instruction.mem_cycles_left == -1):

                    # hit
                    if (self.cache[cache_location][0] == -1 or self.cache[cache_location][0] == mem_location):
                        mem_cycles_left = 0
                        instruction.to_fp_reg = self.cache[cache_location][1]
                        self.forwarding_fp[instruction.parameter1] = instruction.to_fp_reg

                    # miss
                    else:
                        mem_cycles_left = 2

                # still under penalty
                elif (instruction.mem_cycles_left == 2):
                    instruction.mem_cycles_left -= 1
                elif (instruction.mem_cycles_left == 1):

                    # penalty for miss served, now load from memory and place in cache
                    instruction.mem_cycles_left -= 1
                    instruction.to_fp_reg = self.memory[mem_location]
                    self.cache[cache_location] == (mem_location, instruction.to_fp_reg)
                    self.forwarding_fp[instruction.parameter1] = instruction.to_fp_reg

            # store in memory location and cache
            elif (instruction.instruction == "S.D"):
                self.memory[mem_location] = instruction.to_mem
                self.cache[cache_location] = (mem_location, instruction.to_mem)
                instruction.mem_cycles_left = 0

            # no actual memory involved, just get ready to store in register
            elif (instruction.instruction == "LI"):
                instruction.to_int_reg = instruction.parameter2
                instruction.mem_cycles_left = 0

                self.forwarding_int[instruction.parameter1] = instruction.to_int_reg

            # Just like L.D
            elif (instruction.instruction == "LW"):
                # first time trying to check cache
                if (instruction.mem_cycles_left == -1):

                    # hit
                    if (self.cache[cache_location][0] == -1 or self.cache[cache_location][0] == mem_location):
                        mem_cycles_left = 0
                        instruction.to_int_reg = self.cache[cache_location][1]
                        self.forwarding_int[instruction.parameter1] = instruction.to_int_reg
                    # miss
                    else:
                        mem_cycles_left = 2

                # still under penalty
                elif (instruction.mem_cycles_left == 2):
                    instruction.mem_cycles_left -= 1
                elif (instruction.mem_cycles_left == 1):

                    # penalty for miss served, now load from memory and place in cache
                    instruction.mem_cycles_left -= 1
                    instruction.to_int_reg = self.memory[mem_location]
                    self.cache[cache_location] == (mem_location, instruction.to_fp_reg)
                    self.forwarding_int[instruction.parameter1] = instruction.to_int_reg

            # store in memory and cache
            elif (instruction.instruction == "SW"):
                self.memory[mem_location] = instruction.to_mem
                self.cache[cache_location] = (mem_location, instruction.to_mem)
                instruction.mem_cycles_left = 0

            # none of the other instructions need to go into memory
            else:
                instruction.mem_cycles_left == 0

    # for writing to registers
    def writeBack_instruction(self, line):
        self.writeback_instruction = line

        # failsafe against blank instruction objects (AKA empty strings)
        if line != "":
            row = self.find_index(line)

            if 'wb' in self.pipeLineResults[row]:
                self.writeback_instruction = ""
                return

            instruction = self.instruction_objects[self.find_index(line)]

            # write to correct register if an applicable instruction is here
            if (instruction.instruction in ["L.D", "ADD.D", "SUB.D", "MUL.D", "DIV.D"]):
                self.fp_registers[instruction.parameter1] = instruction.to_fp_reg
            elif (instruction.instruction in ["LI", "LW", "ADD", "SUB", "ADDI"]):
                self.int_registers[instruction.parameter1] = instruction.to_int_reg

    # clean pipeline (for branching)
    def flush_pipeline(self):
        self.fetched_instruction = ""
        self.decoded_instruction = ""
        self.executed_instruction = ""

    # output all the registers
    def print_registers(self):
        print("Integer Registers:")
        for i in range(len(self.int_registers)):
            print(f"R{i}: {self.int_registers[i]}")
        print("\nFloating-Point Registers:")
        for i in range(len(self.fp_registers)):
            print(f"F{i}: {self.fp_registers[i]}")

    # output all memory
    def print_memory(self):
        print("Memory:")
        for i in range(len(self.memory)):
            print(f"{i}: {self.memory[i]}")

    # manages the pipeline
    def run_pipeline(self):

        # while there are instructions to process, keep going
        while not (
                self.fetched_instruction == "" and self.decoded_instruction == "" and self.executed_instruction == "" and self.memory_instruction == "" and self.writeback_instruction == "") or self.next_instruction == 0:
            [row.append("  ") for row in self.pipeLineResults]

            # WB Stage
            self.writeBack_instruction(self.memory_instruction)

            '''

            if self.MEM_stall:
                self.mem_instruction(self.memory_instruction)
            else:
            '''
            # MEM Stage
            self.mem_instruction(self.executed_instruction)
            '''

            if self.EX_stall or self.EX_repeat:
                self.execute_instruction(self.executed_instruction)
            else:
            '''
            # EX Stage
            self.execute_instruction(self.decoded_instruction)

            '''
            if self.ID_stall:
                self.decode_instruction(self.decoded_instruction)
            else:
            '''
            # ID Stage
            self.decode_instruction(self.fetched_instruction)

            # IF Stage
            self.fetch_instruction(self.next_instruction)

            self.clock_cycle += 1
            self.update_column()
        [print(row) for row in self.pipeLineResults]
        print(" ")
        self.print_registers()
        print(" ")
        self.print_memory()

    # Updates a new column
    def update_column(self):

        # Updates WB block
        if self.writeback_instruction != "":
            row = self.find_index(self.writeback_instruction)
            col = self.clock_cycle
            if 'wb' not in self.pipeLineResults[row]:
                self.pipeLineResults[row][col] = "wb"

        # Updates MEM block
        if self.memory_instruction != "":
            row = self.find_index(self.memory_instruction)
            col = self.clock_cycle
            self.pipeLineResults[row][col] = "mem"

        # updates EX block
        if self.executed_instruction != "":
            row = self.find_index(self.executed_instruction)
            col = self.clock_cycle

            # If instruction had a lable
            if self.executed_instruction[:5] != "Loop:":
                # if instruction was not FP instruction
                if self.executed_instruction[:5] not in ["ADD.D", "SUB.D", "MUL.D", "DIV.D"]:
                    if self.EX_stall and 'ex' in self.pipeLineResults[row]:
                        self.pipeLineResults[row][col] = 'stall'
                    self.pipeLineResults[row][col] = "ex"
                else:
                    instruction = self.instruction_objects[row]
                    if instruction.instruction in ["ADD.D", "SUB.D"]:
                        output = "A" + str(2 - instruction.cycles_left)
                        self.pipeLineResults[row][col] = output
                    elif instruction.instruction == "MUL.D":
                        output = "M" + str(10 - instruction.cycles_left)
                        self.pipeLineResults[row][col] = output
                    elif instruction.instruction == "DIV.D":
                        output = "D" + str(40 - instruction.cycles_left)
                        self.pipeLineResults[row][col] = output
            else:
                # If instruction was not FP instruction
                if self.executed_instruction.split()[1] not in ["ADD.D", "SUB.D", "MUL.D", "DIV.D"]:
                    if self.EX_stall and 'ex' in self.pipeLineResults[row]:
                        self.pipeLineResults[row][col] = 'stall'
                    else:
                        self.pipeLineResults[row][col] = "ex"
                else:
                    instruction = self.instruction_objects[row]
                    if instruction.instruction in ["ADD.D", "SUB.D"]:
                        output = "A" + str(2 - instruction.cycles_left)
                        self.pipeLineResults[row][col] = output
                    elif instruction.instruction == "MUL.D":
                        output = "M" + str(10 - instruction.cycles_left)
                        self.pipeLineResults[row][col] = output
                    elif instruction.instruction == "DIV.D":
                        output = "D" + str(40 - instruction.cycles_left)
                        self.pipeLineResults[row][col] = output

        # Updates ID block
        if self.decoded_instruction != "":
            row = self.find_index(self.decoded_instruction)
            col = self.clock_cycle
            instruction = self.instruction_objects[row]
            if self.ID_stall:
                if 'id' not in self.pipeLineResults[row]:
                    self.pipeLineResults[row][col] = "id"
                else:
                    self.pipeLineResults[row][col] = "stall"
            else:
                self.pipeLineResults[row][col] = "id"

        # Updates IF block
        if self.fetched_instruction != "":
            row = self.find_index(self.fetched_instruction)
            col = self.clock_cycle
            instruction = self.instruction_objects[row]
            if self.IF_stall:
                if 'if' not in self.pipeLineResults[row]:
                    self.pipeLineResults[row][col] = "if"
                else:
                    self.pipeLineResults[row][col] = "stall"
            else:
                self.pipeLineResults[row][col] = "if"

    # Find index of line in pipelineResults
    def find_index(self, line):
        for i in range(len(self.pipeLineResults) - 1, 0, -1):
            if self.pipeLineResults[i][0] == line:
                return i
        return 0


if __name__ == '__main__':
    processor = Processor()

    # Take the instruction file name as user input
    filename = input("Enter the instruction file name: ")

    # Process the instruction file
    processor.process_instruction_file(filename)
    processor.run_pipeline()

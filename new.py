from components import process_command

nonexecution_stages = ["if", "id", "mem", "wb"]
additionCycle = ["if", "id", "A1", "A2", "mem", "wb"]
subtractionCycle = ["if", "id", "A1", "A2", "mem", "wb"]
multiplicationCycle = ["if", "id", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "mem", "wb"]
divisionCycle = ["if", "id"] + ["D" + str(i) for i in range(1, 41)] + ["mem", "wb"]
oneCycle = ["if", "id", "ex", "mem", "wb"]


class Instruction:
    def __init__(self, full_name, instruction_name, parameter1, parameter2=None, parameter3=None):

        self.full_name = full_name

        self.instruction = instruction_name

        self.parameter1 = parameter1
        self.parameter2 = parameter2
        self.parameter3 = parameter3

        self.cycles_left = 0

        self.completed = False

        self.shouldStall = False

        self.to_mem = ""
        self.to_int_reg = ""
        self.to_fp_reg = ""

        self.forwarding1 = False
        self.forwarding2 = False

        # -1 denotes that it dosn't apply to instruction
        self.mem_cycles_left = -1

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


class Processor:
    def __init__(self):
        self.fp_adder_pipeline_cycles = 2
        self.fp_multiplier_pipeline_cycles = 10
        self.fp_divider_pipeline_cycles = 40
        self.integer_unit_cycles = 1
        self.fp_registers = [0.0] * 32
        self.int_registers = [0] * 32
        self.memory = [45, 12, 0, 92, 10, 135, 254, 127, 18, 4, 55, 8, 2, 98, 13, 5, 233, 158, 167]
        self.branch_prediction = 1
        self.instructions = []
        self.instruction_objects = []
        self.next_instruction = 0
        self.fetched_instruction = ""
        self.decoded_instruction = ""
        self.executed_instruction = ""
        self.memory_instruction = ""
        self.writeback_instruction = ""
        self.busy_fp_registers = []
        self.busy_int_registers = []
        self.forwarding_int = {}
        self.forwarding_fp = {}
        self.clock_cycle = 0
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

    def process_instruction_file(self, filename):
        with open(filename, 'r') as file:
            instructions = file.readlines()
        instructions = [line.strip() for line in instructions]
        self.instructions = instructions

        for i in range(len(self.instructions)):

            if (":" in self.instructions[i]):
                subroutine = self.instructions[i][0:self.instructions[i].find(":")]
                self.subroutines[subroutine] = i

    def fetch_instruction(self, index):
        print("Index:", index)
        if index < len(self.instructions):
            self.instruction_objects.append("")

            line = self.instructions[index]
            row = self.find_index(line)

            name, par1, par2, par3 = process_command(line)
            instruction = Instruction(line, name, par1, par2, par3)
            self.instruction_objects[row] = instruction
            instruction.decode()

            self.fetched_instruction = instruction
            print(name, par1, par2, par3)
            print("fetched:", self.fetched_instruction)

            self.pipeLineResults.append([self.fetched_instruction.full_name])
            for i in range(0, self.clock_cycle + 1):
                self.pipeLineResults[len(self.pipeLineResults) - 1].append("  ")
        else:
            self.fetched_instruction = ""
        return self.fetched_instruction

    def decode_instruction(self, instruction):

        if (not isinstance(instruction, str)):

            row = self.find_index(instruction.full_name)

            if 'wb' in self.pipeLineResults[row]:
                self.decoded_instruction = ""
                return

            if "id" not in self.pipeLineResults[row]:
                if (instruction.instruction in ["BEQ", "BNE"] and self.branch_prediction == 1) or instruction.instruction == "J":
                    subroutine = instruction.full_name.split()[-1].split(",")[-1]
                    self.next_instruction = self.subroutines[subroutine]
                else:
                    self.next_instruction += 1

            # second and third parameters read from registers
            if (instruction.instruction in ["ADD", "ADD.D", "SUB.D", "SUB", "MUL.D", "DIV.D"]):

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

            # first parameter reads from a register
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

            # second parameter reads from a register
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
                if ('$' in instruction.full_name.split()[-1]):
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

            if (instruction.instruction in ["L.D", "ADD.D", "SUB.D", "MUL.D", "DIV.D"]):
                if not (instruction.shouldStall):
                    self.busy_fp_registers.append(instruction.parameter1)
            elif (instruction.instruction in ["LI", "LW", "ADD", "ADDI", "SUB"]):
                if not (instruction.shouldStall):
                    self.busy_int_registers.append(instruction.parameter1)

    def execute_instruction(self, instruction):

        if not isinstance(instruction, str):
            row = self.find_index(instruction.full_name)
            if 'wb' in self.pipeLineResults[row]:
                self.executed_instruction = ""
                return

            if (instruction.cycles_left > 1):
                instruction.cycles_left -= 1
                self.EX_repeat = True
            else:
                instruction.cycles_left -= 1
                instruction.completed = True

                # the passes will be done in the mem stage
                if (instruction.instruction == "L.D"):
                    if ('$' in instruction.full_name.split()[-1]):
                        self.busy_fp_registers.remove(
                            instruction.parameter3) if instruction.parameter3 in self.busy_fp_registers else None
                        if instruction.forwarding1:
                            print("Check:", self.forwarding_int)
                            instruction.parameter3 = self.forwarding_int[instruction.parameter3]
                        else:
                            print("Check:", self.forwarding_int)
                            instruction.parameter3 = self.fp_registers[instruction.parameter3]

                elif (instruction.instruction == "S.D"):
                    if instruction.forwarding1:
                        instruction.to_mem = self.forwarding_fp[instruction.parameter1]
                    else:
                        instruction.to_mem = self.fp_registers[instruction.parameter1]

                elif (instruction.instruction == "LI"):
                    pass
                elif (instruction.instruction == "LW"):
                    pass

                elif (instruction.instruction == "SW"):
                    if instruction.forwarding1:
                        instruction.to_mem = self.forwarding_int[instruction.parameter1]
                    else:
                        instruction.to_mem = self.int_registers[instruction.parameter1]

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

                elif (instruction.instruction == "BEQ"):
                    if instruction.forwarding1:
                        param1 = self.forwarding_int[instruction.parameter1]
                    else:
                        param1 = self.int_registers[instruction.parameter1]

                    if instruction.forwarding2:
                        param2 = self.forwarding_int[instruction.parameter2]
                    else:
                        param2 = self.int_registers[instruction.parameter2]

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
                    print("Params:", param1, param2)
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

    def mem_instruction(self, instruction):

        if not isinstance(instruction, str):
            row = self.find_index(instruction.full_name)
            if 'wb' in self.pipeLineResults[row]:
                self.memory_instruction = ""
                return

            instruction = self.instruction_objects[self.find_index(instruction.full_name)]

            # holds true for anything that has to do with cache, irrelevant otherwise
            print(instruction.instruction, instruction.parameter1, instruction.parameter2, instruction.parameter3)
            if (instruction.instruction in ["L.D", "S.D", "SW", "LW"]):
                mem_location = (instruction.parameter3 + instruction.parameter2) % 19
                cache_location = mem_location % 4

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
                print("To_int_reg:", instruction.to_int_reg)
                self.forwarding_int[instruction.parameter1] = instruction.to_int_reg

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

    def writeBack_instruction(self, instruction):

        if not isinstance(instruction, str):
            row = self.find_index(instruction.full_name)
            if 'wb' in self.pipeLineResults[row]:
                self.writeback_instruction = ""
                return

            instruction = self.instruction_objects[self.find_index(instruction.full_name)]

            if (instruction.instruction in ["L.D", "ADD.D", "SUB.D", "MUL.D", "DIV.D"]):
                self.fp_registers[instruction.parameter1] = instruction.to_fp_reg
            elif (instruction.instruction in ["LI", "LW", "ADD", "SUB", "ADDI"]):
                self.int_registers[instruction.parameter1] = instruction.to_int_reg

    def flush_pipeline(self):
        self.fetched_instruction = ""  #
        self.decoded_instruction = ""
        self.executed_instruction = ""

    def print_registers(self):
        print("Integer Registers:")
        for i in range(len(self.int_registers)):
            print(f"R{i}: {self.int_registers[i]}")
        print("\nFloating-Point Registers:")
        for i in range(len(self.fp_registers)):
            print(f"F{i}: {self.fp_registers[i]}")

    def run_pipeline(self):

        while not (
                self.fetched_instruction == "" and self.decoded_instruction == "" and self.executed_instruction == "" and self.memory_instruction == "" and self.writeback_instruction == "") or self.next_instruction == 0:
            [row.append("  ") for row in self.pipeLineResults]

            # WB Stage
            self.writeBack_instruction(self.writeback_instruction)
            #
            self.writeback_instruction = ""

            '''

            if self.MEM_stall:
                self.mem_instruction(self.memory_instruction)
            else:
            '''
            # MEM Stage
            self.mem_instruction(self.memory_instruction)
            if (not isinstance(self.memory_instruction,str)):
                if (self.memory_instruction.mem_cycles_left == 0):
                    self.writeback_instruction = self.memory_instruction
                    self.memory_instruction = ""
                else:
                    pass
            '''

            if self.EX_stall or self.EX_repeat:
                self.execute_instruction(self.executed_instruction)
            else:
            '''
            # EX Stage
            self.execute_instruction(self.executed_instruction)
            if (not isinstance(self.executed_instruction, str)):
                if (self.executed_instruction.cycles_left > 0):
                    self.memory_instruction = ""
                elif self.executed_instruction == 0:
                    self.memory_instruction = self.executed_instruction
                    self.executed_instruction = ""
                elif (not isinstance(self.memory_instruction, str)):
                    pass
                else:
                    self.execute_instruction(self.executed_instruction)

            '''
            if self.ID_stall:
                self.decode_instruction(self.decoded_instruction)
            else:
            '''
            # ID Stage
            self.decode_instruction(self.decoded_instruction)
            if (not isinstance(self.decoded_instruction, str)):
                if (self.decoded_instruction.shouldStall or isinstance(self.executed_instruction, str)):
                    pass
                else:
                    self.executed_instruction = self.decoded_instruction
                    self.decoded_instruction = ""

            # IF Stage
            if (isinstance(self.decoded_instruction, str)):
                self.decoded_instruction = self.fetched_instruction
                self.fetched_instruction = self.fetch_instruction(self.next_instruction)
            else:
                pass

            self.clock_cycle += 1
            self.update_column()
            [print(row) for row in self.pipeLineResults]
            print(" ")
        self.print_registers()

    def update_column(self):
        #print("Update fetched:", self.fetched_instruction.full_name)
        #print("Update decoded:", self.decoded_instruction.full_name)
        #print("Update executed:", self.executed_instruction.full_name)
        #print("Update memory:", self.memory_instruction.full_name)
        #print("Update writeback:", self.writeback_instruction.full_name)

        if not isinstance(self.writeback_instruction, str):
            row = self.find_index(self.writeback_instruction.full_name)
            col = self.clock_cycle
            if 'wb' not in self.pipeLineResults[row]:
                self.pipeLineResults[row][col] = "wb"

        if not isinstance(self.memory_instruction, str):
            row = self.find_index(self.memory_instruction.full_name)
            col = self.clock_cycle
            self.pipeLineResults[row][col] = "mem"

        if not isinstance(self.executed_instruction, str):
            row = self.find_index(self.executed_instruction.full_name)
            col = self.clock_cycle
            if self.executed_instruction.full_name[:5] != "Loop:":
                if self.executed_instruction.full_name[:5] not in ["ADD.D", "SUB.D", "MUL.D", "DIV.D"]:
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
                if self.executed_instruction.full_name.split()[1] not in ["ADD.D", "SUB.D", "MUL.D", "DIV.D"]:
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

        if not isinstance(self.decoded_instruction, str):
            row = self.find_index(self.decoded_instruction.full_name)
            col = self.clock_cycle
            instruction = self.instruction_objects[row]
            if self.ID_stall:
                if 'id' not in self.pipeLineResults[row]:
                    self.pipeLineResults[row][col] = "id"
                else:
                    self.pipeLineResults[row][col] = "stall"
            else:
                self.pipeLineResults[row][col] = "id"

        if not isinstance(self.fetched_instruction, str):
            row = self.find_index(self.fetched_instruction.full_name)
            col = self.clock_cycle
            instruction = self.instruction_objects[row]
            if self.IF_stall:
                if 'if' not in self.pipeLineResults[row]:
                    self.pipeLineResults[row][col] = "if"
                else:
                    self.pipeLineResults[row][col] = "stall"
            else:
                self.pipeLineResults[row][col] = "if"

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

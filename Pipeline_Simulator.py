from components import process_command

nonexecution_stages = ["if", "id", "mem", "wb"]
additionCycle = ["if", "id", "A1", "A2", "mem", "wb"] 
subtractionCycle = ["if", "id", "A1", "A2", "mem", "wb"]
multiplicationCycle = ["if", "id", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "mem", "wb"]
divisionCycle = ["if", "id"] + ["D"+str(i) for i in range(1, 41)] + ["mem", "wb"]
oneCycle = ["if", "id", "ex", "mem", "wb"]


class Instruction:
    def __init__(self, full_name, instruction_name, parameter1, parameter2 = None, parameter3 = None):

        self.full_name = full_name

        self.instruction = instruction_name
        
        self.parameter1 = parameter1
        self.parameter2 = parameter2
        self.parameter3 = parameter3
        

        self.fullName = full_name

        self.completed = False

    def cycles_left(self, value):
        self.cycles_left = value
        self.completed = (self.cycles_left == 0)
    
    def decode(self):
        
        if(self.instruction == "L.D"):
            self.dest_f_register = self.parameter1
            self.offset = self.parameter2
            self.source_addr = self.parameter3
            self.cycles_left = 1
        elif(self.instruction == "S.D"):
            self.source_f_register = self.parameter1
            self.offset = self.parameter2
            self.dest_addr = self.parameter3
            self.cycles_left = 1
        elif(self.instruction == "LI"):
            self.dest_i_register = self.parameter1
            self.immediate = self.parameter2
            self.cycles_left = 1
        elif(self.instruction == "LW"):
            self.dest_i_register = self.parameter1
            self.offset = self.parameter2
            self.source_addr = self.parameter3
            self.cycles_left = 1
        elif(self.instruction == "SW"):
            self.source_i_register = self.parameter1
            self.offset = self.parameter2
            self.dest_addr = self.parameter3
            self.cycles_left = 1
        elif(self.instruction == "ADD"):
            self.dest_i_register = self.parameter1
            self.source_i_register1 = self.parameter2
            self.source_i_register2 = self.parameter3
            self.cycles_left = 1
        elif(self.instruction == "ADDI"):
            self.dest_i_register = self.parameter1
            self.source_i_register = self.parameter2
            self.immediate = self.parameter3
            self.cycles_left = 1
        elif(self.instruction == "ADD.D"):
            self.dest_f_register = self.parameter1
            self.source_f_register1 = self.parameter2
            self.source_f_register2 = self.parameter3
            self.cycles_left = 2
        elif(self.instruction == "SUB.D"):
            self.dest_f_register = self.parameter1
            self.source_f_register1 = self.parameter2
            self.source_f_register2 = self.parameter3
            self.cycles_left = 2
        elif(self.instruction == "SUB"):
            self.dest_i_register = self.parameter1
            self.source_i_register1 = self.parameter2
            self.source_i_register2 = self.parameter3
            self.cycles_left = 1
        elif(self.instruction == "MUL.D"):
            self.dest_f_register = self.parameter1
            self.source_f_register1 = self.parameter2
            self.source_f_register2 = self.parameter3
            self.cycles_left = 10
        elif(self.instruction == "DIV.D"):
            self.dest_f_register = self.parameter1
            self.source_f_register1 = self.parameter2
            self.source_f_register2 = self.parameter3
            self.cycles_left = 40
        elif(self.instruction == "BEQ"):
            self.source_i_register1 = self.parameter1
            self.source_i_register2 = self.parameter2
            self.subroutine = self.parameter3
            self.cycles_left = 1
        elif(self.instruction == "BNE"):
            self.source_i_register1 = self.parameter1
            self.source_i_register2 = self.parameter2
            self.subroutine = self.parameter3
            self.cycles_left = 1
        elif(self.instruction == "J"):
            self.jmp_addr = self.parameter1
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
        self.branch_predictions = {}  # Stores branch predictions
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
        self.clock_cycle = 0
        self.IF_stall = False
        self.ID_stall = False
        self.EX_stall = False
        self.MEM_stall = False

        #store subroutines
        self.subroutines = {}

        #the 4 cache blocks
        self.cache = [None, None, None, None]

        #to hold the results
        self.pipeLineResults = []



    def process_instruction_file(self, filename):
        with open(filename, 'r') as file:
            instructions = file.readlines()
        instructions = [line.strip() for line in instructions]
        self.instructions = instructions

        for i in range(len(self.instructions)):

            if(":" in self.instructions[i]):
                subroutine = self.instructions[i][0:self.instructions[i].find(":")]
                #self.instructions[i] = self.instructions[i][self.instructions[i].find(":") + 2:]

                self.subroutines[subroutine] = i
        

    def fetch_instruction(self, index):
        if index < len(self.instructions):
            self.fetched_instruction = self.instructions[index]
            self.pipeLineResults.append([self.fetched_instruction])
            for i in range(0, self.clock_cycle + 1):
                self.pipeLineResults[len(self.pipeLineResults)-1].append("  ")
        else:
            self.fetched_instruction = ""
        return self.fetched_instruction


    def decode_instruction(self, line):
        self.decoded_instruction = line
        instruction = None

        if(line != ""):

            row = self.find_index(line)
            if 'wb' in self.pipeLineResults[row]:
                self.decoded_instruction = ""
                return
            if "id" not in self.pipeLineResults[row]:
                self.next_instruction += 1

            name, par1, par2, par3 = process_command(line)

            instruction = Instruction(line, name, par1, par2, par3)
            self.instruction_objects[row] = instruction

            #instruction.decode()

            #second and third parameters read from registers
            if(instruction.instruction in ["ADD", "ADD.D", "SUB.D", "SUB", "MUL.D", "DIV.D"]):

                if(instruction.instruction in ["ADD", "SUB"]):
                    if(instruction.parameter2 in self.busy_int_registers or instruction.parameter3 in self.busy_int_registers):
                        instruction.shouldStall = True
                        self.ID_stall = True
                        self.IF_stall = True
                    else:
                        instruction.shouldStall = False
                else:
                    if(instruction.parameter2 in self.busy_fp_registers or instruction.parameter3 in self.busy_fp_registers):
                        instruction.shouldStall = True
                        self.ID_stall = True
                        self.IF_stall = True
                    else:
                        instruction.shouldStall = False

            #first parameter reads from a register
            elif(instruction.instruction in ["S.D", "SW"]):
                if(instruction.instruction == "S.D"):
                    if(instruction.parameter1 in self.busy_fp_registers):
                        instruction.shouldStall = True
                        self.ID_stall = True
                        self.IF_stall = True
                    else:
                        instruction.shouldStall = False
                else:
                    if(instruction.parameter1 in self.busy_int_registers):
                        instruction.shouldStall = True
                        self.ID_stall = True
                        self.IF_stall = True
                    else:
                        instruction.shouldStall = False

            #second parameter reads from a register
            elif(instruction.instruction == "ADDI"):
                if(instruction.parameter2 in self.busy_int_registers):
                    instruction.shouldStall = True
                    self.ID_stall = True
                    self.IF_stall = True
                else:
                    instruction.shouldStall = False

            #load from memory, since mems happen in order, there should be no hazards here
            # LI only puts it in the register in the Writeback stage, so also, no memory hazards
            elif(instruction.instruction in ["L.D", "LW", "LI"]):
                instruction.shouldStall = False

            if(instruction.instruction in ["L.D", "ADD.D", "SUB.D", "MUL.D", "DIV.D"]):
                if not (instruction.shouldStall):
                    self.busy_fp_registers.append(instruction.parameter1)
            elif(instruction.instruction in ["LI", "LW", "ADD", "ADDI", "SUB"]):
                if not (instruction.shouldStall):
                    self.busy_int_registers.append(instruction.parameter1)

        return line

        


    def execute_instruction(self, line):
        if line != "":
            row = self.find_index(line)
            if 'wb' in self.pipeLineResults[row]:
                self.executed_instruction = ""
                return
            self.executed_instruction = line

    def mem_instruction(self, line):
        if line != "":
            row = self.find_index(line)
            if 'wb' in self.pipeLineResults[row]:
                self.memory_instruction = ""
                return
            self.memory_instruction = line

    def writeBack_instruction(self, line):
        if line != "":
            row = self.find_index(line)
            print(row)
            if 'wb' in self.pipeLineResults[row]:
                self.writeback_instruction = ""
                return
            self.writeback_instruction = line

    def execute_fp_add(self, dest_reg, src_reg1, src_reg2):
        self.fp_registers[dest_reg] = self.fp_registers[src_reg1] + self.fp_registers[src_reg2]

    def execute_fp_sub(self, dest_reg, src_reg1, src_reg2):
        self.fp_registers[dest_reg] = self.fp_registers[src_reg1] - self.fp_registers[src_reg2]

    def execute_fp_mul(self, dest_reg, src_reg1, src_reg2):
        self.fp_registers[dest_reg] = self.fp_registers[src_reg1] * self.fp_registers[src_reg2]

    def execute_fp_div(self, dest_reg, src_reg1, src_reg2):
        self.fp_registers[dest_reg] = self.fp_registers[src_reg1] / self.fp_registers[src_reg2]

    def execute_int_add(self, dest_reg, src_reg1, src_reg2):
        self.int_registers[dest_reg] = self.int_registers[src_reg1] + self.int_registers[src_reg2]

    def execute_int_sub(self, dest_reg, src_reg1, src_reg2):
        self.int_registers[dest_reg] = self.int_registers[src_reg1] - self.int_registers[src_reg2]

    def execute_load(self, dest_reg, mem_address, type):
        # Simulating a load operation from memory
        if type == 0:
            self.fp_registers[dest_reg] = self.memory[mem_address]
        elif type == 1:
            self.int_registers[dest_reg] = self.memory[mem_address]
        elif type == 2:
            self.int_registers[dest_reg] = mem_address
        elif type == 4:
            self.fp_registers[dest_reg] = self.memory[self.int_registers[mem_address]]
        elif type == 5:
            self.int_registers[dest_reg] = self.memory[self.int_registers[mem_address]]

    def execute_store(self, src_reg, mem_address, type):
        # Simulating a store operation to memory
        if type == 0:
            self.memory[mem_address] = self.fp_registers[src_reg]
        elif type == 1:
            self.memory[mem_address] = self.int_registers[src_reg]


            
        
        




    def execute_branch(self, label):
        if label in self.branch_predictions:
            prediction = self.branch_predictions[label]
        else:
            prediction = 1  # Assume taken by default for new branches

        # Execute branch....

        if prediction == 1:  # Branch taken
            # Update the branch prediction to correct (prediction was right)
            self.branch_predictions[label] = 1
        else:  # Branch not taken
            # Update the branch prediction to wrong (prediction was wrong)
            self.branch_predictions[label] = 0

            # Flush the pipeline by clearing any instructions fetched after the branch
            self.flush_pipeline()

            # Fetch the correct instruction corresponding to the branch label
            #correct_instruction = get_instruction_from_label(label)

            # Fetch the correct instruction on the current cycle
            #self.fetch_instruction(correct_instruction)

    def flush_pipeline(self):
        # Assuming there are pipeline stages represented by variables or data structures
        # that hold the fetched, decoded, and executed instructions

        # Example implementation assuming a simple 3-stage pipeline
        self.fetched_instruction = []  # Or pop the last element?
        self.decoded_instruction = []
        self.executed_instruction = []

    def print_registers(self):
        print("Integer Registers:")
        for i in range(len(self.int_registers)):
            print(f"R{i}: {self.int_registers[i]}")
        print("\nFloating-Point Registers:")
        for i in range(len(self.fp_registers)):
            print(f"F{i}: {self.fp_registers[i]}")

    def run_pipeline(self):
        
        while not (self.fetched_instruction == "" and self.decoded_instruction == "" and self.executed_instruction == "" and self.memory_instruction == "" and self.writeback_instruction == "") or self.next_instruction == 0:
            [row.append("  ") for row in self.pipeLineResults]

            # WB Stage
            self.writeBack_instruction(self.memory_instruction)
            
            # MEM Stage
            if self.MEM_stall:
                self.mem_instruction(self.memory_instruction)
            else:
                self.mem_instruction(self.executed_instruction)
            
            # EX Stage    
            if self.EX_stall:
                self.execute_instruction(self.executed_instruction)
            else:
                self.execute_instruction(self.decoded_instruction)
            
            # ID Stage
            if self.ID_stall:        
                self.decode_instruction(self.decoded_instruction)
            else:
                self.decode_instruction(self.fetched_instruction)
                
            # IF Stage
            if self.IF_stall:
                self.fetch_instruction(self.fetched_instruction)
            else:
                self.fetch_instruction(self.next_instruction)
            
            self.clock_cycle += 1
            self.update_column()
        [print(row) for row in self.pipeLineResults]


    def update_column(self):
        if self.fetched_instruction != "":
            row = self.find_index(self.fetched_instruction)
            col = self.clock_cycle
            if self.IF_stall:
                if 'if' not in self.pipeLineResults[row]:
                    self.pipeLineResults[row][col] = "if"
                else:
                    self.pipeLineResults[row][col] = "stall"
            else:
                self.pipeLineResults[row][col] = "if"

        if self.decoded_instruction != "":
            row = self.find_index(self.decoded_instruction)
            col = self.clock_cycle
            if self.ID_stall:
                if 'id' not in self.pipeLineResults[row]:
                    self.pipeLineResults[row][col] = "id"
                else:
                    self.pipeLineResults[row][col] = "stall"
            else:
                self.pipeLineResults[row][col] = "id"

        if self.executed_instruction != "":
            row = self.find_index(self.executed_instruction)
            col = self.clock_cycle
            if self.executed_instruction[:5] != "Loop:":
                if self.executed_instruction[:5] not in ["ADD.D", "SUB.D", "MUL.D", "DIV.D"]:
                    self.pipeLineResults[row][col] = "ex"
                else:
                    pass
            else:
                if self.executed_instruction.split()[1] not in ["ADD.D", "SUB.D", "MUL.D", "DIV.D"]:
                    self.pipeLineResults[row][col] = "ex"
                else:
                    pass
                    
        if self.memory_instruction != "":
            row = self.find_index(self.memory_instruction)
            col = self.clock_cycle
            self.pipeLineResults[row][col] = "mem"

        if self.writeback_instruction != "":
            row = self.find_index(self.writeback_instruction)
            col = self.clock_cycle
            if 'wb' not in self.pipeLineResults[row]:
                self.pipeLineResults[row][col] = "wb"



    def find_index(self, line):
        for i in range(len(self.pipeLineResults)-1,0,-1):
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
"""
    processor.fp_registers[1] = 2.5
    processor.fp_registers[2] = 3.7
    processor.execute_fp_add(0, 1, 2)
    print(processor.fp_registers[0])  # Output: 6.2

    processor.int_registers[3] = 10
    processor.int_registers[4] = 5
    processor.execute_int_sub(5, 3, 4)
    print(processor.int_registers[5])  # Output: 5
"""

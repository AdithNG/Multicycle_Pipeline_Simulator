nonexecution_stages = ["if", "id", "mem", "wb"]
additionCycle = ["if", "id", "A1", "A2", "mem", "wb"] 
subtractionCycle = ["if", "id", "S1", "S2", "mem", "wb"]
multiplicationCycle = ["if", "id", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "mem", "wb"]
divisionCycle = ["if", "id"] + ["D"+str(i) for i in range(1, 41)] + ["mem", "wb"]
oneCycle = ["if", "id", "ex", "mem", "wb"]


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
        self.fetched_instruction = ""
        self.decoded_instruction = ""
        self.executed_instruction = ""
        self.memory_instruction = ""
        self.writeback_instruction = ""
        self.busy_registers = []
        self.clock_cycle = 0

        #the 4 cache blocks
        self.cache = [None, None, None, None]

        #to hold the results
        self.pipeLineResults = []



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

    def process_instruction_file(self, filename):
        with open(filename, 'r') as file:
            instructions = file.readlines()
        instructions = [line.strip() for line in instructions]
        self.instructions = instructions

    def process_command(self, line):

        # stored as an integer initially  as a safe way of verifying that there is no subroutine in the line
        subroutine = ""

        # but if it is a subroutine, store the name of it and strip if from the line so it can be processed
        if ":" in line:
            subroutine = line[:line.find(":") + 1]
            line = line[line.find(":") + 2:]

        line = line.split()
        registers = line[1].split(",")
        instruction = line[0]
        dest_reg = int(registers[0][1])
        self.busy_registers.append(registers[1])

        if instruction == "L.D":
            offset = int(registers[1][:registers[1].find("(")])

            # If src_addr is a register
            if registers[1][registers[1].find("(") + 1] == "$" :
                src_addr = registers[1][registers[1].find("(") + 2: registers[1].find(")")]
                self.execute_load(dest_reg, (src_addr + offset) % 35, 4)

            # If src_addr is a memory location
            else:
                src_addr = registers[1][registers[1].find("(") + 1: registers[1].find(")")]
                self.execute_load(dest_reg, (src_addr + offset) % 19, 0)

        elif instruction == "LI":
            immediate = int(registers[1])
            self.execute_load(dest_reg, immediate, 2)

        elif instruction == "LW":
            offset = int(registers[1][:registers[1].find("(")])
            # If src_addr is a register
            if registers[1][registers[1].find("(") + 1] == "$":
                src_addr = registers[1][registers[1].find("(") + 2: registers[1].find(")")]
                self.execute_load(dest_reg, (src_addr + offset) % 35, 5)

            # If src_addr is a memory location
            else:
                src_addr = int(registers[1][registers[1].find("(") + 1: registers[1].find(")")])
                self.execute_load(dest_reg, (src_addr + offset) % 19, 1)

        elif instruction == "S.D":
            offset = int(registers[1][:registers[1].find("(")])
            src_addr = int(registers[1][registers[1].find("(") + 1: registers[1].find(")")])
            self.execute_load(dest_reg, (src_addr + offset) % 19, 0)

        elif instruction == "SW":
            offset = int(registers[1][:registers[1].find("(")])
            src_addr = int(registers[1][registers[1].find("(") + 1: registers[1].find(")")])
            self.execute_load(dest_reg, (src_addr + offset) % 19, 1)

        elif instruction == "ADD":
            src_reg1 = int(registers[1][1])
            src_reg2 = int(registers[2][1])
            self.execute_int_add(dest_reg, src_reg1, src_reg2)

        elif instruction == "ADDI":
            src_reg1 = int(registers[1][1])
            immediate = int(registers[2])
            self.execute_int_add(dest_reg, src_reg1, immediate)

        elif instruction == "ADD.D":
            src_reg1 = int(registers[1][1])
            src_reg2 = int(registers[2][1])
            self.execute_fp_add(dest_reg, src_reg1, src_reg2)

        elif instruction == "SUB.D":
            src_reg1 = int(registers[1][1])
            src_reg2 = int(registers[2][1])
            self.execute_fp_sub(dest_reg, src_reg1, src_reg2)

        elif instruction == "SUB":
            src_reg1 = int(registers[1][1])
            src_reg2 = int(registers[2][1])
            self.execute_int_sub(dest_reg, src_reg1, src_reg2)

        elif instruction == "MUL.D":
            src_reg1 = int(registers[1][1])
            src_reg2 = int(registers[2][1])
            self.execute_fp_mul(dest_reg, src_reg1, src_reg2)

        elif instruction == "DIV.D":
            src_reg1 = int(registers[1][1])
            src_reg2 = int(registers[2][1])
            self.execute_fp_div(dest_reg, src_reg1, src_reg2)

        elif instruction == "BEQ":
            src_reg1 = int(registers[1][1])
            off18 = registers[2]

        elif instruction == "BNE":
            src_reg1 = int(registers[1][1])
            off18 = registers[2]

        elif instruction == "J":
            addr28 = registers[0]




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
            correct_instruction = get_instruction_from_label(label)

            # Fetch the correct instruction on the current cycle
            self.fetch_instruction(correct_instruction)

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
        i = 0

        """
        while i < len(self.instructions) != []:
            self.fetched_instruction = self.fetch_instruction()
            self.decoded_instruction = self.decode_instruction(self.fetched_instruction)
            self.executed_instruction = self.execute_instruction(self.decoded_instruction)
            self.memory_instruction = self.memory_instruction(self.executed_instruction)
            self.writeback_instruction = self.writeback_instruction(self.memory_instruction)
            i += 1
        """
        


if __name__ == '__main__':
    processor = Processor()

    # Take the instruction file name as user input
    filename = input("Enter the instruction file name: ")

    # Process the instruction file
    instructions = processor.process_instruction_file(filename)
    print(processor.instructions)

    processor.fp_registers[1] = 2.5
    processor.fp_registers[2] = 3.7
    processor.execute_fp_add(0, 1, 2)
    print(processor.fp_registers[0])  # Output: 6.2

    processor.int_registers[3] = 10
    processor.int_registers[4] = 5
    processor.execute_int_sub(5, 3, 4)
    print(processor.int_registers[5])  # Output: 5

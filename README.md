# Multicycle Pipeline Simulator

This repository contains a Python-based multicycle pipeline simulator that emulates the execution of instructions in a processor pipeline.

## Overview

The simulator is divided into three main parts:

1. **Instruction Class and Processor Class:** Defines the instruction attributes and the processor's components such as registers, memory, and stages in the pipeline.

2. **Execution Steps:** Describes the functions responsible for the execution, memory access, write-back, flushing the pipeline, and managing the pipeline's stages.

3. **Pipeline Execution:** Demonstrates how the simulator runs the pipeline for processing the provided instructions.

## Usage

### Running the Simulator

To execute the multicycle pipeline simulator:

1. Clone this repository.
2. Ensure Python is installed on your system.
3. Open a terminal or command prompt and navigate to the directory where the project is located.
4. Run the simulator by executing the following command:
    ```bash
    python multicycle_pipeline_simulator.py
    ```
5. Enter the instruction file name when prompted.

## Instruction File Format

The simulator reads instructions from a file. Each line in the file represents an instruction, following a specific format.

- The instruction format comprises the instruction mnemonic followed by parameters.

- Sample Instruction file is provided in MIPS.txt


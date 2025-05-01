# **Nand2Tetris**
## **Description:**
The Nand2Tetris project implements a computer system from the ground up — starting with basic logic gates and ending with a simple operating system and programs. Based on the "From Nand to Tetris" course, it covers hardware simulation, assembler development, virtual machine implementation, and compiler design.

## **Prerequisites:**
- Java (JDK 8 or higher)
- Nand2Tetris Software Suite
- A code editor or IDE (e.g. VSCode, IntelliJ)

## **Setup Instructions:**

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/nand2tetris.git
    cd nand2tetris
    ```

2. **Download Nand2Tetris Tools:**
    Get the official tools (Hardware Simulator, CPU Emulator, Assembler, VM Emulator) from:
    [https://www.nand2tetris.org/software](https://www.nand2tetris.org/software)

    Extract the tools and place them in a `tools/` directory at the root of your project.

3. **Project Structure:**
    Each chapter has its own folder inside the `projects/` directory:
    ```
    projects/
      01/   // Logic gates (Not.hdl, And.hdl, etc.)
      02/   // ALU and multiplexers
      ...
      12/   // Operating system and high-level applications
    ```

4. **Running Simulations:**
    Open the relevant `.tst` file using the appropriate tool:
    - For `.hdl` hardware files → use **HardwareSimulator**
    - For `.asm` programs → use **CPUEmulator**
    - For `.vm` files → use **VMEmulator**

## **Running a Test Example:**

Test the `And.hdl` gate from Project 01:
```bash
cd projects/01
./tools/HardwareSimulator.sh And.tst  # On macOS/Linux
tools\HardwareSimulator.bat And.tst   # On Windows

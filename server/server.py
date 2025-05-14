import math # Import math for calculations
from mcp.server.fastmcp import FastMCP
from typing import Optional

from components.any_qubit_component import AnyQubit
from components.common import Display, arg_gates, no_arg_gates, gates

# Initialize FastMCP server
MCP_SERVER_NAME = "quantum_chatbot"
mcp = FastMCP(MCP_SERVER_NAME)

# Initialize quantum circuit
circuit = AnyQubit(1, display=Display.TERMINAL)

@mcp.tool()
async def create_circuit(num_qubits: int) -> str:
    """
    Initializes a new quantum circuit with a specified number of qubits (1-5).
    Resets any existing circuit.

    Args:
        num_qubits: The number of qubits for the circuit (integer between 1 and 5).
    
    Returns:
        A string representation of the current state of the circuit.
    """
    if not isinstance(num_qubits, int) or not 1 <= num_qubits <= 5:
        return "Please choose an integer between 1 and 5 qubits."
    
    circuit.qubits = num_qubits
    circuit.reset()
    return f"\n{circuit.get_state()}"

@mcp.tool()
async def apply_gate(target_qubit: int, gate: str, angle: Optional[float] = None) -> str:
    """
    Applies a quantum gate to a specific qubit in the existing circuit.

    Args:
        target_qubit: The index of the qubit to apply the gate to (0-based integer).
        gate: The name of the gate (e.g., 'h', 'x', 'rz'). Case-insensitive. Must be a valid gate.
        angle: The rotation angle in degrees (float). Required only for parametric gates (p, rx, ry, rz). Ignored otherwise.

    Returns:
        A string representation of the current state of the circuit after applying the gate.
    """
    if not isinstance(target_qubit, int) or not 0 <= target_qubit < circuit.qubits:
        return "Please choose a valid qubit index."
    
    gate = gate.lower()
    if gate not in gates:
        return "Please choose a valid gate."

    if gate in arg_gates:
        if angle is None:
            return "Please provide an angle for the gate."
        try:
            angle = float(angle)
        except (ValueError, TypeError):
            return "Please provide a valid angle."
    
    circuit.apply_gate(target_qubit, gate, angle)
    return f"{circuit.get_state()}"

@mcp.tool()
async def show_circuit() -> str:
    """
    Returns the current quantum circuit as a string. Takes no arguments.
    """
    return f"{circuit.get_circuit()}"

@mcp.tool()
async def show_state() -> str:
    """
    Returns the current state of the quantum circuit as a string. Takes no arguments.
    """
    return f"{circuit.get_state()}"

@mcp.tool()
async def reset_circuit() -> str:
    """
    Resets the current quantum circuit. Returns the state of the reset circuit. Takes no arguments.
    """
    circuit.reset()
    return f"{circuit.get_state()}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
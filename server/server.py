import math # Import math for calculations
from mcp.server.fastmcp import FastMCP
from typing import Optional

from components.any_qubit_component import AnyQubit
from components.common import Display, arg_gates, no_arg_gates, gates


class QuantumChatbot():
    def __init__(self):
        self.circuit = None
        self.num_qubits = 0
    
    def _create_circuit(self, num_qubits=1):
        if not isinstance(num_qubits, int) or not 1 <= num_qubits <= 5: # Added type check
            return "Please choose an integer between 1 and 5 qubits."
        self.circuit = AnyQubit(num_qubits, display=Display.TERMINAL)
        self.num_qubits = num_qubits

    def _show_circuit(self):
        if self.circuit is None:
            return "Please create a circuit first."
        
        return self.circuit.get_circuit()
    
    def _apply_gate(self, target, gate, angle=None):
        if self.circuit is None:
            return "Please create a circuit first."
        
        if not isinstance(target, int) or not 0 <= target < self.num_qubits:
            return "Please choose a valid qubit index."
        
        gate = gate.lower()
        if gate not in gates:
            return "Please choose a valid gate."

        angle_deg = None
        if gate in arg_gates:
            if angle is None:
                return "Please provide an angle for the gate."
            try:
                angle_deg = float(angle)
            except (ValueError, TypeError):
                return "Please provide a valid angle."
        elif gate is not None:
            angle_deg = None
            print("Angle is not required for this gate.")

        self.circuit.apply_gate(target, gate, angle=angle_deg)

    def _show_state(self):
        if self.circuit is None:
            return "Please create a circuit first."
        
        return self.circuit.get_state()
    
    def _reset_circuit(self):
        if self.circuit is None:
            return "Please create a circuit first."
        qubits = self.num_qubits
        self.circuit.reset()

# Initialize FastMCP server
MCP_SERVER_NAME = "quantum_chatbot" # Updated server name
mcp = FastMCP(MCP_SERVER_NAME)

quantum_chatbot = QuantumChatbot()


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

    quantum_chatbot._create_circuit(num_qubits)

    return f"\n{quantum_chatbot._show_state()}"

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
    
    quantum_chatbot._apply_gate(target_qubit, gate, angle)

    return f"{quantum_chatbot._show_state()}"

@mcp.tool()
async def show_circuit() -> str:
    """
    Returns the current quantum circuit as a string. Takes no arguments.
    """
    
    return f"{quantum_chatbot._show_circuit()}"

@mcp.tool()
async def show_state() -> str:
    """
    Returns the current state of the quantum circuit as a string. Takes no arguments.
    """
    
    return f"{quantum_chatbot._show_state()}"

@mcp.tool()
async def reset_circuit() -> str:
    """
    Resets the current quantum circuit. Returns the state of the reset circuit. Takes no arguments.
    """
    
    quantum_chatbot._reset_circuit()

    return f"{quantum_chatbot._show_state()}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
import sys
import os

class Interpreter:
    def __init__(self, output_callback, input_callback):
        """
        :param output_callback: Función que recibe un string para mostrar en la terminal.
        :param input_callback: Función que recibe (nombre_var, tipo_var) y retorna el valor ingresado.
        """
        self.output_callback = output_callback
        self.input_callback = input_callback
        self.memory = {}

    def execute(self, program_node):
        try:
            for stmt in program_node.statements:
                self.visit(stmt)
            self.output_callback("\n✅ Ejecución finalizada con éxito.")
        except Exception as e:
            self.output_callback(f"\n❌ Error en tiempo de ejecución: {str(e)}")

    def visit(self, node):
        from src.parser.parser import (
            DeclarationNode, AssignmentNode, CaptureNode, 
            MessageNode, BinaryOpNode, LiteralNode, VariableNode,
            IfNode, WhileNode, ComparisonNode
        )

        if isinstance(node, DeclarationNode):
            # Inicializar variable según su tipo
            if node.var_type == 'Entero': self.memory[node.name] = 0
            elif node.var_type == 'Real': self.memory[node.name] = 0.0
            elif node.var_type == 'Texto': self.memory[node.name] = ""
            elif node.var_type == 'Logico': self.memory[node.name] = False
            else: self.memory[node.name] = None
            
        elif isinstance(node, AssignmentNode):
            val = self.evaluate(node.value_node)
            self.memory[node.name] = val
            
        elif isinstance(node, CaptureNode):
            # Solicitar entrada al usuario a través de la GUI
            val = self.input_callback(node.name, node.var_type)
            # Convertir valor según tipo
            try:
                if node.var_type == 'Entero': val = int(val)
                elif node.var_type == 'Real': val = float(str(val).replace(',', '.'))
                elif node.var_type == 'Logico': val = True if str(val).lower() in ['verdad', 'true', '1'] else False
            except ValueError:
                raise Exception(f"Valor '{val}' no es válido para tipo {node.var_type}")
            self.memory[node.name] = val
            
        elif isinstance(node, MessageNode):
            parts = []
            for arg in node.arguments:
                val = self.evaluate(arg)
                # Formatear números reales para mostrar coma
                if isinstance(val, float):
                    parts.append(str(val).replace('.', ','))
                elif isinstance(val, bool):
                    parts.append("Verdad" if val else "Mentira")
                else:
                    parts.append(str(val))
            self.output_callback(" ".join(parts))

        elif isinstance(node, IfNode):
            condition = self.evaluate(node.condition)
            if condition:
                for stmt in node.then_statements:
                    self.visit(stmt)
            elif node.else_statements:
                for stmt in node.else_statements:
                    self.visit(stmt)

        elif isinstance(node, WhileNode):
            while self.evaluate(node.condition):
                for stmt in node.body_statements:
                    self.visit(stmt)

    def evaluate(self, node):
        from src.parser.parser import (
            BinaryOpNode, LiteralNode, VariableNode, ComparisonNode
        )
        
        if isinstance(node, LiteralNode):
            return node.value
            
        elif isinstance(node, VariableNode):
            if node.name not in self.memory:
                raise Exception(f"Variable '{node.name}' no inicializada.")
            return self.memory[node.name]
            
        elif isinstance(node, BinaryOpNode):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            
            if node.op == '+':
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            if node.op == '-': return left - right
            if node.op == '*': return left * right
            if node.op == '/': 
                if right == 0: raise Exception("División por cero, mi llave.")
                return left / right

        elif isinstance(node, ComparisonNode):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            
            if node.op == '==': return left == right
            if node.op == '!=': return left != right
            if node.op == '<': return left < right
            if node.op == '>': return left > right
            if node.op == '<=': return left <= right
            if node.op == '>=': return left >= right
            
        return None

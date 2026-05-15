class SemanticErrorCosteñol(Exception):
    """Excepción lanzada cuando hay un error semántico (lógico) en el código."""
    def __init__(self, message, token):
        super().__init__(message)
        self.token = token
        self.message = message

class SymbolTable:
    """
    Tabla de Símbolos para realizar análisis semántico.
    Registra las variables declaradas y sus tipos correspondientes.
    """
    def __init__(self):
        self.symbols = {}

    def define(self, name, var_type, token):
        """
        Registra una nueva variable en la tabla.
        Lanza error si la variable ya fue declarada.
        """
        if name in self.symbols:
            raise SemanticErrorCosteñol(
                f"Joda loco estas barrilete — La variable '{name}' ya fue declarada previamente.",
                token
            )
        self.symbols[name] = var_type

    def lookup(self, name, token):
        """
        Busca el tipo de una variable en la tabla.
        Lanza error si no existe.
        """
        if name not in self.symbols:
            raise SemanticErrorCosteñol(
                f"Joda loco estas barrilete — La variable '{name}' no ha sido declarada.",
                token
            )
        return self.symbols[name]

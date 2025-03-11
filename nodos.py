class NodoAST:
    # Clase base para todos los nodos del AST
    pass

class NodoFuncion(NodoAST):
    # Nodo que representa una funcion
    def _init_(self, nombre, parametros, cuerpo):
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo

class NodoParametro(NodoAST):
    # Nodo que representa un parametro de funcion
    def _init_(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre

class NodoAsignacion(NodoAST):
    # Nodo que representa una asignacion de variables
    def _init_(self, nombre, expresion):
        self.nombre = nombre 
        self.expresion = expresion
        
class NodoOperacion(NodoAST):
    # Nodo que representa una operacion aritmetica
    def _init_(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

class NodoRetorno(NodoAST):
    # Nodo que representa la sentencia return
    def _init_(self, expresion):
        self.expresion = expresion

class NodoIdentificador(NodoAST):
    # Nodo que representa a un identificador
    def _init_(self, nombre):
        self.nombre = nombre;

class NodoNumero(NodoAST):
    # Nodo que representa un numero
    def _init_(self, valor):
        self.valor = valor
        
class NodoLlamadaFuncion(NodoAST):
    # Nodo que representa una llamada a funcion
    def _init_(self, nombre, argumentos):
        self.nombre = nombre
        self.argumentos = argumentos
        
class NodoPrograma(NodoAST):
    """
    Nodo que representa un programa completo.
    Contiene una lista de funciones.
    """
    def _init_(self, funciones):
        self.funciones = funciones
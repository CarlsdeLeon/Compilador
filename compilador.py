import re

# === Analisis Lexico ===
# Definir los patrones para los diferentes tipos de tokens
token_patron = {
    "KEYWORD": r'\b(if|else|while|return|printf|int|float|void|double|char)\b',
    "IDENTIFIER": r'\b[a-zA-Z][a-zA-Z0-9]*\b',
    "NUMBER": r'\b\d+(\.\d+)?\b',
    "OPERATOR": r'[\+\-\*\/=\<\>\!]',
    "DELIMITER": r'[(),;{}]',
    "WHITESPACE": r'\s+',
    "STRING": r'"[^"]*"',  
}

def identificar_tokens(texto):
    # Unir todos los patrones en un unico patron realizando grupos nombrados
    patron_general = "|".join(f"(?P<{token}>{patron})" for token, patron in token_patron.items())
    patron_regex = re.compile(patron_general)
    tokens_encontrados = []
    for match in patron_regex.finditer(texto):
        for token, valor in match.groupdict().items():
            if valor is not None and token != "WHITESPACE":
                tokens_encontrados.append((token, valor))
    return tokens_encontrados

# === Analizador Sintactico ===
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def obtener_token_actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def coincidir(self, tipo_esperado):
        token_actual = self.obtener_token_actual()
        if token_actual and token_actual[0] == tipo_esperado:
            self.pos += 1
            return token_actual
        else:
            raise SyntaxError(f'Error sintactico: se esperaba {tipo_esperado}, pero se encontro: {token_actual}')

    def parsear(self):
        # Punto de entrada del analizador sintactico: se espera una funcion
        self.funcion()

    def funcion(self):
        # Gramatica para una funcion: int  IDENTIFIER (int IDENTIFIER) {cuerpo}
        self.coincidir('KEYWORD')  # Tipo de retorno (ej. int)
        self.coincidir('IDENTIFIER')  # Nombre de la funcion
        self.coincidir('DELIMITER')  # se espera un (
        self.parametros()
        self.coincidir('DELIMITER')  # se espera un )
        self.coincidir('DELIMITER')  # se espera un {
        self.cuerpo()
        self.coincidir('DELIMITER')  # se espera un }

    def bucle_while(self):
        # Regla para bucle while: while (EXPRESION_LOGICA) {CUERPO}
        self.coincidir('KEYWORD') #Coincide a while
        self.coincidir('DELIMITER') #se espera un (
        self.expresion_logica()
        self.coincidir('DELIMITER') #se espera un )
        self.coincidir('DELIMITER') #se espera un {
        self.printf_llamada() 
        self.incremento()
        self.coincidir('DELIMITER') #se espera un }

    def incremento(self):
        self.coincidir('IDENTIFIER')
        operador_actual1 = self.obtener_token_actual()
        self.coincidir('OPERATOR')
        operador_actual2 = self.obtener_token_actual()
        self.coincidir('OPERATOR')
        if operador_actual1[1] != operador_actual2[1] or operador_actual1[1] not in ['+','-']:
            raise SyntaxError(f'Error sintactico: se esperaba una declaracion valida, pero se encontro: {operador_actual1[1],operador_actual2[1]}')
        self.coincidir('DELIMITER')

    def parametros(self):
        # Reglas para parametros: int IDENTIFIER (, int IDENTIFIER)*
        self.coincidir('KEYWORD')  # Tipo del parametro
        self.coincidir('IDENTIFIER')  # Nombre del parametro
        while self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
            self.coincidir('DELIMITER')  # se espera una ,
            self.coincidir('KEYWORD')  # tipo del parametro
            self.coincidir('IDENTIFIER')  # nombre del parametro

    def declaracion(self):
        # Regla para declaracion: KEYWORD IDENTIFIER '=' EXPRESION DELIMITER
        self.coincidir('KEYWORD')  # Tipo de dato (ej. int)
        self.coincidir('IDENTIFIER')  # Nombre de la variable

        token_actual = self.obtener_token_actual()
        if token_actual and token_actual[1] == '=':  # Si es una asignación
            self.coincidir('OPERATOR')  # Coincide con '='
            self.expresion()  # El resto de la declaracion aritmetica

        self.coincidir('DELIMITER')  # Se espera un ';'

    def cuerpo(self):
        while self.obtener_token_actual() and self.obtener_token_actual()[1] != '}':
            token_actual = self.obtener_token_actual()

            if token_actual[0] == 'KEYWORD':
                if token_actual[1] == 'if':
                    self.condicional_if_else()  # Procesar if-else

                elif token_actual[1] == 'printf':
                    self.printf_llamada()  # Procesar printf
                elif token_actual[1] == 'while':
                    self.bucle_while() # procesar while
                else:
                    self.declaracion()  # Procesar declaraciones como int x;

            elif token_actual[0] == 'IDENTIFIER':
                siguiente_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                if siguiente_token and siguiente_token[1] == '=':
                    self.coincidir('IDENTIFIER')
                    self.coincidir('OPERATOR')
                    self.expresion()
                    self.coincidir('DELIMITER')
                
                else:
                    self.coincidir('IDENTIFIER')
                    self.coincidir('DELIMITER')

            elif token_actual[1] == 'return':
                self.coincidir('KEYWORD')
                self.expresion()
                self.coincidir('DELIMITER')

            else:
                raise SyntaxError(f'Error sintactico: se esperaba una declaracion valida, pero se encontro: {token_actual}')

    def expresion(self):
        """
        Analiza expresiones matemáticas o de concatenación, por ejemplo:
        - x + y * 2
        - "hola" + nombre
        """
        if self.obtener_token_actual()[0] in ['IDENTIFIER', 'NUMBER', 'STRING']:
            self.coincidir(self.obtener_token_actual()[0])  # Consumir identificador, número o cadena
        else:
            raise SyntaxError(f"Error sintáctico: Se esperaba IDENTIFIER, NUMBER o STRING, pero se encontró {self.obtener_token_actual()}")

        while self.obtener_token_actual() and self.obtener_token_actual()[0] in ['OPERATOR']:
            self.coincidir('OPERATOR')  # Consumir operador
            if self.obtener_token_actual()[0] in ['IDENTIFIER', 'NUMBER', 'STRING']:
                self.coincidir(self.obtener_token_actual()[0])  # Consumir identificador, número o cadena
            else:
                raise SyntaxError(f"Error sintáctico: Se esperaba IDENTIFIER, NUMBER o STRING después de {self.obtener_token_anterior()}")

    def condicional_if_else(self):
        """
        Analiza la estructura de una sentencia if-else.
        """
        self.coincidir('KEYWORD')  # Coincidir con 'if'
        self.coincidir('DELIMITER')  # Apertura de '('

        # Llamar a expresion_logica() para procesar la condición
        self.expresion_logica()

        self.coincidir('DELIMITER')  # Cierre de ')'
        self.coincidir('DELIMITER')  # Apertura de bloque '{'
        self.cuerpo()  # Evaluar el cuerpo del if
        self.coincidir('DELIMITER')  # Cierre de bloque '}'

        # Manejo opcional de else
        if self.obtener_token_actual() and self.obtener_token_actual()[1] == 'else':
            self.coincidir('KEYWORD')  # Coincidir con 'else'
            self.coincidir('DELIMITER')  # Apertura de bloque '{'
            self.cuerpo()  # Evaluar el cuerpo del else
            self.coincidir('DELIMITER')  # Cierre de bloque '}'

    def expresion_logica(self):
        """
        Analiza expresiones lógicas como:
        - resultado > x
        - a == b
        - x != 10 && y < 5
        """
        # La expresión lógica puede iniciar con un IDENTIFIER o un NUMBER
        if self.obtener_token_actual()[0] in ['IDENTIFIER', 'NUMBER']:
            self.coincidir(self.obtener_token_actual()[0])  # Consumir el identificador o número
        else:
            raise SyntaxError(f"Error sintáctico: Se esperaba IDENTIFIER o NUMBER, pero se encontró {self.obtener_token_actual()}")

        # Esperar un operador lógico (>, <, ==, !=)
        if self.obtener_token_actual()[0] == 'OPERATOR':
            self.coincidir('OPERATOR')  # Consumir operador
        else:
            raise SyntaxError(f"Error sintáctico: Se esperaba un OPERADOR, pero se encontró {self.obtener_token_actual()}")

        # Esperar otro IDENTIFIER o NUMBER después del operador
        if self.obtener_token_actual()[0] in ['IDENTIFIER', 'NUMBER']:
            self.coincidir(self.obtener_token_actual()[0])  # Consumir el identificador o número
        else:
            raise SyntaxError(f"Error sintáctico: Se esperaba IDENTIFIER o NUMBER, pero se encontró {self.obtener_token_actual()}")

        # Manejo de operadores lógicos compuestos (&&, ||)
        while self.obtener_token_actual() and self.obtener_token_actual()[1] in ['&&', '||']:
            self.coincidir('OPERATOR')  # Consumir operador lógico
            if self.obtener_token_actual()[0] in ['IDENTIFIER', 'NUMBER']:
                self.coincidir(self.obtener_token_actual()[0])  # Consumir el identificador o número
            else:
                raise SyntaxError(f"Error sintáctico: Se esperaba IDENTIFIER o NUMBER después de {self.obtener_token_anterior()}")

    def printf_llamada(self):
        """
        Maneja las llamadas a printf como:
        printf("Mensaje %d", variable);
        """
        self.coincidir('KEYWORD')  # Coincide con 'printf'
        self.coincidir('DELIMITER')  # Coincide con '('

        # Se espera una cadena como primer argumento
        if self.obtener_token_actual()[0] == 'STRING':
            self.coincidir('STRING')  # Coincide con la cadena
        else:
            raise SyntaxError(f"Error sintactico: Se esperaba STRING, pero se encontro {self.obtener_token_actual()}")

        # Puede haber más argumentos separados por comas
        while self.obtener_token_actual() and self.obtener_token_actual()[1] == ',':
            self.coincidir('DELIMITER')  # Coincidir con ,','
            self.expresion()  # Puede ser un identificador o número

        self.coincidir('DELIMITER')  # Coincide con ')'
        self.coincidir('DELIMITER')  # Coincide con ';'

# === Ejemplo de Uso ===
codigo_fuente = """
int main (int x, int y) {
    int i = 0;
    while (i < 5) {
        printf("Iteracion while: ", i);
        i++;
    }
}
"""

# int suma(int a, int b) {
#         int c = a + b;
#         return c;
#     } 

# int suma(int a, int b) {
#       int c;
#       return c = a + b;
#  }

# int main(int x, int y) {
#     int x = 10;
#     int y = 20;
#     int resultado = x + y;

#     if (resultado > 25) {
#         printf("El resultado es mayor que 25");
#     } else {
#         printf("El resultado es menor o igual a 25");
#     }

#     int i = 0;
#     while (i < 5) {
#         printf("Iteracion while: ", i);
#         i++;
#         if (i == 3) {
#             printf("Se encontro un 3, saliendo del while con break");
#             break;
#         }
#     }

#     for (int j = 0; j < 5; j++) {
#         print("Iteración for: ", j);
#         if (j == 2) {
#             printf("Se encontro un 2, saliendo del for con break");
#             break;
#         }
#     }

#     int opcion = 2;
#     switch (opcion) {
#         case 1:
#             printf("Opcion 1 seleccionada\n");
#             break;
#         case 2:
#             printf("Opcion 2 seleccionada, terminando funcion con return");
#             return 0; 
#         case 3:
#             printf("Opcion 3 seleccionada");
#             break;
#         default:
#             printf("Opcion no valida");
#             break;
#     }

#     printf("Este mensaje no se imprimira si opcion es 2");

#     return 0;
# }

# Analisis lexico
tokens = identificar_tokens(codigo_fuente)
print("Tokens encontrados:")
for tipo, valor in tokens:
    print(f'{tipo}: {valor}')

# Analisis sintactico
try:
    print('\nIniciando analisis sintactico...')
    parser = Parser(tokens)
    parser.parsear()
    print('Analisis sintactico completado sin errores')

except SyntaxError as e:
    print(e)
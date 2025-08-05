from graphviz import Digraph

# Precedencia de operadores
PRECEDENCE = {
    '|': 1,  # Unión (prioridad más baja)
    '.': 2,  # Concatenación
    '?': 3,  # Cero o uno
    '*': 3,  # Cero o más
    '+': 3,  # Uno o más
    '^': 4  # Potencia
}

# Verifica la necesidad de un operador de concatenación
def needs_concat(c1, c2):
    if c1 in {'(', '|'} or c2 in {')', '|', '?', '*', '+'}:
        return False
    if c2 in PRECEDENCE and c2 != '.':
        return False
    return True


# Inserta operadores de concatenación explícitos
def format_regex(regex):
    formatted = []
    i = 0
    while i < len(regex):
        c = regex[i]
        if c == '\\':
            if i + 1 < len(regex):
                formatted.append(c + regex[i + 1])
                i += 2
                continue
            else:
                formatted.append(c)
                i += 1
                continue

        # Manejar épsilon (tanto 'ε' como 'Îµ')
        if c == 'ε' or (c == 'Î' and i + 1 < len(regex) and regex[i + 1] == 'µ'):
            formatted.append('ε')
            if c == 'Î':
                i += 2  # Saltar ambos caracteres
            else:
                i += 1
            continue

        formatted.append(c)
        if i + 1 < len(regex):
            next_c = regex[i + 1]
            if needs_concat(c, next_c):
                formatted.append('.')
        i += 1
    return ''.join(formatted)


# Convierte expresión de infix a postifx
def infix_to_postfix(regex):
    output = []
    operator_stack = []
    formatted_re = format_regex(regex)
    i = 0
    while i < len(formatted_re):
        c = formatted_re[i]

        if c == '\\':
            if i + 1 < len(formatted_re):
                output.append(c + formatted_re[i + 1])
                i += 2
            else:
                output.append(c)
                i += 1
            continue

        if c == 'ε':
            output.append(c)
            i += 1
            continue

        if c == '(':
            operator_stack.append(c)
        elif c == ')':
            while operator_stack and operator_stack[-1] != '(':
                output.append(operator_stack.pop())
            operator_stack.pop()
        elif c in PRECEDENCE:
            while (operator_stack and operator_stack[-1] != '(' and
                   PRECEDENCE[operator_stack[-1]] >= PRECEDENCE[c]):
                output.append(operator_stack.pop())
            operator_stack.append(c)
        else:
            output.append(c)
        i += 1

    while operator_stack:
        output.append(operator_stack.pop())
    return ''.join(output)


# Nodo para el árbol sintáctico (AST)
class ASTNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


# Convierte expresión postfix a un árbol sintáctico
def postfix_to_ast(postfix):
    stack = []
    for char in postfix:
        if char in PRECEDENCE:
            node = ASTNode(char)
            if char in ['*', '?', '+']:  # Operadores unarios
                if stack:
                    node.left = stack.pop()
                else:
                    raise ValueError(f"Falta operando para '{char}'")
            else:  # Operadores binarios
                if len(stack) >= 2:
                    node.right = stack.pop()
                    node.left = stack.pop()
                else:
                    raise ValueError(f"Faltan operandos para '{char}'")
            stack.append(node)
        else:
            stack.append(ASTNode(char))
    if len(stack) != 1:
        raise ValueError("Expresión inválida")
    return stack[0]


# Genera visualización del AST
def visualize_ast(node, graph=None):
    if graph is None:
        graph = Digraph()
        graph.node(name=str(id(node)), label=node.value)

    if node.left:
        graph.node(name=str(id(node.left)), label=node.left.value)
        graph.edge(str(id(node)), str(id(node.left)), label='L')
        visualize_ast(node.left, graph)

    if node.right:
        graph.node(name=str(id(node.right)), label=node.right.value)
        graph.edge(str(id(node)), str(id(node.right)), label='R')
        visualize_ast(node.right, graph)

    return graph


# Función principal que procesa el archivo de entrada
def main():
    archivo_expresiones = "expresiones2.txt"
    try:
        with open(archivo_expresiones, 'r', encoding='utf-8') as file:
            print("\nProcesando expresiones regulares:")
            print("=" * 60)
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                print(f"\nLínea {line_num}: {line}")
                print("-" * 60)

                try:
                    # Paso 1: Convertir a postfix
                    postfix = infix_to_postfix(line)
                    print(f"Postfix: {postfix}")

                    # Paso 2: Construir AST
                    ast = postfix_to_ast(postfix)

                    # Paso 3: Visualizar AST
                    graph = visualize_ast(ast)
                    output_filename = f"arbol_{line_num}"
                    graph.render(output_filename, format='png', cleanup=True)
                    print(f"Árbol generado: {output_filename}.png")

                except Exception as e:
                    print(f"[ERROR] Línea {line_num}: {str(e)}")
                print("=" * 60)
    except FileNotFoundError:
        print(f"[ERROR] Archivo no encontrado: {archivo_expresiones}")


if __name__ == "__main__":
    main()
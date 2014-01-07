#!/usr/bin/env python
# coding: utf8 
# Analisis de Contexto del lenguaje Brainiac.
# Modulo: ContBrainiac
# Autores:  Wilthew, Patricia    09-10910
#           Leopoldo Pimentel    06-40095

import ply.lex as lex
import ply.yacc as yacc
import sys
import funciones
import tablaSimbolos
from LexBrainiax import tokens

contador = -1
listaTablas = []

# Clases utilizadas para imprimir el arbol sintactico
                                               
# Clase para NUMERO
class numero:
    def __init__(self,value):
        self.type = "Numero"
        self.value = value
    def __str__(self):
        global contador
        contador = contador + 1
        tabs = "  "*contador
        str_ = str(self.value) + " "
        contador = contador - 1
        return str_

# Clase para IDENTIFICADOR           
class ident:
    def __init__(self,name):
        self.type = "Identificador"
        self.name = name
    def __str__(self):
        global contador
        contador = contador + 1
        tabs = "  "*contador
        str_ =  str(self.name) + " "
        contador = contador - 1
        return str_

# Clase para EXPRESION UNARIA
class op_un:
    def __init__(self,pre,e):                        
        self.pre = pre
        self.e = e
    def __str__(self):
        global contador
        contador = contador + 1
        tabs = "  "*contador
        str_ = "EXPRESION_UNARIA\n" + tabs + "Operador: " + str(self.pre) + "\n" + tabs +  "Valor: "  + str(self.e) + " "
        contador = contador - 1
        return str_

# Clase para EXPRESION BINARIA                       
class op_bin:
    def __init__(self,left,right,op):
        self.left = left
        self.right = right
        self.op = op
        if op == '+':
            self.op = 'Suma'
        elif op == '-':
            self.op = 'Resta'
        elif op == '~':
            self.op = 'Negacion'
        elif op == '*':
            self.op = 'Multiplicacion'
        elif op == '%':
            self.op = 'Modulo'
        elif op == '/':
            self.op = 'Division'
        elif op == '=':
            self.op = 'Igual'
        elif op == '/=':
            self.op = 'Desigual'
        elif op == '<':
            self.op = 'Menor que'
        elif op == '>':
            self.op = 'Mayor que'
        elif op == '>=':
            self.op = 'Mayor o igual que'
        elif op == '<=':
            self.op = 'Menor o igual que'
        elif op == '&':
            self.op = 'Concatenacion'
        elif op == '#':
            self.op = 'Inspeccion'
        elif op == '\/':
            self.op = 'Or'
        else:
            self.op = 'And'

    def __str__(self):
        global contador
        contador = contador + 1
        tabs = contador*"  "
        tabs_plus =  "  " + tabs
        str_ = "EXPRESION_BINARIA\n" + tabs  + "Operacion: " + str(self.op) + "\n"  
        str_ = str_ + tabs + "Operador izquierdo: " + str(self.left) + "\n"  + tabs + "Operador derecho: " + str(self.right)  + " "
        contador = contador - 1
        return str_

# Clase para ITERACION_INDETERMINADA
class inst_while:
    def __init__(self,cond,inst):
        self.cond = cond
        self.inst = inst

    def __str__(self):
        global contador
        contador = contador + 1
        tabs = "  "*contador
        str_ = "ITERACION_INDETERMINADA\n" + tabs + "Condicion: " 
        str_ = str_+ str(self.cond) + "\n" + tabs + "Instruccion: " + str(self.inst) + " "
        contador = contador - 1
        return str_

# Clase para ITERACION_DETERMINADA
class inst_for:
    def __init__(self,ident,inf,sup,inst):
        self.ident = ident
        self.inf = inf
        self.sup = sup
        self.inst = inst

    def __str__(self):
        global contador
        contador = contador + 1
        tabs = "  "*contador
        str_ = "ITERACION_DETERMINADA\n" + tabs + "Identificador: " + str(self.ident) 
        str_ = str_ + "\n" + tabs + "Cota inf: " + str(self.inf) +", Cota sup: " 
        str_ = str_ + str(self.sup) + "\n" + tabs + "Instruccion: " + str(self.inst) + " "
        contador = contador - 1
        return str_

# Clase para CONDICIONAL
class inst_if:
    def __init__(self,cond,instr0,instr1):
        self.cond = cond
        self.instr0 = instr0
        self.instr1 = instr1
    def __str__(self):
        global contador
        contador = contador + 1
        tabs = "  "*contador
        aux = ""
        if self.instr1 != None:
            aux = "\n" +tabs + "Else: " + str(self.instr1) + " "
        str_ = "CONDICIONAL\n" + tabs + "Guardia: " + str(self.cond) + "\n" + tabs + "Exito: " + str(self.instr0) + aux  
        contador = contador - 1
        return str_

# Clase para B-INSTRUCCION
class inst_b:
    def __init__(self, slist, ident):
        self.slist = slist
        self.ident = ident
    def __pop__(self):
        return self.slist.pop()
    def __len__(self):
        return len(self.slist)
    def __str__(self):
        global contador
        contador = contador +1
        tabs = "  "*contador
        lista_simbolos = ""
        for elem in self.slist:
            lista_simbolos = lista_simbolos + str(elem)
        str_ = "B-INSTRUCCION\n" + tabs + "Lista de simbolos: " + lista_simbolos + "\n" 
        straux = tabs + "Identificador: " + str(self.ident) + " "
        contador = contador - 1
        return str_ + straux

# Clase para ASIGNACION
class inst_asig:
    def __init__(self,ident,val):
        self.ident = ident
        self.val = val
    def __str__(self):          
        global contador
        contador = contador + 1
        tabs = "  "*contador
        str_ = "ASIGNACION\n" + tabs + "Identificador: " + str(self.ident) + "\n" + tabs + "Valor: " + str(self.val) + " "
        contador = contador - 1
        return str_

# Clase para READ
class inst_read:
    def __init__(self,ident):
        self.ident = ident
    def __str__(self):
        global contador      
        contador = contador + 1
        tabs = "  "*contador
        str_ = "READ\n" + tabs + "Identificador: " +  str(self.ident.name) + " "
        contador = contador - 1
        return str_

# Clase para WRITE
class inst_write:
    def __init__(self,expr):
        self.expr = expr
    def __str__(self):
        global contador
        contador += 1
        tabs = contador*"  "
        strw = "WRITE" + "\n" + tabs + "Contenido: " 
        str1 = strw + str(self.expr) + " "
        contador = contador - 1
        return str1

# Clase para SECUENCIACION
class inst_list:
    def __init__(self):
        self.lista = []
    def __len__(self):
        return len(self.lista)
    def __pop__(self):
        return self.lista.pop()
    def __str__(self):
        global contador
        contador = contador + 1
                    
        self.lista.reverse()
        str_ = "SECUENCIACION\n"
        contador = contador + 1
        tabs = contador*"  "
        while self.lista:
            elemento =  self.lista.pop()
            str_ = str_ + tabs +   str(elemento)
            if len(self.lista) != 0:
                str_ = str_ +  "\n" + tabs + "\n"
        contador = contador - 1
        return str_

    def print_(self,contador):
        self.lista.reverse()

        while self.lista:
            elemento =  self.lista.pop()
            elemento.print_(contador,0)
            tabs = contador*"  "
            if len(self.lista) != 0:
                str_ = str_ + ";"
        return str_

# Clase para BLOQUE
class bloque:
    def __init__(self,lista):
        self.lista = lista
    def __len__(self):
        return len(self.lista)
    def __str__(self):
        global contador
        contador = contador + 1
        tabs = "  "*contador
        str_ = "BLOQUE\n"
        str_ = str_ + str(self.lista)
        contador = contador - 1
        return str_







#Clase para DECLARACION de variables
class bloqueDeclaracion:
  def __init__(self,listaDeclaraciones):
    # Esta es una lista de lineas del declare
    self.listaDeclaraciones = listaDeclaraciones
    self.tablaSimbolos = tablaSimbolos.SymTable()
    for i in self.listaDeclaraciones.listaPorTipos:
      retorno = self.tablaSimbolos.merge(i.tablaSimbolos)
      global error
      if retorno is not None:
        print 'Error: Linea '+str(retorno[0])+', columna '+str(retorno[1])+': Variable "'+retorno[2]+'" declarada dos veces'
        error = 1
  def __str__(self):
    global contador
    contador = contador + 1
    tabs = "  "*contador

    contador = contador - 1
    return "Hola"

#Clase para DECLARACION de variables por tipos
class declareTipos:
  def __init__(self,listaPorTipos):
    self.listaPorTipos = listaPorTipos    
  def __str__(self):
    global contador
    contador = contador + 1
    tabs = "  "*contador

    str_ = "DECLARE TIPOS\n + tabs"
    for i in self.listaPorTipos:
        str_ = str_ + str(i)
    
    contador = contador - 1
    return str_

      
#Clase que representara una declaracion de variables
#donde contendra en listaVariables todas las variables
#declaradas y en otro atributo tendra el tipo de esas variables
#declaradas
class unaDeclaracion:
  def __init__(self,listaVariables,tipo):
    global error
    self.listaVariables = listaVariables
    self.tipo = tipo
    self.tablaSimbolos = tablaSimbolos.SymTable()
    for i in self.listaVariables.lista: 
      retorno = self.tablaSimbolos.insert(i)
      if retorno == 1:
        error = retorno
        print 'Error: Linea '+str(i.lineno)+', columna '+str(i.colno)+': Variable "'+i.id+'" declarada dos veces'
  def __str__(self):
    global contador
    contador = contador + 1
    tabs = "  "*contador    
    str_ = tabs + "Variables: "
    str_ += str(self.listaVariables)
    str_ += "declaradas como " + self.tipo
    contador = contador - 1
    return str_

#Clase que representa una lista de variables que se dan en una misma
#linea de un declare
class listaVariables:
  def __init__(self,lista):
    self.lista = lista
  def __str__(self):
    str_ = " "
    for i in self.lista:
      str_ += i.id +","    
    contador = contador - 1                
    return str_










# Llamada principal al analizador sintactico
def main():

    # Se abre el archivo y se guarda su contenido en el string codigo
    file_name = sys.argv[1]
    fp = open(file_name)
    codigo = fp.read()


    # Manejo de gramática y construccion de arbol

    # Definicion del símbolo inicial
    start = 'programa'

    # Precedencia de los operadores
    precedence = (
            ('left','TkDisyuncion'),
            ('left','TkConjuncion'),
            ('left','TkIgual','TkDesigual'),
            ('left','TkMenor','TkMayor','TkMayorIgual','TkMenorIgual'),
            ('left','TkMas','TkResta'),
            ('left','TkMult','TkDiv','TkMod'),
            ('left','TkConcat'),
            ('left','TkAt'),
            ('right','uminus','unot', 'uinspeccion'),                
        )


    # PROGRAMA
    def p_programa(p):
        ''' programa : declaracion TkExecute instlist TkDone
                          |  TkExecute instlist TkDone '''
        if len(p) == 5:
            p[0] = p[3]
        elif len(p) == 4:
            p[0] = p[2]


    # TERMINO UNARIO
    def p_term_num(p):
        ''' term : TkNum '''
        p[0] = numero(p[1])
        str_ = ""
        tabs = (contador+1)*"  "


    # IDENTIFICADOR
    def p_term_ident(p):
        ''' term : TkIdent '''
        p[0] = ident(p[1])
        str_ = ""
        tabs = (contador+1)*"  "


    # EXPRESION UNARIA ARITMETICA
    def p_exp_un(p):
        ''' exp_un : TkResta exp %prec uminus 
                      | TkNegacion exp %prec unot
                      | TkInspeccion exp %prec uinspeccion '''
        p[0] = op_un(p[1],p[2])


    # EXPRESION
    def p_exp(p): 
        ''' exp : term
                | exp_un
                | TkParAbre exp TkParCierra
                | TkCorcheteAbre exp TkCorcheteCierra
                | TkLlaveAbre exp TkLlaveCierra 
                | exp TkMas exp 
                | exp TkMult exp
                | exp TkMod exp
                | exp TkDiv exp
                | exp TkResta exp
                | TkTrue
                | TkFalse
                | exp TkIgual exp
                | exp TkDesigual exp
                | exp TkMenor exp
                | exp TkMayor exp
                | exp TkMenorIgual exp
                | exp TkMayorIgual exp
                | exp TkDisyuncion exp
                | exp TkConjuncion exp 
                | exp TkConcat exp '''

        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4 and p[1] != '(' and p[1] != '[' and p[1] != '{':
            p[0] = op_bin(p[1],p[3],p[2])
        else:
            p[0] = p[2]
                

    # ASIGNACION
    def p_instruccion_asignacion(p):
        ''' instruccion : TkIdent TkAsignacion exp '''
        p[0] = inst_asig(p[1],p[3])


    # READ
    def p_instruccion_read(p):
        ''' instruccion : TkRead exp '''
        p[0] = inst_read(p[2])


    # WRITE
    def p_instruccion_write(p):
        ''' instruccion : TkWrite exp '''
        p[0] = inst_write(p[2])


    # WHILE
    def p_instruccion_while(p):
        ''' instruccion : TkWhile exp TkDo instlist TkDone '''
        p[0] = inst_while(p[2],p[4])


    # FOR
    def p_instruccion_for(p):
        ''' instruccion : TkFor TkIdent TkFrom exp TkTo exp TkDo instlist TkDone'''
        p[0] = inst_for(p[2],p[4],p[6],p[8])

    # IF
    def p_instruccion_if(p):
        ''' instruccion : TkIf exp TkThen instlist TkDone
                            | TkIf exp TkThen instlist TkElse instlist TkDone '''
        if len(p) == 6:
            p[0] = inst_if(p[2],p[4],None)
        else:
            p[0] = inst_if(p[2],p[4],p[6])


    # BLOQUE DE INSTRUCCIONES
    def p_instruccion_bloque(p):
        ''' instruccion :  declaracion TkExecute instlist TkDone
                            | TkExecute instlist TkDone '''
        if len(p) == 4:
            p[0] = inst_bloque(p[2])
        elif len(p) == 5:
            p[0] = inst_bloque(p[3])


    # BLOQUE DE B-INSTRUCCION (Ej: {lista_tape} At [a] )
    def p_instruccion_b(p):
        ''' instruccion : TkLlaveAbre lista_tape TkLlaveCierra TkAt ident_tape '''
        p[0] = inst_b(p[2], p[5])

    def p_ident_tape(p):
        ''' ident_tape : TkCorcheteAbre exp TkCorcheteCierra
                           | TkIdent '''
        if len(p) == 4:        
            p[0] = p[2]
        elif len(p) == 2:
            p[0] = p[1] 

 
    # LISTA DE SIMBOLOS DE B-INSTRUCCIONES (Ej: ++++--...>>><..)
    def p_lista_tape(p):
        ''' lista_tape : lista_tape simb_tape
                         | simb_tape '''
        if len(p) == 2:
            p[0] = []
            p[0].append(p[1])
        else:
            p[0] = p[1]
            p[0].append(p[2])

    def p_simb_tape(p):
        '''simb_tape : TkPunto
                         | TkMayor
                         | TkMenor
                         | TkMas
                         | TkResta
                         | TkComa '''
        p[0] = p[1]


    # SECUENCIACION DE INSTRUCCIONES
    def p_instlist(p):
        '''  instlist : instlist semicoloninst 
                      | instruccion '''
        if len(p) == 2:
            p[0] = inst_list()
            p[0].lista.append(p[1])
        elif len(p) == 3:
            p[0] = p[1]
            p[0].lista.append(p[2])
                
    def p_commainst(p):
        ''' semicoloninst : TkPuntoYComa instruccion '''
        p[0] = p[2]


    # DECLARACION
    def p_declaracion(p):
        ''' declaracion : TkDeclare declist '''
        p[0] = bloqueDeclaracion(p[2])
        global listaTablas
        listaTablas.append(p[0].tablaSimbolos)

    def p_declist(p):
        ''' declist : dec TkPuntoYComa declist 
                    | dec '''
        if len(p)>=4:
            p[0] = declareTipos(p[3].listaPorTipos)
            p[0].listaPorTipos.insert(0,p[1])
        else:
            p[0]=declareTipos([p[1]])

    def p_dec(p):
        ''' dec : varlist TkType tipo '''
        p[0] = unaDeclaracion(p[1],p[3])
        for i in p[1].lista:
            i.setType(p[3])

    def p_varlist(p):
        ''' varlist : TkIdent TkComa varlist 
                    | TkIdent '''
        insercion = tablaSimbolos.variable(p[1],'')
        insercion.setLine(p.lineno(1))
        insercion.setColumn(funciones.hallar_columna(p.slice[1].lexer.lexdata,p.slice[1]))
        if(len(p)>=3):  
            p[3].lista.insert(0,insercion)
            p[0] = listaVariables( p[3].lista)
        else:
            p[0] = listaVariables([insercion])

    def p_tipo(p):
        ''' tipo : TkInteger
                | TkBoolean
                | TkTape '''
        p[0] = p[1]


    #Funcion de error del parser
    def p_error(p):
        c = funciones.hallar_columna(codigo,p)
        print "Error de sintaxis en linea %s, columna %s: token \'%s\' inesperado." % (p.lineno,c,p.value[0])
        sys.exit(0)


    # Se construye la funcion del parser
    parser = yacc.yacc()


    # LOGGER

    # Set up a logging object
    import logging
    logging.basicConfig(
        level = logging.DEBUG,
        filename = "parselog.txt",
        filemode = "w",
        format = "%(filename)10s:%(lineno)4d:%(message)s"
    )
    log = logging.getLogger()

    # Se construye el árbol
    arbol = parser.parse(codigo,debug=log)

    # Se imprime el árbol
    print funciones.print_arbol(arbol)


if __name__ == "__main__":
    main()
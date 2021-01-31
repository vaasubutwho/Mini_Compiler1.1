from lexer import *;


class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter
        self.symbols = set()
        self.labelsDeclared = set()
        self.labelsGotoed = set()
        self.curToken = None;
        self.peekHeaderToken = None;
        self.nextToken();
        self.nextToken();

    def checkToken(self, kind):
        return kind == self.curToken.kind

    def checkpeekHeader(self, kind):
        return kind == self.peekHeaderToken.kind;

    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name);
        self.nextToken();

    def nextToken(self):
        self.curToken = self.peekHeaderToken;
        self.peekHeaderToken = self.lexer.getToken();

    def abort(selfself, message):
        sys.exit("Parsing Error" + message);

    def program(self):
        self.emitter.headerLine("#include <stdio.h>")
        self.emitter.headerLine("int main(void){")
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
        while not self.checkToken(TokenType.EOF):
            self.statement();
        self.emitter.emitLine("return 0;");
        self.emitter.emitLine("}");
        # Check that each label referenced in a GOTO is declared.
        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("Attempting to GOTO to undeclared label: " + label)

    def statement(self):
        if self.checkToken(TokenType.SPEAKMJ):
            print("STATEMENT-PRINT")
            self.nextToken();

            if self.checkToken(TokenType.STRING):
                self.emitter.emitLine("printf(\"" + self.curToken.text + "\\n\");")
                self.nextToken();
            else:
                self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                self.emitter.emitLine("));")

        elif self.checkToken(TokenType.NIKDOUBTSIF):
            print("STATEMENT-IF")
            self.nextToken()
            self.emitter.emit("if(")
            self.comparison()

            self.match(TokenType.DOUBTTRUETHEN)
            self.nl()
            self.emitter.emitLine("){")

            while not self.checkToken(TokenType.ENDNIKDOUBT):
                self.statement()

            self.match(TokenType.ENDNIKDOUBT)
            self.emitter.emitLine("}")

        elif self.checkToken(TokenType.ADIMOVE):
            print("STATEMENT-WHILE")
            self.nextToken()
            self.emitter.emit("while(")
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emitLine("){")

            while not self.checkToken(TokenType.ENDADIMOVE):
                self.statement()

            self.match(TokenType.ENDADIMOVE)
            self.emitter.emitLine("}")


        elif self.checkToken(TokenType.LABEL):
            print("STATEMENT-LABEL")
            self.nextToken()
            if self.curToken.text in self.labelsDeclared:
                self.abort("Label already exists: " + self.curToken.text)
            self.labelsDeclared.add(self.curToken.text)
            self.emitter.emitLine(self.curToken.text + ":")
            self.match(TokenType.IDENT)

        elif self.checkToken(TokenType.GOTO):
            print("STATEMENT-GOTO")
            self.nextToken()
            self.labelsGotoed.add(self.curToken.text)
            self.emitter.emitLine("goto " + self.curToken.text + ";")
            self.match(TokenType.IDENT)

        elif self.checkToken(TokenType.AAYUDECLARE):
            print("STATEMENT-AAYUDECLARE")
            self.nextToken()

            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")
            self.emitter.emit(self.curToken.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()
            self.emitter.emitLine(";")


        elif self.checkToken(TokenType.LISTENMJ):
            print("STATEMENT-INPUT")
            self.nextToken()

            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")

            self.emitter.emitLine("if(0 == scanf(\"%" + "f\", &" + self.curToken.text + ")) {")
            self.emitter.emitLine(self.curToken.text + " = 0;")
            self.emitter.emit("scanf(\"%")
            self.emitter.emitLine("*s\");")
            self.emitter.emitLine("}")
            self.match(TokenType.IDENT)


        else:
            self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")

        self.nl();

    def nl(self):
        print("NEWLINE")
        self.match(TokenType.NEWLINE);
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

    def expression(self):
        print("EXPRESSION")

        self.term()

        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term()

    def comparison(self):
        print("COMPARISON")

        self.expression()
        # Must be at least one comparison operator and another expression.
        if self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()

        while self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()

    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(
            TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(
            TokenType.NOTEQ)

    def term(self):
        print("TERM")

        self.unary()

        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.unary()

    def unary(self):
        print("UNARY")

        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        self.primary()

    def primary(self):
        print("PRIMARY (" + self.curToken.text + ")")

        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            if self.curToken.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.curToken.text)
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        else:
            self.abort("Unexpected currentToken at " + self.curToken.text)

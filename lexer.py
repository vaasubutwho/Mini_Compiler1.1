import sys
import enum


class LEXER:
    def __init__(self, input):
        self.source = input + '\n'
        self.currentCharacter = ''
        self.currentPosition = -1

        self.nextChar()

    # Process the next character.
    def nextChar(self):
        self.currentPosition += 1;
        if self.currentPosition >= len(self.source):
            self.currentCharacter = '\0'
        else:
            self.currentCharacter = self.source[self.currentPosition]

    def peekHeader(self):
        if self.currentPosition + 1 >= len(self.source):
            return '\0'

        return self.source[self.currentPosition + 1];

    def skipWhiteSpace(self):
        while self.currentCharacter == ' ' or self.currentCharacter == '\t' or self.currentCharacter == '\r':
            self.nextChar()

    def skipComment(self):
        if self.currentCharacter=='#':
            while self.currentCharacter!='\n':
                self.nextChar();

    def abort(self, message):
        sys.exit("Please correct the following error(s) encountered during lexing." + message)

    def getToken(self):
        self.skipWhiteSpace()
        self.skipComment();
        currentToken = None;
        if self.currentCharacter == '+':
            currentToken = Token(self.currentCharacter, TokenType.PLUS)
        elif self.currentCharacter == '-':
            currentToken = Token(self.currentCharacter, TokenType.MINUS)
        elif self.currentCharacter == '*':
            currentToken = Token(self.currentCharacter, TokenType.ASTERISK)
        elif self.currentCharacter == '/':
            currentToken = Token(self.currentCharacter, TokenType.SLASH)
        elif self.currentCharacter == '\n':
            currentToken = Token(self.currentCharacter, TokenType.NEWLINE)
        elif self.currentCharacter == '\0':
            currentToken = Token(self.currentCharacter, TokenType.EOF)
        elif self.currentCharacter=='=':
            if self.peekHeader()=='=':
                lastChar=self.currentCharacter;
                self.nextChar();
                currentToken=Token(lastChar+self.currentCharacter, TokenType.EQEQ)
            else:
                currentToken=Token(self.currentCharacter, TokenType.EQ);
        elif self.currentCharacter == '>':
            # Check whether this is currentToken is > or >=
            if self.peekHeader() == '=':
                lastChar = self.currentCharacter
                self.nextChar()
                currentToken = Token(lastChar + self.currentCharacter, TokenType.GTEQ)
            else:
                currentToken = Token(self.currentCharacter, TokenType.GT)
        elif self.currentCharacter == '<':
            # Check whether this is currentToken is < or <=
            if self.peekHeader() == '=':
                lastChar = self.currentCharacter
                self.nextChar()
                currentToken = Token(lastChar + self.currentCharacter, TokenType.LTEQ)
            else:
                currentToken = Token(self.currentCharacter, TokenType.LT)
        elif self.currentCharacter == '!':
            if self.peekHeader() == '=':
                lastChar = self.currentCharacter
                self.nextChar()
                currentToken = Token(lastChar + self.currentCharacter, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peekHeader())
        elif self.currentCharacter == '\"':
            # Get characters between quotations.
            self.nextChar()
            startPos = self.currentPosition

            while self.currentCharacter != '\"':
                # Don't allow special characters in the string. No escape characters, newlines, tabs, or %.
                # We will be using C's printf on this string.
                if self.currentCharacter == '\r' or self.currentCharacter == '\n' or self.currentCharacter == '\t' or self.currentCharacter == '\\' or self.currentCharacter == '%':
                    self.abort("Illegal character in string.")
                self.nextChar()

            tokText = self.source[startPos : self.currentPosition] # Get the substring.
            currentToken = Token(tokText, TokenType.STRING)
        elif self.currentCharacter.isdigit():
            # Leading character is a digit, so this must be a number.
            # Get all consecutive digits and decimal if there is one.
            startPos = self.currentPosition
            while self.peekHeader().isdigit():
                self.nextChar()
            if self.peekHeader() == '.': # Decimal!
                self.nextChar()

                # Must have at least one digit after decimal.
                if not self.peekHeader().isdigit():
                    # Error!
                    self.abort("Illegal character in number.")
                while self.peekHeader().isdigit():
                    self.nextChar()

            tokText = self.source[startPos : self.currentPosition + 1] # Get the substring.
            currentToken = Token(tokText, TokenType.NUMBER)

        elif self.currentCharacter.isalpha():
            # Leading character is a letter, so this must be an identifier or a keyword.
            # Get all consecutive alpha numeric characters.
            startPos = self.currentPosition
            while self.peekHeader().isalnum():
                self.nextChar()

            # Check if the currentToken is in the list of keywords.
            tokText = self.source[startPos : self.currentPosition + 1] # Get the substring.
            keyword = Token.checkIfKeyword(tokText)
            if keyword == None: # Identifier
                currentToken = Token(tokText, TokenType.IDENT)
            else:   # Keyword
                currentToken = Token(tokText, keyword)
        elif self.currentCharacter == '\n':
            # Newline.
            currentToken = Token('\n', TokenType.NEWLINE)
        elif self.currentCharacter == '\0':
            # EOF.
            currentToken = Token('', TokenType.EOF)

        else:
            self.abort("Unknown currentToken: " + self.currentCharacter)

        self.nextChar()
        return currentToken;


class Token:
    def __init__(self, tokenText, tokenKind):
        self.text = tokenText;
        self.kind = tokenKind;
    @staticmethod
    def checkIfKeyword(tokenText):
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX.
            if kind.name == tokenText and 100 <= kind.value < 200:
                return kind
        return None

# TokenType is our enum for all the types of tokens.
class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    # Keywords.
    LABEL = 101
    GOTO = 102
    SPEAKMJ = 103
    LISTENMJ = 104
    AAYUDECLARE= 105
    NIKDOUBTSIF = 106
    DOUBTTRUETHEN = 107
    ENDNIKDOUBT = 108
    ADIMOVE = 109
    REPEAT = 110
    ENDADIMOVE = 111
    # Operators.
    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211

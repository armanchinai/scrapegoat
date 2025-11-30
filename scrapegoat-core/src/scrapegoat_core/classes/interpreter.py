"""
"""

# IMPORTS
import re
from enum import Enum, auto
from abc import ABC, abstractmethod

from .command import GrazeCommand, ChurnCommand, DeliverCommand, FetchCommand
from .conditions import InCondition, IfCondition
from .block import GoatspeakBlock, Query


class TokenType(Enum):
    """
    """
    ACTION = auto()
    CONDITIONAL = auto()
    KEYWORD = auto()
    OPERATOR = auto()
    NUMBER = auto()
    IDENTIFIER = auto()
    FILE_TYPE = auto()
    NEGATION = auto()
    FLAG = auto()
    SEMICOLON = auto()
    UNKNOWN = auto()


class Token:
    """
    """
    def __init__(self, type: str, value: str):
        """
        """
        self.type = type
        self.value = value

    def __repr__(self):
        """
        """
        return f"Token(type={self.type}, value='{self.value}')"
    

class Tokenizer:
    def __init__(self):
        self.ACTIONS = {"select", "scrape", "extract", "output", "visit"}
        self.CONDITIONALS = {"if", "in"}
        self.KEYWORDS = {"position"}
        self.OPERATORS = {"=", "!=", "like"}
        self.NEGATIONS = {"not"}
        self.FILE_TYPES = {"json", "csv"}
        self.FLAGS = {}

    def _preprocess_query(self, query: str) -> str:
        """
        """
        query = re.sub(r'\[.*?\]', '', query, flags=re.DOTALL)
        query = re.sub(r'^\s*!goatspeak\s*', '', query, flags=re.IGNORECASE)
        pattern = r"""
            (?:'[^'\\]*(?:\\.[^'\\]*)*' |      # single-quoted string
            "[^"\\]*(?:\\.[^"\\]*)*" |        # double-quoted string
            //.*$                             # line comment
            )
        """
        def replacer(m):
            s = m.group(0)
            # Only remove if it’s a comment, not quoted text
            return '' if s.strip().startswith('//') else s

        query = re.sub(pattern, replacer, query, flags=re.MULTILINE | re.VERBOSE)
        return query

    def tokenize(self, query: str) -> list[Token]:
        """
        """
        query = self._preprocess_query(query)
        
        tokens = []
        pattern = (
            r'(--[A-Za-z0-9_-]+|'
            r'\bSELECT\b|\bSCRAPE\b|\bEXTRACT\b|\bOUTPUT\b|\bVISIT\b|\bIN\b|\bIF\b|\bPOSITION\b|\bNOT\b|\bLIKE\b|\bJSON\b|\bCSV\b|'
            r'!=|==|=|;|\n|'
            r'"(?:[^"]*)"|\'(?:[^\']*)\'|'
            r'@?[A-Za-z_][A-Za-z0-9_-]*|'
            r'\d+)'
        )

        for match in re.finditer(pattern, query.replace("\n", ""), flags=re.IGNORECASE):
            raw_value = match.group(0)
            token = self._classify_token(raw_value)
            tokens.append(token)
        return tokens

    def _classify_token(self, raw_value: str) -> Token:
        """
        """
        if raw_value[0] in ('"', "'") and raw_value[-1] == raw_value[0]:
            return Token(TokenType.IDENTIFIER, raw_value[1:-1])
        val_lower = raw_value.lower()
        if val_lower.startswith("--"):
            return Token(TokenType.FLAG, val_lower[2:].replace("-", "_"))
        if val_lower in self.ACTIONS:
            return Token(TokenType.ACTION, val_lower)
        if val_lower in self.CONDITIONALS:
            return Token(TokenType.CONDITIONAL, val_lower)
        if val_lower in self.KEYWORDS:
            return Token(TokenType.KEYWORD, val_lower)
        if val_lower in self.OPERATORS:
            return Token(TokenType.OPERATOR, val_lower)
        if val_lower in self.NEGATIONS:
            return Token(TokenType.NEGATION, val_lower)
        if raw_value == ";":
            return Token(TokenType.SEMICOLON, raw_value)
        if val_lower.isdigit():
            return Token(TokenType.NUMBER, val_lower)
        if val_lower in self.FILE_TYPES:
            return Token(TokenType.FILE_TYPE, val_lower)
        return Token(TokenType.IDENTIFIER, raw_value)
    

class Parser(ABC):
    """
    """
    @abstractmethod
    def parse(self, tokens: list[Token], index) -> tuple:
        """
        """
        pass


class FlagParser(Parser):
    """
    """
    def __init__(self):
        """
        """
        pass

    def parse(self, tokens, index) -> tuple:
        """
        """
        flags = {}
        
        while tokens[index].type != TokenType.SEMICOLON:
            token = tokens[index]
            if token.type != TokenType.FLAG:
                raise SyntaxError(f"Expected flag at token {token}")
            flag_name = token.value
            index += 1
            token = tokens[index]
            if token.type != TokenType.IDENTIFIER:
                flag_value = True
            else:
                flag_value = token.value
                index += 1
            flags[flag_name] = flag_value
        return flags, index


class ConditionParser(Parser):
    """
    """
    def __init__(self):
        """
        """
        pass

    def parse(self, tokens, index, element) -> tuple:
        negated = False
        if tokens[index].type == TokenType.NEGATION:
            negated = True
            index += 1
        token = tokens[index]
        if token.type != TokenType.CONDITIONAL:
            raise SyntaxError(f"Expected conditional at {token}")
        if token.value == "if":
            return self._parse_if(tokens, index, element, negated)
        elif token.value == "in":
            return self._parse_in(tokens, index, element, negated)
        
    def _parse_if(self, tokens, index, element, negated) -> tuple:
        """
        """
        index += 1
        token = tokens[index]
        if token.type != TokenType.IDENTIFIER:
            raise SyntaxError(f"Expected key after IF at {token}")
        key = token.value
        index += 1
        token = tokens[index]
        if token.type != TokenType.OPERATOR:
            condition = IfCondition(key=key, value=None, negated=negated, query_tag=element)
            return condition, index
        if token.value == "!=":
            negated = True
        like = token.value == "like"
        index += 1
        token = tokens[index]
        if token.type not in {TokenType.IDENTIFIER, TokenType.NUMBER}:
            raise SyntaxError(f"Expected value after IF {key} = at {token}")
        value = token.value
        condition = IfCondition(key=key, value=value, negated=negated, query_tag=element, like=like)
        index += 1
        return condition, index
    
    def _parse_in(self, tokens, index, element, negated) -> tuple:
        """
        """
        index += 1
        token = tokens[index]
        if token.type == TokenType.KEYWORD:
            index += 1
            token = tokens[index]
            if token.type != TokenType.OPERATOR:
                raise SyntaxError(f"Expected '=' after IN POSITION at {token}")
            if token.value == "!=":
                negated = True
            index += 1
            token = tokens[index]
            if token.type != TokenType.NUMBER:
                raise SyntaxError(f"Expected number after IN POSITION = at {token}")
            position = int(token.value)
            condition = InCondition(target="POSITION", value=position, negated=negated, query_tag=element)
        else:
            if token.type != TokenType.IDENTIFIER:
                raise SyntaxError(f"Expected element after IN at {token}")
            target = token.value
            condition = InCondition(target=target, negated=negated, query_tag=element)
        index += 1
        return condition, index


class ScrapeSelectParser(Parser):
    """
    """
    def __init__(self, condition_parser: ConditionParser, flag_parser: FlagParser):
        """
        """
        self.condition_parser = condition_parser
        self.flag_parser = flag_parser

    def parse(self, tokens, index) -> tuple:
        """
        """
        action = tokens[index].value
        index += 1

        # count
        count = 0
        if tokens[index].type == TokenType.NUMBER:
            count = int(tokens[index].value)
            index += 1

        # element
        if tokens[index].type != TokenType.IDENTIFIER:
            raise SyntaxError(f"Expected element at token {tokens[index]}")
        element = tokens[index].value
        index += 1

        # conditions
        conditions = []
        while tokens[index].type != TokenType.SEMICOLON and tokens[index].type != TokenType.FLAG:
            condition, index = self.condition_parser.parse(tokens, index, element)
            conditions.append(condition)

        # flags
        flags = {}
        if tokens[index].type == TokenType.FLAG:
            flags, index = self.flag_parser.parse(tokens, index)

        instruction = GrazeCommand(action=action, count=count, element=element, conditions=conditions, **flags)
        return instruction, index + 1
    

class ExtractParser(Parser):
    """
    """
    def __init__(self, flag_parser: FlagParser):
        """
        """
        self.flag_parser = flag_parser

    def parse(self, tokens, index) -> tuple:
        """
        """
        fields = []

        index += 1
        
        # fields
        while tokens[index].type != TokenType.SEMICOLON and tokens[index].type != TokenType.FLAG:
            if tokens[index].type == TokenType.IDENTIFIER:
                fields.append(tokens[index].value)
            index += 1
        
        # flags
        flags = {}
        if tokens[index].type == TokenType.FLAG:
            flags, index = self.flag_parser.parse(tokens, index)

        instruction = ChurnCommand(fields=fields, **flags)
        return instruction, index + 1
    

class OutputParser(Parser):
    """
    """
    def __init__(self, flag_parser: FlagParser):
        """
        """
        self.flag_parser = flag_parser

    def parse(self, tokens, index) -> tuple:
        """
        """
        index += 1

        # file type
        if tokens[index].type != TokenType.FILE_TYPE:
            raise SyntaxError(f"Expected file type at token {tokens[index]}")
        file_type = tokens[index].value
        index += 1

        # flags
        flags = {}
        if tokens[index].type == TokenType.FLAG:
            flags, index = self.flag_parser.parse(tokens, index)

        instruction = DeliverCommand(file_type=file_type, **flags)
        return instruction, index + 1
    

class VisitParser(Parser):
    """
    """
    def __init__(self, flag_parser: FlagParser):
        """
        """
        self.flag_parser = flag_parser

    def parse(self, tokens, index) -> tuple:
        """
        """
        index += 1

        # url
        if tokens[index].type != TokenType.IDENTIFIER:
            raise SyntaxError(f"Expected URL at token {tokens[index]}")
        url = tokens[index].value
        index += 1

        # flags
        flags = {}
        if tokens[index].type == TokenType.FLAG:
            flags, index = self.flag_parser.parse(tokens, index)

        instruction = FetchCommand(url=url, **flags)
        return instruction, index + 1


class Interpeter:
    """
    """
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.condition_parser = ConditionParser()
        self.flag_parser = FlagParser()
        self.action_parsers = {
            "visit": VisitParser(self.flag_parser),
            "scrape": ScrapeSelectParser(self.condition_parser, self.flag_parser),
            "select": ScrapeSelectParser(self.condition_parser, self.flag_parser),
            "extract": ExtractParser(self.flag_parser),
            "output": OutputParser(self.flag_parser),
        }

    def _manage_interpreter_state(self, instructions, goatspeak_blocks) -> tuple:
        """
        """
        if len(instructions) >= 2 and instructions[-2].action in ("scrape", "extract", "output") and instructions[-1].action in ("scrape", "select", "visit"):
            current_instructions = instructions[:-1]
            next_instruction = instructions[-1]

            fetch_command = next((cmd for cmd in current_instructions if cmd.action == "visit"), None)
            graze_commands = [cmd for cmd in current_instructions if cmd.action in ("scrape", "select")]
            churn_command = next((cmd for cmd in current_instructions if cmd.action == "extract"), None)
            deliver_command = next((cmd for cmd in current_instructions if cmd.action == "output"), None)

            query = Query(
                graze_commands=graze_commands,
                fetch_command=fetch_command,
                churn_command=churn_command,
                deliver_command=deliver_command,
            )

            instructions = [next_instruction]
            last_block = goatspeak_blocks[-1]
            last_block.query_list.append(query)

        if instructions[-1].action == "visit":
            fetch_command = instructions[-1]
            goatspeak_blocks.append(GoatspeakBlock(fetch_command=fetch_command, query_list=[]))
            instructions = [fetch_command]
            return instructions, goatspeak_blocks
        
        return instructions, goatspeak_blocks
                
    def interpret(self, query: str) -> list[GoatspeakBlock]:
        """
        """
        tokens = self.tokenizer.tokenize(query)
        instructions = []
        goatspeak_blocks = []
        index = 0

        while index < len(tokens):
            token = tokens[index]
            if token.type != TokenType.ACTION:
                raise SyntaxError(f"Expected action at token {token}")
            
            parser = self.action_parsers.get(token.value)
            
            if parser is None:
                raise SyntaxError(f"Unknown action '{token.value}' at token {token}")
            
            instruction, index = parser.parse(tokens, index)
            instructions.append(instruction)
            instructions, goatspeak_blocks = self._manage_interpreter_state(instructions, goatspeak_blocks)

        if instructions:
            fetch_command = next((cmd for cmd in instructions if cmd.action == "visit"), None)
            graze_commands = [cmd for cmd in instructions if cmd.action in ("scrape", "select")]
            churn_command = next((cmd for cmd in instructions if cmd.action == "extract"), None)
            deliver_command = next((cmd for cmd in instructions if cmd.action == "output"), None)

            query = Query(
                graze_commands=graze_commands,
                fetch_command=fetch_command,
                churn_command=churn_command,
                deliver_command=deliver_command,
            )

            if not goatspeak_blocks:
                goatspeak_blocks.append(GoatspeakBlock(fetch_command=fetch_command, query_list=[query]))
            else:
                last_block = goatspeak_blocks[-1]
                last_block.query_list.append(query)
        return goatspeak_blocks

            
def main():
    """
    """
    pass


if __name__ == "__main__":
    main()

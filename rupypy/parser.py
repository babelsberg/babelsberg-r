from rupypy import ast


class ParserError(Exception):
    pass


class Parser(object):
    ARG_STARTSWITH = ["NUMBER", "IDENTIFIER", "SYMBOL_BEGIN"]

    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def read(self, expected):
        return self.read_any([expected])

    def read_any(self, expecteds):
        t = self.tokens[self.position]
        if t.name not in expecteds:
            self.error("%s expected, got %s" % (", ".join(expecteds), t.name))
        self.position += 1
        return t

    def match(self, expected):
        return self.match_any([expected])

    def match_any(self, expecteds):
        return self.tokens[self.position].name in expecteds

    def accept(self, expected):
        return self.accept_any([expected])

    def accept_any(self, expecteds):
        if self.match_any(expecteds):
            return self.read_any(expecteds)
        return None

    def lineno(self, token):
        return token.source_pos.lineno

    def error(self, message):
        raise ParserError(message)

    def parse(self):
        return self.parse_main()

    def parse_main(self):
        block = self.parse_suite(until=["EOF"])
        self.read("EOF")
        return ast.Main(block)

    def parse_suite(self, until):
        stmts = []
        while True:
            if self.match_any(until):
                break
            if self.match("LINE_END"):
                self.read("LINE_END")
                continue
            stmts.append(self.parse_stmt())
            if not self.match("LINE_END"):
                break
            self.read("LINE_END")
        return ast.Block(stmts)

    def parse_stmt(self):
        stmt = self.parse_real_stmt()
        return stmt

    def parse_real_stmt(self):
        if self.match("ALIAS"):
            return self.parse_alias()
        elif self.match("RETURN"):
            return self.parse_return()
        else:
            return ast.Statement(self.parse_expr())

    def parse_alias(self):
        t = self.read("ALIAS")
        t_ident1 = self.read("IDENTIFIER")
        t_ident2 = self.read("IDENTIFIER")
        return ast.Alias(
            ast.ConstantSymbol(t_ident1.source),
            ast.ConstantSymbol(t_ident2.source),
            self.lineno(t)
        )

    def parse_return(self):
        self.read("RETURN")
        return ast.Return(self.parse_expr())

    def parse_expr(self):
        return self.parse_literal_bool()

    def _build_tree_climber(lhs_meth, ops, rhs_meth):
        lhs_meth = "parse_" + lhs_meth
        rhs_meth = "parse_" + rhs_meth

        def impl(self):
            lhs = getattr(self, lhs_meth)()
            if self.match_any(ops):
                t_op = self.read_any(ops)
                op = t_op.source
                rhs = getattr(self, rhs_meth)()
                if op == "!~":
                    return ast.Not(ast.BinOp("=~", lhs, rhs, self.lineno(t_op)))
                elif op == "or":
                    return ast.Or(lhs, rhs)
                elif op == "and":
                    return ast.And(lhs, rhs)
                return ast.BinOp(op, lhs, rhs, self.lineno(t_op))
            return lhs
        return impl

    parse_literal_bool = _build_tree_climber("contained_expr", ["OR_LITERAL", "AND_LITERAL"], "literal_bool")

    def parse_contained_expr(self):
        if self.match("NOT_LITERAL"):
            return self.parse_not()
        elif self.match("YIELD"):
            return self.parse_yield()
        return self.parse_assignment()

    def parse_yield(self):
        t_yield = self.read("YIELD")
        return ast.Yield([self.parse_arg()], self.lineno(t_yield))

    def parse_assignment(self):
        targets = []
        while True:
            if self.accept("UNARY_STAR"):
                targets.append(ast.Splat(self.parse_arg()))
            else:
                targets.append(self.parse_arg())
            if not self.accept("COMMA"):
                break
        if self.match_any(["EQ", "PLUS_EQUAL"]):
            t_op = self.read_any(["EQ", "PLUS_EQUAL"])
            rhs = self.parse_expr()
            if len(targets) == 1:
                return ast.Assignment(targets[0], rhs)
            else:
                return ast.MultiAssignment(targets, rhs)
        elif len(targets) == 1:
            return targets[0]
        else:
            self.error(None)

    def parse_arg(self):
        return self.parse_range()

    parse_range = _build_tree_climber("match", [], "range")
    parse_match = _build_tree_climber("bool", ["EQUAL_TILDE", "EXCLAMATION_TILDE"], "match")
    parse_bool = _build_tree_climber("comparison", ["OR", "AND", "CARET"], "bool")
    parse_comparison = _build_tree_climber("or", ["LEGT", "GT", "LT", "EQEQ", "EQEQEQ", "NE"], "comparison")
    parse_or = _build_tree_climber("and", ["PIPE"], "and")
    parse_and = _build_tree_climber("shiftive", ["AMP"], "and")
    parse_shiftive = _build_tree_climber("additive", ["LSHIFT", "RSHIFT"], "shiftive")
    parse_additive = _build_tree_climber("multitive", ["PLUS", "MINUS"], "additive")
    parse_multitive = _build_tree_climber("unary", ["MUL", "DIV", "MODULO"], "multitive")

    def parse_unary(self):
        if self.match_any("EXCLAMATION"):
            t_op = self.read_any("EXCLAMATION")
            e = self.parse_expr()
            return ast.UnaryOp(t_op.source, e, self.lineno(t_op))
        return self.parse_pow()

    parse_pow = _build_tree_climber("send", ["POW"], "pow")

    def parse_send(self):
        if self.match_any(["IDENTIFIER", "CONSTANT"]):
            t_name = self.read_any(["IDENTIFIER", "CONSTANT"])
            if not self.match_any(["DOT", "COLONCOLON", "LSUBSCRIPT"]):
                args, block_arg = self.parse_send_info()
                if args or block_arg:
                    receiver = ast.Send(ast.Self(self.lineno(t_name)), t_name.source, args, block_arg, self.lineno(t_name))
                elif t_name.name == "IDENTIFIER":
                    return ast.Variable(t_name.source, self.lineno(t_name))
                else:
                    return ast.LookupConstant(ast.Scope(self.lineno(t_name)), t_name.source)
            else:
                receiver = ast.Variable(t_name.source, self.lineno(t_name))
        else:
            receiver = self.parse_primary()
        return self.handle_trailers(receiver)

    def handle_trailers(self, receiver):
        while True:
            if self.accept("DOT"):
                t_ident = self.read("IDENTIFIER")
                if not self.match_any(["DOT", "COLONCOLON", "LSUBSCRIPT"]):
                    args, block_arg = self.parse_send_info()
                    return ast.Send(receiver, t_ident.source, args, block_arg, self.lineno(t_ident))
                receiver = ast.Send(receiver, t_ident.source, [], None, self.lineno(t_ident))
            elif self.accept("COLONCOLON"):
                t_name = self.read_any(["IDENTIFIER", "CONSTANT"])
                if t_name.name == "CONSTANT":
                    receiver = ast.LookupConstant(receiver, t_name.source, self.lineno(t_name))
                else:
                    raise NotImplementedError
            elif self.match("LSUBSCRIPT"):
                t_sub = self.read("LSUBSCRIPT")
                receiver = ast.Subscript(
                    receiver,
                    [self.parse_arg()],
                    self.lineno(t_sub),
                )
                self.read("RBRACKET")
            else:
                break
        return receiver

    def parse_send_info(self):
        args = []
        block = None
        if self.accept("LPAREN"):
            args, block = self.parse_send_args()
            self.read("RPAREN")
        else:
            args, block = self.parse_send_args()
        if self.match("LBRACE"):
            if block:
                self.error()
            block = self.parse_brace_block()
        return args, block

    def parse_send_args(self):
        args = []
        block_arg = None
        while True:
            if self.match("AMP"):
                raise NotImplementedError
            elif self.accept("UNARY_STAR"):
                args.append(ast.Splat(self.parse_arg()))
            else:
                if not self.match_any(self.ARG_STARTSWITH):
                    break
                arg = self.parse_arg()
                if self.accept("ARROW"):
                    pairs = [(arg, self.parse_arg())]
                    while True:
                        if not self.match_any(self.ARG_STARTSWITH):
                            break
                        arg = self.parse_arg()
                        self.read("ARROW")
                        pairs.append((arg, self.parse_arg()))
                        if not self.match("COMMA"):
                            break
                        self.read("COMMA")
                    args.append(ast.Hash(pairs))
                    break
                args.append(arg)
            if not self.match("COMMA"):
                break
            self.read("COMMA")
        return args, block_arg

    def parse_brace_block(self):
        self.read("LBRACE")
        args = []
        splat_arg = None
        if self.match("OR"):
            self.read("OR")
        elif self.match("PIPE"):
            self.read("PIPE")
            args, splat_arg, block_arg = self.parse_arglist()
            self.read("PIPE")
        block = self.parse_suite(["RBRACE"])
        self.read("RBRACE")
        return ast.SendBlock(args, splat_arg, block)

    def parse_primary(self):
        if self.match("DEF"):
            return self.parse_def()
        elif self.match("WHILE"):
            return self.parse_while()
        elif self.match("LPAREN"):
            return self.parse_parens()
        elif self.match("LBRACKET"):
            return self.parse_array()
        elif self.match("NUMBER"):
            return self.parse_number()
        elif self.match("STRING_BEGIN"):
            return self.parse_string_begin()
        elif self.match("REGEXP_BEGIN"):
            return self.parse_regexp_begin()
        elif self.match("SYMBOL_BEGIN"):
            return self.parse_symbol_begin()
        elif self.match("SSTRING"):
            return self.parse_sstring()
        elif self.match("CONSTANT"):
            return self.parse_constant()
        elif self.match("IDENTIFIER"):
            return self.parse_identifier()
        elif self.match("GLOBAL"):
            return self.parse_global()
        elif self.match("INSTANCE_VAR"):
            return self.parse_instance_var()
        raise NotImplementedError

    def parse_def(self):
        self.read("DEF")
        t_name = self.read_any(["IDENTIFIER", "GT", "LT", "GE", "LE", "EQEQ"])
        args, splat_arg, block_arg = self.parse_argdecl()
        block = self.parse_suite(["RESCUE", "ENSURE", "END"])
        self.read("END")
        return ast.Function(None, t_name.source, args, splat_arg, block_arg, block)

    def parse_while(self):
        self.read("WHILE")
        cond = self.parse_expr()
        self.parse_do()
        body = self.parse_suite(["END"])
        self.read("END")
        return ast.While(cond, body)

    def parse_do(self):
        seen = False
        if self.match("LINE_END"):
            self.read("LINE_END")
            seen = True
        if self.match("DO"):
            self.read("DO")
            seen = True
        if not seen:
            self.error()

    def parse_parens(self):
        self.read("LPAREN")
        e = self.parse_expr()
        self.read("RPAREN")
        return e

    def parse_array(self):
        self.read("LBRACKET")
        self.read("RBRACKET")
        return ast.Array([] )

    def parse_argdecl(self):
        paren = self.match("LPAREN")
        if paren:
            self.read("LPAREN")
        args, splat_arg, block_arg = self.parse_arglist()
        if paren:
            self.read("RPAREN")
        else:
            self.read("LINE_END")
        return args, splat_arg, block_arg

    def parse_arglist(self):
        args = []
        splat_arg = None
        block_arg = None
        while True:
            if self.match("IDENTIFIER"):
                t_arg = self.read("IDENTIFIER")
                if self.match("EQ"):
                    self.read("EQ")
                    raise NotImplementedError
                args.append(ast.Argument(t_arg.name))
            elif self.match("UNARY_STAR"):
                raise NotImplementedError
            elif self.match("AMP"):
                raise NotImplementedError
            else:
                break
            if not self.match("COMMA"):
                break
            self.read("COMMA")
        return args, splat_arg, block_arg

    def parse_number(self):
        t_num = self.read("NUMBER")
        if "." in t_num.source or "E" in t_num.source:
            return ast.ConstantFloat(float(t_num.source))
        elif "X" in t_num.source:
            return ast.ConstantInt(int(t_num.source[2:], 16))
        elif "O" in t_num.source:
            return ast.ConstantInt(int(t_num.source[2:], 8))
        elif "B" in t_num.source:
            return ast.ConstantInt(int(t_num.source[2:], 2))
        else:
            return ast.ConstantInt(int(t_num.source))
        raise NotImplementedError

    def parse_string_begin(self):
        self.read("STRING_BEGIN")
        string_parts = self.parse_string()
        self.read("STRING_END")
        return ast.DynamicString(string_parts)

    def parse_regexp_begin(self):
        self.read("REGEXP_BEGIN")
        s = self.parse_string_begin()
        self.read("REGEXP_END")
        if len(s.strvalues) == 1 and isinstance(s.strvalues[0], ast.ConstantString):
            return ast.ConstantRegexp(s.strvalues[0].strvalue)
        return ast.DynamicRegexp(s.strvalues)

    def parse_symbol_begin(self):
        self.read("SYMBOL_BEGIN")
        if self.match("IDENTIFIER"):
            t_sym = self.read("IDENTIFIER")
            return ast.ConstantSymbol(t_sym.source)
        raise NotImplementedError

    def parse_sstring(self):
        t_s = self.read("SSTRING")
        return ast.ConstantString(t_s.source)

    def parse_string(self):
        t_s = self.read("STRING_VALUE")
        return [ast.ConstantString(t_s.source)]

    def parse_constant(self):
        t_const = self.read("CONSTANT")
        return ast.LookupConstant(
            ast.Scope(self.lineno(t_const)), t_const.source, self.lineno(t_const)
        )

    def parse_identifier(self):
        t_ident = self.read("IDENTIFIER")
        return ast.Variable(t_ident.source, self.lineno(t_ident))

    def parse_global(self):
        t_global = self.read("GLOBAL")
        return ast.Global(t_global.source)

    def parse_instance_var(self):
        t_ivar = self.read("INSTANCE_VAR")
        return ast.InstanceVariable(t_ivar.source)

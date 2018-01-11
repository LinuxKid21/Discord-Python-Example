"""
discord bot cog that is used for various number utility functions
"""
import discord
from discord.ext import commands

class BoolUtilsCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bool(self, ctx, exp):
        """Creates truth table from expression using !,*,^,+
        """
        await ctx.send(get_bool_table(exp))

def setup(bot):
    """Sets up the cog"""
    bot.add_cog(BoolUtilsCog(bot))

def get_bool_table(exp):
    """Parses a boolean expression and creates a truth table"""
    boolean_exp = BooleanExpr(exp)
    return "```" + boolean_exp.get_truth_table() + "```"

#####################################################################
#####################################################################
#####################################################################
#####################################################################
#####################################################################

class BooleanExpr:
    orig_exp = "empty"
    disp_exp = "empty"
    post_exp = ""
    var_set = set()
    var_stack = []
    op_stack = []
    result_formatted = ""
    error = False
    error_msg = ""

    prec_dict = {
        '!' : 0, # NOT
        '*' : 1, # AND
        '^' : 2, # XOR
        '+' : 3, # OR
        '(' : 8,
        ')' : 9,
        -1  : 10 # Stack is empty, skip
    }

    def __init__(self, exp):
        self.var_set.clear()
        self.disp_exp = exp
        self.orig_exp = "".join(exp.split())
        self.op_stack[:] = []
        self.var_stack[:] = []
        self.error = False
        self.error_msg = ""
        self.process_exp(self.orig_exp)

    def process_exp(self, exp):
        """
        Processes an in-fix expression and saves a post-fix version
        of the expression on the class level. The post-fix expression
        is easier to evaluate in code, thus leading to greater efficiency.
        """
        self.post_exp = ""
        # Step through chars of booelean expression
        for char in exp:
            # print(char)
            # print(self.op_stack)
            # print(self.var_stack)
            if self.error == True:
                return
            if char == ' ':
                continue
            # Alphas are variables
            elif char.isalpha():
                self.var_set.add(char)
                self.var_stack.append(char)
                self.post_exp += char
            # Start parens
            elif char == '(':
                self.op_stack.append(char)
            # End parens
            elif char == ')':
                while self.get_top(self.op_stack) != '(':
                    self.process_an_op()
                    if self.get_top(self.op_stack) == -1:
                        self.error = True
                        self.error_msg = "Unbalanced paren: )"
                        return
                if self.op_stack:
                    self.op_stack.pop()
            elif self.is_valid_op(char):
                self.process_char(char)
            else:
                self.error = True
                self.error_msg = "{} is not a valid symbol!".format(char)
        if self.error == True:
            return
        while self.op_stack and len(self.var_stack) > 0:
            if self.get_top(self.op_stack) == '(':
                self.error = True
                self.error_msg = "Unbalanced paren: ("
            self.process_an_op()

    def is_valid_op(self, char):
        result = char == '+' or char == '^' or char == '*' or char == '!'
        return result

    def process_char(self, char):
        prec = self.prec_dict[char]
        while prec >= self.prec_dict[self.get_top(self.op_stack)]:
            self.process_an_op()
        self.op_stack.append(char)

    def get_top(self, arr):
        if not arr:
            # self.error = True
            return -1
        return arr[-1]

    def process_an_op(self):
        if not self.op_stack:
            self.error = True
            self.error_msg = "Op stack is empty while trying to process op"
            return
        temp = self.get_top(self.op_stack)
        self.op_stack.pop()
        # print("Processing: {}".format(temp))
        self.post_exp += temp
        if temp == '!':
            pass
        else:
            if len(self.var_stack) < 2:
                self.error = True
                self.error_msg = "Too many operators!"
                return
            self.var_stack.pop()
            self.var_stack.pop()
            self.var_stack.append("NUL")

######################################################################
######################################################################
######################################################################

    def process_all_exps(self):
        self.result_formatted = ""
        vars = []
        for elem in self.var_set:
            vars.append(elem)
        vars.sort()
        var_num = 0
        var_dict = {}
        self.format_header(vars)

        var_dict[vars[var_num]] = False
        self.recurse_through_var(vars, var_dict, var_num + 1)
        var_dict[vars[var_num]] = True
        self.recurse_through_var(vars, var_dict, var_num + 1)
        self.result_formatted += "+" + "---+" * len(vars)
        self.result_formatted += "-" * len(self.disp_exp) + "--+\n"

    def recurse_through_var(self, vars, var_dict, depth):
        if depth >= len(self.var_set):
            self.process_single_exp(var_dict, vars)
        else:
            var_dict[vars[depth]] = False
            self.recurse_through_var(vars, var_dict, depth + 1)
            var_dict[vars[depth]] = True
            self.recurse_through_var(vars, var_dict, depth + 1)

    def process_single_exp(self, dict_bool, vars):
        # print(dict_bool)
        post_stack = []
        for char in self.post_exp:
            # print(post_stack)
            if char.isalpha():
                post_stack.append(dict_bool[char])
            elif char in self.prec_dict:
                if char == '!':
                    one = not post_stack.pop()
                    post_stack.append(one)
                if char == '*':
                    one = post_stack.pop()
                    two = post_stack.pop()
                    result = one and two
                    post_stack.append(result)
                if char == '+':
                    one = post_stack.pop()
                    two = post_stack.pop()
                    result = one or two
                    post_stack.append(result)
                if char == '^':
                    one = post_stack.pop()
                    two = post_stack.pop()
                    result = one and not two or two and not one
                    post_stack.append(result)
        self.format_result(post_stack.pop(), dict_bool, vars)
        # print("Single result: {}".format(post_stack.pop()))

    def format_header(self, vars):
        self.result_formatted += "+" + "---+" * len(vars)
        self.result_formatted += "-" * len(self.disp_exp) + "--+\n"
        for var in vars:
            self.result_formatted += "| {} ".format(var)
        self.result_formatted += "| {} |\n".format(self.disp_exp)
        self.result_formatted += "+---" * len(vars)
        self.result_formatted += "+" + "-" * len(self.disp_exp) + "--+\n"

    def format_result(self, result, dict_bool, vars):
        for var in vars:
            booly = self.bool_to_int(dict_bool[var])
            self.result_formatted += "| {} ".format(booly)
        res = self.bool_to_int(result)
        self.result_formatted += "| {}".format(res)
        self.result_formatted += " " * len(self.disp_exp) + "|\n"

    def bool_to_int(self, booly):
        if booly == True:
            return 1
        else:
            return 0

    def valid_vars(self):
        for i in range(1, len(self.orig_exp)):
            if self.orig_exp[i].isalpha() and self.orig_exp[i - 1].isalpha():
                return False
        return True

    def valid_negation(self):
        for i in range(1, len(self.orig_exp)):
            if self.orig_exp[i] == '!' and self.orig_exp[i - 1].isalpha():
                self.error_msg = "! should come before a variable, not after."
                return False
            if self.orig_exp[i] == '!' and self.orig_exp[i - 1] == ')':
                self.error_msg = "'!' should not follow a ')'"
                return False
            if self.orig_exp[i] == '!' and self.orig_exp[i - 1] == '!':
                self.error_msg = "Please remove redundant ! operators..."
                return False
        return True

    def get_truth_table(self):
        if not self.valid_vars():
            self.error = True
            self.error_msg = "Cannot have two variables in a row..."
        if not self.valid_negation():
            self.error = True
        if self.error == True:
            return "The expression: {}, is invalid!\n{}".format(self.disp_exp,
                                                                self.error_msg)
        if len(set(self.var_set)) > 5:
            return "Too many variables! Will result in spam..."
        # print("Variable set: {}".format(self.var_set))
        # # print(self.op_stack)
        # print("\nIn-fix:   {}".format(self.orig_exp))
        # print("Post-fix: {}".format(self.post_exp))
        self.process_all_exps()
        return self.result_formatted

if __name__ == '__main__':
    exp = "A+C"
    exp_obj = BooleanExpr(exp)
    print(exp_obj.get_truth_table())

    exp = "A*C"
    exp_obj = BooleanExpr(exp)
    print(exp_obj.get_truth_table())

    exp = "A^C+!(A * C)"
    exp_obj = BooleanExpr(exp)
    print(exp_obj.get_truth_table())

    exp = "A+!B*C+!A*C*!D"
    exp_obj_2 = BooleanExpr(exp)
    print(exp_obj_2.get_truth_table())

    exp = "A^C++!(A * C)"
    exp_obj = BooleanExpr(exp)
    print(exp_obj.get_truth_table())

    exp = "A^C+!((A * C)"
    exp_obj = BooleanExpr(exp)
    print(exp_obj.get_truth_table())

    exp = "A^C)++!(A * C))"
    exp_obj = BooleanExpr(exp)
    print(exp_obj.get_truth_table())

    exp = "A^C++!(A * C))"
    exp_obj = BooleanExpr(exp)
    print(exp_obj.get_truth_table())

    exp = "ABCD"
    exp_obj = BooleanExpr(exp)
    print(exp_obj.get_truth_table())

    exp = "!(x + y)"
    exp_obj = BooleanExpr(exp)
    print(exp_obj.get_truth_table())

    exp = "(x!y + y)"
    exp_obj = BooleanExpr(exp)
    print(exp_obj.get_truth_table())

    exp = "(x + y)!"
    exp_obj = BooleanExpr(exp)
    print(exp_obj.get_truth_table())

    exp = "(!!x + y)"
    exp_obj = BooleanExpr(exp)
    print(exp_obj.get_truth_table())

    exp = "(!+!x + y)"
    exp_obj = BooleanExpr(exp)
    print(exp_obj.get_truth_table())

    exp = "!(!(!x + y))"
    exp_obj = BooleanExpr(exp)
    print(exp_obj.get_truth_table())

    exp = "!   !   !x + y"
    exp_obj = BooleanExpr(exp)
    print(exp_obj.get_truth_table())

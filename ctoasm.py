#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

declaration = re.compile(r'([^ ]+) ?= ?([^ ]+)')
operation = re.compile(r'([^ ]+) ?([\+\-]) ?([^ ]+)')
substraction = re.compile(r'(.+)\-(.+)')
addition = re.compile(r'(.+)\+(.+)')
integer = re.compile(r'\d+')
variable = re.compile(r'.+')
char = re.compile(r'(\')(\w)(\')')

code = "a = 2;\nb = 5+a;\nc = a+5;\nd=6+6;\n"

code = code.rstrip('\n')
code = code.rstrip(';')
codeCleaned = code.split(';\n')


class Variable():
    register = -1
    fisrtLine = -1
    lastLine = -1

    def __str__(self):
        return ('Variable: reg {0}, fLine {1}, lLine {2}').format(
            self.register, self.firstLine, self.lastLine)

    def __init__(self, firstLine):
        self.firstLine = firstLine
        self.lastLine = firstLine

    def setRegister(self, register):
        self.register = register

    def setLastLine(self, lastLine):
        self.lastLine = lastLine

    def getLastLine(self):
        return self.lastLine

    def getFirstLine(self):
        return self.firstLine

    def getRegister(self):
        return self.register


class Register():
    status = False

    def catch(self):
        self.status = True

    def release(self):
        self.status = False

    def getStatus(self):
        return self.status


registers = {}

#define accesible registers

for i in range(0, 8):
    registers[i] = Register()

variables = {}

verbose = True


def getRegNotUsed(line):
    for i in registers:
        if(not registers[i].getStatus()):
            return i
    for i in variables:
        if(variables[i].getLastLine() < line):
            return variables[i].register
    return -1


def assignRegister(var, line):
    if(variables[var].getRegister() == -1):
        reg = getRegNotUsed(line)
        variables[var].setRegister(reg)
    else:
        reg = variables[var].getRegister()
    if reg is not -1:
        registers[reg].catch()
    return reg


def searchDeclaration(string):
    s = declaration.search(string)
    if s is not None:
        if verbose: print 'Tenemos una declaración'
        return True
    else:
        return False


def searchAddition(string):
    s = addition.search(string)
    if s is not None:
        if verbose: print 'Tenemos una suma'
        return True
    else:
        return False


def searchInt(string):
    s = integer.search(string)
    if s is not None:
        if verbose: print 'Tenemos un int'
        return True
    else:
        return False


def searchChar(string):
    s = char.search(string)
    if s is not None:
        if verbose: print 'Tenemos un char'
        return True
    else:
        return False


def searchVariable(string):
    s = variable.search(string)
    if s is not None:
        if verbose: print 'Tenemos una variable'
        return True
    else:
        return False


def searchOperation(string):
    s = operation.search(string)
    if s is not None:
        if verbose: print 'Tenemos una operación'
        return True
    else:
        return False


#Check variables
line = 0
for i in codeCleaned:
    if(searchDeclaration(i)):
        s = declaration.search(i)
        dest = s.group(1)
        val = s.group(2)

        if(searchVariable(val) and not searchChar(val) and not searchInt(val)):
            s = variable.search(val)
            val = s.group()
            if val not in variables:
                print ("Error, variable <{0}> was not defined before line {1}".format(val, line))
                exit()
            variables[val].setLastLine(line)
        if dest not in variables:
            variables[dest] = Variable(line)
        else:
            variables[dest].setLastLine(line)

    line += 1

#Parse code to asm
line = 0
for i in codeCleaned:
    if verbose: print ('{0}> {1}'.format(line, i))
    if(searchDeclaration(i)):
        s = declaration.search(i)

        dest = s.group(1)
        val = s.group(2)

        if(searchOperation(val)):
            s = operation.search(val)
            first = s.group(1)
            operator = s.group(2)
            second = s.group(3)

            reg = assignRegister(dest, line)

            if(operator == '+'):
                print ('add {0}, {1}, {2}'.format(dest, first, second))
            if(searchInt(first)):
                if(searchInt(second)):
                    if(operator == '+'):
                        result = int(first) + int(second)
                    elif(operator == '-'):
                        result = int(first) - int(second)
                    print ('mov r{0}, {1}'.format(reg, result))

        elif(searchInt(val)):
            s = integer.search(val)
            reg = assignRegister(dest, line)
            if(reg != -1):
                val = s.group()
                print ('mov r{0}, {1}'.format(reg, val))
        elif(searchChar(val)):
            s = char.search(val)
            reg = assignRegister(dest, line)
            if(reg != -1):
                val = s.group(2)
                print ('mov r{0}, {1}'.format(reg, ord(val)))
        elif(searchVariable(val)):
            s = variable.search(val)
            reg = assignRegister(dest, line)
            if(reg != -1):
                val = s.group()
                regval = assignRegister(val, line)
                print ('mov r{0}, r{1}'.format(reg, regval))

    line += 1

for i in variables:
    print ('{0}->{1}'.format(i, variables[i]))
```
<Program> ::= <Instruction> | <Instruction> <Program> | SPACE
<Instruction> ::= <MoveToken> | <ColorToken> | <PenToken> | <RepInstr> 
<Rep_Program>  <Instruction> | <Instruction> <Rep_Program> |
<MoveToken> ::= FORW DEC DOT |  BACK DEC DOT | LEFT DEC DOT | RIGHT DEC DOT |
<ColorToken> ::= COLOR HEX DOT
<PenToken> ::= DOWN DOT | UP DOT
<RepInstr> ::= REP DEC QUOTE <Rep_program> QUOTE | REP DEC <Instruction>
```

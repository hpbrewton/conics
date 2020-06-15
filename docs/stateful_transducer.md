# Stateful Transducer

A stateful transducer is a simple kind of computer.
It takes an input: a finite sequence of symbols, symbols of which there are also a finite number.
It produces an output, of the same length as the input also with symbols on it, but they can be a different kind of symbols.
Inside the machine are a finite set of states.
The machine proceeds by taking an input, deciding which next state to move to, and then moving there, outputting some output symbol.
In order to help it decide what state to move to next it considers what state it is currently in, the input character, and a finite set of registers.
Registers are just fixed width integers: they can become any value so long as that value can be represented in a fixed number of bits.
 

## A Formula for tranducers

$$ s = f \wedge g(i, r) \implies \wedge r' = d(r) \wedge s' = t \wedge o =  $$
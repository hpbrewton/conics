digraph A {
rankdir = LR;
node [shape=circle,style=filled] start
node [shape=circle,style=filled] second
start -> start [label="s1 / r <= ??a / r = ??b; / s1"];
start -> second [label="s1 / r > ??a  / r = ??b; / s1"];
second -> second [label="s1 / r <= r  / r = r; / s2"];
}
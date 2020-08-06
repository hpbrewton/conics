transducer start r {
    start / s1 / r <= ??a / r = ??b; / s1 / start /
    start / s1 / r > ??a  / r = ??b; / s1 / second /
    second / s1 / r <= r  / r = ??c; / s2 / second /
} examples {
    s1 / s1;
    s1, s1, s1, s1 / s1, s2, s2, s2;
}

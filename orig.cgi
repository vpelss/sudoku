my $input = "000010000301400860900500200700160000020805010000097004003004006048006907000080000";

$a = 8;
$G{ int( ++$a / 9 ) . $a % 9 + 1 } = $_ for split //, $input;
@A = 1 .. 9;

sub c {
    int( ( $_[0] - 1 ) / 3 ) * 3;
}

sub G {
    for $y (@A) {
        for $x (@A) {
            $p = $t = $G{ my $c = $y . $x } && next;
            $t .= $G{ $_ . $x } . $G{ $y . $_ } for @A;
            for $f ( 1 .. 3 ) { $t .= $G{ c($y) + $f . c($x) + $_ } for 1 .. 3 }
            G( $G{$c} = $_ ) && return for grep $t !~ m/$_/, @A;
            return $G{$c} = 0;
        }
    }
    die map { $G{$_} } 9 .. 99;
}
G
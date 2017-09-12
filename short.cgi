use strict;

my %GridFast;
my @OneToNine = 1 .. 9;

#my $input = "000010000301400860900500200700160000020805010000097004003004006048006907000080000";
my $input = "000030000301400860900500200700160000020805010000097004003004006048006907000080000"; #bad
my $a = 8;
$GridFast{ int( ++$a / 9 ) . $a % 9 + 1 } = $_ for split //, $input;
my $output = &TryToSolve();
my @GlobalOutput;
my $rrr = 9;

sub block_offset
{
# returns 0, 3 or 6 for 1..3, 4..6 or 7..9.
# ip 1,2or3 op 0
#ip 4,5,6 op 3
#ip 7,8,9 op 6
int( ( $_[0] - 1 ) / 3 ) * 3;
}

sub TryToSolve()
{
# Note: $GridFast{$y$x}
my $taken; # !!!!!!!!! should be hash to avoid duplicates!
for my $y (@OneToNine)
    {
    for my $x (@OneToNine)
        {
        #look for blank cell. if == 0 then next
        $GridFast{ my $cell = $y . $x } && next; 
        #set taken for this cell based on row and col
        $taken .= $GridFast{ $_ . $x } . $GridFast{ $y . $_ } for @OneToNine;
=pod        
        foreach my $OneToNine ( @OneToNine )
            {
            $taken{ $GridFast{ $OneToNine . $x } } = 1;
            $taken{ $GridFast{ $y . $OneToNine } } = 1;
            }
=cut
        #set taken for block
        for my $yy ( 1 .. 3 )
            {
            for my $xx (1 .. 3)
                {    
                $taken .= $GridFast{ block_offset($y) + $yy . block_offset($x) + $xx }
                #$taken{ $GridFast{ block_offset($y) + $yy . block_offset($x) + $xx } } = 1;
                }
            }
        
        foreach my $try ( grep $taken !~ m/$_/, @OneToNine ) #for 1..9 NOT in $taken
        #foreach my $try ( keys %taken ) #for each non zero $taken
            {
            $GridFast{$cell} = $try;
            #&TryToSolve() && return 1;
            my $result = &TryToSolve(); 
            if($result == 1)
                {return 1;} #return only reached if call returns a true. cascade back condition 
            }
        #this point is reached only if all our $try have failed in this $cell
        $GridFast{$cell} = 0;
        return 0;
        }
    }
#all cells have a non zero value. done
my @output;
for my $y (@OneToNine)
    {
    for my $x (@OneToNine)
        {
        push @GlobalOutput , $GridFast{ my $cell = $y . $x }   
        }
    }
#die map { $GridFast{$_} } 9 .. 99;
#@output = map { $GridFast{$_} } 9 .. 99;
return 1;
}


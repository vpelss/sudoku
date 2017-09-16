sub block_offset
{
# returns 0, 3 or 6 for 1..3, 4..6 or 7..9.
# ip 1,2 or 3 op 0
#ip 4,5,6 op 3
#ip 7,8,9 op 6
int( ( $_[0] - 1 ) / 3 ) * 3;
}

sub TryToSolve()
{
# Note: $GridFast{$y$x}
my $taken; 
for my $y (0..8)
    {
    for my $x (0..8)
        {
        #look for blank cell. if == 0 then next
        $GridFast{ my $cell = $y . $x } && next; 
        #set taken for this cell based on row and col
        $taken .= $GridFast{ $_ . $x } . $GridFast{ $y . $_ } for 0..8;
        #set taken for block
        for my $yy ( 1 .. 3 )
            {
            for my $xx (1 .. 3)
                {    
                $taken .= $GridFast{ block_offset($y) + $yy . block_offset($x) + $xx }
                }
            }
        
        foreach my $try ( grep $taken !~ m/$_/, 0..8 ) #for 1..9 NOT in $taken
            {
            $GridFast{$cell} = $try;
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
return 1;
}

sub IsPuzzleSolvableFast()
{
my $input;
for my $y (0..8)
    {
    for my $x (0..8)
        {
        if( $TempGameArray[$x][$y] == undef )
            {
            $input = $input . "0";
            $GridFast{ $y+1 . $x+1 } = 0;    
            }
        else
            {
            $input = $input . $TempGameArray[$x][$y];
            $GridFast{ $y . $x } =  $TempGameArray[$x][$y];
            }
        }
    }
    
my $output = &TryToSolve();

print $output;
}

#!/usr/bin/perl

#file: SB.pm
package SB;

use warnings;
use strict;
use Storable qw/dclone/;
use Carp;
#use lib "$ENV{PREFIX}/lib/perl5";
#use Acme::Comment type => ’C++’;
#use List::MoreUtils qw/uniq/;
#use List::Util qw/shuffle/;

my $count;
my $count2;

sub new {
my $class = shift;
my %args = @_;
my $self = bless {
# The board references an array of arrayrefs that reference an array
# storing the possibilities in a given cell.
board => $args{board} || [map [ map [ 1 .. 9 ], 1 .. 9 ], 1 .. 9],visited => [],
choices => [],
branch_save => [],
totals => {},
}, $class;
return $self;
}
sub reset {
my $self = shift;
$self->{board} = [
map [ map [ 1 .. 9 ], 1 .. 9 ], 1 .. 9
];
$self->{visited} = [];
$self->{choices} = [];
totals => {},
}
sub revert_logic {
my $self = shift;
$self->{board} = pop @{ $self->{branch_save} };
}
# Read in a file
# The file may contain newlines or not Team # 3779 Page 16 of 36
# Blanks are designated by characters that are not 1-9
sub read {
my $self = shift;
my $fname = shift;
open my $file, "<", $fname or die "$fname: $!";
$self->read_handle($file);
close $file;
}
sub read_handle {
my $self = shift;
my $handle = shift;
# Populate the board with the possibilities gleaned from reading a file
$self->{board} = [
map [
map [
# If the entry is a number from 1 to 9, store [ n ]
# Otherwise if the entry is a "." or something, populate the
# cell with the possibilities [ 1..9 ]
/[1-9]/ ? $_ : 1 .. 9
], m/([ˆ\r\n])/g # list of non-newline characters in the line
], <$handle>
];
$self->is_valid or croak "Invalid board read in from the handle\n";
}
sub is_solved {
my $self = shift;
for my $y (0 .. 8) {
for my $x (0 .. 8) {
$self->get($x, $y) == 1 or return 0;
}
}
return 1;
}
# Set a number for a given cell and recalculate the possibilities for the
sub set {
my $self = shift;
my ($x, $y, $n) = @_;
ref $n eq "ARRAY" or croak "Not an array ref";
$self->{board}[ $y ][ $x ] = $n;
}
# Eliminate the supplied list of possibilities from a given cell
sub eliminate {
my $self = shift;
my $x = shift;
my $y = shift;
my @eliminated;
for my $n (@_) {
# Don’t eliminate the last value
$self->get($x, $y) > 1 or return @eliminated;
my @new = grep $_ != $n, @{ $self->{board}[ $y ][ $x ] };
if (@{ $self->{board}[ $y ][ $x ] } != @new) {
push @eliminated, $n;
# DISPATCH CODE TO HIDDEN PAIRS, AND OTHERS? GOES HERE?
}
$self->{board}[ $y ][ $x ] = \@new; }
return @eliminated;
}
# Whether a cell contains all of the supplied values as possibilities
sub contains {
my $self = shift;
my $x = shift;
my $y = shift;
for my $n (@_) {
my $match = grep $_ == $n, @{ $self->{board}[ $y ][ $x ] };
# Doesn’t contain $n
$match or return 0;
}
return 1;
}
# Get the possibilities for a given cell
sub get {
my $self = shift;
my ($x, $y) = @_;
#if( !$x and !$y ){print"invalid indices: x=$x, y=$y\n"; exit;}
return @{ $self->{board}[ $y ][ $x ] };
}
# Print a board with the unknown values as "."s and the known values as
# themselves
sub print {
my $self = shift;
print join "\n", map {
join "", map { @$_ == 1 ? @$_ : "." } @$_
} @{ $self->{board} };
print "\n";
}
sub print_saved {
my $self = shift;
print join "\n", map {
join "", map { @$_ == 1 ? @$_ : "." } @$_
} @{ $self->{branch_save}[-1] };
print "\n";
}
# Return cells in a particular row
sub in_row {
my $self = shift;
my $n = shift;
return @{ $self->{board}[ $n ] }[ 0 .. 8 ];
}
# Return known cells in a particular row
sub in_row_known {
my $self = shift;
my $n = shift;
return map @$_, grep {
ref eq "ARRAY" and @$_ == 1
} @{ $self->{board}[ $n ] };
}
# Return unknown cells in a particular row
sub in_row_unknown {
my $self = shift;
my $n = shift;
return grep {
ref eq "ARRAY" and @$_ > 1
} @{ $self->{board}[ $n ] };
}
# Return cells in a particular column
sub in_col {
my $self = shift;
my ($x, $y) = @_;
my $n = shift;
return map $_->[$n], grep ref eq "ARRAY", @{ $self->{board} };
}
# Return known cells in the same column as the given cell
sub in_col_known {
my $self = shift;
my $n = shift;
return map @$_, grep {
ref eq "ARRAY" and @$_ == 1
} map $_->[$n], @{ $self->{board} };
}
# Return unknown cells in the same column as the given cell
sub in_col_unknown {
my $self = shift;
my ($x, $y) = @_;
my $n = shift;
return grep {
ref eq "ARRAY" and @$_ > 1
} map $_->[$n], @{ $self->{board} };
}
sub get_row_coords {
my $self = shift;
my $y = shift;
return map [ $_, $y ], 0 .. 8;
}
sub get_col_coords {
my $self = shift;
my $x = shift;
return map [ $x, $_ ], 0 .. 8;
}
# Return all the coordinates of the cells in the same box as the given cell
sub get_box_coords {
my $self = shift;
my ($x, $y) = @_;
my $bx = 3 * int $x / 3;
my $by = 3 * int $y / 3;
my @coords;
for my $cx ($bx .. $bx + 2) {
for my $cy ($by .. $by + 2) {
push @coords, [ $cx, $cy ];
}
}
return @coords;
}
# Return all the cells in the same box as the given cell
sub in_box {
my $self = shift;
my ($x, $y) = @_;
my $base_x = 3 * int $x / 3;
my $base_y = 3 * int $y / 3;
return map @{ $self->{board}[$base_y + $_] }[
map $base_x + $_, 0 .. 2
], 0 .. 2;
}
# Return all the known cells in the same box as the given cell
sub in_box_known {
my $self = shift;
my ($x, $y) = @_;
return map @$_, grep @$_ == 1, $self->in_box($x, $y);
}
sub in_box_unknown {
my $self = shift;
my ($x, $y) = @_;
return grep @$_ > 1, $self->in_box($x, $y);
}
sub naked_singles {
my $self = shift;
my $changed = 0;
for(my $x = 0;$x < 9;$x++) {
for(my $y = 0;$y < 9;$y++) {
my @possible = $self->get($x, $y);
if(@possible == 1) {
for(my $x2 = 0;$x2 < 9;$x2++) {
if($x2 != $x) { if($self->eliminate($x2,$y,$possible[0])) { $changed++;} }
for(my $y2 = 0;$y2 < 9;$y2++) {
if($y2 != $y) { if($self->eliminate($x,$y2,$possible[0])) { $changed++;} }
my @coords = $self->get_box_coords($x,$y);
foreach my $c (@coords) {
my $x2 = $c->[0];
my $y2 = $c->[1];
if($x != $x2 || $y != $y2) {
if($self->eliminate($x2,$y2,$possible[0])) { $changed++; }
}
}
}
}
}
return $changed;
}
sub hidden_singles {
my $self = shift;
my $removed = 0; # number of possibilities removed
for my $y (map 3 * $_, 0 .. 2) {
for my $x (map 3 * $_, 0 .. 2) {
my @box = $self->get_box_coords($x, $y);
my %possible;
for my $cell (@box) {
$possible{"@$cell"} = join "", $self->get(@$cell);
}
for my $n (1 .. 9) {
my @choices = grep $possible{$_} =~ m/$n/, keys %possible;
if (@choices == 1 and length $possible{$choices[0]} > 1) {
# A number is only possible in one cell, set it
my ($cx, $cy) = split / /, $choices[0];
$self->set($cx, $cy, [ $n ]);
# Removed as many possibilities as the string’d get is long
$removed += length $possible{ $choices[0] };
}
}
}
}
return $removed;
}
sub naked_pairs {
my $self = shift;
my $elim_count = 0;
my @boxes;
for my $i (0, 3, 6) {
push @boxes, map [ $self->get_box_coords($i, 3 * $_) ], 0 .. 2;
}
my @cols;
for my $i (0 .. 8) {
push @cols, [ map [ $_, $i ], 0 .. 8 ];
}
my @rows;
for my $i (0 .. 8) {
push @rows, [ map [ $i, $_ ], 0 .. 8 ];
}
my @regions = (@boxes, @cols, @rows);
for my $region (@regions) {
for my $n1 (1 .. 9){
for my $n2 ($n1 + 1 .. 9) {
my @matched;
my $m1 = 0;
my $m2 = 0;
for my $cell (@$region) {
$m1 += $self->contains(@$cell, $n1);
$m2 += $self->contains(@$cell, $n2);
push @matched, $cell if $self->contains(@$cell, $n1, $n2);
}
if ($m1 == 2 and $m2 == 2 and @matched == 2) {
my @get_rid_of = grep { $_ != $n1 and $_ != $n2 } 1 .. 9;
$elim_count += $self->eliminate(
@{ $matched[0] }, @get_rid_of
);
$elim_count += $self->eliminate(
@{ $matched[1] }, @get_rid_of
);
}
}
}
my @pairs;
for my $cell (@$region) {
my $possible = join "", $self->get(@$cell);
if (length $possible == 2) {
push @pairs, $possible;
}
}
for my $pair (@pairs) {
if (2 == grep $pair eq $_, @pairs) {
for my $c (grep join("", $self->get(@$_)) ne $pair, @$region) {
$elim_count += $self->eliminate(@$c, split //, $pair);
}
last;
}
}
}
return $elim_count;
}
sub x_wing
{
my $self = shift;
my $val = 0;
for(my $x = 0;$x < 8;$x++)
    {
    for(my $y = 0; $y < 8;$y++)
        {
        my @a_pos = $self->get($x,$y);
        if(@a_pos > 1)
            {
            foreach my $pos (@a_pos)
                    {
                    for(my $x2 = $x+2;$x2 < 9;$x2++)
                        {
                        #If we find a match in the row, let’s look for a match in the col
                        if($self->contains($x2, $y, $pos))
                            {
                            for(my $y2 = $y+2;$y2 < 9;$y2++)
                                {
                                #Match here too?
                                if($self->contains($x, $y2, $pos))
                                    {
                                    #if the last one has it, we’ve found a box.
                                    if($self->contains($x2, $y2, $pos))
                                        {
                                        my $count = 0;
                                        my $count2 = 0;
                                        #these need to be the *only* choices in two rows or two cols
                                        for(my $i = 0;$i < 9;$i++)
                                            {
                                            $count += $self->contains($x,$i,$pos);
                                            $count2 += $self->contains($x2,$i,$pos);
                                            }
                                        #Are we the only possibilities in two cols? Then delete possibilities if($count == 2 && $count2 == 2) {
                                        #print "Found A\n";
                                        for(my $j = 0;$j < 9;$j++)
                                            {
                                            if($j != $x && $j != $x2)
                                                {
                                                $val += $self->eliminate($j,$y,$pos);
                                                $val += $self->eliminate($j,$y2,$pos);
                                                }
                                            }
                                        }
                                    else
                                        {
                                        $count = 0;
                                        $count2 = 0;
                                        for(my $i = 0;$i < 9;$i++)
                                            {
                                            $count += $self->contains($i,$y,$pos);
                                            $count2 += $self->contains($i,$y2,$pos);
                                            }
                                        if($count == 2 && $count2 == 2)
                                            {
                                            #print "Found B\n";
                                            for(my $j = 0;$j < 9;$j++)
                                                {
                                                if($j != $y && $j != $y2)
                                                    {
                                                    $val += $self->eliminate($x,$j,$pos);
                                                    $val += $self->eliminate($x2,$j,$pos);
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
            }
        }
    }
return $val;
}
#}

sub int_removal {
my $self = shift;
my $val = 0;
#my @coords = (1,5,9);
my @coords = (0, 3, 6);
#/*
#$self->naked_singles();
foreach my $x (@coords) {
foreach my $y (@coords) {
my $s = join "", map @$_, $self->in_box_unknown($x,$y);
#print "$s\n";
my @nums = (1 .. 9);
foreach my $num (@nums) {
my $n = length join "", $s =~ m/($num)/g;
if($n == 2 || $n == 3) {
#print "s: $s n: $n num: $num\n";
my $total = 0;
for(my $i = 0;$i < 2;$i++) {
$total += $self->contains($x,$y+$i,$num);
}
#$n in the same col, delete everywhere else in col
if($total == $n) {
for(my $i = 0;$i < 9;$i++) {
my $v = 0;
if($i != $y && $i != $y+1 && $i != $y+2) {
if($self->eliminate($x,$i,$num)) { $v++; }
}
if($v) { return $val + $v; }
}
}
$total = 0;
for(my $i = 0;$i < 2;$i++) {
$total += $self->contains($x+$i,$y,$num);
}
#$n in the same row, delete everywhere else in row
if($total == $n) {
for(my $i = 0;$i < 9;$i++) {
my $v = 0;
if($i != $x && $i != $x+1 && $i != $x+2) {
if($self->eliminate($i,$y,$num)) { $v++; }
}
if($v) { return $val + $v; }
}
}
}
}
}
}
for(my $i = 0;$i < 9; $i++) {
my $s = join "", map @$_, $self->in_row_unknown($i);
#print "row $i: $s\n";
foreach my $num (1..9) {
my $n = length join "", $s =~ m/($num)/g;
if($n == 2 || $n == 3) {
my $total;
for(my $j = 0;$j < 3; $j++) {
$total = 0;
for(my $k = 0;$k < 3; $k++) {
$total += $self->contains(($j*3)+$k,$i,$num);
}
if($total == $n) {
#print "total of $num (rows) is $total and n was $n\n";
my @box = $self->get_box_coords($j*3,$i);
my $v = 0;
foreach my $c (@box) {
#print "x: $c->[0] y: $c->[1]\n";
if($c->[1] != $i) {
if($self->eliminate($c->[0],$c->[1],$num)) { $v++; }
}
}
if($v) { return $val + $v; }
}
}
}
}
}
for(my $i = 0;$i < 9; $i++) {
my $s = join "", map @$_, $self->in_col_unknown($i,0);
foreach my $num (1..9) {
my $n = length join "", $s =~ m/($num)/g;
if($n == 2 || $n == 3) {
my $total;
for(my $j = 0;$j < 3; $j++) {
$total = 0;
for(my $k = 0;$k < 3; $k++) {
$total += $self->contains($i,($j*3)+$k,$num);
}
if($total == $n) {
#print "total of $num (cols) is $total and n was $n\n";
my @box = $self->get_box_coords($i,$j*3);
my $v = 0;
foreach my $c (@box) {
if($c->[0] != $i) {
if($self->eliminate($c->[0],$c->[1],$num)) { $v++; }
}
}
if($v) { return $val + $v; }
}
}
}
}
}
return $val;
}
sub deadly_rects {
my $self = shift;
my @coords = (0,3);
my @box = (0..2);
foreach my $x (@coords) {
foreach my $y (@coords) {
for(my $i = 0;$i < 3;$i++) {
for(my $j = 0;$j < 3;$j++) {
}
}
}
}
}
sub nishio {
my $self = shift;
my $min_poss = 10;
my $x_coord = -1;
my $y_coord = -1;
my @poss;
my @foo;
for(my $y = 0; $y < 9; $y++){
for(my $x = 0; $x < 9; $x++){
@poss = $self->get($x,$y);
#if(scalar(@poss) < $min_poss && scalar(@poss) > 1){
# $min_poss = scalar(@poss);
if (@poss > 1) {
push @foo, [ $x, $y ];
}
}
}
# for my $y (shuffle 0 .. 8) {
# for my $x (shuffle 0 .. 8) {
# my @possible = $self->get($x, $y);
# next if @possible == 1;
# $x_coord = $x;
# $y_coord = $y;
# }
# }
if(@foo == 0){
if (!$self->is_solved and !$self->is_valid) {
$self->back;
return;
}
}
else{
($x_coord, $y_coord) = @{ $foo[rand @foo] };
my @new_poss = $self->get($x_coord,$y_coord);
my $branch_value = $new_poss[int(rand(scalar(@new_poss)))];
$self->branch($x_coord, $y_coord, $branch_value);
# print "depth = ", $self->get_depth, "\n";
}
}
sub seed {
my $self = shift;
my $target = shift;
# Fill in completely empty cells
my $sanity = 0;
my $found = 0;
while ($found < $target) {
my $x = int rand 9;
my $y = int rand 9;
$self->get($x,$y) == 9 or next;
my $value = 1 + int rand 9;
if ( $self->is_valid($x, $y, $value) ){
$self->branch($x, $y, $value);
$found ++;
}
}
}
sub is_valid {
my $self = shift;
if (@_ == 0) {
for my $cy (0 .. 8) {
for my $cx (0 .. 8) {
my @p = $self->get($cx, $cy);
@p == 1 or next;
#print "is_valid($cx, $cy, $p[0]) = ", $self->is_valid($cx, $cy, $p[0]);
return 0 if $self->is_valid($cx, $cy, $p[0]) == 0;
}
}
return 1;
}
my ($x, $y, $n) = @_;
my @row_values = map $self->get(@$_), grep {
# Known element and not at the same spot as is being checked
($x != $_->[0] or $y != $_->[1]) and $self->get(@$_) == 1
} $self->get_row_coords($y);
foreach my $rv (@row_values){
return 0 if $n == $rv;
}
my @col_values = map $self->get(@$_), grep {
# Known element and not at the same spot as is being checked
($x != $_->[0] or $y != $_->[1]) and $self->get(@$_) == 1
} $self->get_col_coords($x);
foreach my $cv (@col_values){
return 0 if $n == $cv;
}
my @box_values = map $self->get(@$_), grep{
# Known element and not at the same spot as is being checked
($x != $_->[0] or $y != $_->[1]) and $self->get(@$_) == 1
} $self->get_box_coords($x, $y);
foreach my $bv (@box_values){
return 0 if $n == $bv;
}
# Didn’t find anything wrong, must be ok, at least for the cell at the
# provided (x, y)’s point of view
return 1;
}
sub get_depth {
my $self = shift;
return scalar @{ $self->{visited} };
}
sub branch {
my $self = shift;
my ($x, $y, $value) = @_;
push @{ $self->{choices} }, {
x => $x,
y => $y,
value => $value,
};
$self->eliminate($x, $y, $value);
# push copy, rest of possibilities
my $copy = dclone($self->{board});
push @{ $self->{visited} }, $copy;
# reset totals
$self->{totals} = {};
$self->set($x, $y, [ $value ]);
push @{ $self->{branch_save} }, dclone($self->{board});
}
# Back track and return the choice that was made at that level
sub back {
my $self = shift;
$self->{board} = pop @{ $self->{visited} };
# reset totals
$self->{totals} = {};
pop @{ $self->{branch_save} };
return pop @{ $self->{choices} };
}

sub y_wing {
my $self = shift;
my $elim = 0;
for my $y (0 .. 8) {
for my $x (0 .. 8) {
my @p = $self->get($x, $y);
@p == 2 or next;
my @influence = $self->influence($x, $y);
my @matches;
for my $coord (@influence) {
for my $n (@p) {
# Has two possibilities
$self->get(@$coord) == 2 or next;
# Contains one of the possibilities
$self->contains(@$coord, $n) or next;
# but not both
$self->contains(@$coord, @p) and next;
push @matches, $coord;
}
}
@matches or next;
for my $n (1 .. 9) {
next if $self->contains($x, $y, $n);
my @pincers = grep $self->contains(@$_, $n), @matches;
@pincers or next;
if (@pincers == 2) {
my $sg1 = join "", $self->get(@{$pincers[0]});
my $sg2 = join "", $self->get(@{$pincers[1]});
next if $sg1 eq $sg2;
# And not in the pincers box
my $bx = int $pincers[0][0] / 3 == int $pincers[1][0] / 3;
my $by = int $pincers[0][1] / 3 == int $pincers[1][1] / 3;
next if $bx and $by;
# And not in the pincers row or column
$pincers[0][0] != $pincers[1][0] or next;
$pincers[0][1] != $pincers[1][1] or next;
my @ii = $self->influence_intersect(map @$_, @pincers);
#print "($x, $y):", join("",$self->get($x, $y)),
# " => ",
# "(@{$pincers[0]}):", join("", $self->get(@{$pincers[0]})),
# ", (@{$pincers[1]}):",join("", $self->get(@{$pincers[1]})),"\n";
#print " ii=", join " ", map "[@$_]", @ii;
#print "\n";
# Don’t delete the master cell
@ii = grep { $x != $_->[0] or $y != $_->[1] } @ii;
#print " ii=", join " ", map "[@$_]", @ii;
#print "\n";
# Eliminate all cells in the ii that contain $n
# except for the single values
@ii = grep $self->get(@$_) > 1, @ii;
#print " ii=", join " ", map "[@$_]", @ii;
#print "\n";
#print " eliminate(@$_, $n):", $self->get(@$_), "\n" for @ii;
$elim += $self->eliminate(@$_, $n) for @ii;
}
}
}
}
return $elim;
}

# Return all the coords that the given cell has an influence on
sub influence {
my $self = shift;
my ($x, $y) = @_;
my @coords = (
$self->get_box_coords($x, $y),
$self->get_col_coords($x),
$self->get_row_coords($y)
);
# Don’t return the coordinate itself
@coords = grep { ($_->[0] == $x and $_->[1] == $y) ? 0 : 1 } @coords;
return map [ split / / ], uniq map join(" ", @$_), @coords;
}

# Return the intersection of two influences as an array of coords
sub influence_intersect {
my $self = shift;
my ($x1, $y1, $x2, $y2) = @_;
my @inf1 = $self->influence($x1, $y1);
my @inf2 = $self->influence($x2, $y2);
# Intersection of the influences with hashes
my %int;
($int{join " ", @$_} ||= 0) ++ for @inf1, @inf2;
return map [ split / / ], grep $int{$_} == 2, keys %int;
}
# Progress through the puzzle by logic
# Returns whether anything happened
sub solve {
my $self = shift;
my @algos = @_; # which algorithms to use
# push saved last branch thing
#push @{ $self->{branch_save} }, dclone($self->{board});
my %t;
$t{$_} = 0 for @algos;
my $anything = 0;
my $working = 1; # whatever you’re doing, it’s working!
while ($working) {
$working = 0;
for my $algo (@algos) {
my $elim = 0; # how many were eliminated with this algorithm
if ($algo eq "ns") {
$elim = $self->naked_singles;
}
elsif ($algo eq "hs") {
$elim = $self->hidden_singles;
}
elsif ($algo eq "np") {
$elim = $self->naked_pairs;
}
elsif ($algo eq "ir") {
$elim = $self->int_removal;
}
elsif ($algo eq "xw") {
$elim = $self->x_wing;
}
elsif ($algo eq "yw") {
$elim = $self->y_wing;
}
$self->{totals}{$algo} ||= 0;
$self->{totals}{$algo} += $elim;
$working = 1 if $elim > 0;
redo if $elim;
}
$anything += $working;
}
#my $totals = $self->{totals}[-1];
#print "totals ", join(", ", map "$_:$totals->{$_}", keys %$totals), "\n";
#$self->print;
#print "\n";
return $anything;
}
1;
file: make_board.pl
#!/usr/bin/env perl
use warnings;
use strict;
$|++;
use SB;
my $sb = SB->new;
my $filename = shift;
open my $fh, ">>", $filename;
END {
close $fh;
}
#my $seed = shift @ARGV || 0;
#if (-e $seed and not -d $seed) {
# $sb->read($seed);
# $sb->print;
#}
#else {
# $sb->seed($seed);
# $sb->is_valid or die "NOT VALID\n";
#}
my %levels = (
sour => { # Gumbo chicken
can_have => [ qw/ns hs/ ],
must_have => [ qw/ns/ ],
},
mild => {
can_have => [ qw/ns hs np/ ],
must_have => [ qw/np/ ],
},
spicy => { # Spicy chicken
can_have => [ qw/ns hs np ir/ ],
must_have => [ qw/ir/ ],
},
cajun => { # Chicken chicken: chicken chicken chicken
can_have => [ qw/ns hs np ir xw xy/ ],
must_have => [ qw/xw xy/ ], # one or more of these
},
# insanity => qw//,
);
my $level = shift @ARGV || "mild";
searching: while (1) {
$sb->solve(qw/ns hs np hs ir xw yw/);
# $sb->solve(qw/ns hs np hs xw yw/);
if (not $sb->is_valid) {
# The board isn’t valid, back track
$sb->back;
print "Invalid, back tracking\n";
}
elsif ($sb->is_solved) {
# Hit a solved state (leaf node)
# See if the board conforms to the constraints
print $fh "TOTALS ",
join ", ", map "$_:$sb->{totals}{$_}", keys %{ $sb->{totals} };
print $fh "\n";
# Methods used to solve the last branch
my @used = grep $sb->{totals}{$_}, keys %{ $sb->{totals} };
print $fh "USED @used\n";
print "SOLUTION (@used)\n";
# my $must = 0;
# for my $method (@used) {
# if (grep $method eq $_, @{ $levels{$level}{must_have} }) {
# $must = 1;
# }
# if (not grep $method eq $_, @{ $levels{$level}{can_have} }) {
# # Method not allowed in the target difficulty level
# $sb->back;
# next searching;
# }
# }
# if ($must == 0) {
# $sb->back;
# next searching;
# }
#last searching;
$sb->back;
next searching;
}
else {
# Run nishio to generate a new branch
print "New branch (", $sb->get_depth, ")\n";
$sb->nishio;
$sb->solve(qw/ns hs np hs ir xw yw/);
}
}
#$sb->print;
#print "** PUZZLE **\n";
$sb->print_saved;
file: solve.pl
#!/usr/bin/env perl
use warnings;
use strict;
$|++;
use SB;
my $sb = SB->new;
my $puzzle = shift @ARGV || "4/";
my ($path, $file_num) = split m{:}, $puzzle;
#my @files = glob "../boards/qqwing/${level}_files/*";
$file_num ||= 0;
if ($file_num < 0) {
$file_num = int rand grep /ˆ\./, glob $path;
}
if (-d $path) {
opendir my($dh), $path;
for (my $i = 0; $i <= $file_num; $i++) {
my $f = scalar(readdir $dh);
redo if $f =˜ m/ˆ\./;
}
$path = "$path/" .readdir $dh;
closedir $dh;
}
print "$path : $file_num\n";
my @algos = qw{ ns hs np ir xw yw };
@algos = @ARGV if @ARGV;
print "Using algorithms: @algos\n";
if ($path eq "-") {
$sb->read_handle(*STDIN);
}
else {
$sb->read($path);
}
$sb->is_valid or print "Not valid\n";
print "\n** INITIAL **\n";
$sb->print;
print "\n";
$sb->solve(@algos);
print "\n** FINAL **\n";
$sb->print;
print "\n";
$sb->is_valid or print "Not valid\n";
$sb->is_solved or print "Not solved\n";
print "Totals: ", join ", ",
map "$_=$sb->{totals}{$_}", keys %{ $sb->{totals} };
print "\n";
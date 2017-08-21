#!c:\perl64\bin\perl.exe -d

#!/usr/bin/perl -d

#still have not implemented XWing or YWing searches
#maybe run a brute force generic solvable routine after all the other tests? too slow!


use strict;
use List::Util qw(shuffle);
use sudokuvars;
#get setup variables the proper way
my $archivepath = $sudokuvars::archivepath;
my $archiveurl  = $sudokuvars::archiveurl;
my $scripturl  = $sudokuvars::scripturl;

my %cellsIn; #quickly find cells in: $cellsIn{row}{$y} $cellsIn{col}{$x} $cellsIn{squ}{$squ}
my @cellLocation; #quick col,row,and squ location : $cellLocation[$bigX][$bigY][$littleX][$littleY] = {col=>$x , row=>$y , squ=> $squ}; #returns which # of the region we are in

my $difficulty;
my $globalstring; #shows ns,hs,np,ir count numbers
my $blanksquares = 0;
my $HS = 0;
my $NS = 0;
my $NP;
my $IR = 0;
my $IR1 = 0;
my $IR2 = 0;
#NEW
my %in;
my %CellsIn; # $CellsIn{'row' | 'col' | 'squ'}{0 - 8} will return ( (x,y) , (x,y) , () , ... )
my %IAmIn; # $IAmIn{$x}{$y} returns ( row# , col# , squ # ) so ($row,$col,$squ) = $IAmIn{$x.$y};
my @AllCells; #array of ($x,$y) values
my @AllBlankCells; #array of ($x,$y) values
my @FullGameArray; #simple $FullGameArray[$x][$y] = $value | undef
my @GameArray; #simple $GameArray[$x][$y] = $value | undef
my @TempGameArray; #simple $TempGameArray[$x][$y] = $value | undef
#my @RecursiveTempGameArray;
my @PossibleNumberArray; #global for recursive routines. $PossibleNumberArray[$x][$y]{0 - 9} = 1|undef Note: Final value is a series of hashes = 1 so we can easily remove them = undef
my %methods; # $methods{ns} = 1 indicates to use that method/routine also use ns,hs,np,ir
my $RemoveAttempCount;
my $starttime = time;
my $timetotry = 5;
my $NumberOfPicks = 1; #how many numbers should we try to remove and then test at once?
my $target = 50;

my $debug = 1;

eval { &Main(); };                            # Trap any fatal errors so the program hopefully
if ($@) { &CgiErr("fatal error: $@"); }     # never produces that nasty 500 server error page.
exit;   # There are only two exit calls in the script, here and in in &cgierr.

sub Main()
{
print "Content-type: text/html\n\n";
$in{difficulty} = 'Difficult';
%in = &ParseForm; #get input arguments
if ( $debug ) { open (TROUBLE, ">aaa.html") }
&CalcRegionalCellLocations(); #build @cellsIn  : used quickly find cells in regions
&CreateFullSudokuGrid();
if ( $debug ) {
      print TROUBLE "<p>Game Array Created</p>";
      print TROUBLE &PrintTempGameArrayDebug();
      }
&CopyGameArrays( \@TempGameArray , \@FullGameArray );
&CopyGameArrays( \@TempGameArray , \@GameArray );
if ($in{difficulty} eq '') {$in{difficulty} = 'Medium'}
if ($in{difficulty} eq 'Simple')
     {
     $methods{ns} = 1;
     }
if ($in{difficulty} eq 'Easy')
     {
     $methods{ns} = 1;
     $methods{hs} = 1;
     }
if ($in{difficulty} eq 'Medium')
     {
     $methods{ns} = 1;
     $methods{np} = 1;
     $methods{hs} = 1;
     }
if ($in{difficulty} eq 'Difficult')
     {
     $methods{ns} = 1;
     $methods{np} = 1;
     $methods{hs} = 1;
     $methods{ir} = 1;
     }

$blanksquares = 0;
#start removing numbers from game grid
&RecursiveRemoveCells();
=pod
#while ( (time() - $starttime) <= $timetotry )
while ( $blanksquares < 57 )
      {
      if($debug) { print TROUBLE &PrintTempGameArrayDebug() }
      &CopyGameArrays( \@GameArray  , \@TempGameArray );
      my %RemoveList;
      for (my $count = 0; $count < $NumberOfPicks ; $count++) #loop to remove a bunch at one time
            {
            my $x = int(rand(9));
            my $y = int(rand(9));
            #add to remove list. we may need to restore them if we can't solve board
            if ($TempGameArray[$x][$y] == undef){next} #no need to try and remove an already removed spot
            $RemoveList{"$x$y"} = $TempGameArray[$x][$y];
            if($debug) {print TROUBLE "$TempGameArray[$x][$y] removed at $x,$y : ";}
            delete $TempGameArray[$x][$y]; #remove picked number
            }
      if($debug) {print TROUBLE "$NumberOfPicks numbers removed, Trying to solve...<br>";}
      #after ANY square is removed, test to see if it is solvable.
      $RemoveAttempCount++;
      &CalcAllBlankCellsInTempGameArray();
      #if ( &RecursiveSolveTempGameArray(@AllBlankCells) ) #if it is not solvable replace the number in the grid
      #or
      if ( &IsPuzzleSolvable() ) #if it is not solvable replace the number in the grid
            {
            foreach my $cell (keys %RemoveList)
                  {
                  my ($x,$y) = split('',$cell);
                  delete $GameArray[$x][$y]; #remove from real game array
                  $blanksquares++;
                  }
            if($debug) {print TROUBLE "Solvable: continuing...<br>";}
            }
      else
            {
            foreach my $cell (keys %RemoveList)
                  {
                  my ($x,$y) = split('',$RemoveList{$cell});
                  $TempGameArray[$x][$y] = $RemoveList{$cell}; #was not solvable. replace removed numbers
                  }
            if($debug) {print TROUBLE "Not Solvable: replaced $NumberOfPicks numbers<br>";}
            }
      }
=cut

$blanksquares = 0;
foreach my $cell ( @AllCells )
      {
      my ($x,$y) = @{ $cell };
      my $choice = $GameArray[$x][$y];
      if ($choice == '') {$blanksquares++}
      }
my $TimeTaken = (time() - $starttime);
my $exposedsquares = 81 - $blanksquares;
$globalstring = " RemoveAttempCount: $RemoveAttempCount | NS: $NS | HS: $HS | NP: $NP | IR1: $IR1  | IR2: $IR2 | Blank: $blanksquares | Time: $TimeTaken";
$difficulty = "Simple";
if ($HS > 0 )
      {$difficulty = "Easy";}
if ($NP > 0 )
      {$difficulty = "Medium";}
if ($IR > 0 )
      {$difficulty = "Hard";}

if($debug) {print TROUBLE &PrintGameArrayDebug();}

open (DATA, "<./templates/index.html") or die("Template file /templates/index.html does not exist");
my @DATA = <DATA>;
close (DATA);
my $template_file = join('' , @DATA);

my $jscalcpuzz = "";
#replace cell template data
for (my $y = 0; $y < 9 ; $y++)
      {
      for (my $x = 0; $x < 9 ; $x++)
#foreach my $cell ( @AllCells )
            {
            #my ($x,$y) = @{ $cell };
            $template_file =~ s/<\%solution\_$x\_$y\%>/$FullGameArray[$x][$y]/g;
            if ( $GameArray[$x][$y] != undef )
                  {
                  $template_file =~ s/<\%cell\_$x\_$y\%>/$GameArray[$x][$y]<!--static-->/g;
                  $jscalcpuzz .= $GameArray[$x][$y];
                  }
            else
                  {
                  $template_file =~ s/<\%cell\_$x\_$y\%>//g;
                  $jscalcpuzz .= "-";
                  }
            }
      $jscalcpuzz .= "\n";
      #$possibilities .= "<br>\n";
      }

#$template_file =~ s/%possibilities%/$possibilities/g;
$template_file =~ s/%jscalcpuzz%/$jscalcpuzz/g;
$template_file =~ s/\%archivepath\%/$archivepath/g;
$template_file =~ s/\%archiveurl\%/$archiveurl/g;
$template_file =~ s/\%scripturl\%/$scripturl/g;
my $uid = $in{uid}; #facebook user ID number
if ($uid eq '') {$uid='common'} #for non facebook games
$template_file =~ s/\%uid\%/$uid/g;
my $name = $in{name}; #facebook user name
$name =~ s/\%20/ /g; #get rid of %20 for spaces
$template_file =~ s/\%name\%/$name/g;
$template_file =~ s/\%blanksquares\%/$blanksquares/g;
$template_file =~ s/\%exposedsquares\%/$exposedsquares/g;
#$template_file =~ s/\%difficulty\%/$in{difficulty}/g;
$template_file =~ s/\%difficulty\%/$difficulty/g;
#$template_file =~ s/\%attempts\%/$attempts/g;
#$template_file =~ s/\%attempts\%/$difficultycount/g;
$template_file =~ s/\%globalstring\%/$globalstring/g;

#archive the puzzle!
my $game = time();

$template_file =~ s/\%game\%/$game/g;
$template_file = "$template_file";

#write archive game file and directory
if (not -d ("$archivepath")) {mkdir("$archivepath")  or die("Could not create archive path $archivepath");}
if (not -d ("$archivepath/$uid")) {mkdir("$archivepath/$uid")  or die("Could not create archive path $archivepath/$uid");}
if (not -d ("$archivepath/$uid/$game")) {mkdir("$archivepath/$uid/$game")  or die("Could not create archive path $archivepath/$uid/$game");}
open (DATA, ">$archivepath/$uid/$game/index.html") or die("Could not create archive file $archivepath/$uid/$game/index.html");
print DATA $template_file;
close (DATA);
#open (DATA, ">$archivepath/$uid/$game/out.txt") or die("Could not create chat file $archivepath/$uid/$game/out.txt");
#close (DATA);

#print a jump to game page output
print qq|<META HTTP-EQUIV="Refresh" CONTENT="0; URL=$archiveurl/$uid/$game/?uid=$uid&name=$name">|; #name is for chat

print "\n\n";
if ($debug) {close TROUBLE;}
};

sub CalcRegionalCellLocations()
{
#build @cellsIn  : used quickly find cells in regions
#squ are numbered:
#036
#147
#258
for (my $y = 0; $y < 9 ; $y++)
      {
      for (my $x = 0; $x < 9 ; $x++)
            {
            push @AllCells , [$x,$y];
            push @{ $CellsIn{'row'}{$y} } , [$x,$y];
            push @{ $CellsIn{'col'}{$x} } , [$x,$y];
            my $squ = int($x/3) * 3 + int($y/3);
            #if ($debug) {print TROUBLE "$x,$y:$squ<br>"}
            push @{ $CellsIn{'squ'}{$squ} } , [$x,$y];
            #note col and row not required as $x and $y are equivalent. But I add it anyway.
            $IAmIn{'col'}{$x}{$y} = $x;
            $IAmIn{'row'}{$x}{$y} = $y;
            $IAmIn{'squ'}{$x}{$y} = $squ;
            }
      }
}

sub CreateFullSudokuGrid()
{
#fully fill in global $gameArray with valid sudoku numbers
#&FillPossibilityArray1to9();
&SetPossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules(); #require to prime RecursiveChoice
&RecursiveCellSet( @AllCells );
}

sub RecursiveCellSet()
{
#recursively go through each @AllCells
#randomly choose a possible value
#test, said value, to ensure that all cells still have valid possibilities
my @RemainingCells = @_;
if (scalar(@RemainingCells) == 0)
      {
      return(1)
      } #no more cells. done
my $Cell = shift @RemainingCells;
my ($x , $y) = @{ $Cell };
my $result = &SetPossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules();
if($debug) { print TROUBLE &PrintProbArrayDebug() }
if ( $result == 0 )
      {
      if($debug) { print TROUBLE "No Probabilities Somewhere Returning<br>" }
      return(0)
      }
my @CellProbabilities = shuffle keys %{ $PossibleNumberArray[$x][$y] } ;
do
      {
      #if we are here, we are either:
      #forging ahead
      #returning from an failed recurse attempt. blank $GameArray[$x][$y] and try another choice if available
      delete $TempGameArray[$x][$y];
      if (scalar @CellProbabilities == 0)
            {
            if($debug) { print TROUBLE "No Probabilities left at $x,$y Returning<br>" }
            return(0);
            }
      my $choice = shift @CellProbabilities;
      $TempGameArray[$x][$y] = $choice; #remove choice from $PossibleNumberArray[$x][$y]
      if($debug) { print TROUBLE &PrintTempGameArrayDebug() }
      }
until( &RecursiveCellSet( @RemainingCells ) );
return(1); #cascade
}

sub SetPossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules()
{
#IMPORTANT totally rebuilds/wipes @PossibleNumberArray
#fill up @PossibleNumberArray based on values in @$gameArray for each $row,$col,$squ
#if any cell has no possibility return 0 - fail - indicates not a valid sudoku
#DOES NOT SET $gameArray here
#that will be done in another routine
&FillPossibilityArray1to9();
foreach my $cell ( @AllCells )
      {
      my ($x,$y) = @{ $cell };
      my $choice = $TempGameArray[$x][$y];
      if ($choice != undef)
            {
            foreach my $region ( 'col' , 'row' , 'squ' )
                  {
                  my $RegionValue = $IAmIn{$region}{$x}{$y} ;
                  my @list = @{ $CellsIn{$region}{$RegionValue} };
                  foreach my $cell ( @list)
                        {
                        my ($x,$y) = @{ $cell };
                        if ( $TempGameArray[$x][$y] != undef )
                              {#$TempGameArray[$x][$y] is already set for this cell so no possibility to set here ()
                              delete $PossibleNumberArray[$x][$y];
                              }
                        else
                              {#remove the $choice from the cell
                              delete $PossibleNumberArray[$x][$y]{$choice};
                              my @Probabilities = keys %{ $PossibleNumberArray[$x][$y] };
                              #is the @Probabilities set empty - fail
                              if ( scalar(@Probabilities) == 0 ) {return(0)}
                              }
                        }
                  }
            }
      }
return (1); #all cells have at least 1 possibility!
}

sub FillPossibilityArray1to9()
{
foreach my $cell ( @AllCells )
      {
      my ($x,$y) = @{ $cell };
      foreach my $value ( 1 .. 9 )
            {
            $PossibleNumberArray[$x][$y]{$value} = 1; #see definition explanation
            }
      }
}

sub CopyGameArrays()
{
my $From = $_[0]; #ref to the 3 type of @GameArray's
my $To = $_[1];

foreach my $cell ( @AllCells )
      {
      my ($x,$y) = @{ $cell };
      ${$To}[$x][$y] = ${$From}[$x][$y];
      }
}

sub CopyPossibleNumberArrays()
{
#not tested
#not used

my $From = $_[0]; #ref to the 3 type of @PossibleNumberArray's
my $To = $_[1];

foreach my $cell ( @AllCells )
      {
      my ($x,$y) = @{ $cell };
      #$PossibleNumberArray[$x][$y]{$value} = 1
      foreach my $PossibleNumber ( keys %{$PossibleNumberArray[$x][$y]} )
            {
            ${$To}[$x][$y]{$PossibleNumber} = ${$From}[$x][$y]{$PossibleNumber};
            }
      }
}

sub IsPuzzleSolvable()
{
#this takes a partially filled @TempGameArray (copied from @GameArray) and tries to see if it is solvable
#if it is solvable, we return 1 and get to remove our randomly removed number from @GameArray
#if it is not solvable by our various techniques, We must return 0 and replace the removed number
#and try to remove another and see if it is solvable

#we have randomly removed a number so:
#lets try and solve the puzzle now
# initialize @PossibleNumberArray using NS technique on the @TempGameArray
# continually try and solve by reducing @PossibleNumberArray by various techniques, IR, NP, HS and finally NS
#my $pickednumber;
#my @canbe;
#my @cantbe;
my $AnyProgress = 1; #set so we can enter loop
my $solved = 0;
my $blanksquaresleft;
#my $found;
my $loopcount = 0;
my $LpNS = 0;
my $LpHS = 0;
my $LpNP = 0;
my $LpIR1 = 0;
my $LpIR2 = 0;
my $string;
$HS = 0;
$NS = 0;
$NP =0;
$IR = 0;
$IR1 = 0;
$IR2 = 0;

#initialize @PossibleNumberArray
#&FillPossibilityArray1to9();
&SetPossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules();
if ( $debug ) {
      #$string =  Printgrid($gameArrayTemp);
      #print TROUBLE "-----------------------------<br>Game Array Temp <br>";
      }
if ( $debug ) {
      #$string =  Printgrid2($PossibleNumberArray);
      #print TROUBLE "Set Posibilities<br>";
      }
$AnyProgress = 1;
$blanksquaresleft = 1; #get us in the 'while' door
while ( ($blanksquaresleft == 1) and ($AnyProgress > 0) ) #start fresh each time until we get a run where all squares are filled
      {
      #try all &SetXX. these reduce possibilities when possible, returning how many possibility reductions were found
      #then try &SetNS as it alone clears up, and sets, the single possibilities! IT IS THE ONLY ONE THAT SETS THE $gameArrayTemp
      $AnyProgress = 0; #set it up to fail. if any possibility is removed using any technique, it still might be solvable
      #these should be first as they do not narrow possibilities down to one. Nor do they set a square on it's own. Give them a chance
=pod
      if ($methods{np})
            {
            $LpNP = &SetNP(); #Set NP method 1 for Local regions
            if ($LpNP > 0)
                  {
                  $NP += $LpNP;
                  $AnyProgress += $LpNP;
                  if ( $debug )
                        {
                        print TROUBLE "Set $LpNP NP <br>";
                        }
                  }
            }

      if ($methods{hs})
            {
            #start filling in puzzle using various techniques.
            $LpHS =  &SetHS(); #Set HS Local squares
            $HS += $LpHS;
            $AnyProgress += $LpHS;
            if ($LpHS)
              {
              if ( $debug )
                    {
                    print TROUBLE "Set $LpHS HS<br>";
                    }
                  }
            }
=cut
       if ($methods{ir})
            {
            $LpIR1 = &SetIR1(); #Set IR1 for rows and columns
            $IR += $LpIR1;
            $IR1 += $LpIR1;
            if ($LpIR1)
              {
              if ( $debug )
                  {
                  print TROUBLE "Set IR1<br>$string";
                  }
              }
            $AnyProgress += $LpIR1;
            }

       if ($methods{ir})
            {
            $LpIR2 = &SetIR2(); #Set IR2 for rows and columns
            $IR += $LpIR2;
            $IR2 += $LpIR2;
            if ($LpIR2)
              {
              if ( $debug )
                  {
                  print TROUBLE "Set IR2<br>$string";
                  }
              }
            $AnyProgress += $LpIR2;
            }

        #clears up all single possibilities. that is why it is last!
      if ($methods{ns})
            {
            if ($debug) {print TROUBLE "Try NS<br>"}
            $LpNS =  &SetNS(); #Set NS based on previously calculated possibilities
            $NS += $LpNS;
            $AnyProgress += $LpNS;
            if ($LpNS)
                  {
                  if ($debug) {print TROUBLE "Set $LpNS NS<br>"}
                  }
           }

      #lets see if we are done yet
      $blanksquaresleft = &AreThereBlankSquares();
      $loopcount++;
      }

if ($blanksquaresleft == 0)
     {
     $solved = 1;
     } #it is only solvable if there are no blank squares left!

if ($debug) {
     print TROUBLE "<br>\n solvable:$solved | blankleft:$blanksquaresleft | NS:$NS | NP:$NP | HS:$HS | IR:$IR | loopcount:$loopcount<br>\n";
     }
return ($solved);
};

sub CalcAllBlankCellsInTempGameArray()
{
@AllBlankCells=(); #erase old global or bad things will happen
for (my $y = 0; $y < 9 ; $y++)
      {
      for (my $x = 0; $x < 9 ; $x++)
            {
            if ($TempGameArray[$x][$y] == undef)
                  {
                  push @AllBlankCells , [$x,$y];
                  }
            }
      }
}

my %RemovedCells; #RemovedCells{"$x$y"} = 1; So we can search which ones faster, and delete them easily!
#might not be required

sub RecursiveRemoveCells()
{
my %RemovedList;
#Test for time
#if( (time() - $starttime) <= $timetotry ) {return 1}
#Test for $blanksquares
if($blanksquares >= $target)
      {
      return 1
      }
#&SetPossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules(); #reset PossibilityArray
if (&IsPuzzleSolvable()==0)
            {
            return 0
            } #note: tests previous call
do
      {
      #was not solvable. replace removed numbers. Note: will be blank on forward
      foreach my $cell (keys %RemovedList)
            {
            my ($x,$y) = split('',$RemovedList{$cell});
            $TempGameArray[$x][$y] = $RemovedList{$cell};
            $GameArray[$x][$y] = $RemovedList{$cell};
            }
      if($debug) {print TROUBLE "Not Solvable: replaced $NumberOfPicks numbers<br>";}
      #try to remove some random cells
      for (my $count = 0; $count < $NumberOfPicks ; $count++) #loop to remove a bunch at one time
            {
            #maybe later to make it truely recursive, we will have a shuffled list of all full, removable squares we can shift off
            my $x = int(rand(9));
            my $y = int(rand(9));
            #if(RemovedCells{"$x$y"} == 1) {next}  #ignore ones already removed
            #add to remove list. we may need to restore them if we can't solve board
            if ($GameArray[$x][$y] == undef){next} #no need to try and remove an already removed spot
            $RemovedList{"$x$y"} = $GameArray[$x][$y];
            if($debug) {print TROUBLE "$GameArray[$x][$y] removed at $x,$y : ";}
            delete $TempGameArray[$x][$y]; #remove picked number
            delete $GameArray[$x][$y]; #remove picked number
            $RemoveAttempCount++;
            $blanksquares++;
            }
      #if($debug) {print TROUBLE "Solvable: continuing...<br>";}
      #and test in &RecursiveRemoveCells()
      }
until( &RecursiveRemoveCells() );
return 1; #cascade back
}

sub RecursiveSolveTempGameArray()
{
#IMPORTANT: Does not require IsPuzzleSolvible loop.
#It can replace it.
#It tests for solve all in one! cannot be used with other solve methods.

#recursively go through each @AllBlankCells
#try a possibility from ProbabilityArray
#test, said value, to ensure that all cells still have valid possibilities
#true - set tempgamearray next recursive
#false - try another possibility
#out of possibilities return fail 0
#on return if no posibility return else try next possibility
my @RemainingBlankCells = @_;
if (scalar(@RemainingBlankCells) == 0)
      {
      return(1)
      } #no more cells. done
my $Cell = shift @RemainingBlankCells;
my ($x , $y) = @{ $Cell };
if($debug) { print TROUBLE "Entering RecursiveSolveTempGameArray. Shift $x,$y off RemainingBlankCells. RemainingBlankCells is now @RemainingBlankCells<br>" }
my $result = &SetPossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules();
if ( $result == 0 )
      {
      if($debug) { print TROUBLE "SetPossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules returned 0 at $x,$y<br>" }
      return(0)
      }
if($debug) { print TROUBLE "SetPossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules is:</br>" }
if($debug) { print TROUBLE &PrintProbArrayDebug() }
if($debug) { print TROUBLE "TempGameArray is:</br>" }
if($debug) { print TROUBLE &PrintTempGameArrayDebug() }
my @CellPossibilities = keys %{ $PossibleNumberArray[$x][$y] } ;
do
      {
      #if we are here, we are either: forging ahead or returning from an failed recurse attempt.  blank $GameArray[$x][$y] and try another choice if available
      if($debug) { print TROUBLE "deleted $TempGameArray[$x][$y] in TempGameArray[$x][$y]<br>" }
      delete $TempGameArray[$x][$y];
      if($debug) { print TROUBLE "@CellPossibilities are posibilities at $x,$y <br>" }
      #if (scalar @CellPossibilities == 0) allows for incorrect game grids
      if (scalar @CellPossibilities != 1)
            {
            if($debug) { print TROUBLE "No Possibilities left at $x,$y Returning 0<br>" }
            return(0);
            }
      my $choice = shift @CellPossibilities;
      if($debug) { print TROUBLE "Trying $choice at in TempGameArray[$x][$y] and then calling next RemainingBlankCells with RecursiveSolveTempGameArray with @RemainingBlankCells<br>" }
      $TempGameArray[$x][$y] = $choice; #set $choice
      }
until( &RecursiveSolveTempGameArray( @RemainingBlankCells ) );
#we are done calculating so we MUST remove solved square as they are actually meant to be blank ones
if($debug) { print TROUBLE "Puzzle is solved and backtracking so deleting TempGameArray $TempGameArray[$x][$y] at $x,$y </br>" }
delete $TempGameArray[$x][$y];
return(1); #cascade
}

sub SetIR1()
{
#First, it scans each row or col region for all possibilities.
#If exactly two or three exist for a single number in the same box,
#their values may be eliminated from the rest box.
my $countIR;
#for each col or row region if 1 - 3 possibilities exist for a number that is bound by a box region
#remove that possibility everywhere else in the bound box region
foreach my $region ( 'col' , 'row' )
      {
      for my $RegionValue (0 .. 8)
            {
            #Step 1: go through each cell in each col and row
            #build up $PossibilityLocationsInRegion{$PossibleNumber}{'squares'} = 012 joining squ's. One lone number is a winner
            #$PossibilityLocationsInRegion{$PossibleNumber}{'xyxyxy'} = "xyxyxyx" count and location
            my %PossibilityLocationsInRegion;
            #$PossibilityLocationsInRegion{Possibility #} = xyxyxyxy... (appended).
            #The length gives the frequency count, eg xyxy means $PossibleNumber occurs twice
            my @list = @{ $CellsIn{$region}{$RegionValue} };
            foreach my $cell ( @list)
                  {
                  my ($x,$y) = @{ $cell };
                  foreach my $PossibleNumber (keys %{ $PossibleNumberArray[$x][$y] } )
                        {
                        #$PossibilityLocationsInRegion{$PossibleNumber}{'xyxyxy'} = xyxyxyxy...
                        #if =xyxy then $PossibleNumber is in two locations
                        my $squ = $IAmIn{'squ'}{$x}{$y};
                        $PossibilityLocationsInRegion{$PossibleNumber}{'squares'} = "$PossibilityLocationsInRegion{$PossibleNumber}{'squares'}" . "$squ";
                        $PossibilityLocationsInRegion{$PossibleNumber}{'xyxyxy'} = "$PossibilityLocationsInRegion{$PossibleNumber}{'xyxyxy'}" . "$x$y";
                        }
                  }
            foreach my $PossibleNumber ( keys %PossibilityLocationsInRegion )
                  {
                  my $squares = $PossibilityLocationsInRegion{$PossibleNumber}{'squares'};
                  my $xyxyxy = $PossibilityLocationsInRegion{$PossibleNumber}{'xyxyxy'};
                  if (length($squares)==1)
                        {
                        #if ( (length($xyxyxy)==2) or  (length($xyxyxy)==4) or (length($xyxyxy)==6) )
                        if ( (length($xyxyxy)==4) or (length($xyxyxy)==6) )
                              {#found a IR1 for this $PossibleNumber
                              #remove $PossibleNumber from $squ, then restore to $xyxyxy locations
                              $countIR++;
                              my @list = @{ $CellsIn{'squ'}{$squares} };
                              foreach my $cell ( @list)
                                    {
                                    my ($x,$y) = @{ $cell };
                                    delete  $PossibleNumberArray[$x][$y]{$PossibleNumber};
                                    }
                              #restore to $xyxyxy locations
                              @list = split('' , $xyxyxy); #locations to restore $PossibleNumber
                              until(scalar(@list) == 0)
                                    {
                                    my $x = shift @list;
                                    my $y = shift @list;
                                    $PossibleNumberArray[$x][$y]{$PossibleNumber}=1;
                                    }
                              }
                        }
                  }
            }
      }
return $countIR; #return the number of HS hidden singles
};

sub SetIR2()
{
#for each square look for 2-3 possibilities that are bound by one row or column region
#when found, remove all other possibilities for all non intersecting cells in that row or column region
my $countIR;
#for each col or row region if 1 - 3 possibilities exist for a number that is bound by a box region
#remove that possibility everywhere else in the bound box region
foreach my $region ( 'squ' )
      {
      for my $RegionValue (0 .. 8)
            {
            #Step 1: go through each cell in each col and row
            #build up $PossibilityLocationsInRegion{$PossibleNumber}{'squares'} = 012 joining squ's. One lone number is a winner
            #$PossibilityLocationsInRegion{$PossibleNumber}{'xyxyxy'} = "xyxyxyx" count and location
            my %PossibilityLocationsInRegion;
            #$PossibilityLocationsInRegion{Possibility #} = xyxyxyxy... (appended).
            #The length gives the frequency count, eg xyxy means $PossibleNumber occurs twice
            my @list = @{ $CellsIn{$region}{$RegionValue} };
            foreach my $cell ( @list)
                  {
                  my ($x,$y) = @{ $cell };
                  foreach my $PossibleNumber ( keys %{ $PossibleNumberArray[$x][$y] } )
                        {
                        #$PossibilityLocationsInRegion{$PossibleNumber}{'xyxyxy'} = xyxyxyxy...
                        #if =xyxy then $PossibleNumber is in two locations
                        my $row = $IAmIn{'row'}{$x}{$y};
                       $PossibilityLocationsInRegion{$PossibleNumber}{'row'} = "$PossibilityLocationsInRegion{$PossibleNumber}{'row'}" . "$row";
                        my $col = $IAmIn{'col'}{$x}{$y};
                        $PossibilityLocationsInRegion{$PossibleNumber}{'col'} = "$PossibilityLocationsInRegion{$PossibleNumber}{'col'}" . "$col";
                        $PossibilityLocationsInRegion{$PossibleNumber}{'xyxyxy'} = "$PossibilityLocationsInRegion{$PossibleNumber}{'xyxyxy'}" . "$x$y";
                        }
                  }
            foreach my $PossibleNumber ( keys %PossibilityLocationsInRegion )
                  {
                  my $rows = $PossibilityLocationsInRegion{$PossibleNumber}{'row'};
                  my $cols = $PossibilityLocationsInRegion{$PossibleNumber}{'col'};
                  my $xyxyxy = $PossibilityLocationsInRegion{$PossibleNumber}{'xyxyxy'};
                  if (length($rows)==1)
                        {
                         if ( (length($xyxyxy)==4) or (length($xyxyxy)==6) )
                              {#found a IR2 for this $PossibleNumber
                              #remove $PossibleNumber from $row, then restore to $xyxyxy locations
                              $countIR++;
                              my @list = @{ $CellsIn{'row'}{$rows} };
                              foreach my $cell ( @list)
                                    {
                                    my ($x,$y) = @{ $cell };
                                    delete  $PossibleNumberArray[$x][$y]{$PossibleNumber};
                                    }
                              #restore to $xyxyxy locations
                              @list = split('' , $xyxyxy); #locations to restore $PossibleNumber
                              until(scalar(@list) == 0)
                                    {
                                    my $x = shift @list;
                                    my $y = shift @list;
                                    $PossibleNumberArray[$x][$y]{$PossibleNumber}=1;
                                    }
                              }
                        }
                  if (length($cols)==1)
                        {
                        if ( (length($xyxyxy)==4) or (length($xyxyxy)==6) )
                              {#found a IR2 for this $PossibleNumber
                              #remove $PossibleNumber from $col, then restore to $xyxyxy locations
                              $countIR++;
                              my @list = @{ $CellsIn{'col'}{$cols} };
                              foreach my $cell ( @list)
                                    {
                                    my ($x,$y) = @{ $cell };
                                    delete  $PossibleNumberArray[$x][$y]{$PossibleNumber};
                                    }
                              #restore to $xyxyxy locations
                              @list = split('' , $xyxyxy); #locations to restore $PossibleNumber
                              until(scalar(@list) == 0)
                                    {
                                    my $x = shift @list;
                                    my $y = shift @list;
                                    $PossibleNumberArray[$x][$y]{$PossibleNumber}=1;
                                    }
                              }
                        }
                  }
            }
      }
return $countIR; #return the number of HS hidden singles
};


sub SetNP()
{
#Naked Pairs 1 and 2
#NP1 The first version of Naked Pairs searches each region (row, column and 3 x 3 square) for two possibility values that occur only twice in, and share two cells, which may or may not contain other possibilities. Because they occur
#only in these two cells, one of them must go in one cell and the other in the second. Therefore, any other values in these two cells may be eliminated.
#or
#NP2 if in a region, two cells share two possibilities that are not in another cell in this region,
#we can eliminate all other possibilities in these two cells
my $countNP;
foreach my $region ( 'col' , 'row' , 'squ' )
      {
      for my $RegionValue (0 .. 8)
            {
            #Step 1: go through each cell in each region
            #for each region count number of possibilities for numbers 1-9 so we can find possibilities
            #that exist in this region twice later
            my %NPCountOnce; # set $NPCountOnce{1 for np1} = 1 $NPCountOnce{2 for np2} = 1 for each region, so we only count NP once or twice per region
            my %PossibilityLocationsInRegion;
            #$PossibilityLocationsInRegion{Possibility #} = xyxyxyxy... (appended).
            #The length gives the frequency count, so xyxy occurs twice
            #The pattern xyxy gives a simple comparison method
            my %PossibilitiesInRegion2;
            my @list = @{ $CellsIn{$region}{$RegionValue} };
            foreach my $cell ( @list)
                  {
                  my ($x,$y) = @{ $cell };
                  foreach my $PossibleNumber ( keys %{ $PossibleNumberArray[$x][$y] } )
                        {
                        #$PossibilityLocationsInRegion{$PossibleNumber} = xyxyxyxy...
                        #if =xyxy then $PossibleNumber is in two locations
                        $PossibilityLocationsInRegion{$PossibleNumber} = "$PossibilityLocationsInRegion{$PossibleNumber}" . "$x$y";
                        }
                  }
            #Step 2: for this region delete values that don't occur twice
            foreach my $PossibleNumber ( keys %PossibilityLocationsInRegion )
                  {
                  my $xyxy = $PossibilityLocationsInRegion{$PossibleNumber};
                  if ( length($xyxy) != 4 )
                        {
                        delete $PossibilityLocationsInRegion{$PossibleNumber};
                        }
                  else
                        {
                        #Step 3: look for $PossibilityLocationsInRegion{$PossibleNumber} that are in same locations by:
                        #converting to $PossibilitiesInRegion2{xyxyxy}{$PossibleNumber(s)} = 1.
                        #If there are two $PossibilitiesInRegion2{$xyxy}{'possiblenumbers'}{$PossibleNumber} we will have found a NP
                        $PossibilitiesInRegion2{$xyxy}{'possiblenumbers'}{$PossibleNumber} = 1; #if we have two {$PossibleNumber}, we have a winner
                        $PossibilitiesInRegion2{$xyxy}{'count'}++;
                        }
                  }
            #Step 4: Look for winners, $PossibilitiesInRegion2{$xyxy}'possiblenumbers'}{$PossibleNumber} with 2 $PossibleNumber keys, and set
            foreach my $xyxy ( keys %PossibilitiesInRegion2 )
                  {
                  if ($PossibilitiesInRegion2{$xyxy}{'count'} == 2)
                        {
                        my ($x1,$y1,$x2,$y2) = split('' , $xyxy); #locations of NP pair
                        my ($value1,$value2) = keys %{ $PossibilitiesInRegion2{$xyxy}{'possiblenumbers'} }; #values of NP pair
                        #NP1
                        #only in these two cells, one of them must go in one cell and the other in the second. Therefore, any other values in these two cells may be eliminated.
                        #if only two values in $PossibleNumberArray[$x1][$y1], then ignore as NP is already set
                        if ( scalar( keys %{ $PossibleNumberArray[$x1][$y1] } ) != 2  ) #ignore if only two values already
                              {
                              delete $PossibleNumberArray[$x1][$y1]; #get rid of old ones
                              $PossibleNumberArray[$x1][$y1]{$value1} = 1; #restore NP
                              $PossibleNumberArray[$x1][$y1]{$value2} = 1;
                              $NPCountOnce{1}=1;
                              }
                        if ( scalar( keys %{ $PossibleNumberArray[$x2][$y2] } ) != 2  )
                              {
                              delete $PossibleNumberArray[$x2][$y2]; #get rid of old ones
                              $PossibleNumberArray[$x2][$y2]{$value1} = 1; #restore NP
                              $PossibleNumberArray[$x2][$y2]{$value2} = 1;
                              $NPCountOnce{1}=1;
                              }
                        #NP2
                        #The second version scans each region (row, column and 3 x 3 square) for two cells,
                        #each containing ONLY the same two possibilities.
                        #Because one of these values must occur in each of the two cells,
                        #they cannot occur anywhere else in that region, and may be eliminated from the lists
                        #of possibilities for every other cell in the region.
                        #remove all $value1 and $value2 from $PossibleNumberArray[$x2][$y2] , excluding $x1,$y1 and $x2,y2
                        foreach my $cell ( @list)
                              {
                              my ($x,$y) = @{ $cell };
                              if(("$x$y" ne "$x1$y1") and ("$x$y" ne "$x2$y2")) #excluding $x1,$y1 and $x2,y2
                                    {
                                    if ($PossibleNumberArray[$x][$y]{$value1} == 1)
                                          {
                                          delete $PossibleNumberArray[$x][$y]{$value1};

                                          }
                                    if ($PossibleNumberArray[$x][$y]{$value2} == 1)
                                          {
                                          delete $PossibleNumberArray[$x][$y]{$value2};
                                          $NPCountOnce{2}=1;
                                          }
                                    }
                              }
                        }

                  }
            if($NPCountOnce{1}==1){$countNP++}
            if($NPCountOnce{2}==1){$countNP++}
           }
      }
return $countNP; #return the number of HP
};

sub SetHS()
{
#Hidden Singles
#IMPORTANT: do not run SetPossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules as it will muck up posibilities changed by NP
#for each number 1-9 check each region 0-8 (squ row col) and  see if that number exists only once in @PossibleNumberArray
#if so, that number is at the only possible location in that region.
#remove all possibilities except than number for that location
#set number for that location in @TempGameArray (done later in NS)
#later remove that possibility number from all other affected overlapping regions (done in NS)
my $countHS;
foreach my $region ( 'col' , 'row' , 'squ' )
      {
      for my $RegionValue (0 .. 8)
            {
            my %PossibilityLocationsInRegion; #will record count and location for each $PossibleNumber
            #Step 1: for each region count number of possibilities for numbers 1-9 and record location
            my @list = @{ $CellsIn{$region}{$RegionValue} };
            foreach my $cell ( @list)
                  {
                  my ($x,$y) = @{ $cell };
                  foreach my $PossibleNumber ( keys %{ $PossibleNumberArray[$x][$y] } )
                        {
                        $PossibilityLocationsInRegion{$PossibleNumber}{'count'}++;
                        $PossibilityLocationsInRegion{$PossibleNumber}{'location'}{"$x$y"} = 1;
                        }
                  }
            #look for $PossibleNumber that occurs only once in region
            foreach my $PossibleNumber ( keys %PossibilityLocationsInRegion )
                        {
                        if($PossibilityLocationsInRegion{$PossibleNumber}{'count'} == 1)
                              { #found HS
                              $countHS++;
                              my ($xy) = keys %{ $PossibilityLocationsInRegion{$PossibleNumber}{'location'} };
                              my ($x,$y) = split('',$xy); #should only be one!
                              #$TempGameArray[$x][$y] = $PossibleNumber;  #set @TempGameArray
                              delete $PossibleNumberArray[$x][$y]; #clear @PossibleNumberArray
                              $PossibleNumberArray[$x][$y]{$PossibleNumber} = 1; #set @PossibleNumberArray
                              if ($debug) {print TROUBLE "Found HS $PossibleNumber at $x,$y <br>"}
                              }
                        }
            }
      }
return $countHS; #return the number of HS hidden singles
};

sub SetNS()
{
#NS Naked Singles
#for @AllCells. if you find a cell with one possible value, set @TempGameArray as that value and remove value from @PossibleNumberArray
#remove the possibility from the affected squ,row,col regions
#only one that sets @TempGameArray
my $countNS = 0;
foreach my $region ( 'col' , 'row' , 'squ' )
      {
      my %PossibilityLocationsInRegion;
      #will record count and location for each $PossibleNumber
      for my $RegionValue (0 .. 8)
            {
            #Step 1: find cells with single possibility
            my @list = @{ $CellsIn{$region}{$RegionValue} };
            foreach my $cell ( @list)
                  {
                  my ($x,$y) = @{ $cell };
                  if (scalar(keys %{ $PossibleNumberArray[$x][$y] }) == 1)
                        {
                        $countNS++;
                        my ($PossibleNumber) = keys %{ $PossibleNumberArray[$x][$y] };
                        $TempGameArray[$x][$y] = $PossibleNumber;
                        #wipe $PossibleNumber from all affected $row,$col,$squ
                        foreach my $region ( 'col' , 'row' , 'squ' )
                              {
                              my $RegionValue = $IAmIn{$region}{$x}{$y};
                              my @list = @{ $CellsIn{$region}{$RegionValue} };
                              foreach my $cell ( @list)
                                    {
                                    my ($x1,$y1) = @{ $cell };
                                    #if ( ($x != $x1) and ($y != $y1) ) #ignore our cell
                                          {
                                          delete $PossibleNumberArray[$x1][$y1]{$PossibleNumber};
                                          }
                                    }
                              }
                        }
                  }
            }
      }
return $countNS;
};



sub AreThereBlankSquares
{
foreach my $cell ( @AllCells )
      {
      my ($x,$y) = @{ $cell };
      if($TempGameArray[$x][$y] == undef)
            {
            return(1);
            }
      }
return(0);
};

sub PrintTempGameArrayDebug()
{        #for game array
my $string = "";

$string .=  "<table border='1'>";

for (my $y = 0; $y < 9 ; $y++)
      {
      $string .=  "<tr>";
      for (my $x = 0; $x < 9 ; $x++)
            {
            $string .=  "<td border='1'>";
            $string .=  $TempGameArray[$x][$y];
            $string .=  "</td>";
            }
      $string .=  "</tr>";
      }
$string .=  "</table>";

return $string;
}

sub PrintGameArrayDebug()
{        #for game array
my $string = "";

$string .=  "<table border='1'>";

for (my $y = 0; $y < 9 ; $y++)
      {
      $string .=  "<tr>";
      for (my $x = 0; $x < 9 ; $x++)
            {
            $string .=  "<td border='1'>";
            $string .=  $GameArray[$x][$y];
            $string .=  "</td>";
            }
      $string .=  "</tr>";
      }
$string .=  "</table>";

return $string;
}

sub PrintProbArrayDebug()
{ #for prob array
my $string = "";

$string .=  "<table border='1'>";

for (my $y = 0; $y < 9 ; $y++)
      {
      $string .=  "<tr>";
      for (my $x = 0; $x < 9 ; $x++)
            {
            $string .=  "<td border='1'>";
            my @orderedlist = sort keys %{ $PossibleNumberArray[$x][$y] };
            my $str = join (',' , @orderedlist );
            $string .=  $str;
            $string .=  "</td>";
            }
      $string .=  "</tr>";
      }
$string .=  "</table>";

return $string;
}

sub ParseForm {
# --------------------------------------------------------
# Parses the form input and returns a hash with all the name
# value pairs. Removes SSI and any field with "---" as a value
# (as this denotes an empty SELECT field.

        my (@pairs, %in);
        my ($buffer, $pair, $name, $value);

        if ($ENV{'REQUEST_METHOD'} eq 'GET') {
                @pairs = split(/&/, $ENV{'QUERY_STRING'});
        }
        elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
                read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
                 @pairs = split(/&/, $buffer);
        }
        else {
                &CgiErr ("This script must be called from the Web\nusing either GET or POST requests\n\n");
        }
        PAIR: foreach $pair (@pairs) {
                ($name, $value) = split(/=/, $pair);

                $name =~ tr/+/ /;
                $name =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

                $value =~ tr/+/ /;
                $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

                $value =~ s/<!--(.|\n)*-->//g;                          # Remove SSI.
                if ($value eq "---") { next PAIR; }                  # This is used as a default choice for select lists and is ignored.
                (exists $in{$name}) ?
                        ($in{$name} .= "~~$value") :              # If we have multiple select, then we tack on
                        ($in{$name}  = $value);                                  # using the ~~ as a seperator.
        }
        return %in;
}


sub CgiErr {
# --------------------------------------------------------
# Displays any errors and prints out FORM and ENVIRONMENT
# information. Useful for debugging.
#

    print "<PRE>\n\nCGI ERROR\n==========================================\n";
    $_[0]      and print "Error Message       : $_[0]\n";
    $0         and print "Script Location     : $0\n";
    $]         and print "Perl Version        : $]\n";

    print "\nForm Variables\n-------------------------------------------\n";
    foreach my $key (sort keys %in) {
        my $space = " " x (20 - length($key));
        print "$key$space: $in{$key}\n";
    }
=pod
    print "\nEnvironment Variables\n-------------------------------------------\n";
    foreach $env (sort keys %ENV) {
        my $space = " " x (20 - length($env));
        print "$env$space: $ENV{$env}\n";
    }
=cut
    print "\n</PRE>";
    exit -1;
}

sub __SetGameArrayWithSinglePossibility()
{
#Not such a good idea. No benefit

#NS Naked Singles
#for @AllCells. if you find a cell with one possible value, set @TempGameArray as that value and remove value from @PossibleNumberArray
#remove the possibility from the affected squ,row,col regions
#only one that sets @TempGameArray

foreach my $cell ( @AllCells)
      {
      my ($x,$y) = @{ $cell };
      if (scalar(keys %{ $PossibleNumberArray[$x][$y] }) == 1)
            {
            #$countNS++;
            my ($PossibleNumber) = keys %{ $PossibleNumberArray[$x][$y] };
            $TempGameArray[$x][$y] = $PossibleNumber;
            delete $PossibleNumberArray[$x][$y]{$PossibleNumber};
            }
      }
};


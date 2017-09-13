#!c:\perl64\bin\perl.exe -d

#!/usr/bin/perl -d

#still have not implemented XWing or YWing searches
#maybe run a brute force generic solvable routine after all the other tests? too slow!

#try with blank Possibility Array, all blank. Then work backwards. Ex:

#try with full Possibility Array, all blank. Then work backwards. Ex: set single grid # if ns works there by not creating a spot with no possibilitis!
#faster? and more direct and we can target types of searches

#INTERFACE: right click brings up phone like number pad with all possibilities.
#use English;
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
my $XW = 0;
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
my @TempPossibleNumberArray; #global for recursive routines. $PossibleNumberArray[$x][$y]{0 - 9} = 1|undef Note: Final value is a series of hashes = 1 so we can easily remove them = undef
my %methods; # $methods{ns} = 1 indicates to use that method/routine also use ns,hs,np,ir
my %GridFast;
#my @OneToNine = 1 .. 9;
my $RemoveAttempCount;
my $starttime;
my $TimeTaken;
my $timetotry = 5;
my $NumberOfPicks = 1; #how many numbers should we try to remove and then test at once? too big and we overshoot and fall back a lot 2 is good
my $target = 60;
my $debug = 1;

eval { &Main(); };                            # Trap any fatal errors so the program hopefully
if ($@) { &CgiErr("fatal error: $@"); }     # never produces that nasty 500 server error page.
exit;   # There are only two exit calls in the script, here and in in &cgierr.

sub Main()
{
print "Content-type: text/html\n\n";
$in{difficulty} = 'Difficult';
%in = &ParseForm; #get input arguments

$methods{ns} = 1; #always on
if($in{'HS'}) {$methods{hs} = 1;}
if($in{'NP'}) {$methods{np} = 1;}
if($in{'IR'}) {$methods{ir} = 1;}
if($in{'XW'}) {$methods{xw} = 1;}
$timetotry = $in{'TimeToTry'};
$timetotry =~ s/\D*//g;
if($timetotry > 20){$timetotry = 20}
$target = $in{'NumberOfSquares'};
$target =~ s/\D*//g;
if($target > 60){$target = 60}

if ( $debug ) { open (DEBUG, ">../aaa.html") }
&CalcRegionalCellLocations(); #build @cellsIn  : used quickly find cells in regions

$starttime = time();
#&FillTempPossibilityArray1to9();
#RecursiveBuild(@AllCells);
$TimeTaken = time() - $starttime;
if ( $debug ){  print DEBUG "Time for CreateFullSudokuGridRecursive: $TimeTaken</br>";}
print DEBUG &PrintTextGameArrayDebug();
#exit;

$starttime = time();
$debug = 0;
&CreateFullSudokuGridRecursive( @AllCells );
$TimeTaken = time() - $starttime;
$debug = 1;
if ( $debug ){  print DEBUG "Time for CreateFullSudokuGridRecursive: $TimeTaken</br>";}

&CopyGameArrays( \@TempGameArray , \@FullGameArray );
&CopyGameArrays( \@TempGameArray , \@GameArray );
if ( $debug )
      {
      print DEBUG "<p>Game Array Created</p>";
      print DEBUG &PrintTempGameArrayDebug();
      }

$starttime = time();
$blanksquares = 0;
#start removing numbers from game grid
my $result;
$result = &RecursiveRemoveCells( @AllCells ) ;

if($result==0){die "could not solve"};
$TimeTaken = (time() - $starttime);
if ( $debug ) { print DEBUG &PrintTextGameArrayDebug(); }

#count blank squares. required?
$blanksquares = 0;
foreach my $cell ( @AllCells )
      {
      my ($x,$y) = @{ $cell };
      my $choice = $GameArray[$x][$y];
      if ($choice == '') {$blanksquares++}
      }

my $exposedsquares = 81 - $blanksquares;
$globalstring = " RemoveAttempCount: $RemoveAttempCount | NS: $NS | HS: $HS | NP: $NP | IR1: $IR1  | IR2: $IR2 | XW: $XW | Blank: $blanksquares | Time: $TimeTaken";
$difficulty = "Simple";
if ($HS > 0 )
      {$difficulty = "Easy";}
if ($NP > 0 )
      {$difficulty = "Medium";}
if ($IR > 0 )
      {$difficulty = "Hard";}

if($debug) {print DEBUG &PrintGameArrayDebug();}

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
if ($debug) {close DEBUG;}
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
            #if ($debug) {print DEBUG "$x,$y:$squ<br>"}
            push @{ $CellsIn{'squ'}{$squ} } , [$x,$y];
            #note col and row not required as $x and $y are equivalent. But I add it anyway.
            $IAmIn{'col'}{$x}{$y} = $x;
            $IAmIn{'row'}{$x}{$y} = $y;
            $IAmIn{'squ'}{$x}{$y} = $squ;
            }
      }
}

sub RecursiveBuild()
{
#recursively go through each @AllCells
#randomly choose a possible value
#test, said value, to ensure that all cells still have valid possibilities
#my %RemovedList;
my $choice;

&PrintPossibilityArrayHTML();
&PrintGameArrayHTML();
my @RemainingCells = shuffle @_;
&CopyGameArrays( \@GameArray , \@TempGameArray );
if($debug) { print DEBUG "moved GameArray to TempGameArray. Checking if TempGameArray is solvable. <br>" }
if ( &IsPuzzleSolvable() == 1 )
      {
      return(1);
      } #solvable. done
if($debug) { print DEBUG "Not solvable. <br>" }
if ( scalar @RemainingCells == 0 )
    {
    if($debug) { print DEBUG "Ran out of AllCells/ Error condition. <br>" }
    return(1);
    } #error. done
my $Cell = shift @RemainingCells;
my ($x , $y) = @{ $Cell };
if($debug) { print DEBUG "Setting PossibilityArray based on GameArray using sudoku rules. <br>" }
my $result = &SetPossibilityArrayBasedOnGameArrayValuesUsingSudokuRules();
if($debug) { print DEBUG &PrintGameArrayDebug() }
if($debug) { print DEBUG &PrintTempGameArrayDebug() }
if($debug) { print DEBUG &PrintPossibilityArrayDebug() }
if ( $result == 0 )
      {
      if($debug) { print DEBUG "No Possibilities Somewhere based on GameArray Returning<br>" }
      return(0)
      }
my @CellPossibilities = shuffle keys %{ $PossibleNumberArray[$x][$y] } ;
do
    {
    if($debug) { print DEBUG "CellPossibilities: @CellPossibilities at $x,$y<br>" }
    #if we are here, we are either:
    #forging ahead
    #returning from an failed recurse attempt. blank $GameArray[$x][$y] and try another choice if available
    $PossibleNumberArray[$x][$y]{ $GameArray[$x][$y] } = 1; #restore old possibility on fail
    if($debug) { print DEBUG "Possibility $choice replaced at $x,$y<br>" }
    delete $GameArray[$x][$y];
    if (scalar @CellPossibilities == 0)
          {
          if($debug) { print DEBUG "No Possibilities left at $x,$y Returning<br>" }
          return(0);
          }
    $choice = shift @CellPossibilities;
    #delete $TempPossibleNumberArray[$x][$y]{$choice}; #remove chosen possibility
    if($debug) { print DEBUG "Removing Possibility $choice at $x,$y<br>" }
    #if(scalar @CellPossibilities == 0)
      {
      $GameArray[$x][$y] = $choice;
      if($debug) { print DEBUG "Seting GameArray at $x,$y with $choice<br>" }
      }
    #$TempGameArray[$x][$y] = $choice; #remove choice from $PossibleNumberArray[$x][$y]
    #if($debug) { print DEBUG &PrintTempGameArrayDebug() }
    if($debug) { print DEBUG "Next Recursion<br>" }
    }
until( &RecursiveBuild(@RemainingCells ) );
return(1); #cascade
}

sub SetPossibilityArrayBasedOnGameArrayValuesUsingSudokuRules()
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
      my $choice = $GameArray[$x][$y];
      if ($choice != undef)
            {
            foreach my $region ( 'col' , 'row' , 'squ' )
                  {
                  my $RegionValue = $IAmIn{$region}{$x}{$y} ;
                  my @list = @{ $CellsIn{$region}{$RegionValue} };
                  foreach my $cell ( @list)
                        {
                        my ($x,$y) = @{ $cell };
                        if ( $GameArray[$x][$y] != undef )
                              {#$TempGameArray[$x][$y] is already set for this cell so no possibility to set here ()
                              delete $PossibleNumberArray[$x][$y];
                              }
                        else
                              {#remove the $choice from the cell
                              delete $PossibleNumberArray[$x][$y]{$choice};
                              my @Possibilities = keys %{ $PossibleNumberArray[$x][$y] };
                              #is the @Possibilities set empty - fail
                              if ( scalar(@Possibilities) == 0 ) {return(0)}
                              }
                        }
                  }
            }
      }
return (1); #all cells have at least 1 possibility!
}


sub CreateFullSudokuGridRecursive()
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
if($debug) { print DEBUG &PrintPossibilityArrayDebug() }
if ( $result == 0 )
      {
      if($debug) { print DEBUG "No Possibilities Somewhere Returning<br>" }
      return(0)
      }
my @CellPossibilities = shuffle keys %{ $PossibleNumberArray[$x][$y] } ;
do
      {
      #if we are here, we are either:
      #forging ahead
      #returning from an failed recurse attempt. blank $GameArray[$x][$y] and try another choice if available
      delete $TempGameArray[$x][$y];
      if (scalar @CellPossibilities == 0)
            {
            if($debug) { print DEBUG "No Possibilities left at $x,$y Returning<br>" }
            return(0);
            }
      my $choice = shift @CellPossibilities;
      $TempGameArray[$x][$y] = $choice; #remove choice from $PossibleNumberArray[$x][$y]
      if($debug) { print DEBUG &PrintTempGameArrayDebug() }
      }
until( &CreateFullSudokuGridRecursive( @RemainingCells ) );
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
                              my @Possibilities = keys %{ $PossibleNumberArray[$x][$y] };
                              #is the @Possibilities set empty - fail
                              if ( scalar(@Possibilities) == 0 ) {return(0)}
                              }
                        }
                  }
            }
      }
return (1); #all cells have at least 1 possibility!
}

sub Reduce1_9PossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules()
{
#IMPORTANT totally rebuilds/wipes @PossibleNumberArray
#fill up @PossibleNumberArray based on values in @$gameArray for each $row,$col,$squ
#if any cell has no possibility return 0 - fail - indicates not a valid sudoku
#DOES NOT SET $gameArray here
#that will be done in another routine
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
                              my @Possibilities = keys %{ $PossibleNumberArray[$x][$y] };
                              #is the @Possibilities set empty - fail
                              if ( scalar(@Possibilities) == 0 ) {return(0)}
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

sub FillTempPossibilityArray1to9()
{
foreach my $cell ( @AllCells )
      {
      my ($x,$y) = @{ $cell };
      foreach my $value ( 1 .. 9 )
            {
            $TempPossibleNumberArray[$x][$y]{$value} = 1; #see definition explanation
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
#note the techniques used must not be a blind recursive or random attempt. Those types solve for grids without unique solutions!!!!  
#$debug = 0;
#this takes a partially filled @TempGameArray and continually try to solve it by various techniques, IR, NP, HS and finally NS
#it fails if there is no progress on one loop
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
my $LpXW = 0;
my $string;
$HS = 0;
$NS = 0;
$NP =0;
$IR = 0;
$IR1 = 0;
$IR2 = 0;
$XW = 0;

&FillPossibilityArray1to9();
&Reduce1_9PossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules();
#OR
#&SetPossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules();
if($debug) { print DEBUG &PrintTempGameArrayDebug() }
#if($debug) { print DEBUG &PrintPossibilityArrayDebug() }

$AnyProgress = 1;
$blanksquaresleft = 1; #get us in the 'while' door
while ( ($blanksquaresleft == 1) and ($AnyProgress > 0) ) #start fresh each time until we get a run where all squares are filled
      {
      #try all &SetXX. these reduce possibilities when possible, returning how many possibility reductions were found
      #then try &SetNS as it alone clears up, and sets, the single possibilities! IT IS THE ONLY ONE THAT SETS THE $gameArrayTemp
      $AnyProgress = 0; #set it up to fail. if any possibility is removed using any technique, it still might be solvable
      #these should be first as they do not narrow possibilities down to one. Nor do they set a square on it's own. Give them a chance

#$methods{ir} =0;
#$methods{hs} = 0;
if($debug) { print DEBUG &PrintPossibilityArrayDebug() }

      if ($methods{xw})
            {
            $LpIR1 = &SetXW(); #Set XW
            $XW += $LpIR1;
            if ($LpXW)
              {
              if ( $debug )
                  {
                  print DEBUG "Set XP<br>";
                  }
              }
            $AnyProgress += $LpXW;
            }
$debug=0;
       if ($methods{ir})
            {
            $LpIR1 = &SetIR1(); #Set IR1 for rows and columns
            $IR += $LpIR1;
            $IR1 += $LpIR1;
            if ($LpIR1)
              {
              if ( $debug )
                  {
                  print DEBUG "Set IR1<br>";
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
                  print DEBUG "Set IR2<br>";
                  }
              }
            $AnyProgress += $LpIR2;
            }

        if ($methods{np})
            {
            $LpNP = &SetNP(); #Set NP method 1 for Local regions
            if ($LpNP > 0)
                  {
                  $NP += $LpNP;
                  $AnyProgress += $LpNP;
                  if ( $debug )
                        {
                        print DEBUG "Set $LpNP NP <br>";
                        #if($debug) { print DEBUG &PrintPossibilityArrayDebug() }
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
                    print DEBUG "Set $LpHS HS<br>";
                    }
                  }
            }

        #clears up all single possibilities. that is why it is last!
      if ($methods{ns})
            {
            if ($debug) {print DEBUG "Try NS<br>"}
            $LpNS =  &SetNS(); #Set NS based on previously calculated possibilities
            $NS += $LpNS;
            $AnyProgress += $LpNS;
            if ($LpNS)
                  {
                  if ($debug) {print DEBUG "Set $LpNS NS<br>"}
                  }
           }
$debug=1;

      #lets see if we are done yet
      $blanksquaresleft = &AreThereBlankSquares();
      $loopcount++;
      }

if ($blanksquaresleft == 0)
     {
     $solved = 1;
     } #it is only solvable if there are no blank squares left!

#if ($debug) {print DEBUG "<br>\n solvable:$solved | blankleft:$blanksquaresleft | NS:$NS | NP:$NP | HS:$HS | IR:$IR | loopcount:$loopcount<br>\n";}

$debug = 1;
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

sub RecursiveRemoveCells()
{
#&PrintGameArrayHTML();
#&PrintPossibilityArrayHTML();

my @CellsToRemove = shuffle @_; #will get shorter each loop by $NumberOfPicks
my %RemovedList;
$RemoveAttempCount++;
if($debug) {print DEBUG "Entering RecursiveRemoveCells. Count $RemoveAttempCount.<br>";}
#if($debug) { print DEBUG "GameArray is:</br>" }
#if($debug) { print DEBUG &PrintGameArrayDebug() }

if($debug) {print DEBUG "Testing IsPuzzleSolvable.<br>";}
&CopyGameArrays( \@GameArray  , \@TempGameArray );
#&CalcAllBlankCellsInTempGameArray();
#if ( &RecursiveSolveTempGameArray(@AllBlankCells)==0 ) #if it is not solvable replace the number in the grid
if (&IsPuzzleSolvable()==0)
#if (&IsPuzzleSolvableFast()==0)
      {
      if($debug) {print DEBUG "Previous RecursiveRemoveCells was not Solvable. Returning 0<br>";}
      return 0
      } #note: tests previous call
if($debug) {print DEBUG "Previous RecursiveRemoveCells was Solvable. Contiuing.<br>"}
#if( (time() - $starttime) >= $timetotry ) {if($debug) {print DEBUG "Time limit reached. Return 1<br>";}; return 1;} #Test for time
if($blanksquares >= $target)
      {
      if($debug) {print DEBUG "Reached target. Return 1<br>";}
      return 1
      } #Test for $target
do
      { #was not solvable. replace removed numbers. Note: will be blank on forward
      foreach my $cell (keys %RemovedList)
            {
            my ($x,$y) = split('',$cell);
            #$TempGameArray[$x][$y] = $RemovedList{$cell};
            $GameArray[$x][$y] = $RemovedList{$cell};
            delete $RemovedList{$cell}; #otherwise %$RemovedList piles up and we get errors
            push @CellsToRemove , [$x,$y]; # restore removed cells to list so we can remove them AGAIN
            $blanksquares--;
            if($debug) {print DEBUG "Restoring $RemovedList{$cell} to \$GameArray[$x][$y].<br>";}
            }
      if( (time() - $starttime) >= $timetotry ) {if($debug) {print DEBUG "Time limit reached. Return 1<br>";}; return 1;} #Test for time
      #if($debug) {print DEBUG "Restoring \%RemovedList if any.<br>";}
      #try to remove some random cells
      for (my $count = 0; $count < $NumberOfPicks ; $count++) #loop to remove a bunch at one time
            {
            #maybe later to make it truly recursive, we will have a shuffled list of all full, removable squares we can shift off
            if (scalar @CellsToRemove == 0){return 0} #out of random cells to try
            my $CellRef = shift @CellsToRemove ;
            my $x = $CellRef->[0];
            my $y = $CellRef->[1];
            if ($GameArray[$x][$y] == undef)
                  {
                  next;
                  } #no need to try and remove an already removed spot
            $RemovedList{"$x$y"} = $GameArray[$x][$y]; #add to remove list. we may need to restore them if we can't solve board
            if($debug) {print DEBUG "$GameArray[$x][$y] removed at $x,$y : ";}
            #delete $TempGameArray[$x][$y]; #remove picked number
            delete $GameArray[$x][$y]; #remove picked number
            if($debug) {print DEBUG "Deleting $GameArray[$x][$y] from both TempGameArray and GameArray.<br>";}
            $blanksquares++;
            }
      #if($debug) {print DEBUG "Solvable: continuing...<br>";}
      #and test in &RecursiveRemoveCells()
      if($debug) {print DEBUG "Calling next \&RecursiveRemoveCells.<br>"}
      }
until( &RecursiveRemoveCells(@CellsToRemove) );
return 1; #cascade back
}

sub RecursiveSolveTempGameArray()
{
#IMPORTANT: Does not require IsPuzzleSolvible loop.
#It can replace it.
#It tests for solve all in one! cannot be used with other solve methods.

#recursively go through each @AllBlankCells
#try a possibility from PossibilityArray
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
if($debug) { print DEBUG "Entering RecursiveSolveTempGameArray. Shift $x,$y off RemainingBlankCells. RemainingBlankCells is now @RemainingBlankCells<br>" }
my $result = &SetPossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules();
if ( $result == 0 )
      {
      if($debug) { print DEBUG "SetPossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules returned 0 at $x,$y<br>" }
      return(0)
      }
if($debug) { print DEBUG "SetPossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules is:</br>" }
if($debug) { print DEBUG &PrintPossibilityArrayDebug() }
if($debug) { print DEBUG "TempGameArray is:</br>" }
if($debug) { print DEBUG &PrintTempGameArrayDebug() }
my @CellPossibilities = keys %{ $PossibleNumberArray[$x][$y] } ;
do
      {
      #if we are here, we are either: forging ahead or returning from an failed recurse attempt.  blank $GameArray[$x][$y] and try another choice if available
      if($debug) { print DEBUG "deleted $TempGameArray[$x][$y] in TempGameArray[$x][$y]<br>" }
      delete $TempGameArray[$x][$y];
      if($debug) { print DEBUG "@CellPossibilities are posibilities at $x,$y <br>" }
      #if (scalar @CellPossibilities == 0) allows for incorrect game grids
      if (scalar @CellPossibilities != 1)
            {
            if($debug) { print DEBUG "No Possibilities left at $x,$y Returning 0<br>" }
            return(0);
            }
      my $choice = shift @CellPossibilities;
      if($debug) { print DEBUG "Trying $choice at in TempGameArray[$x][$y] and then calling next RemainingBlankCells with RecursiveSolveTempGameArray with @RemainingBlankCells<br>" }
      $TempGameArray[$x][$y] = $choice; #set $choice
      }
until( &RecursiveSolveTempGameArray( @RemainingBlankCells ) );
#we are done calculating so we MUST remove solved square as they are actually meant to be blank ones
if($debug) { print DEBUG "Puzzle is solved and backtracking so deleting TempGameArray $TempGameArray[$x][$y] at $x,$y </br>" }
delete $TempGameArray[$x][$y];
return(1); #cascade
}

sub SetXW()
{
#Find Possibility that occurs twice in one row, then another row
#if the two possibilities match columns, we can remove that possibility from the remaining cells in the columns
#do the same for columns!
my $countXW;
my $XWCountOnce;
my %TwoValues;
my %opposite;
$opposite{'row'} = 'col';
$opposite{'col'}='row';
foreach my $region ( 'row' , 'col' )
    {
    my %TwoValues = {};
    foreach my $RegionValue (0 .. 8) #for each row and col
        {
        my %PossibilityLocationsInRegion = {};
        my @list = @{ $CellsIn{$region}{$RegionValue} };
        #my $ColString ;
        foreach my $cell ( @list) #for each cell
            {
            my ($x,$y) = @{ $cell };
            my $opposite = $opposite{$region};
            my $OppositeRegion = $IAmIn{$opposite}{$x}{$y};
            foreach my $PossibleNumber ( keys %{ $PossibleNumberArray[$x][$y] } ) #for each Possibility
                {
                $PossibilityLocationsInRegion{$PossibleNumber}{$OppositeRegion} = 1; #record our col or row found
                }
            }
        foreach my $PossibleNumber ( keys %PossibilityLocationsInRegion ) #for each found $PossibleNumber in row or col
            {
            my @OppositeRegions = keys %{ $PossibilityLocationsInRegion{$PossibleNumber} };
            if(scalar @OppositeRegions == 2) #found two
                {
                my ($OR1,$OR2) = sort @OppositeRegions;
                #$TwoValues{$PossibleNumber}{"$OR1$OR2"}{$RegionValue} = 1; # later,if we have 2 or more values, we have a hit!
                $TwoValues{$PossibleNumber}{"$OR1$OR2"} = $TwoValues{$PossibleNumber}{"$OR1$OR2"} . "$RegionValue"; # later,if we have length 2 or more values, we have a hit!
print DEBUG "XW: Possibility $PossibleNumber found at $region $RegionValue and $opposite{$region}'s $OR1,$OR2<br>";
                }
            }
        }
    #look for xwing
    foreach my $PossibleNumber ( keys %TwoValues  ) #for each found $PossibleNumber in row or col
        {
        foreach my $ORPair ( keys %{ $TwoValues{$PossibleNumber} } ) #for each found $PossibleNumber in row or col
            {# $ORPair will aways be two as we tested for 2 previously. Do not test again
            my $CurrentRegions = $TwoValues{$PossibleNumber}{$ORPair}; #rows if we are doing rows, cols if doing cols
                if(length $CurrentRegions == 2)
                    {#XW hit!
                    my ($Row1,$Row2);
                    my ($Col1,$Col2);
                    my ($OR1,$OR2); #Other Region
                    if($region eq 'row')
                        {
                        ($Row1,$Row2) = split('',$CurrentRegions);
                        ($Col1,$Col2) = split('',$ORPair);
                        ($OR1,$OR2) = ($Col1,$Col2);
                        }
                    else
                        {
                        ($Row1,$Row2) = split('',$ORPair);
                        ($Col1,$Col2) = split('',$CurrentRegions);
                        ($OR1,$OR2) = ($Row1,$Row2);
                        }
                    #Ignore our trigger cells
                    my $Keep1 = "$Col1$Row1";
                    my $Keep2 = "$Col1$Row2";
                    my $Keep3 = "$Col2$Row1";
                    my $Keep4 = "$Col2$Row2";
                    #try to remove $PossibleNumber from $CellsIn{ $opposite{'$CurrentRegions'} }{Or1 and Or2} }
                    my $OR = $opposite{$region};
                    foreach my $RegionNumber ($OR1,$OR2)
                        {
                        my @list = @{ $CellsIn{$OR}{$RegionNumber} };
                            foreach my $cell ( @list) #for each cell in squ
                                {
                                my ($x,$y) = @{ $cell };
                                my $xy = "$x$y";
                                if( ($xy ne $Keep1) and ($xy ne $Keep2) and ($xy ne $Keep3) and ($xy ne $Keep4) )
                                    {#don't remove ours
                                    if($PossibleNumberArray[$x][$y]{$PossibleNumber} == 1) #only count cells where we will be removing something!
                                        {
print DEBUG "XW found: Possibility $PossibleNumber deleted at cell $x,$y as triggered at Cols: $Col1,$Col2 and Rows: $Row1,$Row2<br>";
                                        delete $PossibleNumberArray[$x][$y]{$PossibleNumber}; #removing $PossibleNumber from other cells in squ
                                        $XWCountOnce=1;
                                        }
                                    }
                                }
                        }
                    if($XWCountOnce==1){$countXW++;$XWCountOnce=0;}
                    }
            }
        }
    }

#print DEBUG "XW: Possibility $PossibleNumber deleted at cell $x,$y as $PossibleNumber was at $NumberOfPossibilitiesInSquare locations in $region $RegionValue and square $square<br>";

return $countXW; #return the number of IR1
};

sub SetIR1()
{
#First, it scans each row or col region for all possibilities.
#If exactly two or three exist for a single number in the same box,
#their values may be eliminated from the rest box.
my $countIR;
#for each col or row region if 2 - 3 possibilities exist for a number that is bound by a box region
#remove that possibility everywhere else in the bound box region
foreach my $region ( 'col' , 'row' )
      {
      foreach my $RegionValue (0 .. 8) #for each row and col
            {
            my %PossibilityLocationsInRegion;
            my @list = @{ $CellsIn{$region}{$RegionValue} };
             foreach my $cell ( @list) #for each cell
                  {
                  my ($x,$y) = @{ $cell };
                  foreach my $PossibleNumber (keys %{ $PossibleNumberArray[$x][$y] } ) #for each Possibility
                        {
                        my $squ = $IAmIn{'squ'}{$x}{$y};
                        $PossibilityLocationsInRegion{$PossibleNumber}{'squares'}{$squ} = 1; #track squares for $PossibleNumber
                        $PossibilityLocationsInRegion{$PossibleNumber}{'cells'}{"$x$y"} = 1; #track cells for $PossibleNumber
                        }
                  }
            foreach my $PossibleNumber ( keys %PossibilityLocationsInRegion ) #for each found $PossibleNumber in row or col
                  {
                  my @squares = keys %{$PossibilityLocationsInRegion{$PossibleNumber}{'squares'}};
                  if (scalar @squares == 1) #$PossibleNumber only found in one intersecting square!
                        {
                        my $square = shift @squares;
                        my $NumberOfPossibilitiesInSquare = scalar keys %{$PossibilityLocationsInRegion{$PossibleNumber}{'cells'}};
                        if ( ($NumberOfPossibilitiesInSquare > 1) and ($NumberOfPossibilitiesInSquare < 4) ) #2-3 $PossibleNumber found in this col or row and squ
                            {
                            my @list = @{ $CellsIn{'squ'}{$square} };
                            foreach my $cell ( @list) #for each cell in squ
                                {
                                my ($x,$y) = @{ $cell };
                                if( $PossibilityLocationsInRegion{$PossibleNumber}{'cells'}{"$x$y"} == undef ) #ignore our trigger cells
                                    {
                                    if($PossibleNumberArray[$x][$y]{$PossibleNumber} == 1) #only count cells where we will be removing something!
                                        {
print DEBUG "IR1: Possibility $PossibleNumber deleted at cell $x,$y as $PossibleNumber was at $NumberOfPossibilitiesInSquare locations in $region $RegionValue and square $square<br>";
                                        delete  $PossibleNumberArray[$x][$y]{$PossibleNumber}; #removing $PossibleNumber from other cells in squ
                                        $countIR++;
                                        }
                                    }
                                }
                              }
                        }
                  }
            }
      }
return $countIR; #return the number of IR1
};

sub SetIR2()
{
my $countIR;
#for each square region if 2 - 3 possibilities exist that is bound by a "SINGLE" row or col region
#remove that possibility everywhere else in the bound col or row region
foreach my $region ( 'squ' )
    {
    foreach my $RegionValue (0 .. 8) #for each square
        {
        my $GlobalSquare = $RegionValue;
        my %PossibilityLocationsInRegion;
        my @list = @{ $CellsIn{$region}{$RegionValue} };
        foreach my $cell ( @list) #for each cell in square
            {
            my ($x,$y) = @{ $cell };
            foreach my $PossibleNumber ( keys %{ $PossibleNumberArray[$x][$y] } ) #for each possibility in the cell in the square
              {
              my $row = $IAmIn{'row'}{$x}{$y};
              $PossibilityLocationsInRegion{$PossibleNumber}{'row'}{$row}++;
              my $col = $IAmIn{'col'}{$x}{$y};
              $PossibilityLocationsInRegion{$PossibleNumber}{'col'}{$col}++;
              $PossibilityLocationsInRegion{$PossibleNumber}{'cells'}{"$x$y"} = 1;
              #print DEBUG "IR2: SQU: $RegionValue \$PossibleNumber: $PossibleNumber added $x$y to <br>";
              }
            }
        foreach my $PossibleNumber ( keys %PossibilityLocationsInRegion ) #for each possibility
            {
            #my @squares = keys %{$PossibilityLocationsInRegion{$PossibleNumber}{'cells'}};
            #my @ref = $PossibilityLocationsInRegion{$PossibleNumber}{'cells'};
            my $NumberOfPossibilitiesInSquare = scalar keys % {$PossibilityLocationsInRegion{$PossibleNumber}{'cells'} };
            #my @foo =  keys %{$PossibilityLocationsInRegion{$PossibleNumber}{'cells'}};
                              #my $test = " @foo";
            #print DEBUG "IR2: squ: $RegionValue \$PossibleNumber: $PossibleNumber \$NumberOfPossibilitiesInSquare: $NumberOfPossibilitiesInSquare and @foo <br>";

            if (  ($NumberOfPossibilitiesInSquare > 1) and ($NumberOfPossibilitiesInSquare < 4)  ) #2-3 $PossibleNumber found in squ
                {
                foreach my $region ('col' , 'row')
                    {
                    foreach my $RegionValue (0 .. 8) #for each row and col
                        {
                        if($NumberOfPossibilitiesInSquare == $PossibilityLocationsInRegion{$PossibleNumber}{$region}{$RegionValue})
                            {#found possibilities that is bound by a "SINGLE" row or col region
                            my @list = @{ $CellsIn{$region}{$RegionValue} };
                            foreach my $cell ( @list) #for each cell in col or row
                                {
                                my ($x,$y) = @{ $cell };
                                if( $PossibilityLocationsInRegion{$PossibleNumber}{'cells'}{"$x$y"} == undef ) #ignore our trigger cells
                                    {
                                    if($PossibleNumberArray[$x][$y]{$PossibleNumber} == 1) #only count cells where we will be removing something!
                                        {
                                        print DEBUG "IR2: Possibility $PossibleNumber deleted at cell $x,$y as $PossibleNumber was at $NumberOfPossibilitiesInSquare locations in square $GlobalSquare and $region $RegionValue  <br>";
                                        delete  $PossibleNumberArray[$x][$y]{$PossibleNumber}; #removing $PossibleNumber from other cells in squ
                                        $countIR++;
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
return $countIR; #return the number of IR2
};

sub SetNP()
{
#Naked Pairs 1 and 2
#NP1 The first version of Naked Pairs searches each region (row, column and 3 x 3 square) for two possibility values that occur only twice in, and share two cells, which may or may not contain other possibilities. Because they occur
#only in these two cells, one of them must go in one cell and the other in the second. Therefore, any other values in these two cells may be eliminated.
#or
#NP2 if in a region, two cells share ONLY two possibilities,
#we can eliminate all other possibilities in this region.
my $countNP;
if ($debug) {print DEBUG "ENTERING NP<br>"}
foreach my $region ( 'col' , 'row' , 'squ' ) #for each region type
      {
      for my $RegionValue (0 .. 8) #for each region
            {
            my %NPCountOnce; # set $NPCountOnce{1 for np1} = 1 $NPCountOnce{2 for np2} = 1 for each region, so we only count NP once or twice per region
            my @list = @{ $CellsIn{$region}{$RegionValue} };
            my %NP1PossibilityLocations;
            # NP1: $PossibilityLocations{"Possibility"}={"x1y1x2y2.."} #xyxy indicates 2 cells for possibility
            my %NP1PossibilitesThatOccurTwice;
            # NP1: Then we create $CellsWithTwoPossibilities{"$x$y$x$y"}{"Poss1 2 etc"}=1 if just Poss1 and Poss2 then NP1 condition
            my %NP2ExclusivePossibilityPairs;
            # NP2: $NP2ExclusivePossibilityPairs{"$Poss1$Poss2..."} = "$x1$y1$x2$y2..."}
            #"$Poss1$Poss2 MUST be sorted so we can compare!
            #two $Poss1$Poss2 AND a $x1$y1 and $x2$y2 is a NP2 case
            foreach my $cell ( @list)
                {
                my ($x,$y) = @{ $cell };
                my $NP2SortedPossibilityString;
                foreach my $PossibleNumber ( sort keys %{ $PossibleNumberArray[$x][$y] } ) #must sort for NP2 data structure!!!
                    {
                    #NP1
                    $NP1PossibilityLocations{$PossibleNumber} = "$NP1PossibilityLocations{$PossibleNumber}" . "$x$y";
                    #NP2:
                    $NP2SortedPossibilityString = "$NP2SortedPossibilityString" . "$PossibleNumber";
                    }
                #NP2
                #note that $NP2SortedPossibilityString may NOT be 2 possibilities. We will filter later
                $NP2ExclusivePossibilityPairs{$NP2SortedPossibilityString} = "$NP2ExclusivePossibilityPairs{$NP2SortedPossibilityString}" . "$x$y";
                #if ($debug) {print DEBUG "$NP2SortedPossibilityString at $x,$y |"}
                }
            #if ($debug) {print DEBUG "<br>"}
            #NP1
            foreach my $PossibleNumber ( keys %NP1PossibilityLocations )
                {
                if(length $NP1PossibilityLocations{$PossibleNumber} == 4) #only want possibilities in 2 cells
                    {
                    $NP1PossibilitesThatOccurTwice{"$NP1PossibilityLocations{$PossibleNumber}"}{$PossibleNumber} = 1;
                    }
                }
            #look for NP1
            foreach my $xyxy (keys %NP1PossibilitesThatOccurTwice)
                {
                my @SharedPossibilites =  keys %{ $NP1PossibilitesThatOccurTwice{$xyxy} };
                if( scalar @SharedPossibilites == 2 ) #and now in SHARE those locations with another Possibility
                    {
                    #replace Possibilities in xyxy cells with Poss1 and Poss2 EXCLUSIVELY
                    my ($Poss1,$Poss2) =  @SharedPossibilites;
                    my ($x1,$y1,$x2,$y2) = split('',$xyxy);
                    #only count (and remove) is there are Possibilities to remove!
                    if( scalar keys % { $PossibleNumberArray[$x1][$y1] } > 2 )
                        {
                        delete $PossibleNumberArray[$x1][$y1];
                        delete $PossibleNumberArray[$x2][$y2];
                        $PossibleNumberArray[$x1][$y1]{$Poss1} = 1;
                        $PossibleNumberArray[$x1][$y1]{$Poss2} = 1;
                        $PossibleNumberArray[$x2][$y2]{$Poss1} = 1;
                        $PossibleNumberArray[$x2][$y2]{$Poss2} = 1;
if ($debug) {print DEBUG "NP1: Poss @SharedPossibilites at $xyxy Removing all other poss at $xyxy in $region $RegionValue<br>"}
                        $NPCountOnce{1}=1;
                        }
                    }
                }
            #look for NP2
            foreach my $NP2SortedPossibilityString (keys %NP2ExclusivePossibilityPairs)
                {
                if(length $NP2SortedPossibilityString == 2) # only look at cells with two possibilities
                    {
                    if(length $NP2ExclusivePossibilityPairs{$NP2SortedPossibilityString} == 4) #pair of cells found
                        {
                        #remove possibility pair from all other cells in region
                        my ($Poss1,$Poss2) =  split('' , $NP2SortedPossibilityString);
                        my ($x1,$y1,$x2,$y2) = split('' , $NP2ExclusivePossibilityPairs{$NP2SortedPossibilityString});
                        foreach my $cell ( @list)
                            {
                            my ($x,$y) = @{ $cell };
                            if( ("$x$y" ne "$x1$y1") and ("$x$y" ne "$x2$y2") )  #ignore trigger cells
                                {
                                if( $PossibleNumberArray[$x][$y]{$Poss1}==1 or $PossibleNumberArray[$x][$y]{$Poss2}==1 )
                                    { #only count (and remove) is there are Possibilities to remove!
                                    delete $PossibleNumberArray[$x][$y]{$Poss1};
                                    delete $PossibleNumberArray[$x][$y]{$Poss2};
                                    $NPCountOnce{2}=1;
if ($debug) {print DEBUG "NP2: Poss$Poss1,$Poss2($NP2SortedPossibilityString) at $x1,$y1 and $x2,$y2 ($NP2ExclusivePossibilityPairs{$NP2SortedPossibilityString}) Removing all other poss at cell $x,$y $region $RegionValue<br>"}
                                    }
                                }
                            }
                        }
                    }
                }
            if($NPCountOnce{1}==1){$countNP++;$NPCountOnce{1}=0;}
            if($NPCountOnce{2}==1){$countNP++;$NPCountOnce{2}=0;}
            }
        }
if ($debug) {print DEBUG "LEAVING NP<br>"}
return $countNP; #return the number of NP
};

sub SetHS()
{
#Hidden Singles
#IMPORTANT: do not run SetPossibilityArrayBasedOnTempGameArrayValuesUsingSudokuRules as it will muck up posibilities changed by NP
#for each number 1-9 check each region 0-8 (squ row col) and  see if that number exists only once in @PossibleNumberArray
#if so, that number is at the only possible location in that region.
#remove all possibilities except than number for that location
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
                              if ($debug) {print DEBUG "Found HS $PossibleNumber at $x,$y setting PossibleNumberArray to $PossibleNumber<br>"}
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
if ($debug) {print DEBUG "NS found at $x,$y for possibility $PossibleNumber for row col squ . Removing $PossibleNumber for row $IAmIn{'row'}{$x}{$y} col $IAmIn{'col'}{$x}{$y} squ $IAmIn{'squ'}{$x}{$y}<br>"}
                        #wipe $PossibleNumber from all affected $row,$col,$squ
                        foreach my $region ( 'col' , 'row' , 'squ' )
                              {
                              my $RegionValue = $IAmIn{$region}{$x}{$y};
                              my @list = @{ $CellsIn{$region}{$RegionValue} };
                              foreach my $cell ( @list)
                                    {
                                    my ($x1,$y1) = @{ $cell };
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
my $string = "TempGameArray:</br>";

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
my $string = "GameArray: </br>";

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

sub PrintTextGameArrayDebug()
{        #for game array
my $string = "<pre>";

for (my $y = 0; $y < 9 ; $y++)
      {
      for (my $x = 0; $x < 9 ; $x++)
            {
            if($GameArray[$x][$y] != undef)
                  {
                  $string .=  "$GameArray[$x][$y]";
                  }
            else
                  {
                  $string .=  "-";
                  }
            }
      $string .=  "\r";
      }
$string .=  "</pre>";
return $string;
}

sub PrintTextTempGameArrayDebug()
{        #for game array
my $string = "<pre>";

for (my $y = 0; $y < 9 ; $y++)
      {
      for (my $x = 0; $x < 9 ; $x++)
            {
            if($TempGameArray[$x][$y] != undef)
                  {
                  $string .=  "$TempGameArray[$x][$y]";
                  }
            else
                  {
                  $string .=  "-";
                  }
            }
      $string .=  "\r";
      }
$string .=  "</pre>";
return $string;
}

sub PrintTextPossibilityArrayDebug()
{        #for game array
my $string = "<pre>";

for (my $y = 0; $y < 9 ; $y++)
      {
      for (my $x = 0; $x < 9 ; $x++)
            {
            if($PossibleNumberArray[$x][$y] != undef)
                  {
                  $string .=  "$PossibleNumberArray[$x][$y]";
                  }
            else
                  {
                  $string .=  "-";
                  }
            }
      $string .=  "\r";
      }
$string .=  "</pre>";
return $string;
}

sub PrintGameArrayHTML()
{        #for game array
open (HTML, ">./GameArray.html");
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

print HTML $string;
close HTML;
#return $string;
}

sub PrintPossibilityArrayHTML()
{ #for poss array
open (HTML, ">./PossibilityArray.html");

my $string .=  "<table border='1'>";

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

print HTML $string;
close HTML;
}

sub PrintPossibilityArrayDebug()
{ #for poss array
my $string = "PossibilityArray:</br>";

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

sub PrintTempPossibilityArrayDebug()
{ #for poss array
my $string = "TempPossibilityArray:</br>";

$string .=  "<table border='1'>";

for (my $y = 0; $y < 9 ; $y++)
      {
      $string .=  "<tr>";
      for (my $x = 0; $x < 9 ; $x++)
            {
            $string .=  "<td border='1'>";
            my @orderedlist = sort keys %{ $TempPossibleNumberArray[$x][$y] };
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
for my $y (0..8)
    {
    for my $x (0..8)
        {
        #look for blank cell. if == 0 then next
        $GridFast{ my $cell = $y . $x } && next; 
        #set taken for this cell based on row and col
        $taken .= $GridFast{ $_ . $x } . $GridFast{ $y . $_ } for 0..8;
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
        
        foreach my $try ( grep $taken !~ m/$_/, 0..8 ) #for 1..9 NOT in $taken
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
for my $y (0..8)
    {
    for my $x (0..8)
        {
        #push @GlobalOutput , $GridFast{ my $cell = $y . $x }   
        }
    }
#die map { $GridFast{$_} } 9 .. 99;
#@output = map { $GridFast{$_} } 9 .. 99;
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
    
#try 3 line? simpler?
#my $a = 8;
#my $output = $G{ int( ++$a / 9 ) . $a % 9 + 1 } = $_ for split //, <>;
my $output = &TryToSolve();

print $output;

=pod
echo 000010000301400860900500200700160000020805010000097004003004006048006907000080000 | perl sudoku.pl

$_=$`.$_.$'.<>;split//;${/[@_[map{$i-($i="@-")%9+$_,9*$_+$i%
9,9*$_%26+$i-$i%27+$i%9-$i%3}0..8]]/o||do$0}for/0/||print..9
=cut
}



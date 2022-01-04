# Sudoku Algorithm Part 1 Filling the puzzle

Step one of creating a Sudoku puzzle is obviously filling in the whole 9 x 9 grid with numbers that fit the constraints of Sudoku rules:

1. Each row must contain the numbers 1 to 9.
2. Each column must contain the numbers 1 to 9.
3. Each 3 x 3 local square must contain the numbers 1 to 9.

After staring at a blank page for a few hours, I decided to see how others tackled the task of creating Sudoku puzzles.

Some  interesting pages I found were:
https://davidbau.com/archives/2006/09/04/sudoku_generator.html
https://www.sudokuonline.us/make_your_own_sudoku_puzzle.php
https://ostermiller.org/qqwing/
https://www.codeproject.com/KB/recipes/Abhishek_Sudoku.aspx

The last link is the one that sparked an idea for my own algorithm. In broken English the author attempts to explain how he wrote his program. I misinterpreted parts of his article, but it created a few good ideas to start my own Sudoku algorithm.

To fill the Sudoku grid, I use what I term a 9 x 9 Potential Array. What each cell in the Potential Array holds is a list of possible values that could potentially work in that cell based on Sudoku rules.

With a blank 9 x 9 Sudoku grid, each cell in the Potential Array must be (1..9) as there are no limitations yet. Our Sudoku Game Array is empty right now.

1. We the randomly choose an empty cell in the Sudoku Game Array. This is effectively, any list of 2 or more numbers in the Potential Array.  
In the same cell in the Potential Array, we randomly choose one of the potential list numbers and remove all the other numbers in that list. 
We take that chosen number and place it in the Sudoku Game Array.
This cell is set.

2. Each time we set a value in the Sudoku Game Array, we must recalculate the Potential Array based on the values placed in the Sudoku Game Array. For example, if there is a 7 in row 2, there can be no other 7’s in the rest of the row. Therefore the all the Potential Array lists for row 2 will be stripped of the number 7. The same holds true for the cells column and the local 3 x 3 square that the cell resides in.

3. If we find a list in the Potential Array that contains NO values, then our attempt at filling the Sudoku board has failed, and we must start again.

4. I then go through every cell in the Potential Array looking for a list that only contains one number. If it contains one number, that cell in the Sudoku Game Array MUST become that number.

5. Check if Sudoku Game Array is complete. If so, exit. Note that all cells in the Potential Array will have a single values at this point.

6. Go to step 1.

Using this method finds a workable Sudoku grid between 1 to ten try’s on average.

A recursive algorithm could be used, but as my algorithm works, I did not follow that route. 

The next article will cover the task of removing numbers from the Sudoku Game Array so we can have a Sudoku puzzle with only one possible solution.

# Sudoku Algorithm Part 2 Removing numbers from the board

So we now have a 9 x 9 grid with numbers that fit the constraints of Sudoku rules:

1. Each row must contain the numbers 1 to 9.
2. Each column must contain the numbers 1 to 9.
3. Each of the nine 3 x 3 local square must contain the numbers 1 to 9.

Now we have to remove numbers from the board one at a time. We can’t just remove any number. Each time we remove a number we will need to verify that the board can be solved. In essence, we will need to  try and solve the Sudoku puzzle each time we remove another number using the methods (ns,hs,np,ir,xw,yw) listed below. If we only use the simplest methods to see if the puzzle can be solved, then our puzzle will be simpler. For example using only ns and hs methods we will have a very simple Sudoku puzzle. If we use all the methods (ns,hs,np,ir,xw,yw) our puzzle has the potential to be more difficult. 

So obviously we need to write a Sudoku solving algorithm with the ability to try all the methods (ns,hs,np,ir,xw,yw).

My Sudoku solving algorithm uses a while loop:
while ( ($blanksquaresleft == 1) and ($solvable == 1) ) {keep randomly blanking cells and try to solve the Sudoku grid}
If we can solve the Sudoku grid,  return a success code. $solvable == 1

The $solvable variable is set to 1 if we have at least filled in one blank square during the last loop. This at least gives us the hope that this 9 x 9 grid is solvable. If, during the last loop, we did not fill in any blank squares, this Sudoku grid is not solvable, so quit and return our failure. ????

$LpNS, $LpHS, etc are return variables indicating that we filled in $LpNS number of cells for that type of Sudoku fill algorithm NS.
if ( ($LpNS > 0) or ($LpHS > 0) ) {$solvable = 1} #still might be solvable! keep going
else {$solvable = 0} #our algorithm can’t solve this board! quit and return a failure code

We loop until we cannot fill in another cell or we complete the Sudoku puzzle. 
If we cannot fill in a cell, we return a fail condition, replace the number in the last random cell we tried to remove, and remove another number from a randomly selected cell. 
If we finally fill in all the Sudoku cells we return successfully and try to remove yet another random cell from the Sudoku board and try and solve that board.

My breakout condition for the Sudoku number removal loop, is set by a time limit. My code is sufficiently fast that 5 seconds is plenty to get the Suduku board down to 25 visible numbers.

The next part we need to code are the algorithms to actually fill in the blank squares. See the next article.

#  Sudoku Algorithm Part 3 The Seven Basic Ways of Solving Sudoku Stratagies

To my knowledge, there are 7 basic methods to try and solve Sudoku puzzles. Naked Singles (NS), Hidden Singles (HS), Naked Pairs (NP), Hidden Pairs (HP), Intersection Removal (IR), X-Wing (XW), and Y-Wing (YW).

Naked Singles (NS): Naked Singles routine iterates through all the empty squares on the board, calculating the possible values in each cell based on Sudoku’s rules. When we find a cell with a single possibility we fill in the Sudoku cell with that value.  Then we remove that possibility from all the cells in the affected column, row and square regions. We run this routine first as all the ones below rely on the cell's update possibility lists.

Hidden Singles (HS): Hidden Singles scan each row, column and 3 x 3 square for the "number of possibilities" (not the possibilities) for each number ranging from one to nine. When it finds a cell containing a possibility of a number that appears only once in a row, column or 3 x 3 square, we fill in the Sudoku board with that value.  Then we remove that possibility from the affected column, row and 3 x 3 square regions.

Naked Pairs (NP):

The first version of Naked Pairs searches each region (row, column and 3 x 3 square) for two possibility values that occur only twice in, and share two cells, which may or may not contain other possibilities. Because they occur
only in these two cells, one of them must go in one cell and the other in the second. Therefore, any other values in these two cells may be eliminated.

The second version scans each region (row, column and 3 x 3 square) for two cells, each containing ONLY the same two possibilities. Because one of these values must occur in each of the two cells, they cannot occur anywhere else in that region, and may be eliminated from the lists of possibilities for every other cell in the region.

Hidden Pairs (HP):

Hidden Pairs are taken care of  by the combination of Naked Singles and Hidden Singles algorithms.

Intersection Removal (IR):

If exactly two or three possibilities exist for a single number in a 3 x 3 box and they are restricted to one row or column, their values may be eliminated from the rest of the row or column. The case of one possibility is covered by HS above.

If exactly two or three possibilities exist for a single number in a row or column and it is bound by a 3 x 3 box, the number can be eliminated from the rest of the box. The case of one possibility is covered by HS above.

X-Wing (XW):

Look for a single possibility value that occurs exactly twice in two rows. If the cells containing
the value line up in two columns to form a rectangle, all occurrences of the value may be
removed from both columns. This also works the other way, starting with columns and eliminating
from rows.

Y-Wing (YW)
Y-wings work by eliminating possibilities from intersections of influence. Each cell exerts
a range of influence on all the others cells in the same row, column, and box. Y-wing is a
complex, advanced technique, so we present an example:

Suppose a cell has exactly two possibilities A and B. This cell AB is the pivot. Consider
two cells, AC and BC, which are influenced by AB, but do not influence each other. If they
each share exactly one possibility with AB and exactly one possibility with each other, then
the possibility held in common between AC and BC, C, can be eliminated from every cell in
the intersection of AC and BC’s ranges of influence.

<HTML>
  <HEAD>
         <META NAME="KEYWORDS"
          CONTENT="Sudoku , Friends ,infinite , instant , unlimited , Sudoku , number, game, generator , puzzle , script , Sudoku, printable">
         <META NAME="DESCRIPTION"
          CONTENT="Sudoku of Death. Sudoku Puzzle Generator Script to create Sudoku for prining or saving for use in your web browser">

         <TITLE>Sudoku of Death. Puzzle Generator by Emogic.com</TITLE>
  </HEAD>
   <BODY BACKGROUND="sudoku.gif">
         <CENTER>
                <TABLE CELLPADDING="0" CELLSPACING="0" BGCOLOR="#FFFFFF">
                  <TR>
                         <TD></TD>
                  </TR>
                </TABLE>
                <TABLE CELLPADDING="0" CELLSPACING="1" BGCOLOR="#000000">
                  <TR>
                         <TD>
                                <TABLE CELLPADDING="5" CELLSPACING="0" BGCOLOR="#FFFFFF">
                                  <TR>
                                         <TD>
                                                <CENTER>
                                                  <H3>Sudoku Puzzles made by Emogic's Sudoku of Death
                                                         Generator</H3></CENTER>
                                                <CENTER>
                                                  <P><A HREF="/cgi/sudoku/">Create a new Sudoku Puzzle</A> </P> 
							<? echo linkgames("/sudoku/common/" , getgames('.') );  ?>
</CENTER>
                                                 </TD>
                                  </TR>
                                </TABLE></TD>
                  </TR>
                </TABLE>
                <TABLE CELLPADDING="0" CELLSPACING="0" BGCOLOR="#FFFFFF">
                  <TR>
                         <TD> </TD>
                  </TR>
                </TABLE> <?
function getgames($GameSavePath)
        {
        //input: server path to saved games , the uid of the game owner
        //output: a sorted array of the game numbers
        $gamesarray = array();
        if (is_dir("$GameSavePath") == FALSE) {return $gamesarray;}
        if ($handle = opendir("$GameSavePath"))
                {
            while (false !== ($file = readdir($handle)))
                        {
                if ($file != "." && $file != ".." &&is_dir($file))
                                {
                                array_push($gamesarray , "$file");
                        }
                        }
                }
        sort($gamesarray); //sort numerically
        return $gamesarray;
        }

function linkgames($GameURL , $games)
        {
         //input: base url to games , the uid of the game owner , array of the owners games , the name or /uid of the person who wants to join this game
         //output: a formated link to the game

         if ($games == array()) {return "No games created.<br>";} 
		 $outstr = '';
		 foreach ($games as $game) { $outstr = "$outstr<a href='$GameURL/$game/'><u>$game</u></a> &nbsp;&nbsp;";
         //$outstr = "$outstr <br>";
         } return($outstr); } ?>
         </BODY>
</HTML>
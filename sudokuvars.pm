package sudokuvars;

#relative to script location or full server path if microsoft
$archivepath = "../../sudoku";

#$baseurl = "https://www.emogic.com";
#$baseurl = "http://127.0.0.1";
$baseurl = "";
$archiveurl = "$baseurl/sudoku";

$scripturl = "$baseurl/cgi/sudoku";

$SEND_MAIL= "/usr/lib/sendmail -t";
#example: $SEND_MAIL="/usr/lib/sendmail -t";

#$SMTP_SERVER="mail.yourdomain.com";
#use SMTP_SERVER if SEND_MAIL is unavailable, BUT NOT BOTH
#example: $SMTP_SERVER="mail.yourdomain.com";

$from = "Sudoku of Death Mailer Ver 1.0 <vpelss\@emogic.com>";
#This will be in all Email from addresses
#example $from = "Tarot Mailer Ver 1.0 <vpelss\@emogic.com>";
#THE SLASH IS MANDITORY!

$subject = "Deadly Sudoku from Emogic.com";
#email subject. Note: The script adds the visitors name will show at the end
$subject = 'I have a Deadly Sudoku for you!';
@mysites=($baseurl , "http://www.somewhereincanada.com", "http://www.emogic.com");



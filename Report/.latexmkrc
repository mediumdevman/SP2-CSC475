# Build settings for latexmk (also used by Overleaf).
use Cwd;
my $here = getcwd();

# Look for the ISMIR template files (ismir.sty, cite.sty, IEEEtran.bst, figs/) in template/
ensure_path('TEXINPUTS', "$here/template//");
ensure_path('BSTINPUTS', "$here/template//");
ensure_path('BIBINPUTS', "$here//");

# Put build leftovers (.aux, .log, .bbl, ...) in build/; the PDF stays here
$emulate_aux = 1;
$aux_dir = 'build';
$out_dir = '.';

# Don't write main.fls next to the PDF (this latexmk version ignores aux_dir for it)
$recorder = 0;

#include "strTheory.h"

std::string inputFile;
//int freeVarMaxLen = 7;
// -------------------------------
// default behavior:
//   avoid loop inducing cut
// -------------------------------
//bool avoidLoopCut = true;

/**
 * Test Procedural Attachment Theory.
 */
void pa_theory_example()
{
    if (inputFile == "")
    {
        printf("No input file is provided.\n");
        return;
    }
    Z3_context ctx = mk_my_context();
    Z3_theory Th = mk_pa_theory(ctx);
    ctx = Z3_theory_get_context(Th);

    // load cstr from inputFile
    Z3_ast fs = Z3_parse_smtlib2_file(ctx, inputFile.c_str(), 0, 0, 0, 0, 0, 0);

#ifdef DEBUGLOG
    __debugPrint(logFile, "\nInput loaded:\n-----------------------------------------------\n");
    printZ3Node(Th, fs);
    __debugPrint(logFile, "\n-----------------------------------------------\n");
#endif

    Z3_assert_cnstr(ctx, fs);
    check(ctx);
    Z3_del_context(ctx);
}

int main(int argc, char ** argv)
{
    logFile = NULL;
    std::string primStr;
    inputFile = std::string("");
    int c;

    static struct option long_options[] =
    {
        { "input", required_argument, 0, 'f' },
        { "freevarlen", required_argument, 0, 'l' },
        { "help", no_argument, 0, 'h' },
        { "allowloopcut", no_argument, 0, 'p' },
        { 0, 0, 0, 0 }
    };

#ifdef DEBUGLOG
    if(logFile == NULL)
    logFile = fopen("log", "w");
    __debugPrint(logFile, "Input file: %s\n", inputFile.c_str() );
#endif

    while (1)
    {
        int option_index = 0;
        c = getopt_long(argc, argv, "hpf:l:", long_options, &option_index);

        if (c == -1)
            break;

        switch (c)
        {
            case 'f':
            {
                inputFile = std::string(optarg);
                break;
            }
            case 'l':
            {
                //freeVarMaxLen = atoi(optarg);
                break;
            }
            case 'p':
            {
                // Allow loop cut
                // May not terminate on some input
                //avoidLoopCut = false;
                break;
            }
            case 'h':
            {
                break;
            }
            default:
                exit(0);
        }
    }
#ifdef DEBUGLOG
    fflush(stdout);
    printf("Input File:\n");
    printf("\t%s\n", inputFile.c_str());
    printf("Free Variable Max Length:\n");
    printf("\t%d\n", freeVarMaxLen);
    printf("\n");
    fflush(stdout);
#endif

    pa_theory_example();

#ifdef DEBUGLOG
    fclose(logFile);
#endif

    return 0;
}


/*
 * Description: The file is to provide a sample main function to test the two io classes.
 * 
 * Abstract from the page: http://www.kegel.com/dkftpbench/nonblocking.html
 */

main()
{
    filesender_t c;
    int sock = fileno(stdout);

    c.sendFile("foo.txt", sock);
    do {
        int done = c.handle_io();
        if (done) 
            break;
    }
}

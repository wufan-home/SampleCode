/*
 * Description: The goal of the class is to provide the synchronous and blocking I/Os
 * which send the contents of a file to a socket (i.e., through a socket file descriptor).
 * 
 * Abstract from the page: http://www.kegel.com/dkftpbench/nonblocking.html
 */

#define BUFSIZE 1024
class filesender_t {
public:
    /* Send a file on the given socket.
     * 'filename' is the name of the file to send.
     * 'socket' is an open network connection.
     * On exit, socket is closed.
     */
    void sendFile(const char *filename, int socket)
    {
        int fd;
        int nread; 
        int nwrite, i;
        char buf[BUFSIZE];

        /* Open the file */
        fd = open(filename, O_RDONLY);
        if (fd < 0)
            fatal_error("open failed");

        /* Send the file, one chunk at a time */
        do {                                            /* loop in time! */
            /* Get one chunk of the file from disk */
            nread = read(fd, buf, BUFSIZE);
            if (nread == 0) {
                /* All done; close the file and the socket. */
                close(fd);
                close(socket);
                break;
            }

            /* Send the chunk */
            for (i=0; i<nread; i += nwrite) {        /* loop in time! */
                /* write might not take it all in one call,
                 * so we have to try until it's all written
                 */
                nwrite = write(socket, buf + i, nread - i);
                if (nwrite < 0) 
                    fatal_error("write failed");
            }
        }
    }
};

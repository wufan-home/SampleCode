follow_1-129.213.128.84:~/network/tcp/cpp > clear
/*
 *
 *
 * */

#include <iostream>
#include <stdlib.h>
#include <string>

#include "client.h"

int main(int argn, char *argv[])
{
    char ip[30];
    unsigned short port = 0;
    bool isIpV4 = true;

    switch(argn)
    {
        case 3:
            std::cout << "Parsing data from the file " << argv[2] << std::endl;
            break;
        case 9:
            std::cout << "The host ip = " << argv[2]
                      << ", port = " << argv[4]
                      << ", version = " << argv[6] << "."
                      << std::endl;
            break;
        default:
            std::cout << "ERROR: Incorrect parameter format." << std::endl;
            std::cout << "Sample usage: start -ip <ip_address> -p <port_number> -v <4 or 6> [-m <message>]" << std::endl;
            std::cout << "Or start -f <file_name>" << std::endl;
            return 0;
    }

    TCPConnection *connection = new TCPConnection(ip, port, isIpV4);
    connection->connect();
    connection->connect();
    connection->disconnect();

    return 1;
}

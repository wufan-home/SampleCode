/* 
 * 
 * 
 * */ 

#include <iostream> 
#include <stdlib.h>  
#include <string> 

#include "client.h" 
#include "common.h" 

int main(int argn, char *argv[]) 
{
    TCPConnectionInfo connectiongInfo;

    switch(argn) 
    { 
        case 3: 
            std::cout << "Parsing data from the file " << argv[2] << std::endl; 
            break;
        case 7:
        case 9:
            std::cout << "The host ip = " << argv[2] 
                      << ", port = " << argv[4] 
                      << ", version = " << argv[6] << "." 
                      << std::endl;
            
            strcpy(connectiongInfo.ip, argv[2]); 
            connectiongInfo.port = Common::getPortNumber(argv[4]); 
            connectiongInfo.isIpV4 = (strcmp(argv[6], "4") == 0);
            
            break;
        default:
            std::cout << "ERROR: Incorrect parameter format." << std::endl;
            std::cout << "Sample usage: start -ip <ip_address> -p <port_number> -v <4 or 6> [-m <message>]" << std::endl;
            std::cout << "Or start -f <file_name>" << std::endl;
            return 0;
    }

    std::cout << connectiongInfo.ip << ", " << connectiongInfo.port << ", " << connectiongInfo.isIpV4 << std::endl;

    TCPConnection *connection = new TCPConnection(connectiongInfo.ip, connectiongInfo.port, connectiongInfo.isIpV4);
    connection->init();
    
    
    connection->disconnect();
    delete connection;

    return 1;
} 

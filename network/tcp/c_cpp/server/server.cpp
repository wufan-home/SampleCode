/*
 * Name: start.cpp
 * Description: The starter of a TCP server.
 * Platform: Ubuntu Linux 16.04/
 * Author: Fan Wu
 * Date: 03/01/2020
 * */

#include <cstring> 
#include <iostream>
#include <netinet/in.h>
#include <unistd.h>
#include <sys/socket.h>

int main(int argn, char *argv[])
{ 
    std::cout << "[INFO] Start to launch a TCP server service." << std::endl; 

    int sockFd = socket(AF_INET, SOCK_STREAM, 0); 
    if (sockFd < 0)
    {
        std::cout << "[ERROR] Failed to create the socket of a TCP server service." << std::endl;
        return 0;
    } 
    else 
    { 
        std::cout << "[INFO] Successfully created a socket file descriptor of a TCP server service." << std::endl;
    } 

    // Establish the listenning to a specific port.
    sockaddr_in serverInformation;
    bzero((char *) &serverInformation, sizeof(serverInformation));

    serverInformation.sin_family = AF_INET; 
    serverInformation.sin_addr.s_addr = INADDR_ANY; 
    serverInformation.sin_port = 17001;  

    if (bind(sockFd, (struct sockaddr *) &serverInformation, sizeof(serverInformation)) < 0) 
    { 
        std::cout << "[ERROR] Failed to bind the TCP server service to the specific port." << std::endl;
        return 0; 
    } 
    else 
    { 
        std::cout << "[INFO] Successfully bind the server service to the specific port." << std::endl;
    }
    
    std::cout << "[INFO] Start to listen to the port: " << serverInformation.sin_port << "." << std::endl;
    listen(sockFd, 5);

    sockaddr_in clientInformation; 
    socklen_t clientLen = sizeof(clientInformation); 
    char cmd[20];
    strcpy(cmd, "run"); 
    // do 
    //{ 
        int clientSockFd = accept(sockFd, (struct sockaddr *) &clientInformation, &clientLen);
        if (clientSockFd < 0)
        { 
            std::cout << "[ERROR] Failed to accept the TCP requests." << std::endl;
            // continue;
        } 
        else
        { 
            std::cout << "[INFO] Successfully accept the TCP requests from the IP address " << clientInformation.sin_addr.s_addr << "." << std::endl;
        } 

        char buffer[256];
        bzero(buffer, 256);
        if (read(clientSockFd, buffer, 255) < 0) 
        {   
            std::cout << "[ERROR] Failed to read message from the socket." << std::endl;
            // continue;
        }
        
        std::cout << "[INFO] The received message is " << buffer << "." << std::endl;

        // std::cout << "[Console] Input the command: ";
        // std::cin >> cmd;
    // } while (strcmp(cmd, "exit")); 

    close(sockFd);

    std::cout << "[INFO] End the existed TCP server service." << std::endl;

    return 1;
}

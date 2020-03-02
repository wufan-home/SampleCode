/* 
 * 
 * Name: client.cpp 
 * Description: This is the implementation of tcp class.
 * Platform: Ubuntu Linux 16.04.
 * Author: Fan Wu 
 * Date: 02/25/2020 
 *
 * */ 

#include "client.h" 

TCPConnection::TCPConnection(char ip[], unsigned short port, bool isIpV4 = true)
{ 
    if (strlen(ip) > 16 || (isIpV4 && (strlen(ip) > 15 || strlen(ip) < 7)))
    {
        std::cout << "Incorrect ip address format inputed. The ip format is "
                  << (isIpV4 ? "ipV4" : "ipV6") << ". "
                  << "The ip address is set to be empty."
                  << std::endl;
    }
    else
    { 
        strcpy(isIpV4 ? _ipV4 : _ipV6, ip);
        _port = port; 
    }

    _isIpV4 = isIpV4;
    _isConnected = false;
}

int TCPConnection::init()
{
    if (_isConnected) 
    { 
        std::cout << "The tcp connection " << (_isIpV4 ? _ipV4 : _ipV6) << ":" << _port 
                  << " has been built. No new connection is needed." << std::endl;

        return 0;
    } 

    std::cout << "One new tcp connection " << _ipV4 << ":" << _port << " is built." << std::endl;
    
    // Create a socket to establish a TCP connection.
    _sockFd = socket(PF_INET, SOCK_STREAM, 0); 
    if (_sockFd < 0) 
    { 
        std::cout << "ERROR: Failed to create a socket." << std::endl;
        return -1;
    }
    else
    {
        std::cout << "Successfully created a socket." << std::endl;
    }
        
    // Establish the TCP connection.
    sockaddr_in serv_addr; 
    bzero((char *) &serv_addr, sizeof(serv_addr)); 
    
    serv_addr.sin_family = AF_INET; 
    strcpy((char *)(&serv_addr.sin_addr.s_addr), _ipV4);
    serv_addr.sin_port = _port;
    if (connect(_sockFd, (struct sockaddr *) &serv_addr,sizeof(serv_addr)) < 0)
    { 
        std::cout << "ERROR: Failed to establish TCP connection." << std::endl;
        return -1;
    }
    _isConnected = true;

    return 0;
}
    
void TCPConnection::disconnect()
{
    // Close the connection. 
    close(_sockFd); 
    std::cout << "New tcp connection " << _ipV4 << ":" << _port << " has been closed." << std::endl; 
    _isConnected = false;  
} 

int TCPConnection::read()
{    
    return 1;  
}

int TCPConnection::write(char byteStream)
{
    return 1;
}


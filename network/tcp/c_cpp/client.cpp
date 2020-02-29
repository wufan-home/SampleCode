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

int TCPConnection::connect()
{
    if (_isConnected)
    {
        std::cout << "The tcp connection " << (_isIpV4 ? _ipV4 : _ipV6) << ":" << _port
                  << " has been built. No new connection is needed." << std::endl;

        return 1;
    }

    std::cout << "One new tcp connection " << _ipV4 << ":" << _port << " is built." << std::endl;
    _isConnected = true;

    return 1;
}

void TCPConnection::disconnect()
{
    std::cout << "One new tcp connection " << _ipV4 << ":" << _port << " has been closed." << std::endl;
    _isConnected = false;
}

int TCPConnection::send(char byteStream)
{
    return 1;
}

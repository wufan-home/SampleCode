#ifndef __CLIENT_H__ 
#define __CLIENT_H__

#include <cstring>
#include <iostream>
#include <unistd.h>
#include <netinet/in.h>
#include <sys/socket.h>

#include "common.h"

class TCPConnection { 
public:
    TCPConnection(char ip[], unsigned short port, bool isIpV4); 

    int init();
    void disconnect();
    
    int read();
    int write(char byteStream);
private:
    char _ipV4[16];  // C-format string: the content is 12 digits and 3 dots.
    char _ipV6[16];  // The size is not correct!!!
    unsigned short _port;  // Range: 0 to 65535. Reserved: 0 to 1023.
    
    int _sockFd;

    bool _isIpV4;
    bool _isConnected; 
};

#endif 

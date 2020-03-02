/*
 *  Name: common.h
 *  Description: Common utilities to help construct TCP connections.
 *  Platform: Ubuntu Linux 16.04.
 *  Author: Fan Wu
 *  Date: 02/29/2020
 * */

#ifndef __COMMON_H__ 
#define __COMMON_H__ 

struct TCPConnectionInfo 
{
    TCPConnectionInfo(): port(0), isIpV4(true) {} 

    char ip[30]; 
    unsigned short port; 
    bool isIpV4; 
};


class Common 
{ 
public: 
    static unsigned short getPortNumber(char portString[]); 
    static TCPConnectionInfo parstDataFile(char fileName[]);
}; 

#endif 

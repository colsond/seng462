/****************** SERVER CODE ****************/
/* http://www.programminglogic.com/example-of-client-server-program-in-c-using-sockets-and-tcp/ */


#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>
#include <errno.h>

int main(){
  int welcomeSocket, newSocket;
  char buffer[1024];
  struct sockaddr_in server;
  struct sockaddr_in client;
  socklen_t addr_size;
  char *client_ip;
  int client_port = 0;
  int bind_status = 0;

  welcomeSocket = socket(AF_INET, SOCK_STREAM, 0);
  
  if (welcomeSocket < 0) {
    fprintf(stderr,"Could not create socket: %s\n",strerror(welcomeSocket));
    return(-1);
  } else {
    fprintf(stderr,"Socket file descriptor created: %d\n",welcomeSocket);
  }

  server.sin_family = AF_INET;
  server.sin_addr.s_addr = INADDR_ANY;
//  server.sin_addr.s_addr = inet_addr("142.104.91.142");
  server.sin_port = htons(44421);
  memset(server.sin_zero, '\0', sizeof server.sin_zero);  

  if(bind(welcomeSocket, (struct sockaddr *) &server, sizeof(server))==0) {
    fprintf(stderr,"Bind successful.\n");
  } else {
    bind_status = errno;
    fprintf(stderr,"Bind failed: %s\n",strerror(bind_status));
    return(-1);
  }

  if(listen(welcomeSocket,5)==0) {
    printf("Listening\n");
  } else {
    printf("Listening error\n");
    return(-1);
  }

  addr_size = sizeof client;
  while(newSocket = accept(welcomeSocket, (struct sockaddr *) &client, &addr_size)) {
  if (newSocket<0) {
    fprintf(stderr,"Client is unacceptable.\n");
    return(-1);
  } else {
    fprintf(stderr,"Client is accepted.\n");
  }

//  client_ip = inet_ntoa(client.sin_addr);
//  client_port = ntohs(client.sin_port);

//  printf("Client connected from: %s (%d)\n",client_ip,client_port);

  recv(newSocket,buffer,1024,0);
  printf("-%s-\n",buffer);

  strcpy(buffer,"Hello World!");
  send(newSocket,buffer,13,0);
  }
  return 0;
}

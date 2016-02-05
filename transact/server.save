/****************** SERVER CODE ****************/
/* http://www.programminglogic.com/example-of-client-server-program-in-c-using-sockets-and-tcp/ */


#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>
#include <errno.h>

struct command {
  char transaction_id[10];
  char command_type[20];
  char userid[20];
  char stock[4];
  char amount[20];
};

struct command in_queue[10];

void *request_handler(void *arg);

int main(){
  int welcomeSocket, newSocket;
  char in_buffer[20];
  char out_buffer[20];
  struct sockaddr_in server;
  struct sockaddr_in client;
  socklen_t addr_size;

  pthread_t threads;

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
      fprintf(stderr,"Client is unacceptable: %s\n",strerror(errno));
      return(-1);
    } else {
      fprintf(stderr,"Client is accepted.\n");
    }

  pthread_create(&threads,NULL,(void*)&request_handler,&newSocket);
//    client_ip = inet_ntoa(client.sin_addr);
//    client_port = ntohs(client.sin_port);

//    fprintf(stderr,"Client connected from: %s (%d)\n",client_ip,client_port);

//    while(recv(newSocket,in_buffer,1024,0)) {
//      printf("-%s-\n",in_buffer);

//      strcpy(out_buffer,"Hello World!");
//      send(newSocket,out_buffer,13,0);
//    }
    pthread_join(threads, NULL);
    close(newSocket);
    fprintf(stderr,"Connection closed.\n");
  }
  return 0;
}

void *request_handler(void* arg) {

int socket_handle = *((int*)arg);
char in_buffer[1024];
char out_buffer[1024];
char scratch[1024];
char *buffer_pointer = in_buffer;
char *token;
const char delim[] = " ,";

  while(recv(socket_handle,in_buffer,1024,0)) {
    fprintf(stderr,"%s",in_buffer);
    strcpy(out_buffer,"Thanks!");
    send(socket_handle,out_buffer,8,0);
  }
/*
  recv(socket_handle,in_buffer,1024,0);


  token = strsep(&buffer_pointer,delim);
  strcpy(in_queue[0].transaction_id,token);
  token = strsep(&buffer_pointer,delim);
  strcpy(in_queue[0].command_type, token);

  if (strcmp(in_queue[0].command_type,"QUOTE") == 0) {
    token = strsep(&buffer_pointer,delim);
    strcpy(in_queue[0].userid,token);
    token = strsep(&buffer_pointer,delim);
    strcpy(in_queue[0].stock,token);
    strcpy(in_queue[0].amount,"0");

    fprintf(stderr,"%s\n%s\n",in_queue[0].command_type,in_queue[0].userid);
  } else 
  {
    fprintf(stderr,"Bad command: %s\n",in_queue[0].command_type);
  } 
*/
}//request_handler

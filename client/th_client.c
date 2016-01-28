/*http://www.programminglogic.com/example-of-client-server-program-in-c-using-sockets-and-tcp/*/
/****************** CLIENT CODE ****************/

#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>
#include <errno.h>
#include <pthread.h>

struct sockaddr_in serverAddr;
socklen_t addr_size;
int msg_max = 1;
int conn_num = 0;

void *connector(void*);

int main(int argc, char *argv[]){
//  int conn_num = 0;
  int conn_max = 1;
  int msg_num = 0;
//  int msg_max = 1;
  int count[10] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

//  pthread_t threads[10] = {0};
  pthread_t threads;

  serverAddr.sin_family = AF_INET;

  if (argc == 1) {
    printf("Not enough arguments. Use %s quote|local [# of connections] [# of msgs]\n",argv[0]);
  } else {
    if (strcmp(argv[1],"quote")==0) {
      serverAddr.sin_port = htons(4444);
      serverAddr.sin_addr.s_addr = inet_addr("142.104.90.11");
    } else
    if (strcmp(argv[1],"local")==0) {
      serverAddr.sin_port = htons(44421);
      serverAddr.sin_addr.s_addr = inet_addr("142.104.91.142");
    } else {
      printf("Use %s quote|local [# of connections] [# of msgs]\n",argv[0]);
      return(-1);
    }
  
    /* Set all bits of the padding field to 0 */
    memset(serverAddr.sin_zero, '\0', sizeof serverAddr.sin_zero);  


    addr_size = sizeof serverAddr;


    // Set the upper limit of the messages per connection. Default is 1
    if (argc > 2) {
      conn_max = atoi(argv[2]);
    }
    if (argc > 3) {
      msg_max = atoi(argv[3]);
    }

    for(conn_num=0;conn_num<conn_max;conn_num++) {
      pthread_create(&threads,NULL,(void*)&connector,&conn_num);
      pthread_join(threads, NULL);
    } //conn for loop
  }

  return 0;
}

void *connector(void *arg) {

  int msg_num = 0;
//  int msg_max = 1;
  int conn_error = 0;
  int connect_status = 0;
  int clientSocket;
  int send_status = 0;
  int recv_status = 0;
  char inBuffer[1024] = "No Data\n";
  char outBuffer[16]; // 3 for stock, 1 comma, 10 for user, 1 \n, 1 null

  int conn_num = *((int*)arg);

  clientSocket = socket(AF_INET, SOCK_STREAM, 0);

  connect_status = connect(clientSocket, (struct sockaddr *) &serverAddr, addr_size);
  conn_error = errno;

  fprintf(stderr,"Connecting thread %d...\n",conn_num);
  if (connect_status == -1) {
    fprintf(stderr,"Connection failed: %s\n",strerror(conn_error));
    pthread_exit(NULL);
  } else {
    fprintf(stderr,"Connected.\n");
  }

  for(msg_num=0;msg_num<msg_max;msg_num++) {

//    fprintf(stderr,"Type something: ");
//    fgets(outBuffer,15,stdin);
//    sprintf(outBuffer,"zYx,%5.1d\n\0",msg_num);
//    sprintf(outBuffer,"zYx,abcdefghij\n\0",msg_num);
    sprintf(outBuffer,"%cYx,a%d%c\n\0",conn_num+65,msg_num+1,65+msg_num);
    send_status = send(clientSocket, outBuffer, 16, 0);
    fprintf(stderr,"Sent -%s-\nBytes sent: %d\n",outBuffer,send_status);
    if (send_status == 16) {
      sprintf(outBuffer,"cleared");
    } else {
      fprintf(stderr,"send error\n");
    }

    recv_status = recv(clientSocket, inBuffer, 1024, 0);
    fprintf(stderr,"Received -%s-\nBytes received: %d\n",inBuffer,recv_status);
  } //msg for loop
  close(clientSocket);

}


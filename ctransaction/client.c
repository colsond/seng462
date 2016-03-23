/*http://www.programminglogic.com/example-of-client-server-program-in-c-using-sockets-and-tcp/*/
/****************** CLIENT CODE ****************/

#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>


int main(int argc, char *argv[]){
  int clientSocket;
  int connect_status=0;
  int send_status=0;
  int recv_status = 0;
  char inBuffer[1024]="No Data\n";
  char outBuffer[16]; // 3 for stock, 1 comma, 10 for user, 1 \n, 1 null
  struct sockaddr_in serverAddr;
  socklen_t addr_size;

  /*---- Create the socket. The three arguments are: ----*/
  /* 1) Internet domain 2) Stream socket 3) Default protocol (TCP in this case) */
  clientSocket = socket(PF_INET, SOCK_STREAM, 0);
  
  /*---- Configure settings of the server address struct ----*/
  /* Address family = Internet */
  serverAddr.sin_family = AF_INET;
  /* Set port number, using htons function to use proper byte order */

  if (argc == 1) {
    printf("Use %s [quote|local]\n",argv[0]);
  } else {
    if (strcmp(argv[1],"quote")==0) {
      serverAddr.sin_port = htons(4444);
      serverAddr.sin_addr.s_addr = inet_addr("142.104.90.11");
    } else
    if (strcmp(argv[1],"local")==0) {
      serverAddr.sin_port = htons(44421);
      serverAddr.sin_addr.s_addr = inet_addr("142.104.91.142");
    } else {
      serverAddr.sin_port = htons(0);
      serverAddr.sin_addr.s_addr = inet_addr("127.0.0.1");      
    }
  
    /* Set all bits of the padding field to 0 */
    memset(serverAddr.sin_zero, '\0', sizeof serverAddr.sin_zero);  

    printf("Connecting...\n");

    /*---- Connect the socket to the server using the address struct ----*/
    addr_size = sizeof serverAddr;
    connect_status = connect(clientSocket, (struct sockaddr *) &serverAddr, addr_size);

    if (connect_status < 0) {
      printf("Connection failed: %d\n",connect_status);
      return(-1);
    } else {
      fprintf(stderr,"Connected.\n");
    }

    fprintf(stderr,"Type something: ");
    fgets(outBuffer,15,stdin);
//    strcpy(outBuffer,"zYx,bcDefgh");
    send_status = send(clientSocket, outBuffer, strlen(outBuffer),0);
    fprintf(stderr,"Sent -%s-\nBytes sent: %d\n",outBuffer,send_status);

    recv_status = recv(clientSocket, inBuffer, 1024, 0);
    fprintf(stderr,"Received -%s-\nRecv: %d\n",inBuffer,recv_status);
  }
  return 0;
}

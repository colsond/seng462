/****************** SERVER CODE ****************/
/* http://www.programminglogic.com/example-of-client-server-program-in-c-using-sockets-and-tcp/ */

#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>
#include <errno.h>
#include <pthread.h>
#include <signal.h>
#include <time.h>

#define IN_BUFFER	300
#define NUM_WORKERS 200

#define STOCK_FIRST_LETTER_POS 13

#define QUOTE_LOCAL_PORT 44429
#define QUOTE_CACHE_PORT 44428
#define NUM_QUOTE_SERVERS 3
const char * quote_server_list[NUM_QUOTE_SERVERS] = {"142.104.91.131","142.104.91.138","142.104.91.135"};


struct command {
  char transaction_id[10];
  char command_type[20];
  char userid[20];
  char stock[4];
  char amount[20];
};

struct command in_queue[10];

struct queue_node {
	int socket;
	struct queue_node * next;
};

struct queue_node * queue_head = NULL;
pthread_mutex_t	queue_mutex;


void *incoming_handler(void);

int main(){
	unsigned char count = 0;
  pthread_t thread_list[NUM_WORKERS] = {0};

  unsigned int welcomeSocket;
  unsigned int new_conn;

  struct sockaddr_in server;
  struct sockaddr_in client;

  int bind_status = 0;
  socklen_t addr_size;

	struct queue_node * queue_current;


  char *client_ip;
  int client_port = 0;


	// start workers
	for (count = 0;count < NUM_WORKERS;count++) {
		 pthread_create(&thread_list[count],NULL,(void*)&incoming_handler,NULL);
	}

  welcomeSocket = socket(AF_INET, SOCK_STREAM, 0);
  
  if (welcomeSocket < 0) {
    fprintf(stderr,"Could not create socket: %s\n",strerror(welcomeSocket));
    return(-1);
  } else {
    fprintf(stderr,"Socket file descriptor created: %d\n",welcomeSocket);
  }

  server.sin_family = AF_INET;
  server.sin_addr.s_addr = INADDR_ANY;
  server.sin_port = htons(QUOTE_LOCAL_PORT);
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

	signal(SIGPIPE, SIG_IGN);

  addr_size = sizeof client;

  while(1){
		new_conn = accept(welcomeSocket, (struct sockaddr *) &client, &addr_size);
    if (new_conn<0) {
      fprintf(stderr,"Client is unacceptable: %s\n",strerror(errno));
      return(-1);
    } else {
      fprintf(stderr,"Client is accepted.\n");
			pthread_mutex_lock(&queue_mutex);
			if (queue_head == NULL) {
				queue_head = malloc(sizeof (struct queue_node));
				queue_current = queue_head;
			} else {
				queue_current->next = malloc(sizeof (struct queue_node));
				queue_current = queue_current->next;
			}
			queue_current->socket = new_conn;
			queue_current->next = NULL;
			pthread_mutex_unlock(&queue_mutex);
    }

//		fprintf(stderr,"list head %d\n",queue_head->socket);
//		fprintf(stderr,"list current %d\n",queue_current->socket);
  }
  return 0;
}

void *incoming_handler(void) {

	int socket_handle;
	int quoteSocket;
  int connect_status=0;
  int send_status=0;
  int recv_status = 0;
  struct timespec sleeptime;

  sleeptime.tv_sec = 0;
  sleeptime.tv_nsec = 10000000;	// 10 ms

	struct sockaddr_in quoteAddr;

	char in_buffer[IN_BUFFER];
	int count = 0;
	int junk = 0;

	struct queue_node * queue_curr;


	while (1) {

		pthread_mutex_lock(&queue_mutex);
		if (queue_head == NULL) {
			pthread_mutex_unlock(&queue_mutex);
			/* If theres nothing to do then wait */
			nanosleep(&sleeptime, NULL);
		} else {
			queue_curr = queue_head;
			queue_head = queue_head->next;
			pthread_mutex_unlock(&queue_mutex);

			memset(in_buffer,'\0',IN_BUFFER);

			if(recv(queue_curr->socket, in_buffer, IN_BUFFER, 0) < 0) {
				recv_status = errno;
				fprintf(stderr,"recv failed: %s\n",strerror(recv_status));
			}

			quoteSocket = socket(PF_INET, SOCK_STREAM, 0);

			// choose target server based on first character of stock quote
			// we'll do this case-sensitive, even
			if (in_buffer[STOCK_FIRST_LETTER_POS] <= 90) {
				// Upper case
				for (count=1;count<=NUM_QUOTE_SERVERS;count++) {
					junk = count*26/NUM_QUOTE_SERVERS;
					if (in_buffer[STOCK_FIRST_LETTER_POS] < (65 + junk)) {
						inet_aton(quote_server_list[count-1],&quoteAddr.sin_addr);
						break;
					}
				}
			} else {
				// Lower case
				for (count=1;count<=NUM_QUOTE_SERVERS;count++) {
					junk = count*26/NUM_QUOTE_SERVERS;
					if (in_buffer[STOCK_FIRST_LETTER_POS] < (97 + junk)) {
						inet_aton(quote_server_list[count-1],&quoteAddr.sin_addr);
						break;
					}
				}
			}

			fprintf(stderr,"Chosen quote server(char %d %c) %s:%d\n",in_buffer[STOCK_FIRST_LETTER_POS],in_buffer[STOCK_FIRST_LETTER_POS],quote_server_list[count-1],QUOTE_CACHE_PORT);
//			fprintf(stderr,"Chosen quote server %s:%d\n",inet_ntoa(quoteAddr.sin_addr),ntohs(quoteAddr.sin_port));
			quoteAddr.sin_family = AF_INET;
			quoteAddr.sin_port = htons(QUOTE_CACHE_PORT);
			memset(quoteAddr.sin_zero, '\0', sizeof quoteAddr.sin_zero);

//			fprintf(stderr,"Chosen quote server %s:%d\n",inet_ntoa(quoteAddr.sin_addr.s_addr),quoteAddr.sin_port);


			if(connect(quoteSocket, (struct sockaddr *) &quoteAddr, sizeof quoteAddr) < 0) {
				connect_status = errno;
				fprintf(stderr,"connect failed: %s\n",strerror(connect_status));
			} else {
				connect_status = errno;
//				fprintf(stderr,"connect successful: %s\n",strerror(connect_status));
			}
			
			send_status = send(quoteSocket, in_buffer, strlen(in_buffer),0);

			if (send_status < 0) {
				fprintf(stderr,"send failed\n");
			}
			else {
//				fprintf(stderr,"send not failed : %d bytes sent\n", send_status);
			}

			memset(in_buffer,'\0',IN_BUFFER);

			if(recv(quoteSocket, in_buffer, IN_BUFFER, 0) < 0) {
				recv_status = errno;
				fprintf(stderr,"recv failed: %s\n",strerror(recv_status));
			} else {
//				fprintf(stderr,"recv success?\n");
			}
//			fprintf(stderr,"recv2(%d) %s\n",queue_curr->socket,in_buffer);
//			fprintf(stderr,"recv(%d)[%c] %s\n",quoteSocket,in_buffer[STOCK_FIRST_LETTER_POS],in_buffer);

			send_status = send(queue_curr->socket, in_buffer, strlen(in_buffer),0);

			shutdown(queue_curr->socket,2);
			close(queue_curr->socket);
			free(queue_curr);

			memset(in_buffer,'\0',IN_BUFFER);

			shutdown(quoteSocket,2);
			close(quoteSocket);

		} // end if
	} //end while

}//request_handler



//    client_ip = inet_ntoa(client.sin_addr);
//    client_port = ntohs(client.sin_port);

//    fprintf(stderr,"Client connected from: %s (%d)\n",client_ip,client_port);

//    while(recv(newSocket,in_buffer,1024,0)) {
//      printf("-%s-\n",in_buffer);

//      strcpy(out_buffer,"Hello World!");
//      send(newSocket,out_buffer,13,0);
//    }
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

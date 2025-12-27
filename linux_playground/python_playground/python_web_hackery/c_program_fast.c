#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>

int main(){
    pid_t child_pid_number = 0;
    pid_t pid;
    char *process_to_run = "/bin/ls";
    printf("string is: %s\n", process_to_run);
    pid = fork();
    if (pid < 0){
        perror("fork failed");
        // exit(1);
        return 1;
    }
    if (pid == child_pid_number){
        // replaces the process from here!
        char* argv[] = { process_to_run, "-l", "-h", NULL, NULL};
        char* envp[] = { NULL };
        execv(argv[0], argv);
        printf("lol");
    } else {
        printf("parent process");
        sleep(200);
    }
}
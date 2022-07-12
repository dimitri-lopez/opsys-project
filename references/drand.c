#include <stdlib.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    srand48(0);

    printf("Seeded.\n");
    for (int i = 0; i < 100; i++) {
        printf("i: %d | %f\n", i, drand48());

    }



    return 0;
}

#define N 999

int main(int argc, char* argv[]){
        int i,k;

        float A[N+1], B[N+1];
        volatile float C[2*N+1];

        for(i = 0 ; i <= 2*N ; i++){
                C[i] = 0;
                for(k = 0 ; k <= i ; k++){
                        C[i] += (k <= N && i-k <= N) ?
                                A[k] * B[i-k]:
                                0;
                }
        }

}
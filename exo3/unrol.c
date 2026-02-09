#define UNIX        


#include <stdio.h>
#include <math.h>

#include <sys/time.h>     
#include <sys/resource.h> 


void unroll4();
void unroll8();
void unroll16();

void exit();
#define N 100
double a[N][N],b[N][N],c[N][N],bt[N][N],d[N][N];

int main(int argc, char **argv)
{
  int parm;
  int i,j;
  double sum,row_sum;
  double t_start=0.0,t_end=0.0,dtime();
  parm = 4;
  if (argc>1) (sscanf(argv[1], "%d", &parm));
/* defaults */
 if((parm!=4)&&(parm!=8)&&(parm!=16)){
   printf("%s: unrolling factor of %d not implemented\n",argv[0],parm);
   exit(1);}
   printf("%3dx%3d mm - unrolled inner loop, factor of %2d   ",N,N,parm);
     

/* set coefficients so that result matrix should have row entries
 * equal to (1/2)*n*(n-1)*i in row i
 */
  for (i=0;i<N;i++){
    for (j=0;j<N;j++){
       a[i][j] = b[i][j] = (double) i;
    }
  }

/* try to flush cache */
  for(i=0;i<N;i++){
    for (j=0;j<N;j++){
       d[i][j] = 0.0;
    }
  }

 switch(parm){
       case 4:
	 t_start = dtime();
	 unroll4();
	 t_end = dtime();
	 break;   
       case 8:
	 t_start = dtime();
	 unroll8();
	 t_end = dtime();
	 break;   
       case 16:
	 t_start = dtime();
	 unroll16();
	 t_end = dtime();
	 break; }
printf(" utime %10.2f secs\n",t_end-t_start);  


      
       
/* check result */
  sum = 0.5*((double)(N*(N-1)));
  for (i=0;i<N;i++){
    row_sum = ((double)i)*sum;
    for (j=0;j<N;j++){
       if (c[i][j]!=row_sum){
       printf("error in result entry c[%d][%d]: %e != %e\n",
		i,j,c[i][j],row_sum);
       exit(1);
       }
       if (a[i][j]!=((double)i)){
       printf("error in entry a[%d][%d]: %e != %d\n",
		i,j,a[i][j],i);
       exit(1);
       }
       if (b[i][j]!=((double)i)){
       printf("error in entry b[%d][%d]: %e != %d\n",
		i,j,b[i][j],i);
       exit(1);
       }
    }
  }
  return 0;
}

void msg(cmd)
char *cmd;
{
 /*   printf("  usage: %s -<option> [<n>]\n",cmd); */
/*    printf("  option n - normal matrix multiply\n"); */
/*    printf("  option v - normal matrix multiply using temp variable\n"); */
/*    printf("  option u - innermost loop unrolled by factor of n=4,8,16\n"); */
/*    printf("  option p - matrix multiply using pointers\n"); */
/*    printf("  option t - matrix multiply using transpose of b matrix\n"); */
/*    printf("  option i - matrix multiply with interchanged loops\n"); */
/*    printf("  option b - matrix multiply using blocking with step=n\n"); */
/*    printf("  option m - matrix multiply using Maeno method of blocking,\n"); */
/*    printf("             n specifies size of subarray (divisible by 4)\n"); */
/*    printf("  option w - matrix multiply using Warner method of blocking,\n"); */
/*    printf("             n specifies size of subarray (divisible by 2)\n"); */
/*    printf("  option r - matrix multiply using the Robert method with:\n"); */
/*    printf("             b transpose, pointers, and temporary variables\n"); */
}


void unroll4(){
    int i,j,k;
    double temp;
    for (i=0;i<N;i++){
       for (j=0;j<N;j++){
	   temp = 0.0;
	   for (k=0;k<(N-3);k+=4){
	       temp += a[i][k]*b[k][j];
	       temp += a[i][k+1]*b[k+1][j];
	       temp += a[i][k+2]*b[k+2][j];
	       temp += a[i][k+3]*b[k+3][j];
	   }
	   for (;k<N;k++){
	       temp += a[i][k]*b[k][j];
	   }
	   c[i][j] = temp;
       }
    }
}

void unroll8(){
    int i,j,k;
    double temp;
    for (i=0;i<N;i++){
       for (j=0;j<N;j++){
	   temp = 0.0;
	   for (k=0;k<(N-7);k+=8){
	       temp += a[i][k]*b[k][j];
	       temp += a[i][k+1]*b[k+1][j];
	       temp += a[i][k+2]*b[k+2][j];
	       temp += a[i][k+3]*b[k+3][j];
	       temp += a[i][k+4]*b[k+4][j];
	       temp += a[i][k+5]*b[k+5][j];
	       temp += a[i][k+6]*b[k+6][j];
	       temp += a[i][k+7]*b[k+7][j];
	   }
	   for (;k<N;k++){
	       temp += a[i][k]*b[k][j];
	   }
	   c[i][j] = temp;
       }
    }
}

void unroll16(){
    int i,j,k;
    double temp;
    for (i=0;i<N;i++){
       for (j=0;j<N;j++){
	   temp = 0.0;
	   for (k=0;k<(N-15);k+=16){
	       temp += a[i][k]*b[k][j];
	       temp += a[i][k+1]*b[k+1][j];
	       temp += a[i][k+2]*b[k+2][j];
	       temp += a[i][k+3]*b[k+3][j];
	       temp += a[i][k+4]*b[k+4][j];
	       temp += a[i][k+5]*b[k+5][j];
	       temp += a[i][k+6]*b[k+6][j];
	       temp += a[i][k+7]*b[k+7][j];
	       temp += a[i][k+8]*b[k+8][j];
	       temp += a[i][k+9]*b[k+9][j];
	       temp += a[i][k+10]*b[k+10][j];
	       temp += a[i][k+11]*b[k+11][j];
	       temp += a[i][k+12]*b[k+12][j];
	       temp += a[i][k+13]*b[k+13][j];
	       temp += a[i][k+14]*b[k+14][j];
	       temp += a[i][k+15]*b[k+15][j];
	   }
	   for (;k<N;k++){
	       temp += a[i][k]*b[k][j];
	   }
	   c[i][j] = temp;
       }
    }
}


/*****************************************************/
/* Various timer routines.                           */
/* Al Aburto, aburto@nosc.mil, 18 Feb 1997           */
/*                                                   */
/* t = dtime() outputs the current time in seconds.  */
/* Use CAUTION as some of these routines will mess   */
/* up when timing across the hour mark!!!            */
/*                                                   */
/* For timing I use the 'user' time whenever         */
/* possible. Using 'user+sys' time is a separate     */
/* issue.                                            */
/*                                                   */
/* Example Usage:                                    */
/* [timer options added here]                        */
/* main()                                            */
/* {                                                 */
/* double starttime,benchtime,dtime();               */
/*                                                   */
/* starttime = dtime();                              */ 
/* [routine to time]                                 */
/* benchtime = dtime() - starttime;                  */
/* }                                                 */
/*                                                   */
/* [timer code below added here]                     */
/*****************************************************/

/*****************************************************/
/*  UNIX dtime(). This is the preferred UNIX timer.  */
/*  Provided by: Markku Kolkka, mk59200@cc.tut.fi    */
/*  HP-UX Addition by: Bo Thide', bt@irfu.se         */
/*****************************************************/
#ifdef UNIX
#include <sys/time.h>
#include <sys/resource.h>

#ifdef hpux
#include <sys/syscall.h>
#define getrusage(a,b) syscall(SYS_getrusage,a,b)
#endif

struct rusage rusage;

double dtime()
{
 double q;

 getrusage(RUSAGE_SELF,&rusage);

 q = (double)(rusage.ru_utime.tv_sec);
 q = q + (double)(rusage.ru_utime.tv_usec) * 1.0e-06;
	
 return q;
}
#endif

/***************************************************/
/*  UNIX_Old dtime(). This is the old UNIX timer.  */
/*  Make sure HZ is properly defined in param.h !! */
/***************************************************/
#ifdef UNIX_Old
#include <sys/types.h>
#include <sys/times.h>
#include <sys/param.h>

#ifndef HZ
#define HZ 60
#endif

struct tms tms;

double dtime()
{
 double q;

 times(&tms);

 q = (double)(tms.tms_utime) / (double)HZ;
	
 return q;
}
#endif


/********************************************/
/* Another UNIX timer using gettimeofday(). */
/* However, getrusage() is preferred.       */
/********************************************/
#ifdef GTODay
#include <sys/time.h>

struct timeval tnow;

double dtime()
{
 double q;

 gettimeofday(&tnow,NULL);
 q = (double)tnow.tv_sec + (double)tnow.tv_usec * 1.0e-6;

 return q;
}
#endif


/*-------- End of mm.c, say goodnight Becky! (Sep 1992) --------*/



#define inBounds(i,N) ((i>=0)&&(i<N))


__kernel void bilateral( __global float* input, __global float* output,const int N, const int width, const float beta)
{
  int i = get_global_id(0);


  float res = 0;
  float sum = 0;
  float val0 = input[i];
  float val1;
  float weight;
  
  for(int j = -width;j<=width;j++){
	
	if inBounds(i+j,N) {
		
  		  val1  = input[i+j];
  		  weight = exp(-beta*.5f*(val0-val1)*(val0-val1));
  		  res += val1*weight;
  		  sum += weight;
  		}

  }

  output[i] = res/sum;
    
  
}

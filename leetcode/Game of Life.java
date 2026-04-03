class Solution {
    public void gameOfLife(int[][] matrix) {

        // number of rows
        int n = matrix.length;

        // number of columns
        int m = matrix[0].length;

        // creating a duplicate matrix to store state
        int[][] dup = new int[n][m];
        for(int i = 0; i < n; i++ ){
            for(int j = 0; j < m ; j++ ){
                dup[i][j]=matrix[i][j];
            }
        }

        // iterating through matrix
        for(int i = 0; i < n; i++ ){
            for(int j = 0; j < m; j++ ){

                // counting state of 8 neighbours
                // always run 9 times -> Time :: O(1) 
                int sum = 0;
                for(int x = -1; x <= 1 ; x++ ){
                    for(int y = -1; y <= 1 ; y++){
                        int r=i+x;
                        int c=j+y;
                        if( r >= 0 && c >= 0 && r < n && c < m){
                            // neglect its own status
                            if(x==0 && y==0){
                                continue;
                            }else{
                                sum+=dup[r][c];
                            }
                        }
                    }
                }

                // checking current state of element
                if(dup[i][j] == 1){
                    if(sum < 2) matrix[i][j]=0;
                    else if(sum > 3) matrix[i][j]=0;
                }else{
                    if(sum == 3) matrix[i][j]=1;
                }
            }
        }
    }
}